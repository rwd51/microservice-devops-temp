from fastapi import HTTPException
from api.logger import logger
from api.schema import EmailNotificationRequest, EmailNotificationResponse, NotificationType
import os
import requests
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# For sync calls to auth service
NGINX_HOST = os.getenv("NGINX_HOST", "localhost")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@trainbooking.com")

# Templates
EMAIL_TEMPLATES = {
    NotificationType.OTP: """
    <html>
    <body>
        <h1>Train Booking OTP</h1>
        <p>Hello,</p>
        <p>Your OTP for verification is: <strong>{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>Thank you,<br>Train Booking Team</p>
    </body>
    </html>
    """,
    NotificationType.BOOKING_CONFIRMATION: """
    <html>
    <body>
        <h1>Booking Confirmation</h1>
        <p>Hello {name},</p>
        <p>Your booking has been confirmed!</p>
        <p><strong>Booking Details:</strong></p>
        <ul>
            <li>Train: {train_name}</li>
            <li>From: {source}</li>
            <li>To: {destination}</li>
            <li>Date: {date}</li>
            <li>Seat: {seat}</li>
            <li>Ticket ID: {ticket_id}</li>
        </ul>
        <p>Thank you for choosing our service!</p>
        <p>Regards,<br>Train Booking Team</p>
    </body>
    </html>
    """,
    NotificationType.PAYMENT_CONFIRMATION: """
    <html>
    <body>
        <h1>Payment Confirmation</h1>
        <p>Hello {name},</p>
        <p>Your payment of {amount} {currency} has been confirmed!</p>
        <p><strong>Payment Details:</strong></p>
        <ul>
            <li>Payment ID: {payment_id}</li>
            <li>Transaction ID: {transaction_id}</li>
            <li>Amount: {amount} {currency}</li>
            <li>Ticket ID: {ticket_id}</li>
        </ul>
        <p>Thank you for your payment!</p>
        <p>Regards,<br>Train Booking Team</p>
    </body>
    </html>
    """,
    NotificationType.GENERAL: """
    <html>
    <body>
        <h1>{subject}</h1>
        <p>Hello {name},</p>
        <p>{message}</p>
        <p>Regards,<br>Train Booking Team</p>
    </body>
    </html>
    """
}

def send_email(to_email, subject, html_content):
    """
    Send an email using SMTP
    """
    # In production, use a proper email service provider like SendGrid, Mailgun, etc.
    # This is a basic implementation for demonstration
    
    # Mock email sending in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        logger.info(f"MOCK: Email would be sent to {to_email} with subject '{subject}'")
        message_id = str(uuid.uuid4())
        return message_id
        
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        message_id = str(uuid.uuid4())
        logger.info(f"Email sent to {to_email} with subject '{subject}'")
        return message_id
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

def send_email_notification(notification: EmailNotificationRequest, bearer_token: str):
    """
    Send an email notification based on the request data
    """
    # Verify the user's identity
    try:
        endpoint = f"http://{NGINX_HOST}/verify-token"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        # We can get user info if needed
        # user_data = response.json()
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying token with auth service")
    
    # Get template based on notification type
    template = EMAIL_TEMPLATES.get(notification.notification_type)
    if not template:
        logger.error(f"No template found for notification type: {notification.notification_type}")
        raise HTTPException(status_code=400, detail=f"No template found for notification type: {notification.notification_type}")
    
    # Format template with provided data
    template_data = notification.template_data or {}
    try:
        html_content = template.format(**template_data)
    except KeyError as e:
        logger.error(f"Missing template data: {e}")
        raise HTTPException(status_code=400, detail=f"Missing template data: {str(e)}")
    
    # Send email
    message_id = send_email(notification.to_email, notification.subject, html_content)
    
    # Return response
    return EmailNotificationResponse(
        message_id=message_id,
        status="sent",
        message=f"Email notification of type {notification.notification_type} sent to {notification.to_email}"
    )

def process_payment_completed_event(event_data):
    """
    Process payment completed event from RabbitMQ
    """
    logger.info(f"Processing payment completed event: {event_data}")
    
    try:
        # Get payment details
        payment_id = event_data.get("payment_id")
        ticket_id = event_data.get("ticket_id")
        user_id = event_data.get("user_id")
        amount = event_data.get("amount")
        transaction_id = event_data.get("transaction_id")
        
        # Get ticket and user details
        # In a real implementation, we would call the auth and train services
        # to get these details
        
        # For now, let's mock this part
        user_email = "user@example.com"  # In production, get this from auth service
        user_name = "User"  # In production, get this from auth service
        
        # Get ticket details
        try:
            endpoint = f"http://{NGINX_HOST}/ticket/{ticket_id}"
            response = requests.get(endpoint)
            response.raise_for_status()
            ticket_data = response.json()
            
            # Get train details
            train_endpoint = f"http://{NGINX_HOST}/train/{ticket_data.get('train_id')}"
            train_response = requests.get(train_endpoint)
            train_response.raise_for_status()
            train_data = train_response.json()
        except Exception as e:
            logger.error(f"Error fetching ticket/train details: {e}")
            # Continue with mock data
            ticket_data = {
                "id": ticket_id,
                "seat_number": "A1",
                "train_id": 1
            }
            train_data = {
                "id": 1,
                "name": "Express Train",
                "source": "Source City",
                "destination": "Destination City",
                "departure_time": "2023-04-10T10:00:00"
            }
        
        # Send payment confirmation email
        notification = EmailNotificationRequest(
            to_email=user_email,
            subject="Payment Confirmation - Train Booking",
            notification_type=NotificationType.PAYMENT_CONFIRMATION,
            template_data={
                "name": user_name,
                "payment_id": payment_id,
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": "INR",
                "ticket_id": ticket_id
            }
        )
        
        # Send booking confirmation email
        booking_notification = EmailNotificationRequest(
            to_email=user_email,
            subject="Booking Confirmation - Train Booking",
            notification_type=NotificationType.BOOKING_CONFIRMATION,
            template_data={
                "name": user_name,
                "train_name": train_data.get("name"),
                "source": train_data.get("source"),
                "destination": train_data.get("destination"),
                "date": train_data.get("departure_time"),
                "seat": ticket_data.get("seat_number"),
                "ticket_id": ticket_id
            }
        )
        
        # In production, we would actually send these emails
        # For now, we'll just log it
        logger.info(f"Would send payment confirmation email to {user_email}")
        logger.info(f"Would send booking confirmation email to {user_email}")
        
        # Mock sending
        send_email(notification.to_email, notification.subject, 
                   EMAIL_TEMPLATES[notification.notification_type].format(**notification.template_data))
        
        send_email(booking_notification.to_email, booking_notification.subject,
                  EMAIL_TEMPLATES[booking_notification.notification_type].format(**booking_notification.template_data))
        
        logger.info(f"Processed payment completed event for payment {payment_id}")
        return True
    except Exception as e:
        logger.error(f"Error processing payment completed event: {e}")
        return False