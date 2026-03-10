from pwdlib import PasswordHash


hash_password = PasswordHash.recommended()

def create_password_hash(plain_password: str) -> str:
    """Turns plain password into hashed password"""
    return hash_password.hash(plain_password)