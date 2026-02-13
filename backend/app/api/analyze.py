"""Analysis API endpoints."""

import time
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_settings
from ..core.logging import get_logger, log_request_info
from ..schemas import AnalysisResponse
from ..services import ModelService
from ..services.auth import auth_service
from ..models.database import db
from ..utils import (
    FileValidationError,
    save_upload_file,
    cleanup_temp_file
)

router = APIRouter(prefix="/analyze", tags=["analysis"])
logger = get_logger("api.analyze")
model_service = ModelService()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user."""
    token = credentials.credentials
    user = auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/xray", response_model=AnalysisResponse)
async def analyze_xray(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> AnalysisResponse:
    """Analyze knee X-ray image for authenticity and arthritis severity.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded X-ray image file
        current_user: Authenticated user
        
    Returns:
        Analysis results
        
    Raises:
        HTTPException: If file validation or analysis fails
    """
    request_id = f"xray_{int(time.time())}"
    start_time = time.time()
    
    log_request_info(
        request_id=request_id,
        method="POST",
        path="/analyze/xray",
        filename=file.filename,
        content_type=file.content_type
    )
    
    temp_file_path = None
    
    try:
        # Validate and save uploaded file
        temp_file_path = save_upload_file(file)
        
        # Run analysis
        results = model_service.analyze_xray(temp_file_path)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        # Convert to response format
        response = AnalysisResponse(**results)
        
        # Store in user history
        try:
            confidence = results.get("confidence")
            db.add_analysis_history(
                user_id=current_user["id"],
                analysis_type="xray",
                filename=file.filename,
                results=results,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Failed to store analysis history: {str(e)}")
        
        logger.info(
            "xray_analysis_success",
            request_id=request_id,
            filename=file.filename,
            processing_time=time.time() - start_time,
            status=results.get("status", "unknown"),
            user_id=current_user["id"]
        )
        
        return response
        
    except FileValidationError as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.warning(
            "xray_analysis_validation_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File validation failed",
                "message": str(e),
                "request_id": request_id
            }
        )
        
    except Exception as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.error(
            "xray_analysis_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": "Internal server error during analysis",
                "request_id": request_id
            }
        )


@router.post("/ct", response_model=AnalysisResponse)
async def analyze_ct_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> AnalysisResponse:
    """Analyze CT scan image for authenticity.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded CT scan image file
        current_user: Authenticated user
        
    Returns:
        Analysis results
        
    Raises:
        HTTPException: If file validation or analysis fails
    """
    request_id = f"ct_{int(time.time())}"
    start_time = time.time()
    
    log_request_info(
        request_id=request_id,
        method="POST",
        path="/analyze/ct",
        filename=file.filename,
        content_type=file.content_type
    )
    
    temp_file_path = None
    
    try:
        # Validate and save uploaded file
        temp_file_path = save_upload_file(file)
        
        # Run analysis
        results = model_service.analyze_ct_scan(temp_file_path)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        # Convert to response format
        response = AnalysisResponse(**results)
        
        # Store in user history
        try:
            confidence = results.get("confidence")
            db.add_analysis_history(
                user_id=current_user["id"],
                analysis_type="ct",
                filename=file.filename,
                results=results,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Failed to store analysis history: {str(e)}")
        
        logger.info(
            "ct_analysis_success",
            request_id=request_id,
            filename=file.filename,
            processing_time=time.time() - start_time,
            status=results.get("status", "unknown"),
            user_id=current_user["id"]
        )
        
        return response
        
    except FileValidationError as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.warning(
            "ct_analysis_validation_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File validation failed",
                "message": str(e),
                "request_id": request_id
            }
        )
        
    except Exception as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.error(
            "ct_analysis_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": "Internal server error during analysis",
                "request_id": request_id
            }
        )
