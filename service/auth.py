import hashlib

def hash_password(password: str) -> str :
    password_byte = password.encode()
    hashed_password = hashlib.sha3_256(password_byte).hexdigest()
    return hashed_password

def verify_password(plain_password: str , hashed_password: str) -> bool:
    hashed_plain_password = hash_password(plain_password)
    return hashed_plain_password == hashed_password

