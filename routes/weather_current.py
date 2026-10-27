from flask import Blueprint, jsonify

from config import WEATHER_URL
from errors import APIError
from weather_service import (
    call_openweather,
    find_coordinates,
    get_location_from_request,
)

weather_current_bp = Blueprint(
    "weather_current", __name__, url_prefix="/api/weather"
)


# Final URL  ->  /api/weather/current
@weather_current_bp.route("/current", methods=["GET"])
def current_weather():

    city, country = get_location_from_request()
    latitude, longitude = find_coordinates(city, country)

    weather = call_openweather(
        WEATHER_URL,
        {"lat": latitude, "lon": longitude, "units": "metric"},
        "retrieve current weather"
    )

    try:
        main = weather["main"]
        condition = weather["weather"][0]
        wind = weather.get("wind", {})
        system = weather.get("sys", {})

        data = {
            "city": weather["name"],
            "country": system.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": main["temp"],
            "feels_like_c": main["feels_like"],
            "minimum_temperature_c": main.get("temp_min"),
            "maximum_temperature_c": main.get("temp_max"),
            "humidity_percent": main["humidity"],
            "pressure_hpa": main["pressure"],
            "wind_speed_mps": wind.get("speed"),
            "visibility_m": weather.get("visibility"),
            "description": condition["description"],
            "icon": condition["icon"],
            "sunrise": system.get("sunrise"),
            "sunset": system.get("sunset"),
            "observed_at": weather.get("dt")
        }
    except (KeyError, IndexError, TypeError):
        raise APIError("Received an invalid response from the weather service.", 502)

    return jsonify({"status": "success", "data": data}), 200