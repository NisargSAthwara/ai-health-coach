from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.data.db import get_db
from backend.services.auth_service import verify_password, get_password_hash, create_access_token
from backend.services.db_service import get_user_by_email, create_user
from models.db_models import User
from backend.schemas import UserCreate, Token

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = create_user(db, user.email, hashed_password, user.name)
    access_token_expires = timedelta(days=7) 
    access_token = create_access_token(data={"sub": str(new_user.id)},expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_id": new_user.id, "name": new_user.name}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(data={"sub": str(user.id)},expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "name": user.name}