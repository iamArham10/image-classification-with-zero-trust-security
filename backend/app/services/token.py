"""
This file contains token rotation service
"""

import os
from datetime import datetime
from ..core.config import settings

class TokenRotationService:
    @staticmethod
    def rotate_token():
        # Generate a new token
        new_token = os.urandom(32).hex()

        # changing ADMIN_CREATION_TOKEN in .env file 
        BASE_DIR = Path(__file__).resolve().parent.parent
        env_path = str(BASE_DIR / '.env')

        # Read all lines
        with open(env_path, "r") as file:
            lines = file.readlines()

        # Modify the target line
        for i, line in enumerate(lines):
            if "ADMIN_CREATION_TOKEN" in line:
                lines[i] = f"ADMIN_CREATION_TOKEN={new_token}\n"
        
        # Write back updated lines 
        with open(env_path, "w") as file:
            file.writelines(lines)



