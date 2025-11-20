"""
SQLAlchemy ORM models for the application.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Index, event
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class Product(Base):
    """Product model representing items in the catalog."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    quantity = Column(Integer, default=0)
    active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"


class Webhook(Base):
    """Webhook configuration for event notifications."""
    
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)  # e.g., "product.created", "import.completed"
    enabled = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, url={self.url}, event_type={self.event_type})>"


class UploadTask(Base):
    """Track CSV upload tasks and their progress."""
    
    __tablename__ = "upload_tasks"
    
    id = Column(String(36), primary_key=True, index=True)  # Task ID
    filename = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    created_products = Column(Integer, default=0)
    updated_products = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<UploadTask(id={self.id}, filename={self.filename}, status={self.status})>"


class WebhookLog(Base):
    """Log webhook execution attempts."""
    
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<WebhookLog(id={self.id}, webhook_id={self.webhook_id}, status_code={self.status_code})>"
