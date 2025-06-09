from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.schemas import TokenData

from backend.config.settings import SECRET_KEY, ALGORITHM
from backend.services import db_service
from backend.services.db_service import get_user_by_id
from backend.data.db import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print("🟡 Received Token:", token)  
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[str(ALGORITHM)])
        print('Decoded payload:', payload)
        user_id: str = payload.get("sub")
        if user_id is None:
            print("❌ No user_id found in token.")
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError as e:
        print("❌ JWTError:", str(e))
        raise credentials_exception
    print("🔍 Looking for user ID:", token_data.user_id)
    user = get_user_by_id(db, user_id=token_data.user_id)
    print("🔎 User returned:", user)
    if user is None:
        print("❌ User not found in DB.")
        raise credentials_exception
    print("✅ Authenticated user:", user.email)
    return user