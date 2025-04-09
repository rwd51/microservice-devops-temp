from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True
        
class GetUser(UserBase):
    id: int

    class Config:
        from_attributes = True
        
class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None
    
class UserInDB(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True