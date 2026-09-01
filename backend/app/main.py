from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="CampusQuery API",
    description="Citation-grounded university knowledge assistant",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to CampusQuery API",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="CampusQuery backend",
    )