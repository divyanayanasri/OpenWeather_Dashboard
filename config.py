import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# OpenWeather settings
API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Values that indicate an API key has not been configured
PLACEHOLDER_KEYS = {
    "",
    "your_openweather_api_key_here",
    "your_new_rotated_api_key",
    "your_new_rotated_api_key_value",
}
# MySQL settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "weatherhub_db")