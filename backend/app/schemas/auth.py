"""Authentication schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User creation schema (admin only)."""
    account_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_admin: bool = False


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    account_name: str
    email: str
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None


class AnalysisHistory(BaseModel):
    """Analysis history entry schema."""
    id: int
    analysis_type: str
    filename: str
    results: dict
    timestamp: datetime
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """History response schema with pagination."""
    history: List[AnalysisHistory]
    total: int
    page: int
    page_size: int
    has_more: bool
