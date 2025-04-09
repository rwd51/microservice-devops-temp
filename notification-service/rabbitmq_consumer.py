import pika
import json
import os
import time
from api.logger import logger
from api.services import process_payment_completed_event

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

def get_connection():
    """
    Create a connection to RabbitMQ
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)

def process_message(ch, method, properties, body):
    """
    Process messages from RabbitMQ
    """
    try:
        message = json.loads(body)
        logger.info(f"Received message: {message}")
        
        event_type = message.get("event_type")
        if event_type == "payment.completed":
            # Process payment completed event
            success = process_payment_completed_event(message.get("payload", {}))
            if success:
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Negative acknowledge, requeue the message
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            # Acknowledge the message to remove it from the queue
            ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError:
        logger.error("Failed to decode message as JSON")
        # Negative acknowledge, don't requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Negative acknowledge, requeue the message
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    """
    Start consuming messages from RabbitMQ
    """
    while True:
        try:
            # Connect to RabbitMQ
            connection = get_connection()
            channel = connection.channel()
            
            # Declare the queue
            channel.queue_declare(queue='payment_events', durable=True)
            
            # Set prefetch count
            channel.basic_qos(prefetch_count=1)
            
            # Set up the consumer
            channel.basic_consume(
                queue='payment_events',
                on_message_callback=process_message,
                auto_ack=False
            )
            
            logger.info("Started consuming messages from payment_events queue")
            
            # Start consuming
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.error("Lost connection to RabbitMQ. Reconnecting...")
            time.sleep(5)
        except pika.exceptions.ChannelClosedByBroker:
            logger.error("Channel closed by broker. Reconnecting...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error in RabbitMQ consumer: {str(e)}")
            time.sleep(5)