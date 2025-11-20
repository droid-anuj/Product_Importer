"""
Upload router for handling CSV file uploads and progress tracking.
"""

import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..schemas import UploadResponse, UploadProgressResponse
from ..services.progress import ProgressService
from ..workers.tasks import process_csv_task

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file for product import.
    
    - **file**: CSV file with columns: sku, name, description, price, quantity, active
    - Returns: task_id for tracking progress
    """
    
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Create upload directory if it doesn't exist
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file temporarily
    file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
    
    contents = await file.read()
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    # Initialize progress tracking
    progress_service = ProgressService()
    progress_service.init_progress(task_id, file.filename)
    
    # Trigger async Celery task
    process_csv_task.delay(task_id, file_path)
    
    return UploadResponse(
        task_id=task_id,
        filename=file.filename,
        message="Upload started. Check progress at /api/upload/progress/{task_id}"
    )


@router.get("/progress/{task_id}", response_model=UploadProgressResponse)
async def get_upload_progress(
    task_id: str,
):
    """
    Get the progress of an ongoing upload task.
    
    - **task_id**: The task ID returned from the upload endpoint
    """
    
    progress_service = ProgressService()
    progress_data = progress_service.get_progress(task_id)
    
    if not progress_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Calculate progress percentage
    total = progress_data.get('total_rows', 0)
    processed = progress_data.get('processed_rows', 0)
    progress_percentage = (processed / total * 100) if total > 0 else 0
    
    return UploadProgressResponse(
        task_id=task_id,
        filename=progress_data.get('filename', ''),
        status=progress_data.get('status', 'pending'),
        total_rows=total,
        processed_rows=processed,
        created_products=progress_data.get('created_products', 0),
        updated_products=progress_data.get('updated_products', 0),
        failed_rows=progress_data.get('failed_rows', 0),
        progress_percentage=progress_percentage,
        error_message=progress_data.get('error_message'),
        created_at=progress_data.get('created_at'),
        completed_at=progress_data.get('completed_at'),
    )
