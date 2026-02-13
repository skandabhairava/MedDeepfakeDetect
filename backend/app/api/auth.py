"""Authentication API endpoints."""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_settings
from ..core.logging import get_logger
from ..schemas.auth import (
    UserCreate, UserLogin, UserResponse, PasswordChange, 
    Token, HistoryResponse
)
from ..services.auth import auth_service
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


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin) -> Token:
    """Authenticate user and return access token."""
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


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Change user password."""
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
    
    return {"message": "Password changed successfully"}


@router.get("/history", response_model=HistoryResponse)
async def get_user_history(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
) -> HistoryResponse:
    """Get user analysis history with pagination."""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 50:
        page_size = 10
    
    history_data = db.get_user_history(current_user["id"], page, page_size)
    
    return HistoryResponse(**history_data)


@router.delete("/history/{history_id}")
async def delete_history_item(
    history_id: int,
    current_user: dict = Depends(get_current_user)
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
    """List all users (admin only)."""
    # This would require adding a list_users method to the database
    # For now, return empty list as placeholder
    return []
