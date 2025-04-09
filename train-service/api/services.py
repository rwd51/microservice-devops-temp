from fastapi import HTTPException
from api.logger import logger
from sqlalchemy.orm import Session
from api.models import Train, Ticket
from api.schema import TrainBase, TicketBase
from api.redis_client import redis_client, lock_seat, unlock_seat
from typing import List

import os
import requests

# For sync calls to auth service
NGINX_HOST = os.getenv("NGINX_HOST", "localhost")

# Create Train
def create_train(train: TrainBase, db: Session):
    db_train = Train(
        name=train.name,
        source=train.source,
        destination=train.destination,
        departure_time=train.departure_time
    )
    db.add(db_train)
    db.commit()
    db.refresh(db_train)
    logger.info(f"Train {db_train.name} created")
    return db_train

# Get Trains
def get_trains(db: Session):
    logger.info("Fetching all trains")
    return db.query(Train).all()

# Search Trains
def search_trains(term: str, db: Session):
    logger.info(f"Searching trains with term {term}")
    query = db.query(Train).filter(
        Train.name.ilike(f"%{term}%") | 
        Train.source.ilike(f"%{term}%") | 
        Train.destination.ilike(f"%{term}%")
    )
    return query.all()

# Get Train by ID
def get_train_by_id(train_id: int, db: Session):
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        logger.exception(f"Train with id {train_id} not found")
        raise HTTPException(status_code=404, detail="Train not found")
    return train

# Create Tickets for a Train
def create_tickets(tickets: List[TicketBase], db: Session):
    for ticket in tickets:
        db_ticket = Ticket(
            train_id=ticket.train_id,
            seat_number=ticket.seat_number,
            price=ticket.price
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        logger.info(f"Ticket {db_ticket.id} created for train {db_ticket.train_id}")
    return tickets

# Retrieve available tickets for a train
def get_available_tickets_for_train(train_id: int, db: Session):
    tickets = db.query(Ticket).filter(Ticket.train_id == train_id, Ticket.status == 'available').all()
    
    # remove the locked ones.
    available_tickets = []
    for ticket in tickets:
        key = f"seat:{train_id}:{ticket.seat_number}"
        if not redis_client.exists(key):
            available_tickets.append(ticket)

    logger.info(f"Found {len(available_tickets)} available tickets for train {train_id}")         
    return available_tickets

# Book a ticket
def book_ticket(train_id: int, seat_number: str, db: Session):
    ticket = db.query(Ticket).filter(Ticket.train_id == train_id, Ticket.seat_number == seat_number).first()
    if not ticket:
        # logger.exception(f"Ticket with seat number {seat_number} not found for train {train_id}")
        logger.error(f"Ticket with seat number {seat_number} not found for train {train_id}")
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    key = f"seat:{train_id}:{seat_number}"
    if redis_client.exists(key):
        # logger.exception(f"Seat {seat_number} already locked for train {train_id}")
        logger.error(f"Seat {seat_number} already locked for train {train_id}")
        raise HTTPException(status_code=409, detail="Seat already locked. Please try again later.")
    lock_id = lock_seat(train_id, seat_number)
    
    logger.info(f"Ticket {ticket.id} booked for train {train_id}")
    
    return lock_id

# Confirm booking.
def confirm_booking(train_id: int, seat_number: str, lock_id: str, db: Session, bearer_token: str):
    ticket = db.query(Ticket).filter(Ticket.train_id == train_id, Ticket.seat_number == seat_number).first()
    if not ticket:
        # logger.exception(f"Ticket with seat number {seat_number} not found for train {train_id}")
        logger.error(f"Ticket with seat number {seat_number} not found for train {train_id}")
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    key = f"seat:{train_id}:{seat_number}"
    stored_lock_id = redis_client.get(key)
    if not stored_lock_id:
        # logger.exception(f"Seat {seat_number} not locked for train {train_id}")
        logger.error(f"Seat {seat_number} not locked for train {train_id}")
        raise HTTPException(status_code=409, detail="Seat not locked. Please try again later.")
    
    if stored_lock_id != lock_id:
        # logger.exception(f"Lock id mismatch for seat {seat_number} in train {train_id}")
        logger.error(f"Lock id mismatch for seat {seat_number} in train {train_id}")
        raise HTTPException(status_code=409, detail="Lock id mismatch. Please try again later.")
    
    endpoint = f"http://{NGINX_HOST}/verify-token"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        user_id = response.json().get('id')
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying token with auth service")
    
    ticket.buyer_id = user_id
    ticket.status = 'booked'
    db.commit()
    db.refresh(ticket)
    
    unlock_seat(train_id, seat_number, lock_id)
    
    logger.info(f"Ticket {ticket.id} confirmed for train {train_id}")
    
    return ticket