import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Tuple
from sqlalchemy.orm import Session
from ..models.base_user import BaseUser

class EncryptionService:
    def __init__(self, db: Session):
        self.db = db
        self.salt = os.urandom(16)  

    def _derive_key(self, user_id: int, user_specific_salt: bytes) -> bytes:
        user = self.db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")

        user_data = f"{user.user_id}{user.email}{user.created_at}".encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_specific_salt,
            iterations=100000,
        )
        
        return base64.urlsafe_b64encode(kdf.derive(user_data))

    def encrypt_image(self, image_bytes: bytes, user_id: int) -> Tuple[bytes, bytes]:
        user_specific_salt = os.urandom(16)
        
        key = self._derive_key(user_id, user_specific_salt)
        
        f = Fernet(key)
        
        encrypted_data = f.encrypt(image_bytes)
        
        return encrypted_data, user_specific_salt

    def decrypt_image(self, encrypted_data: bytes, user_id: int, user_specific_salt: bytes) -> bytes:
        """Decrypt image data using user-specific key"""
        key = self._derive_key(user_id, user_specific_salt)
        
        f = Fernet(key)
        
        return f.decrypt(encrypted_data) 