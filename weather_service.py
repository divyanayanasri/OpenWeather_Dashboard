import requests
from flask import request

from config import API_KEY, GEOCODING_URL, PLACEHOLDER_KEYS
from errors import APIError


def get_location_from_request():
    """Read and validate ?city= and ?country=. Returns (city, country)."""
    city = request.args.get("city", "").strip()
    country = request.args.get("country", "").strip().upper()

    if not city:
        raise APIError("Please provide a city name.", 400)

    if API_KEY.lower() in PLACEHOLDER_KEYS:
        raise APIError(
            "OpenWeather API key is not configured. "
            "Please check your .env file.", 500
        )

    return city, country


def call_openweather(url, params, action):
    """Call OpenWeather and return its JSON, or raise an APIError."""
    params = {**params, "appid": API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.Timeout:
        raise APIError("The weather service took too long to respond.", 504)
    except requests.exceptions.RequestException:
        raise APIError("Unable to connect to the weather service.", 502)

    if response.status_code == 401:
        raise APIError(
            "OpenWeather rejected the API key. "
            "Check its validity and activation status.", 502
        )
    if response.status_code == 429:
        raise APIError("OpenWeather API rate limit reached.", 503)
    if response.status_code != 200:
        raise APIError(f"Unable to {action}.", 502)

    try:
        return response.json()
    except ValueError:
        raise APIError("Received an invalid response from the weather service.", 502)


def find_coordinates(city, country):
    """Turn a city name into (latitude, longitude)."""
    query = f"{city},{country}" if country else city

    locations = call_openweather(
        GEOCODING_URL,
        {"q": query, "limit": 1},
        "search for the requested city"
    )

    if not locations:
        raise APIError("City not found. Please check the city name.", 404)

    try:
        return locations[0]["lat"], locations[0]["lon"]
    except (KeyError, IndexError, TypeError):
        raise APIError("Received an invalid response from the weather service.", 502)