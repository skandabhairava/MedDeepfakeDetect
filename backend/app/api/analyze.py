"""Analysis API endpoints."""

import time
import base64
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_settings
from ..core.logging import get_logger, log_request_info
from ..schemas import AnalysisResponse
from ..services import ModelService, queue_service
from ..services.auth import auth_service
from ..services.encryption import encryption_service
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


def get_current_consented_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Validate that the authenticated user has signed the mandatory initial Study Agreement.

    If study_consent_accepted_at is NULL, access to analysis features is strictly forbidden.
    """
    if not current_user.get("study_consent_accepted_at"):
        raise HTTPException(
            status_code=403,
            detail="Study Agreement Required: You must review and accept the mandatory Study Agreement and de-identification warranty before accessing analysis features."
        )
    return current_user


@router.post("/xray")
async def analyze_xray(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    consent_confirmed: bool = Form(True),
    current_user: dict = Depends(get_current_consented_user)
) -> Dict:
    """Analyze knee X-ray image for authenticity and arthritis severity.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded X-ray image file
        name: Analysis study label
        consent_confirmed: Mandatory clinician de-identification certification
        current_user: Authenticated user
        
    Returns:
        Queue submission response with analysis ID and queue position
        
    Raises:
        HTTPException: If file validation or queue submission fails
    """
    if not consent_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Patient consent and de-identification certification are mandatory."
        )

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
    image_base64 = None
    
    try:
        # Check rate limit BEFORE processing file
        can_analyze, wait_time = db.can_user_analyze(
            current_user["id"], 
            queue_service.settings.analysis_rate_limit_seconds
        )
        
        if not can_analyze:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Rate limit exceeded. Please wait {wait_time} seconds.",
                    "wait_time": wait_time,
                    "request_id": request_id
                }
            )
        
        # Read file content as base64
        file_content = await file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Reset file pointer for saving
        file.file.seek(0)
        
        # Validate and save uploaded file
        temp_file_path = save_upload_file(file)
        
        # Submit to queue with consent audit confirmation
        ip_addr = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        queue_result = queue_service.submit_analysis(
            user_id=current_user["id"],
            analysis_type="xray",
            filename=file.filename,
            name=name,
            image_base64=image_base64,
            temp_file_path=temp_file_path,
            consent_confirmed=consent_confirmed,
            consent_ip_addr=ip_addr,
            consent_usr_agent=user_agent
        )
        
        logger.info(
            "xray_analysis_queued",
            request_id=request_id,
            filename=file.filename,
            history_id=queue_result["history_id"],
            queue_position=queue_result["queue_position"],
            user_id=current_user["id"],
            processing_time=time.time() - start_time
        )
        
        return {
            "success": True,
            "message": "Analysis submitted to queue",
            "history_id": queue_result["history_id"],
            "status": queue_result["status"],
            "queue_position": queue_result["queue_position"],
            "estimated_wait_time": queue_result["estimated_wait_time"]
        }
        
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

    except HTTPException:
        raise
        
    except Exception as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.error(
            "xray_analysis_queue_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Queue submission failed",
                "message": "Internal server error during queue submission",
                "request_id": request_id
            }
        )


@router.post("/ct")
async def analyze_ct_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    consent_confirmed: bool = Form(True),
    current_user: dict = Depends(get_current_consented_user)
) -> Dict:
    """Analyze CT scan image for authenticity.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded CT scan image file
        name: Analysis study label
        consent_confirmed: Mandatory clinician de-identification certification
        current_user: Authenticated user
        
    Returns:
        Queue submission response with analysis ID and queue position
        
    Raises:
        HTTPException: If file validation or queue submission fails
    """
    if not consent_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Patient consent and de-identification certification are mandatory."
        )

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
    image_base64 = None
    
    try:
        # Check rate limit BEFORE processing file
        can_analyze, wait_time = db.can_user_analyze(
            current_user["id"], 
            queue_service.settings.analysis_rate_limit_seconds
        )
        
        if not can_analyze:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Rate limit exceeded. Please wait {wait_time} seconds.",
                    "wait_time": wait_time,
                    "request_id": request_id
                }
            )
        
        # Read file content as base64
        file_content = await file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Reset file pointer for saving
        file.file.seek(0)
        
        # Validate and save uploaded file
        temp_file_path = save_upload_file(file)
        
        # Submit to queue with consent audit confirmation
        queue_result = queue_service.submit_analysis(
            user_id=current_user["id"],
            analysis_type="ct",
            filename=file.filename,
            name=name,
            image_base64=image_base64,
            temp_file_path=temp_file_path,
            consent_confirmed=consent_confirmed
        )
        
        logger.info(
            "ct_analysis_queued",
            request_id=request_id,
            filename=file.filename,
            history_id=queue_result["history_id"],
            queue_position=queue_result["queue_position"],
            user_id=current_user["id"],
            processing_time=time.time() - start_time
        )
        
        return {
            "success": True,
            "message": "Analysis submitted to queue",
            "history_id": queue_result["history_id"],
            "status": queue_result["status"],
            "queue_position": queue_result["queue_position"],
            "estimated_wait_time": queue_result["estimated_wait_time"]
        }
        
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

    except HTTPException:
        raise
        
    except Exception as e:
        # Clean up file if it exists
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
        logger.error(
            "ct_analysis_queue_error",
            request_id=request_id,
            filename=file.filename,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Queue submission failed",
                "message": "Internal server error during queue submission",
                "request_id": request_id
            }
        )


@router.get("/status/{history_id}")
async def get_analysis_status(
    history_id: int,
    current_user: dict = Depends(get_current_consented_user)
) -> Dict:
    """Get analysis status by history ID.
    
    Args:
        history_id: Analysis history ID
        current_user: Authenticated user
        
    Returns:
        Analysis status information
        
    Raises:
        HTTPException: If analysis not found or access denied
    """
    try:
        # Get analysis status
        status_info = queue_service.get_analysis_status(history_id)
        
        if not status_info:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Analysis not found",
                    "message": f"Analysis with ID {history_id} not found"
                }
            )
        
        # Verify user owns this analysis
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM analysis_history WHERE id = ?",
                (history_id,)
            )
            row = cursor.fetchone()
            if not row or row["user_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Access denied",
                        "message": "You don't have permission to access this analysis"
                    }
                )
        
        # Get queue stats if still pending
        if status_info["status"] == "pending":
            queue_stats = queue_service.get_queue_stats()
            status_info["queue_stats"] = queue_stats

        # Decrypt gradcam_base64 in completed results
        if status_info["status"] == "completed":
            results = status_info.get("results")
            if isinstance(results, str):
                import json as _json
                results = _json.loads(results)
                status_info["results"] = results
            if isinstance(results, dict) and results.get("gradcam_base64"):
                key = auth_service.get_cached_key(current_user["id"])
                if key:
                    try:
                        results["gradcam_base64"] = encryption_service.decrypt(
                            results["gradcam_base64"], key
                        )
                    except ValueError:
                        logger.warning(
                            f"Failed to decrypt gradcam_base64 in status for "
                            f"history {history_id}"
                        )
                        results["gradcam_base64"] = None
                else:
                    logger.warning(
                        f"No cached key for user {current_user['id']}; "
                        "forcing re-login (encryption_key_expired)."
                    )
                    from fastapi import status as http_status
                    raise HTTPException(
                        status_code=http_status.HTTP_401_UNAUTHORIZED,
                        detail={
                            "message": "Your session encryption key has expired. Please log in again.",
                            "error_code": "encryption_key_expired",
                        },
                    )

        return {
            "success": True,
            "status": status_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status {history_id}: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Status check failed",
                "message": "Internal server error while checking analysis status"
            }
        )
