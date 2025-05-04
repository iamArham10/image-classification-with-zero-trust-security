"""
This file contains token rotation service
"""
from pathlib import Path
import os
from datetime import datetime
from ..core.config import settings

class TokenRotationService:
    @staticmethod
    def rotate_token():
        new_token = os.urandom(32).hex()

        BASE_DIR = Path(__file__).resolve().parent.parent
        env_path = str(BASE_DIR / '.env')

        with open(env_path, "r") as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if "ADMIN_CREATION_TOKEN" in line:
                lines[i] = f"ADMIN_CREATION_TOKEN={new_token}\n"
        
        with open(env_path, "w") as file:
            file.writelines(lines)



