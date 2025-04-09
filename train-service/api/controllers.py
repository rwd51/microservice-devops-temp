from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from api.schema import TrainBase, TicketBase
from api import services
from databaseConfig import get_db
from typing import List

# Add logging here if necessary

router = APIRouter()

# Create Train
@router.post("/train")
async def create_train(train: TrainBase, db: Session = Depends(get_db)):
    return services.create_train(train, db)

# Get Trains
@router.get("/train")
async def get_trains(db: Session = Depends(get_db)):
    return services.get_trains(db)

# Search Trains
@router.get("/train/search")
async def search_trains(term: str, db: Session = Depends(get_db)):
    return services.search_trains(term, db)

# Get Train by ID
@router.get("/train/{train_id}")
async def get_train_by_id(train_id: int, db: Session = Depends(get_db)):
    return services.get_train_by_id(train_id, db)

# Create Tickets for a train
@router.post("/ticket") 
async def create_tickets(tickets: List[TicketBase], db: Session = Depends(get_db)):
    return services.create_tickets(tickets, db)

# Get available tickets for a train
@router.get("/ticket/{train_id}")
async def get_available_tickets_for_train(train_id: int, db: Session = Depends(get_db)):
    return services.get_available_tickets_for_train(train_id, db)

# Book ticket
@router.post("/ticket/book")
async def book_ticket(train_id: int, seat_number: str, db: Session = Depends(get_db)):
    return services.book_ticket(train_id, seat_number, db)

# Confirm booking
@router.put("/ticket/confirm")
async def confirm_booking(train_id: int, seat_number: str, lock_id: str, db: Session = Depends(get_db), authorization: str = Header(None)):
    if authorization is None or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Bearer token missing or Invalid.") # this is technically redundant since nginx will handle
    bearer_token = authorization.split(' ')[1]
    return services.confirm_booking(train_id, seat_number, lock_id, db, bearer_token)


