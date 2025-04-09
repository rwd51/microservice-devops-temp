from fastapi import HTTPException
from api.logger import logger
from sqlalchemy.orm import Session
from api.models import Payment
from api.schema import PaymentInitiateRequest, PaymentResponse, PaymentConfirmRequest, PaymentStatus
from rabbitmq_client import publish_message

import os
import uuid
import requests
from datetime import datetime

# For sync calls to auth service
NGINX_HOST = os.getenv("NGINX_HOST", "localhost")

def initiate_payment(payment: PaymentInitiateRequest, db: Session, bearer_token: str):
    """
    Initiate a payment for a ticket booking
    """
    # Verify the user's identity
    try:
        endpoint = f"http://{NGINX_HOST}/verify-token"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        user_id = response.json().get('id')
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying token with auth service")
    
    ticket_id = payment.ticket_id
    
    # If no specific ticket ID is provided, find an available one
    if ticket_id is None:
        try:
            endpoint = f"http://{NGINX_HOST}/ticket/{payment.train_id}"
            logger.info(f"Checking tickets for train at endpoint: {endpoint}")
            response = requests.get(endpoint)
            logger.info(f"Got response: {response.status_code}")
            response.raise_for_status()
            tickets = response.json()
            logger.info(f"Found {len(tickets)} tickets for train {payment.train_id}")
            
            # Filter for available tickets
            available_tickets = [ticket for ticket in tickets if ticket.get("status") == "available"]
            if not available_tickets:
                logger.error(f"No available tickets for train {payment.train_id}")
                raise HTTPException(status_code=400, detail="No available tickets for this train")
            
            # Select the first available ticket
            selected_ticket = available_tickets[0]
            ticket_id = selected_ticket["id"]
            logger.info(f"Selected ticket {ticket_id} for train {payment.train_id}")
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error finding available ticket: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while finding ticket")
    else:
        # Verify the specified ticket exists and is available
        try:
            # First check if the ticket belongs to the specified train
            endpoint = f"http://{NGINX_HOST}/ticket/{payment.train_id}"
            response = requests.get(endpoint)
            response.raise_for_status()
            tickets = response.json()
            
            # Find the specified ticket
            ticket_found = False
            ticket_available = False
            for ticket in tickets:
                if ticket.get("id") == ticket_id:
                    ticket_found = True
                    if ticket.get("status") == "available":
                        ticket_available = True
                    break
            
            if not ticket_found:
                logger.error(f"Ticket {ticket_id} not found for train {payment.train_id}")
                raise HTTPException(status_code=400, detail="Ticket not found for this train")
                
            if not ticket_available:
                logger.error(f"Ticket {ticket_id} is not available")
                raise HTTPException(status_code=400, detail="Ticket is not available for booking")
                
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error verifying ticket availability: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while verifying ticket")
    
    # Create a new payment record
    payment_id = str(uuid.uuid4())
    new_payment = Payment(
        id=payment_id,
        ticket_id=ticket_id,
        train_id=payment.train_id,
        user_id=user_id,
        amount=payment.amount,
        currency=payment.currency,
        status=PaymentStatus.PENDING,
        payment_method=payment.payment_method,
        created_at=datetime.now()
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    logger.info(f"Payment initiated for ticket {ticket_id} (train {payment.train_id}) by user {user_id}")
    
    # Transform to response model
    return PaymentResponse(
        id=new_payment.id,
        ticket_id=ticket_id,
        train_id=payment.train_id,
        amount=new_payment.amount,
        currency=new_payment.currency,
        status=PaymentStatus(new_payment.status),
        payment_method=payment.payment_method,
        created_at=new_payment.created_at
    )

def confirm_payment(payment: PaymentConfirmRequest, db: Session, bearer_token: str):
    """
    Confirm payment status and trigger notification via RabbitMQ
    """
    # Verify user
    try:
        endpoint = f"http://{NGINX_HOST}/verify-token"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        user_id = response.json().get('id')
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying token with auth service")
    
    # Get payment record
    payment_record = db.query(Payment).filter(Payment.id == payment.payment_id).first()
    if not payment_record:
        logger.error(f"Payment {payment.payment_id} not found")
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if payment belongs to the user
    if payment_record.user_id != user_id:
        logger.error(f"Payment {payment.payment_id} does not belong to user {user_id}")
        raise HTTPException(status_code=403, detail="You are not authorized to confirm this payment")
    
    # Update payment status
    payment_record.status = payment.status
    payment_record.transaction_id = payment.transaction_id
    payment_record.updated_at = datetime.now()
    
    db.commit()
    db.refresh(payment_record)
    
    logger.info(f"Payment {payment.payment_id} updated to status {payment.status}")
    
    # If payment is completed, publish message for notification service
    if payment.status == PaymentStatus.COMPLETED:
        message = {
            "event_type": "payment.completed",
            "payload": {
                "payment_id": payment_record.id,
                "ticket_id": payment_record.ticket_id,
                "user_id": payment_record.user_id,
                "amount": payment_record.amount,
                "transaction_id": payment_record.transaction_id
            }
        }
        try:
            publish_message("payment_events", message)
            logger.info(f"Published payment.completed event for payment {payment.payment_id}")
        except Exception as e:
            logger.error(f"Error publishing payment event: {e}")
            # Continue processing even if message publishing fails
    
    # Transform to response model
    # Transform to response model
    return PaymentResponse(
        id=payment_record.id,
        ticket_id=payment_record.ticket_id,
        train_id=payment_record.train_id,  # Add this line
        amount=payment_record.amount,
        currency=payment_record.currency,
        status=PaymentStatus(payment_record.status),
        payment_method=payment_record.payment_method,
        transaction_id=payment_record.transaction_id,
        created_at=payment_record.created_at,
        updated_at=payment_record.updated_at
    )