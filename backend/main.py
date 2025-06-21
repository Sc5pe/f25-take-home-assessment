from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import requests
import os
from dotenv import load_dotenv
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env_path = Path(__file__).parent.absolute() / ".env"
print("Looking for .env at:", env_path)

load_dotenv(dotenv_path=env_path, override=True)
print("Loaded API KEY:", os.getenv("WEATHERSTACK_API_KEY"))

load_dotenv()

app = FastAPI(title="Weather Data System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_storage: Dict[str, Dict[str, Any]] = {}

class WeatherRequest(BaseModel):
    date: str
    location: str
    notes: Optional[str] = ""

class WeatherResponse(BaseModel):
    id: str

@app.post("/weather", response_model=WeatherResponse)
async def create_weather_request(request: WeatherRequest):
    """
    1. Receive JSON data (date, location, notes)
    2. Call WeatherStack API for the location
    3. Store combined data with unique ID in memory
    4. Return the ID to frontend
    """
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    
    print("Loaded API KEY:", api_key)

    if not api_key:
        raise HTTPException(status_code=500, detail="WeatherStack API key is not set")

    response = requests.get(
        "http://api.weatherstack.com/current",
        params={"access_key": api_key, "query": request.location}
    )

    if response.status_code != 200 or "error" in response.json():
        raise HTTPException(status_code=400, detail="Error fetching weather data")

    weather_data = response.json()
    weather_id = str(uuid.uuid4())

    weather_storage[weather_id] = {
        "date": request.date,
        "location": request.location,
        "notes": request.notes,
        "weather": weather_data
    }

    return WeatherResponse(id=weather_id)

@app.get("/weather/{weather_id}")
async def get_weather_data(weather_id: str):
    """
    Retrieve stored weather data by ID.
    This endpoint is already implemented for the assessment.
    """
    if weather_id not in weather_storage:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return weather_storage[weather_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
def root():
    return {"message": "Weather API is running"}