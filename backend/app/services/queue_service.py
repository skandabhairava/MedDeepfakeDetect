"""Queue management service for handling analysis requests."""

import asyncio
import threading
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, List, Any
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass

from fastapi import HTTPException

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.database import db
from ..services.model_service import ModelService
from ..services.encryption import encryption_service
from ..utils import cleanup_temp_file


class AnalysisStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisTask:
    """Analysis task data structure."""
    id: int
    user_id: int
    analysis_type: str
    filename: str
    name: str
    image_base64: str
    temp_file_path: str
    queue_position: int
    user_key: Optional[bytes] = None  # AES-256 key from session cache; None → skip encrypt


class QueueService:
    """Queue service for managing analysis requests with thread pool."""
    
    def __init__(self):
        """Initialize queue service."""
        self.settings = get_settings()
        self.logger = get_logger("queue_service")
        
        # Thread pool for processing analyses
        self.executor = ThreadPoolExecutor(
            max_workers=self.settings.max_worker_threads,
            thread_name_prefix="analysis_worker"
        )
        
        # Task queue for pending analyses
        self.task_queue = Queue(maxsize=self.settings.queue_size_limit)
        
        # Model service instance
        self.model_service = ModelService()
        
        # Queue management
        self._queue_thread = None
        self._running = False
        self._lock = threading.Lock()
        
        # Start queue processor
        self.start_queue_processor()
    
    def start_queue_processor(self) -> None:
        """Start the queue processor thread."""
        if self._queue_thread is None or not self._queue_thread.is_alive():
            self._running = True
            self._queue_thread = threading.Thread(
                target=self._process_queue,
                name="queue_processor",
                daemon=True
            )
            self._queue_thread.start()
            self.logger.info("Queue processor started")
    
    def stop_queue_processor(self) -> None:
        """Stop the queue processor."""
        with self._lock:
            self._running = False
        if self._queue_thread and self._queue_thread.is_alive():
            self._queue_thread.join(timeout=5)
        self.executor.shutdown(wait=True)
        self.logger.info("Queue processor stopped")
    
    def _process_queue(self) -> None:
        """Process tasks from the queue."""
        while self._running:
            try:
                # Get task from queue with timeout
                task = self.task_queue.get(timeout=1.0)
                
                # Submit task to thread pool
                future = self.executor.submit(self._process_analysis_task, task)
                
                # Clear the task from queue
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in queue processor: {str(e)}")
                continue
    
    def _process_analysis_task(self, task: AnalysisTask) -> None:
        """Process a single analysis task."""
        try:
            # Update status to processing
            processing_started = datetime.now(timezone.utc).isoformat()
            db.update_analysis_status(
                task.id,
                AnalysisStatus.PROCESSING.value,
                processing_started=processing_started
            )
            
            self.logger.info(f"Started processing analysis {task.id} for user {task.user_id}")
            
            # Run analysis based on type
            if task.analysis_type == "xray":
                results = self.model_service.analyze_xray(task.temp_file_path)
            elif task.analysis_type == "ct":
                results = self.model_service.analyze_ct_scan(task.temp_file_path)
            else:
                raise ValueError(f"Unknown analysis type: {task.analysis_type}")
            
            # Encrypt gradcam_base64 inside results (if key available)
            if task.user_key and "gradcam_base64" in results and results["gradcam_base64"]:
                try:
                    results["gradcam_base64"] = encryption_service.encrypt(
                        results["gradcam_base64"], task.user_key
                    )
                except Exception as enc_err:
                    self.logger.error(
                        f"Failed to encrypt gradcam_base64 for analysis {task.id}: {enc_err}"
                    )

            # Update status to completed
            processing_completed = datetime.now(timezone.utc).isoformat()
            
            db.update_analysis_status(
                task.id,
                AnalysisStatus.COMPLETED.value,
                results=results,
                processing_completed=processing_completed
            )
            
            self.logger.info(f"Completed analysis {task.id} for user {task.user_id}")
            
        except Exception as e:
            # Update status to failed
            processing_completed = datetime.now(timezone.utc).isoformat()
            
            db.update_analysis_status(
                task.id,
                AnalysisStatus.FAILED.value,
                processing_completed=processing_completed
            )
            
            self.logger.error(f"Failed analysis {task.id} for user {task.user_id}: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                cleanup_temp_file(task.temp_file_path)
            except Exception as e:
                self.logger.error(f"Error cleaning up temp file {task.temp_file_path}: {str(e)}")
    
    def submit_analysis(self, user_id: int, analysis_type: str, filename: str, name: str,
                       image_base64: str, temp_file_path: str,
                       consent_confirmed: bool = True, consent_ip_addr: None|str=None, consent_usr_agent: str|None=None) -> Dict[str, Any]:
        """Submit analysis request to queue.

        The caller's AES key is fetched from the session cache and used to
        encrypt ``image_base64`` before it is written to the database.  The
        same key is snapshotted into the :class:`AnalysisTask` so the
        background worker can encrypt the ``gradcam_base64`` after inference.
        """
        try:
            # Enforce study agreement feature lock
            user = db.get_user_by_id(user_id)
            if not user or not user.get("study_consent_accepted_at"):
                self.logger.warning(
                    f"User {user_id} attempted analysis without signing initial study agreement"
                )
                raise HTTPException(
                    status_code=403,
                    detail="Study Agreement Required: You must review and accept the mandatory Study Agreement and de-identification warranty before submitting analyses."
                )

            # Fetch the user's AES key from the session cache
            # Import here to avoid circular import at module level
            from ..services.auth import auth_service
            user_key = auth_service.get_cached_key(user_id)

            from fastapi import status as http_status
            if user_key is None:
                self.logger.warning(
                    f"No cached encryption key for user {user_id}"
                )
                raise HTTPException(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "message": "Encryption session expired. Please re-authenticate to encrypt analysis data.",
                        "error_code": "encryption_key_expired"
                    }
                )

            # Encrypt image_base64 before DB write
            encrypted_image = image_base64

            try:
                encrypted_image = encryption_service.encrypt(image_base64, user_key)
            except Exception as enc_err:
                self.logger.error(
                    f"Failed to encrypt image_base64 for user {user_id}: {enc_err}"
                )
                raise HTTPException(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to encrypt image. Please retry later."
                )

            # Encrypt filename and name metadata (may contain PHI identifiers)
            encrypted_filename = filename
            encrypted_name = name
            try:
                encrypted_filename = encryption_service.encrypt(filename, user_key)
                encrypted_name = encryption_service.encrypt(name, user_key)
            except Exception as enc_err:
                self.logger.error(
                    f"Failed to encrypt metadata for user {user_id}: {enc_err}"
                )
                raise HTTPException(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to encrypt metadata. Please retry later."
                )

            # Add to database with pending status and consent audit flag
            history_id = db.add_analysis_history(
                user_id=user_id,
                analysis_type=analysis_type,
                filename=encrypted_filename,
                name=encrypted_name,
                image_base64=encrypted_image,
                results={"status": "pending", "message": "Waiting in queue"},
                status=AnalysisStatus.PENDING.value,
                consent_confirmed=consent_confirmed,
                consent_ip_addr=consent_ip_addr,
                consent_usr_agent=consent_usr_agent
            )
            
            # Update user's last analysis time
            db.update_user_last_analysis(user_id)
            
            # Update queue positions
            db.update_queue_positions()
            queue_position = db.get_queue_position(history_id)

            queue_position = queue_position or 1
            
            # Create task — pass the original (plaintext) image for model inference
            # and the key so the worker can encrypt gradcam after inference
            task = AnalysisTask(
                id=history_id,
                user_id=user_id,
                analysis_type=analysis_type,
                filename=filename,
                name=name,
                image_base64=image_base64,  # plaintext; only used for model processing
                temp_file_path=temp_file_path,
                queue_position=queue_position,
                user_key=user_key
            )
            
            # Add to queue
            self.task_queue.put(task)
            
            self.logger.info(f"Submitted analysis {history_id} to queue at position {queue_position}")
            
            return {
                "success": True,
                "message": "Analysis submitted to queue",
                "history_id": history_id,
                "status": AnalysisStatus.PENDING.value,
                "queue_position": queue_position,
                "estimated_wait_time": queue_position * 30  # 30 seconds per analysis estimate
            }
        except HTTPException:
            raise

        except Exception as e:
            self.logger.error(f"Error submitting analysis to queue: {str(e)}")
            raise
    
    def get_analysis_status(self, history_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis status from database."""
        try:
            # Update queue positions first to ensure accurate data
            db.update_queue_positions()
            
            status_info = db.get_analysis_status(history_id)
            if not status_info:
                return None
            
            # Get full analysis details if completed
            if status_info["status"] == AnalysisStatus.COMPLETED.value:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT results, processing_started, processing_completed
                        FROM analysis_history WHERE id = ?
                        """,
                        (history_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        status_info.update({
                            "results": row["results"],
                            "processing_started": row["processing_started"],
                            "processing_completed": row["processing_completed"]
                        })
            
            return status_info
            
        except Exception as e:
            self.logger.error(f"Error getting analysis status: {str(e)}")
            return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            pending_analyses = db.get_pending_analyses()
            
            return {
                "pending_count": len(pending_analyses),
                "queue_capacity": self.settings.queue_size_limit,
                "worker_threads": self.settings.max_worker_threads,
                "queue_utilization": len(pending_analyses) / self.settings.queue_size_limit
            }
            
        except Exception as e:
            self.logger.error(f"Error getting queue stats: {str(e)}")
            return {
                "pending_count": 0,
                "queue_capacity": self.settings.queue_size_limit,
                "worker_threads": self.settings.max_worker_threads,
                "queue_utilization": 0.0
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on queue service."""
        stats = self.get_queue_stats()
        
        return {
            "queue_processor_running": self._running and (self._queue_thread and self._queue_thread.is_alive()),
            "thread_pool_active": not self.executor._shutdown,
            "queue_stats": stats,
            "model_service_health": self.model_service.health_check()
        }


# Global queue service instance
queue_service = QueueService()
