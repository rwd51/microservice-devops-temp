from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from databaseConfig import Base

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    password = Column(String(128)) # should be hashed.
    email = Column(String(50))
    