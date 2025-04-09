from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, Dict, Any, List

class NotificationType(str, Enum):
    OTP = "otp"
    BOOKING_CONFIRMATION = "booking_confirmation"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    GENERAL = "general"

class EmailNotificationRequest(BaseModel):
    to_email: EmailStr
    subject: str
    notification_type: NotificationType
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class EmailNotificationResponse(BaseModel):
    message_id: str
    status: str
    message: str
    
    class Config:
        from_attributes = True