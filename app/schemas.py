"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


# ===== Product Schemas =====

class ProductBase(BaseModel):
    """Base product schema with common fields."""
    sku: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = 0
    active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list."""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== Webhook Schemas =====

class WebhookBase(BaseModel):
    """Base webhook schema."""
    url: str = Field(..., min_length=5, max_length=2000)
    event_type: str = Field(..., min_length=1, max_length=50)
    enabled: bool = True


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[str] = None
    event_type: Optional[str] = None
    enabled: Optional[bool] = None


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookLogResponse(BaseModel):
    """Schema for webhook log response."""
    id: int
    webhook_id: int
    event_type: str
    status_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Upload Schemas =====

class UploadProgressResponse(BaseModel):
    """Schema for upload progress response."""
    task_id: str
    filename: str
    status: str
    total_rows: int
    processed_rows: int
    created_products: int
    updated_products: int
    failed_rows: int
    progress_percentage: float
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class UploadResponse(BaseModel):
    """Schema for upload initiation response."""
    task_id: str
    filename: str
    message: str


# ===== Webhook Test Schemas =====

class WebhookTestRequest(BaseModel):
    """Schema for testing a webhook."""
    event_type: str = Field(default="test", min_length=1)


class WebhookTestResponse(BaseModel):
    """Schema for webhook test response."""
    webhook_id: int
    status_code: Optional[int]
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
