"""
Webhook service for triggering and managing webhook callbacks.
"""

import requests
import json
from typing import Tuple, Optional


class WebhookService:
    """Trigger and manage webhooks."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize webhook service.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
    
    def trigger_webhook(
        self,
        url: str,
        event_type: str,
        payload: dict,
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Send webhook request.
        
        Args:
            url: Webhook URL
            event_type: Type of event
            payload: Event payload
            
        Returns:
            Tuple of (status_code, response_body)
            
        Raises:
            Exception: If request fails after retries
        """
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Event': event_type,
        }
        
        data = json.dumps({
            'event': event_type,
            'data': payload,
        })
        
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout,
                )
                
                return response.status_code, response.text
            
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    continue
        
        raise last_exception or Exception("Webhook request failed")
    
    def trigger_webhook_async(
        self,
        webhook_id: int,
        url: str,
        event_type: str,
        payload: dict,
    ):
        """
        Trigger webhook asynchronously via Celery.
        (This is called from Celery task)
        
        Args:
            webhook_id: Database webhook ID
            url: Webhook URL
            event_type: Event type
            payload: Payload data
        """
        
        try:
            from ..workers.tasks import send_webhook_task
            send_webhook_task.delay(webhook_id, url, event_type, payload)
        except ImportError:
            # If celery is not available, trigger synchronously
            self.trigger_webhook(url, event_type, payload)
