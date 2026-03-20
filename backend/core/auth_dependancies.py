import os
from dotenv import load_dotenv
from pwdlib import PasswordHash
from datetime import timedelta
import jwt

from backend.core.dependencies import utc_now
from backend.core.dependencies import check_null_env


load_dotenv()
hash_password = PasswordHash.recommended()
algorithm = check_null_env(os.getenv("ALGORITHM"))
secret_key = check_null_env(os.getenv("SECRET_KEY"))
access_token_expiration = int(check_null_env(os.getenv("ACCESS_TOKEN_EXPIRATION")))
refresh_token_expiration = int(check_null_env(os.getenv("REFRESH_TOKEN_EXPIRATION")))

def create_password_hash(plain_password: str) -> str:
    """Turns plain password into hashed password"""
    return hash_password.hash(plain_password)

def check_password_hash(plain_password: str, hashed_password: str):
    """Checks whether hashed password and plain password are the same"""
    return hash_password.verify(password=plain_password, hash=hashed_password)

def _create_token(data: dict,
                  expiration: timedelta,
                  token_type: str):
    """Creates the token blueprint which type can be changed to access or refresh"""
    to_encode = data.copy()
    exp_time = utc_now() + expiration
    to_encode.update({"exp":exp_time, "type":token_type})
    return jwt.encode(to_encode,key=secret_key, algorithm=algorithm)

def create_access_token(user_id:int):
    """Takes the user id, returns the jwt access token"""
    return _create_token(data={"sub":str(user_id)}, 
                         expiration=timedelta(minutes=access_token_expiration), 
                         token_type="access")

def create_refresh_token(user_id: int):
    """Takes the user id, returns the jwt refresh token"""
    return _create_token(data={"sub":str(user_id)},
                               expiration=timedelta(hours=refresh_token_expiration),
                               token_type="refresh")

