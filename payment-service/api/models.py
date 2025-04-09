from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey
from sqlalchemy.sql import func

from databaseConfig import Base

class Payment(Base):
    __tablename__ = 'payment'
    
    id = Column(String(50), primary_key=True)  # UUID
    ticket_id = Column(Integer, nullable=False)
    train_id = Column(Integer, nullable=False)  # Add this line
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(String(20), default="pending")  # pending, completed, failed
    payment_method = Column(String(20), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())