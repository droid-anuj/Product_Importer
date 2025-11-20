"""
Progress tracking service using Redis for real-time upload progress.
"""

import json
from datetime import datetime
import redis

from ..config import get_settings

settings = get_settings()


class ProgressService:
    """Track upload progress in Redis with JSON serialization."""
    
    PREFIX = "upload_progress:"
    TTL = 86400 * 7  # 7 days
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def init_progress(self, task_id: str, filename: str) -> None:
        """
        Initialize progress tracking for a new upload.
        
        Args:
            task_id: Unique task identifier
            filename: Name of the uploaded file
        """
        
        progress_data = {
            'task_id': task_id,
            'filename': filename,
            'status': 'pending',
            'total_rows': 0,
            'processed_rows': 0,
            'created_products': 0,
            'updated_products': 0,
            'failed_rows': 0,
            'error_message': None,
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
        }
        
        key = f"{self.PREFIX}{task_id}"
        self.redis_client.setex(
            key,
            self.TTL,
            json.dumps(progress_data)
        )
    
    def update_progress(
        self,
        task_id: str,
        status: str = None,
        total_rows: int = None,
        processed_rows: int = None,
        created_products: int = None,
        updated_products: int = None,
        failed_rows: int = None,
        error_message: str = None,
        completed: bool = False,
    ) -> None:
        """
        Update progress data.
        
        Args:
            task_id: Task identifier
            status: Current status
            total_rows: Total rows in CSV
            processed_rows: Rows processed so far
            created_products: Products created
            updated_products: Products updated
            failed_rows: Failed rows
            error_message: Error message if any
            completed: Whether task is completed
        """
        
        key = f"{self.PREFIX}{task_id}"
        data = self.get_progress(task_id)
        
        if not data:
            return
        
        if status is not None:
            data['status'] = status
        if total_rows is not None:
            data['total_rows'] = total_rows
        if processed_rows is not None:
            data['processed_rows'] = processed_rows
        if created_products is not None:
            data['created_products'] = created_products
        if updated_products is not None:
            data['updated_products'] = updated_products
        if failed_rows is not None:
            data['failed_rows'] = failed_rows
        if error_message is not None:
            data['error_message'] = error_message
        
        if completed:
            data['status'] = 'completed'
            data['completed_at'] = datetime.now().isoformat()
        
        self.redis_client.setex(
            key,
            self.TTL,
            json.dumps(data)
        )
    
    def get_progress(self, task_id: str) -> dict:
        """
        Get progress data for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Progress data dictionary or None
        """
        
        key = f"{self.PREFIX}{task_id}"
        data = self.redis_client.get(key)
        
        if not data:
            return None
        
        return json.loads(data)
    
    def mark_failed(self, task_id: str, error_message: str) -> None:
        """
        Mark a task as failed.
        
        Args:
            task_id: Task identifier
            error_message: Error message
        """
        
        self.update_progress(
            task_id,
            status='failed',
            error_message=error_message,
            completed=True,
        )
    
    def delete_progress(self, task_id: str) -> None:
        """
        Delete progress data (cleanup).
        
        Args:
            task_id: Task identifier
        """
        
        key = f"{self.PREFIX}{task_id}"
        self.redis_client.delete(key)
