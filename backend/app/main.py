# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .middleware.session import SessionMiddleware
from .middleware.ip_restriction import IPRestrictionMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware
from .api.routes import auth, db_health 

app = FastAPI(
    title="Student Attendance System",
    description='Facial Recognition Attendance System with Zero Trust Security',
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(db_health.router, prefix=f"{settings.API_V1_STR}/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": f"Welcome to Student Attendance System API"}