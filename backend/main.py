import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import users, rooms, reservation, statistics, import_schedule
from utils.scheduler import start_scheduler
from database import engine
from models import Base

from prometheus_fastapi_instrumentator import Instrumentator

# Load environment variables
load_dotenv()

# Create tables in DB (if they don't exist)
Base.metadata.create_all(bind=engine)

# Init app
app = FastAPI()
Instrumentator().instrument(app).expose(app)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # include 127.0.0.1 for some dev setups
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(reservation.router)
app.include_router(statistics.router)
app.include_router(import_schedule.router)

# Start APScheduler
start_scheduler()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "room-reservation-backend"
    }