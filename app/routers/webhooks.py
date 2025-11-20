"""
Webhooks router for CRUD operations and webhook management.
"""

import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Webhook, WebhookLog
from ..schemas import (
    WebhookCreate, WebhookUpdate, WebhookResponse,
    WebhookLogResponse, WebhookTestRequest, WebhookTestResponse
)
from ..services.webhook_service import WebhookService

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=201)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
):
    """Create a new webhook."""
    
    db_webhook = Webhook(**webhook.model_dump())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    return db_webhook


@router.get("/", response_model=list[WebhookResponse])
def list_webhooks(
    event_type: str = Query(None),
    enabled: bool = Query(None),
    db: Session = Depends(get_db),
):
    """
    List webhooks with optional filtering.
    
    - **event_type**: Filter by event type
    - **enabled**: Filter by enabled status
    """
    
    query = db.query(Webhook)
    
    if event_type:
        query = query.filter(Webhook.event_type.ilike(f"%{event_type}%"))
    if enabled is not None:
        query = query.filter(Webhook.enabled == enabled)
    
    return query.all()


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
):
    """Get a single webhook by ID."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: Session = Depends(get_db),
):
    """Update a webhook."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    update_data = webhook_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
):
    """Delete a webhook."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()
    
    return {"message": "Webhook deleted successfully"}


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
def test_webhook(
    webhook_id: int,
    test_request: WebhookTestRequest,
    db: Session = Depends(get_db),
):
    """
    Test a webhook by sending a test payload.
    
    - **webhook_id**: ID of the webhook to test
    - **test_request**: Test request payload with event_type
    """
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook_service = WebhookService()
    
    start_time = time.time()
    try:
        status_code, response_body = webhook_service.trigger_webhook(
            webhook.url,
            test_request.event_type,
            {"test": True, "event_type": test_request.event_type}
        )
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log the attempt
        log = WebhookLog(
            webhook_id=webhook_id,
            event_type=test_request.event_type,
            status_code=status_code,
            response_body=response_body[:500] if response_body else None,
        )
        db.add(log)
        db.commit()
        
        return WebhookTestResponse(
            webhook_id=webhook_id,
            status_code=status_code,
            response_time_ms=response_time_ms,
            success=200 <= status_code < 300,
        )
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log the failure
        log = WebhookLog(
            webhook_id=webhook_id,
            event_type=test_request.event_type,
            error_message=str(e),
        )
        db.add(log)
        db.commit()
        
        return WebhookTestResponse(
            webhook_id=webhook_id,
            status_code=None,
            response_time_ms=response_time_ms,
            success=False,
            error_message=str(e),
        )


@router.get("/{webhook_id}/logs", response_model=list[WebhookLogResponse])
def get_webhook_logs(
    webhook_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get recent logs for a webhook.
    
    - **webhook_id**: ID of the webhook
    - **limit**: Maximum number of logs to return
    """
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    logs = db.query(WebhookLog)\
        .filter(WebhookLog.webhook_id == webhook_id)\
        .order_by(WebhookLog.created_at.desc())\
        .limit(limit)\
        .all()
    
    return logs
