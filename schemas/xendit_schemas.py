# Xendit Invoice schemas
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class InvoiceRequest(BaseModel):
    external_id: str
    amount: int
    payer_email: str
    description: str
    success_redirect_url: str
    failure_redirect_url: str
    invoice_duration: Optional[int] = None  # Duration in seconds from creation

class XenditInvoiceRequestBody(BaseModel):
    id: str
    external_id: str
    user_id: str
    is_high: bool
    payment_method: str
    status: str
    merchant_name: str
    amount: float
    paid_amount: float
    bank_code: str
    paid_at: datetime
    payer_email: EmailStr
    description: Optional[str] = "No description"
    adjusted_received_amount: Optional[float] = 0.0
    fees_paid_amount: Optional[float] = 0.0
    updated: datetime
    created: datetime
    currency: str
    payment_channel: str
    payment_destination: str

class InvoicePaidWebhook(BaseModel):
    id: str
    external_id: str
    user_id: str
    is_high: bool
    payment_method: str
    status: str
    merchant_name: str
    amount: float
    paid_amount: float
    bank_code: str
    paid_at: datetime
    payer_email: EmailStr
    description: Optional[str] = "No description"
    adjusted_received_amount: Optional[float] = 0.0
    fees_paid_amount: Optional[float] = 0.0
    updated: datetime
    created: datetime
    currency: str
    payment_channel: str
    payment_destination: str
    payment_id: str
    failure_redirect_url: Optional[str] = None
    success_redirect_url: Optional[str] = None
