from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from api.schema import PaymentInitiateRequest, PaymentResponse, PaymentConfirmRequest
from api import services
from databaseConfig import get_db

router = APIRouter()

@router.post("/payment/initiate")
async def initiate_payment(payment: PaymentInitiateRequest, 
                          db: Session = Depends(get_db), 
                          authorization: str = Header(None)):
    """
    Initiate a payment request for a ticket booking
    """
    if authorization is None or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Bearer token missing or Invalid.")
    
    bearer_token = authorization.split(' ')[1]
    return services.initiate_payment(payment, db, bearer_token)

@router.post("/payment/confirm")
async def confirm_payment(payment: PaymentConfirmRequest, 
                         db: Session = Depends(get_db), 
                         authorization: str = Header(None)):
    """
    Confirm payment status, which will trigger RabbitMQ event for notification
    """
    if authorization is None or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Bearer token missing or Invalid.")
    
    bearer_token = authorization.split(' ')[1]
    return services.confirm_payment(payment, db, bearer_token)