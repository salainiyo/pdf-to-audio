from fastapi import APIRouter, status, HTTPException, Depends, Request
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from loguru import logger
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt

from backend.database.db import get_session
from backend.core.auth_user import current_user
from backend.models.users import *
from backend.core.auth_dependancies import create_password_hash, check_password_hash, create_access_token, create_refresh_token
from backend.core.rate_limiting import limiter
from backend.core.auth_dependancies import secret_key, algorithm


router = APIRouter()
auth_router =  APIRouter(prefix="/auth")
oauth_scheme = OAuth2PasswordBearer("/auth/login")

def token_checking(token: str, session:Session):
    token_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                     detail="Invalid credentials",
                                     headers={"WWW-Authenticate":"bearer"})
    if not token:
        raise token_exception
    statement = select(AccessTokenBlocklist).where(AccessTokenBlocklist.token == token)
    blocked_token = session.exec(statement).first()
    if blocked_token is not None:
        raise token_exception  
    
    
    payload = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
    user_id = payload.get("sub")
    if not user_id or payload.get("type")!="access":
        raise token_exception
    db_user = session.get(User, int(user_id))
    if not db_user:
        raise token_exception
    return db_user


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
                            detail=f"{user.email} exists")
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
    
@auth_router.post("/login", response_model=TokensRead)
@limiter.limit("5/minute")
def login(request: Request,
          form_data: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    logger.info(f"{form_data.username} is trying to log in")
    statement = select(User).where(User.email == form_data.username)
    db_user = session.exec(statement).first()
    if not db_user or not check_password_hash(form_data.password, db_user.password_hash):
        logger.info(f"Invalid credentials for {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")
    try:
        access_token = create_access_token(user_id=db_user.id)#type:ignore
        refresh_token = create_refresh_token(user_id=db_user.id)#type:ignore
        tokens = TokensRead(access_token=access_token, refresh_token=refresh_token)

        logger.success(f"{form_data.username} logged in successfully")
        return tokens
    except Exception as e:
        logger.error(f"login failed for {form_data.username}, the error is {str(e)}")

@auth_router.post("/logout", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def logout(request: Request,
           logout_data: LogoutRequest,
           token: str = Depends(oauth_scheme),
           session: Session = Depends(get_session)):
    token_checking(token=token, session=session)
    access_block = AccessTokenBlocklist(token=token, token_type="access")
    refresh_block = RefreshTokenBlocklist(token=logout_data.refresh_token, token_type="refresh")
    
    try:
        session.add(access_block)
        session.add(refresh_block)
        session.commit()
        logger.success("User successfully logged out")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error happened, {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error")

@auth_router.post("/me", response_model=UserRead)
@limiter.limit("5/minute")
def current_user_route(request: Request,
                       actual_user: User = Depends(current_user),
                       session: Session = Depends(get_session)):
    return actual_user

@auth_router.post("/refresh", response_model=TokensRead)
@limiter.limit("5/minute")
def refresh(request: Request,
            token:str = Depends(oauth_scheme),
            session:Session = Depends(get_session)):
    db_user = token_checking(token=token, session=session)
    access_token = create_access_token(user_id=db_user.id) #type:ignore
    refresh_token = create_refresh_token(user_id=db_user.id) #type:ignore
    tokens = TokensRead(access_token=access_token, refresh_token=refresh_token)
    return tokens     
