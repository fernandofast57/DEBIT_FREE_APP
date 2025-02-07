import hashlib
import secrets

def generate_secure_token(length: int = 32) -> str:
    return secrets.token_hex(length)

def generate_hex_key(length: int = 32) -> str:
    """Genera una chiave esadecimale crittograficamente sicura"""
    return secrets.token_hex(length)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()