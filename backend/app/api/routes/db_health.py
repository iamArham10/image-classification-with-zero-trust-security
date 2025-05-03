from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from ...db.session import get_db
from sqlalchemy import text
router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check DB connection
        result = db.execute(text("SELECT 1")).scalar()
        return {"db_status": "connected" if result == 1 else "disconnected"}
    except Exception as e:
        return {"db_status": "disconnected", "error": str(e)}
