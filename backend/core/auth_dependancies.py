from pwdlib import PasswordHash


hash_password = PasswordHash.recommended()

def create_password_hash(plain_password: str) -> str:
    """Turns plain password into hashed password"""
    return hash_password.hash(plain_password)

def check_password_hash(plain_password: str, hashed_password: str):
    """Checks whether hashed password and plain password are the same"""
    return hash_password.verify(password=plain_password, hash=hashed_password)