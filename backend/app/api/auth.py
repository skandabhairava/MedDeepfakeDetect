"""Authentication API endpoints."""

import json
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_settings
from ..core.logging import get_logger
from ..schemas.auth import (
    UserCreate, UserLogin, UserResponse, PasswordChange,
    Token, HistoryResponse
)
from ..services.auth import auth_service
from ..services.encryption import encryption_service
from ..models.database import db

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger("api.auth")
security = HTTPBearer()
settings = get_settings()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user."""
    token = credentials.credentials
    user = auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current authenticated admin user."""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_consented_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Validate that the authenticated user has signed the mandatory initial Study Agreement.

    If study_consent_accepted_at is NULL, access to platform features is strictly locked.
    """
    if not current_user.get("study_consent_accepted_at"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Study Agreement Required: You must review and accept the mandatory Study Agreement and de-identification warranty before accessing platform features."
        )
    return current_user


def _decrypt_history_entry(entry: dict, key: Optional[bytes]) -> dict:
    """Decrypt image_base64, results.gradcam_base64, filename, and name in a history entry.

    If *key* is None or decryption fails, the raw (ciphertext) value is
    returned — the frontend must handle missing image gracefully.
    """
    if key is None:
        return entry

    # Decrypt filename
    raw_filename = entry.get("filename")
    if raw_filename:
        try:
            entry["filename"] = encryption_service.decrypt(raw_filename, key)
        except ValueError:
            logger.warning(f"Failed to decrypt filename for history entry {entry.get('id')}")

    # Decrypt name
    raw_name = entry.get("name")
    if raw_name:
        try:
            entry["name"] = encryption_service.decrypt(raw_name, key)
        except ValueError:
            logger.warning(f"Failed to decrypt name for history entry {entry.get('id')}")

    # Decrypt image_base64
    raw_image = entry.get("image_base64")
    if raw_image:
        try:
            entry["image_base64"] = encryption_service.decrypt(raw_image, key)
        except ValueError:
            logger.warning(f"Failed to decrypt image_base64 for history entry {entry.get('id')}")
            entry["image_base64"] = None  # Surface as missing rather than garbled

    # Decrypt results.gradcam_base64
    results = entry.get("results")
    if isinstance(results, dict):
        raw_gradcam = results.get("gradcam_base64")
        if raw_gradcam:
            try:
                results["gradcam_base64"] = encryption_service.decrypt(raw_gradcam, key)
            except ValueError:
                logger.warning(
                    f"Failed to decrypt gradcam_base64 for history entry {entry.get('id')}"
                )
                results["gradcam_base64"] = None
        entry["results"] = results

    return entry


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin) -> Token:
    """Authenticate user, cache encryption key, return access token."""
    user = auth_service.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        logger.warning(f"Login failed for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    """Evict the cached encryption key and invalidate the session.

    The JWT itself is stateless and continues to be valid until expiry —
    the frontend should discard it.  The encryption key is immediately
    removed from memory, so no further decryption is possible with this
    session's key even if the token is reused.
    """
    auth_service.evict_cached_key(current_user["id"])
    logger.info(f"User {current_user['email']} logged out; encryption key evicted")
    return {"message": "Logged out successfully"}


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_admin_user)
) -> UserResponse:
    """Create a new user (admin only)."""
    try:
        user_id = auth_service.create_user(
            account_name=user_data.account_name,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin
        )

        user = db.get_user_by_id(user_id)
        return UserResponse(**user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Get current user information."""
    return UserResponse(**current_user)


@router.delete("/me")
async def delete_current_user_account(current_user: dict = Depends(get_current_user)) -> dict:
    """Delete current user account and all associated analysis history (Apple Guideline 5.1.1(v) & GDPR Art. 17)."""
    user_id = current_user["id"]
    auth_service.evict_cached_key(user_id)

    success = db.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already deleted"
        )
    logger.info(f"User self-deleted account: {current_user['email']} (ID: {user_id})")
    return {"message": "Account and all associated data permanently deleted"}


@router.post("/study-consent", response_model=UserResponse)
async def accept_study_consent(request: Request, current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Record that the authenticated user has accepted the First-Login Study Agreement.

    This endpoint is called by the mandatory first-login modal. The server
    timestamps the acceptance in UTC and persists it to the users table.
    The modal cannot be dismissed without calling this endpoint — the
    timestamp serves as the audit record.
    """
    from datetime import datetime, timezone as tz
    accepted_at = datetime.now(tz.utc).isoformat()
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    db.set_study_consent(current_user["id"], accepted_at, ip_addr, user_agent)
    logger.info(
        f"First-login study consent accepted: user={current_user['email']} "
        f"(ID={current_user['id']}) at={accepted_at}"
    )
    # Return the updated user record so the frontend can update its store
    updated_user = db.get_user_by_id(current_user["id"])
    return UserResponse(**updated_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_consented_user)
) -> dict:
    """Change user password and transparently re-encrypt all image data in background."""
    success = auth_service.change_password(
        user_id=current_user["id"],
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return {"message": "Password changed successfully. All image data has been re-encrypted."}


@router.get("/history", response_model=HistoryResponse)
async def get_user_history(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_consented_user)
) -> HistoryResponse:
    """Get user analysis history with pagination (images decrypted transparently)."""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 50:
        page_size = 10

    history_data = db.get_user_history(current_user["id"], page, page_size)

    # Retrieve the cached AES key for this user
    key = auth_service.get_cached_key(current_user["id"])
    if key is None:
        logger.warning(
            f"No cached encryption key for user {current_user['id']}; "
            "history images will not be decrypted. User should re-login.",
            extra={"event": f"No cached encryption key for user {current_user['id']}; history images will not be decrypted. User should re-login."}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Your session encryption key has expired. Please log in again to access your history.",
                "error_code": "encryption_key_expired",
            },
        )

    # Decrypt each entry in-place
    history_data["history"] = [
        _decrypt_history_entry(entry, key)
        for entry in history_data["history"]
    ]

    return HistoryResponse(**history_data)



@router.delete("/history/{history_id}")
async def delete_history_item(
    history_id: int,
    current_user: dict = Depends(get_current_consented_user)
) -> dict:
    """Delete a specific analysis history item."""
    success = db.delete_analysis_history(current_user["id"], history_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="History item not found or you don't have permission to delete it"
        )

    return {"message": "History item deleted successfully"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(current_user: dict = Depends(get_admin_user)) -> list[UserResponse]:
    """List all users with their analysis counts (admin only)."""
    users = db.list_users()
    return [UserResponse(**u) for u in users]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Delete a user account and their analysis history.

    A user can delete their own account (self-service deletion),
    and an administrator can delete any user account.
    """
    if not current_user.get("is_admin", False) and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this account"
        )

    # Evict the encryption key for the deleted user
    auth_service.evict_cached_key(user_id)

    success = db.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"User {user_id} deleted by {current_user['email']}")
    return {"message": "Account and all associated data permanently deleted"}
