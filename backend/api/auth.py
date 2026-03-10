from fastapi import FastAPI, APIRouter, status, HTTPException, Depends, Request
from sqlmodel import Session, select

from database.db import get_session
from models.users import User, UserCreate, UserRead
from core.auth_dependancies import create_password_hash
from core.rate_limiting import limiter

auth_router =  APIRouter(prefix="/auth")

@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(request: Request, user:UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User exists")
    hash_password = create_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hash_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user