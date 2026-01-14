"""
Password utilities using bcrypt
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt. Truncate to 72 bytes as required by bcrypt.
    """
    # bcrypt only supports passwords up to 72 bytes; truncate by bytes, not characters
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if passwords match, False otherwise
    """
    # Truncate password to 72 bytes to match hashing behavior
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)
