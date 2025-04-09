from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api import auth
from databaseConfig import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from api.schema import Token, UserCreate, GetUser

# Add logging here if necessary

router = APIRouter()

@router.get("/verify-token")
async def get_current_user(
    token: Annotated[str, Depends(auth.oauth2_scheme)],
    db: Session = Depends(get_db)
) -> GetUser:
    return auth.get_current_user(token, db)

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    return auth.login_user(form_data, db)

@router.post("/register")
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> Token:
    return auth.register_user(user, db)