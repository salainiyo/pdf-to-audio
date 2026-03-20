from fastapi import APIRouter, status, HTTPException, Depends, Request
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from loguru import logger

from backend.database.db import get_session
from backend.models.users import User, UserCreate, UserRead
from backend.core.auth_dependancies import create_password_hash, check_password_hash
from backend.core.rate_limiting import limiter


router = APIRouter()
auth_router =  APIRouter(prefix="/auth")


@router.get("/")
@limiter.limit("5/minute")
def health_check(request:Request):
    logger.success("API RUNNING...")
    return{
        "status":"active",
        "version":"0.0.1"
    }


@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_user(request: Request, user:UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    db_user = session.exec(statement).first()
    if db_user:
        logger.info(f"{user.email} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User exists")
    hash_password = create_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hash_password
    )
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.success(f"{new_user.email} registered sucessfully")
        return new_user
    
    except IntegrityError:
        session.rollback()
        logger.exception(f"{user.email} not registered. Integrity error. Possible email duplicate")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Integrity error. Possible email duplicate")

    except Exception as e:
        logger.exception(f"{user.email} not registered. {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error")
    
@auth_router.post("/login")
@limiter.limit("5/minute")
def login(request: Request,
          user: UserCreate,
          session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    db_user = session.exec(statement).first()
    if not db_user or not check_password_hash(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")
    