from pydantic import BaseModel

class TrainBase(BaseModel):
    name: str
    source: str
    destination: str
    departure_time: str
    
    class Config:
        from_attributes = True
    
class TicketBase(BaseModel):
    train_id: int
    seat_number: str
    price: float
    
    class Config:
        from_attributes = True