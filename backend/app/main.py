# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .middleware.security import SecurityMiddleware
from .api.routes import auth, db_health, classification, admin_management, user_management, audit_log


app = FastAPI(
    title="Image Classification System",
    description='Image Classification System with Zero Trust Security',
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

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(db_health.router, prefix=f"{settings.API_V1_STR}/health", tags=["health"])
app.include_router(classification.router, prefix=f"{settings.API_V1_STR}/classification", tags=["classification"])
app.include_router(admin_management.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin_management"])
app.include_router(user_management.router, prefix=f"{settings.API_V1_STR}/user", tags=["user_management"])
app.include_router(audit_log.router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit_logs"])

@app.get("/")
async def root():
    return {"message": f"Welcome to Image Classification System API"}