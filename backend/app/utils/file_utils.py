"""File handling utilities."""

import os
import tempfile
from pathlib import Path
from typing import Optional
import uuid

from fastapi import UploadFile, HTTPException
from PIL import Image
import structlog

from ..core.config import get_settings


logger = structlog.get_logger("file_utils")


class FileValidationError(Exception):
    """File validation error."""
    pass


def validate_file_extension(filename: str) -> bool:
    """Validate file extension.
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        True if extension is allowed
        
    Raises:
        FileValidationError: If extension is not allowed
    """
    settings = get_settings()
    
    # Get file extension
    ext = Path(filename).suffix.lower().lstrip('.')
    
    if ext not in settings.allowed_extensions:
        raise FileValidationError(
            f"File extension '{ext}' not allowed. "
            f"Allowed extensions: {settings.allowed_extensions}"
        )
    
    return True


def validate_file_size(file_size: int) -> bool:
    """Validate file size.
    
    Args:
        file_size: Size of file in bytes
        
    Returns:
        True if size is within limits
        
    Raises:
        FileValidationError: If file is too large
    """
    settings = get_settings()
    
    if file_size > settings.max_file_size:
        raise FileValidationError(
            f"File size {file_size} bytes exceeds maximum allowed size "
            f"of {settings.max_file_size} bytes"
        )
    
    return True


def validate_image_file(file_path: str) -> bool:
    """Validate that file is a valid image.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file is a valid image
        
    Raises:
        FileValidationError: If file is not a valid image
    """
    try:
        with Image.open(file_path) as img:
            # Try to load the image data
            img.verify()
            
        # Reopen to check if it can be processed
        with Image.open(file_path) as img:
            img.load()
            
        return True
        
    except Exception as e:
        raise FileValidationError(f"Invalid image file: {str(e)}")


def save_upload_file(
    upload_file: UploadFile,
    destination_dir: Optional[str] = None
) -> str:
    """Save uploaded file to disk.
    
    Args:
        upload_file: Uploaded file from FastAPI
        destination_dir: Directory to save file (optional)
        
    Returns:
        Path to saved file
        
    Raises:
        FileValidationError: If file validation fails
    """
    settings = get_settings()
    
    # Validate file
    validate_file_extension(upload_file.filename)
    validate_file_size(upload_file.size)
    
    # Determine destination directory
    if destination_dir is None:
        destination_dir = settings.upload_dir
    
    # Create directory if it doesn't exist
    upload_dir = Path(destination_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            content = upload_file.file.read()
            buffer.write(content)
        
        # Validate image
        validate_image_file(str(file_path))
        
        logger.info(
            "file_saved_successfully",
            filename=upload_file.filename,
            saved_path=str(file_path),
            file_size=upload_file.size
        )
        
        return str(file_path)
        
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        
        logger.error(
            "file_save_failed",
            filename=upload_file.filename,
            error=str(e)
        )
        
        raise FileValidationError(f"Failed to save file: {str(e)}")


def cleanup_temp_file(file_path: str) -> None:
    """Securely clean up temporary file by overwriting before unlinking.
    
    Args:
        file_path: Path to file to remove
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            # Ephemeral Storage Safeguard: zero-fill file sectors before unlinking
            # to prevent forensic recovery of temporary plaintext medical imagery
            try:
                size = path.stat().st_size
                if size > 0:
                    with open(path, "ba+", buffering=0) as f:
                        f.write(b"\x00" * size)
                        f.flush()
                        os.fsync(f.fileno())
            except Exception as wipe_err:
                logger.warning("failed_to_zerofill_temp_file", file_path=file_path, error=str(wipe_err))

            path.unlink()
            logger.info("temp_file_cleaned_up", file_path=file_path)
    except Exception as e:
        logger.warning(
            "failed_to_cleanup_temp_file",
            file_path=file_path,
            error=str(e)
        )



def get_file_info(file_path: str) -> dict:
    """Get file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get basic file info
        stat = path.stat()
        
        # Get image info if it's an image
        image_info = {}
        try:
            with Image.open(file_path) as img:
                image_info = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size
                }
        except Exception:
            # Not an image or corrupted
            pass
        
        return {
            "filename": path.name,
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "extension": path.suffix.lower(),
            "image_info": image_info
        }
        
    except Exception as e:
        logger.error("failed_to_get_file_info", file_path=file_path, error=str(e))
        raise
