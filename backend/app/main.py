from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router.router_admin import router as admin_router

app = FastAPI (
    title='Student Attendance System',
    description='Facial Recognition Attendance System with Zero Trust Security',
    version="0.1.0"
)

# Configure CORS to allow request from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Student Attendance System API"}

# Include routers
app.include_router(admin_router)