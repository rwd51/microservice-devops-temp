from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NETBANKING = "netbanking"
    UPI = "upi"

class PaymentInitiateRequest(BaseModel):
    train_id: int
    ticket_id: Optional[int] = None  # Make it optional - will be selected automatically if not provided
    amount: float
    currency: str = "INR"  # Default to INR
    payment_method: PaymentMethod
    
    class Config:
        from_attributes = True

class PaymentConfirmRequest(BaseModel):
    payment_id: str
    transaction_id: str
    status: PaymentStatus
    
    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: str
    ticket_id: int
    train_id: int  # Add this field
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True