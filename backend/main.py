from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from database.database import get_db, engine
from database.models import Base
from routers import contracts, prime_contractors, subcontractors, procurement_officers, communications, revenue_tracking, auth, dashboard
from auth.auth import authenticate_user, create_access_token

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KDP Global Contract Brokerage System",
    description="Federal contract brokerage database system for KDP Global Enterprises",
    version="1.0.0"
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", ["http://localhost:3000"])
if isinstance(origins, str):
    origins = origins.strip("[]").replace('"', '').split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(prime_contractors.router, prefix="/api/prime-contractors", tags=["prime-contractors"])
app.include_router(subcontractors.router, prefix="/api/subcontractors", tags=["subcontractors"])
app.include_router(procurement_officers.router, prefix="/api/procurement-officers", tags=["procurement-officers"])
app.include_router(communications.router, prefix="/api/communications", tags=["communications"])
app.include_router(revenue_tracking.router, prefix="/api/revenue-tracking", tags=["revenue-tracking"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "KDP Global Contract Brokerage System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)