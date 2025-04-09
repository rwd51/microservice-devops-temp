from fastapi import APIRouter, Depends, HTTPException, Header
from api.schema import EmailNotificationRequest, EmailNotificationResponse
from api import services

router = APIRouter()

@router.post("/notification/email")
async def send_email_notification(notification: EmailNotificationRequest, 
                                authorization: str = Header(None)):
    """
    Send an email notification (OTP, booking confirmation, etc.)
    """
    if authorization is None or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Bearer token missing or Invalid.")
    
    bearer_token = authorization.split(' ')[1]
    return services.send_email_notification(notification, bearer_token)