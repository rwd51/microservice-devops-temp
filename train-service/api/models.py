from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from databaseConfig import Base

class Train(Base):
    __tablename__ = 'train'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    source = Column(String(50))
    destination = Column(String(50))
    departure_time = Column(DateTime, default=func.now())
    
class Ticket(Base):
    __tablename__ = 'ticket'
    
    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey('train.id', ondelete='CASCADE'))
    seat_number = Column(String(50))
    price = Column(Float)
    status = Column(String(50), default='available', nullable=False) # available or booked.
    buyer_id = Column(Integer, nullable=True)
    
    train = relationship('Train')
    