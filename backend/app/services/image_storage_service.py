import os
import hashlib
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.image_classification import ImageClassification
from .encryption_service import EncryptionService

class ImageStorageService:
    def __init__(self, db: Session):
        self.db = db
        backend_dir = Path(__file__).parent.parent.parent.parent
        self.storage_path = backend_dir / 'storage' / 'images'
        print(f"Storage path: {self.storage_path.absolute()}")  # Debug log
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            print(f"Storage directory created/verified at: {self.storage_path.absolute()}")
        except Exception as e:
            print(f"Error creating storage directory: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create storage directory: {str(e)}")
        
        self.encryption_service = EncryptionService(db)

    async def store_image(self, image_bytes: bytes, classification_id: int) -> str:
        try:
            classification = self.db.query(ImageClassification).filter(
                ImageClassification.classification_id == classification_id
            ).first()
            
            if not classification:
                raise HTTPException(status_code=404, detail="Classification not found")

            encrypted_data, user_specific_salt = self.encryption_service.encrypt_image(
                image_bytes, 
                classification.user_id
            )

            filename = f"{classification.image_hash}_{classification_id}.enc"
            file_path = self.storage_path / filename
            print(f"Attempting to store image at: {file_path.absolute()}")  # Debug log

            try:
                with open(file_path, 'wb') as f:
                    f.write(user_specific_salt)  
                    f.write(encrypted_data)      
                print(f"Successfully stored image at: {file_path.absolute()}")
            except Exception as e:
                print(f"Error writing file: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to write image file: {str(e)}")

            classification.image_path = str(file_path)
            classification.encryption_salt = user_specific_salt.hex()  
            self.db.commit()

            return str(file_path)
        except Exception as e:
            print(f"Error in store_image: {str(e)}")  
            raise HTTPException(status_code=500, detail=f"Failed to store image: {str(e)}")

    def get_image_path(self, classification_id: int) -> str:
        classification = self.db.query(ImageClassification).filter(
            ImageClassification.classification_id == classification_id
        ).first()
        
        if not classification or not classification.image_path:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return classification.image_path

    def get_decrypted_image(self, classification_id: int) -> bytes:
        classification = self.db.query(ImageClassification).filter(
            ImageClassification.classification_id == classification_id
        ).first()
        
        if not classification or not classification.image_path:
            raise HTTPException(status_code=404, detail="Image not found")

        try:

            file_path = Path(classification.image_path)
            print(f"Attempting to read image from: {file_path.absolute()}")  
            
            if not file_path.exists():
                print(f"File does not exist at: {file_path.absolute()}")
                raise HTTPException(status_code=404, detail="Image file not found")

            with open(file_path, 'rb') as f:
                user_specific_salt = f.read(16) 
                encrypted_data = f.read()      

            return self.encryption_service.decrypt_image(
                encrypted_data,
                classification.user_id,
                user_specific_salt
            )
        except Exception as e:
            print(f"Error in get_decrypted_image: {str(e)}")  
            raise HTTPException(status_code=500, detail=f"Failed to decrypt image: {str(e)}") 