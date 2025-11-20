"""
Celery background tasks for async processing.
"""

import os
import logging
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import SessionLocal
from ..models import Product, Webhook, WebhookLog
from ..services.csv_parser import CSVParser
from ..services.progress import ProgressService
from ..services.webhook_service import WebhookService
from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def get_celery_app():
    """Get or create Celery app instance."""
    try:
        # Try to import from celery_app module
        from celery_app import celery_app
        return celery_app
    except ImportError:
        # Fallback: create a minimal celery app
        from celery import Celery as CeleryApp
        app = CeleryApp(
            "product_importer",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND,
        )
        app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
        )
        return app


# Get celery app instance
celery_app = get_celery_app()


@celery_app.task(name="process_csv")
def process_csv_task(task_id: str, file_path: str):
    """
    Process CSV file in batches and upsert products.
    
    Args:
        task_id: Task identifier
        file_path: Path to the CSV file
    """
    
    db = SessionLocal()
    progress_service = ProgressService()
    
    try:
        logger.info(f"Starting CSV processing for task {task_id}")
        progress_service.update_progress(task_id, status='processing')
        
        # Count total rows first
        with open(file_path, 'r') as f:
            total_rows = sum(1 for _ in f) - 1  # Subtract header
        
        progress_service.update_progress(task_id, total_rows=total_rows)
        
        created_count = 0
        updated_count = 0
        failed_count = 0
        processed_count = 0
        
        # Process CSV in batches
        for batch, errors in CSVParser.parse_csv(file_path):
            processed_count += len(batch)
            failed_count += len(errors)
            
            # Upsert batch
            for product_data in batch:
                try:
                    sku = product_data['sku']
                    
                    # Check if product exists (case-insensitive)
                    existing = db.query(Product).filter(
                        func.lower(Product.sku) == sku.lower()
                    ).first()
                    
                    if existing:
                        # Update existing product
                        for key, value in product_data.items():
                            setattr(existing, key, value)
                        updated_count += 1
                    else:
                        # Create new product
                        new_product = Product(**product_data)
                        db.add(new_product)
                        created_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing product {product_data.get('sku')}: {str(e)}")
                    failed_count += 1
            
            # Bulk commit
            db.commit()
            
            # Update progress
            progress_service.update_progress(
                task_id,
                processed_rows=processed_count,
                created_products=created_count,
                updated_products=updated_count,
                failed_rows=failed_count,
            )
            
            logger.info(
                f"Batch processed: {processed_count}/{total_rows} rows, "
                f"{created_count} created, {updated_count} updated"
            )
        
        # Mark as completed
        progress_service.update_progress(
            task_id,
            status='completed',
            processed_rows=processed_count,
            created_products=created_count,
            updated_products=updated_count,
            failed_rows=failed_count,
            completed=True,
        )
        
        logger.info(f"CSV processing completed for task {task_id}")
        
        # Trigger webhooks for import completion
        trigger_webhooks_for_event('import.completed', {
            'task_id': task_id,
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count,
        })
    
    except Exception as e:
        logger.error(f"Error processing CSV {task_id}: {str(e)}")
        progress_service.mark_failed(task_id, str(e))
    
    finally:
        db.close()
        
        # Cleanup temp file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")


@celery_app.task(name="send_webhook")
def send_webhook_task(
    webhook_id: int,
    url: str,
    event_type: str,
    payload: dict,
):
    """
    Send webhook request and log result.
    
    Args:
        webhook_id: Webhook database ID
        url: Webhook URL
        event_type: Event type
        payload: Event payload
    """
    
    db = SessionLocal()
    
    try:
        webhook_service = WebhookService()
        status_code, response_body = webhook_service.trigger_webhook(
            url, event_type, payload
        )
        
        # Log success
        log = WebhookLog(
            webhook_id=webhook_id,
            event_type=event_type,
            status_code=status_code,
            response_body=response_body[:500] if response_body else None,
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Webhook {webhook_id} triggered successfully: {status_code}")
    
    except Exception as e:
        logger.error(f"Webhook {webhook_id} failed: {str(e)}")
        
        # Log failure
        log = WebhookLog(
            webhook_id=webhook_id,
            event_type=event_type,
            error_message=str(e),
        )
        db.add(log)
        db.commit()
    
    finally:
        db.close()


def trigger_webhooks_for_event(event_type: str, payload: dict):
    """
    Trigger all webhooks for a specific event.
    
    Args:
        event_type: Type of event
        payload: Event payload
    """
    
    db = SessionLocal()
    
    try:
        webhooks = db.query(Webhook).filter(
            Webhook.event_type == event_type,
            Webhook.enabled == True,
        ).all()
        
        for webhook in webhooks:
            send_webhook_task.delay(
                webhook.id,
                webhook.url,
                event_type,
                payload,
            )
    
    finally:
        db.close()
