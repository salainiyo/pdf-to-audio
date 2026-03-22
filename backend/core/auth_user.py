import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from jwt.exceptions import InvalidTokenError
from loguru import logger

from backend.database.db import get_session
from backend.models.users import User, AccessTokenBlocklist, RefreshTokenBlocklist
from backend.core.auth_dependancies import secret_key, algorithm


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def current_user(token:str = Depends(oauth_scheme), session:Session = Depends(get_session)):
    logger.info("Attempting login...")
    auth_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                   detail="Unauthorized access",
                                   headers={"WWW-Authenticate":"bearer"})
    statement = select(AccessTokenBlocklist).where(AccessTokenBlocklist.token == token)
    blocked_token = session.exec(statement).first()
    if blocked_token:
        logger.warning("Attempting login is using blocked token")
        raise auth_exception
    try:
        payload = jwt.decode(jwt=token, key=secret_key, algorithms=algorithm)
        token_type: str|None = payload.get("type")
        user_id: int|None = payload.get("sub")
        if user_id is None or token_type != "access":
            logger.warning("Corrupted token")
            raise auth_exception

    except InvalidTokenError:
        logger.error("Invalid token")
        raise auth_exception
    
    except Exception as e:
        logger.error(f"an error occured, {str(e)}")
        raise auth_exception
    
    db_user = session.get(User, int(user_id))
    if not db_user:
        logger.info("User trying to log in not found")
        raise auth_exception
    logger.success(f"{db_user.email} logged in sucessfully")
    return db_user