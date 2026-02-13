"""Authentication service."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
import bcrypt

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.database import db
from ..schemas.auth import TokenData

logger = get_logger("services.auth")
settings = get_settings()

# Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        
        # Create default admin if no users exist
        self._create_default_admin()
    
    def _create_default_admin(self) -> None:
        """Create default admin user if no users exist."""
        existing_users = db.get_user_by_email("admin@medicaldeepfake.com")
        if not existing_users:
            default_password = "admin123"  # Change this in production
            password_hash = self.hash_password(default_password)
            db.create_user(
                account_name="Administrator",
                email="admin@medicaldeepfake.com",
                password_hash=password_hash,
                is_admin=True
            )
            logger.warning("Created default admin user. Please change the default password!")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    def verify_password(self, plain_password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and extract user data."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            token_data = TokenData(email=email)
            return token_data
        except JWTError:
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password."""
        user = db.get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        logger.info(f"User authenticated: {email}")
        return user
    
    def create_user(self, account_name: str, email: str, password: str, is_admin: bool = False) -> int:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password and create user
        password_hash = self.hash_password(password)
        user_id = db.create_user(account_name, email, password_hash, is_admin)
        
        logger.info(f"Created new user: {email} (Admin: {is_admin})")
        return user_id
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = db.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not self.verify_password(current_password, user["password_hash"]):
            return False
        
        # Update password
        new_password_hash = self.hash_password(new_password)
        success = db.update_user_password(user_id, new_password_hash)
        
        if success:
            logger.info(f"Password changed for user ID: {user_id}")
        
        return success
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by JWT token."""
        token_data = self.verify_token(token)
        if not token_data:
            return None
        
        user = db.get_user_by_email(token_data.email)
        return user


# Global auth service instance
auth_service = AuthService()
