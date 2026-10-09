"""Authentication service with per-user encryption key management."""

import json
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple

from jose import JWTError, jwt
import bcrypt

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.database import db
from ..schemas.auth import TokenData
from .encryption import encryption_service

logger = get_logger("services.auth")
settings = get_settings()


# ---------------------------------------------------------------------------
# In-memory session key cache
# ---------------------------------------------------------------------------
# Maps user_id -> (key_bytes, expires_at_datetime_utc)
# Protected by a threading.Lock — this dict is written by login and read by
# every authenticated request that needs to decrypt / encrypt image data.
# ---------------------------------------------------------------------------

_KEY_CACHE: Dict[int, Tuple[bytes, datetime]] = {}
_CACHE_LOCK = threading.Lock()


class AuthService:
    """Authentication service with integrated encryption key lifecycle."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.access_token_expire_minutes

        # Create default admin if no users exist
        self._create_default_admin()

    # ------------------------------------------------------------------
    # Default admin bootstrap
    # ------------------------------------------------------------------

    def _create_default_admin(self) -> None:
        """Create default admin user if no users exist."""
        existing_users = db.get_user_by_email("admin@medveri.xyz")
        if not existing_users:
            default_password = settings.admin_default
            password_hash = self.hash_password(default_password)
            user_id = db.create_user(
                account_name="Administrator",
                email="admin@medveri.xyz",
                password_hash=password_hash,
                is_admin=True,
            )
            # Assign encryption salt immediately
            salt = encryption_service.generate_salt()
            db.set_user_encryption_salt(user_id, salt.hex())
            logger.warning("Created default admin user. Please change the default password!")

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed: str) -> bool:
        """Verify a password against its bcrypt hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed.encode("utf-8"),
        )

    # ------------------------------------------------------------------
    # JWT helpers
    # ------------------------------------------------------------------

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a signed JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT and extract user data."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            return TokenData(email=email)
        except JWTError:
            return None

    # ------------------------------------------------------------------
    # Session key cache
    # ------------------------------------------------------------------

    def _cache_key(self, user_id: int, key: bytes) -> None:
        """Store derived key in the in-memory cache with a TTL."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        with _CACHE_LOCK:
            _KEY_CACHE[user_id] = (key, expires_at)
        logger.debug(f"Cached encryption key for user {user_id}")

    def get_cached_key(self, user_id: int) -> Optional[bytes]:
        """Return the cached AES key for *user_id*, or None if absent / expired."""
        with _CACHE_LOCK:
            entry = _KEY_CACHE.get(user_id)
            if entry is None:
                return None
            key, expires_at = entry
            if datetime.now(timezone.utc) >= expires_at:
                del _KEY_CACHE[user_id]
                logger.debug(f"Evicted expired encryption key for user {user_id}")
                return None
            return key

    def evict_cached_key(self, user_id: int) -> None:
        """Remove the cached key for *user_id* (called on logout)."""
        with _CACHE_LOCK:
            _KEY_CACHE.pop(user_id, None)
        logger.debug(f"Evicted encryption key for user {user_id}")

    def _derive_and_cache_key(self, user_id: int, password: str) -> Optional[bytes]:
        """Derive the AES key from password + salt, cache it, and return it."""
        salt_hex = db.get_user_encryption_salt(user_id)
        if not salt_hex:
            logger.error(f"No encryption salt found for user {user_id}")
            return None
        salt = bytes.fromhex(salt_hex)
        key = encryption_service.derive_key(password, salt)
        self._cache_key(user_id, key)
        return key

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user, derive + cache the encryption key, return user dict."""
        user = db.get_user_by_email(email)
        if not user:
            return None

        if not self.verify_password(password, user["password_hash"]):
            return None

        # Derive and cache AES key from plaintext password (in-memory only)
        self._derive_and_cache_key(user["id"], password)

        logger.info(f"User authenticated: {email}")
        return user

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def create_user(self, account_name: str, email: str, password: str,
                    is_admin: bool = False) -> int:
        """Create a new user with a freshly generated encryption salt."""
        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        password_hash = self.hash_password(password)
        user_id = db.create_user(account_name, email, password_hash, is_admin)

        # Generate and store per-user Argon2 salt immediately
        salt = encryption_service.generate_salt()
        db.set_user_encryption_salt(user_id, salt.hex())

        logger.info(f"Created new user: {email} (Admin: {is_admin})")
        return user_id

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password and transparently re-encrypt all image data.

        Steps:
          1. Verify current password (bcrypt).
          2. Derive old AES key from current password.
          3. Fetch all analysis rows and decrypt image_base64 / gradcam_base64
             with the old key.
          4. Generate a new Argon2 salt, derive a new AES key.
          5. Re-encrypt every image field with the new key.
          6. Persist new salt, new password hash, re-encrypted blobs atomically.
        """
        user = db.get_user_by_id(user_id)
        if not user:
            return False

        if not self.verify_password(current_password, user["password_hash"]):
            return False

        # --- Step 2: derive old key ---
        old_salt_hex = db.get_user_encryption_salt(user_id)
        if old_salt_hex:
            old_salt = bytes.fromhex(old_salt_hex)
            old_key = encryption_service.derive_key(current_password, old_salt)
        else:
            old_key = None

        # --- Step 3: fetch all history rows ---
        rows = db.get_user_history_for_reencrypt(user_id)

        # --- Step 4: new salt + key ---
        new_salt = encryption_service.generate_salt()
        new_key = encryption_service.derive_key(new_password, new_salt)

        # --- Step 5: re-encrypt each row ---
        reencrypted = []
        for row in rows:
            new_image_b64 = row["image_base64"]
            results_dict = json.loads(row["results"]) if isinstance(row["results"], str) else row["results"]
            new_filename = row.get("filename")
            new_name = row.get("name")

            # Re-encrypt image_base64
            if new_image_b64 and old_key:
                try:
                    plaintext = encryption_service.decrypt(new_image_b64, old_key)
                    new_image_b64 = encryption_service.encrypt(plaintext, new_key)
                except ValueError:
                    # Could not decrypt — leave as-is (e.g. corrupted entry)
                    logger.warning(f"Could not re-encrypt image_base64 for history {row['id']}")

            # Re-encrypt gradcam_base64 inside results
            gradcam = results_dict.get("gradcam_base64")
            if gradcam and old_key:
                try:
                    plaintext = encryption_service.decrypt(gradcam, old_key)
                    results_dict["gradcam_base64"] = encryption_service.encrypt(plaintext, new_key)
                except ValueError:
                    logger.warning(f"Could not re-encrypt gradcam_base64 for history {row['id']}")

            # Re-encrypt filename metadata
            if new_filename and old_key:
                try:
                    plaintext = encryption_service.decrypt(new_filename, old_key)
                    new_filename = encryption_service.encrypt(plaintext, new_key)
                except ValueError:
                    logger.warning(f"Could not re-encrypt filename for history {row['id']}")

            # Re-encrypt name metadata
            if new_name and old_key:
                try:
                    plaintext = encryption_service.decrypt(new_name, old_key)
                    new_name = encryption_service.encrypt(plaintext, new_key)
                except ValueError:
                    logger.warning(f"Could not re-encrypt name for history {row['id']}")

            reencrypted.append((row["id"], new_image_b64, json.dumps(results_dict), new_filename, new_name))

        # --- Step 6: persist everything ---
        new_password_hash = self.hash_password(new_password)
        db.update_user_password(user_id, new_password_hash)
        db.set_user_encryption_salt(user_id, new_salt.hex())

        for (hist_id, img, results_json, fname, nm) in reencrypted:
            db.update_analysis_images(hist_id, img, results_json, fname, nm)

        # Update the in-memory cache with the new key
        self._cache_key(user_id, new_key)

        logger.info(
            f"Password changed and {len(reencrypted)} history rows re-encrypted "
            f"for user ID: {user_id}"
        )
        return True

    # ------------------------------------------------------------------
    # Token-based user lookup
    # ------------------------------------------------------------------

    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by JWT token."""
        token_data = self.verify_token(token)
        if not token_data:
            return None
        return db.get_user_by_email(token_data.email)


# Global auth service instance
auth_service = AuthService()
