from flask import Blueprint, jsonify

from config import FORECAST_URL
from errors import APIError
from weather_service import (
    call_openweather,
    find_coordinates,
    get_location_from_request,
)

weather_forecast_bp = Blueprint(
    "weather_forecast", __name__, url_prefix="/api/weather"
)


# Final URL  ->  /api/weather/forecast
@weather_forecast_bp.route("/forecast", methods=["GET"])
def weather_forecast():

    city, country = get_location_from_request()
    latitude, longitude = find_coordinates(city, country)

    forecast_data = call_openweather(
        FORECAST_URL,
        {"lat": latitude, "lon": longitude, "units": "metric"},
        "retrieve the forecast"
    )

    try:
        forecast_list = []

        for item in forecast_data.get("list", []):
            main = item.get("main", {})
            weather_info = item.get("weather", [{}])[0]

            forecast_list.append({
                "forecast_time_utc": item.get("dt_txt"),
                "temperature_c": main.get("temp"),
                "feels_like_c": main.get("feels_like"),
                "humidity_percent": main.get("humidity"),
                "description": weather_info.get("description"),
                "icon": weather_info.get("icon"),
                "wind_speed_mps": item.get("wind", {}).get("speed"),
                "precipitation_probability_percent": round(
                    item.get("pop", 0) * 100
                )
            })

        data = {
            "city": forecast_data["city"]["name"],
            "country": forecast_data["city"]["country"],
            "timezone_offset_seconds": forecast_data["city"]["timezone"],
            "forecast_count": len(forecast_list),
            "forecast": forecast_list
        }
    except (KeyError, IndexError, TypeError, AttributeError):
        raise APIError("Received an invalid forecast response.", 502)

    return jsonify({"status": "success", "data": data}), 200