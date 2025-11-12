from fastapi import FastAPI
from app.models import create_tables

app = FastAPI(title="Travel Snapshot API")

# Create tables when server starts
create_tables()

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
