# WeatherHub — OpenWeather Dashboard

A web-based weather dashboard built with Flask, Python, HTML, CSS, and JavaScript. WeatherHub is designed to provide weather information through a clean, responsive interface.

## Dashboard Preview

<!-- Save your screenshot at screenshots/weatherhub-dashboard.png -->
![WeatherHub Dashboard](screenshots/weatherhub-dashboard.png)

## Features

- **Current Weather:** Retrieve current weather information for a selected city.
- **Weather Forecast:** View forecast information when supported by the configured weather API.
- **Favourite Cities:** Create, view, update, and delete saved favourite cities.
- **Responsive Interface:** A dashboard layout designed for desktop and smaller screens.
- **Modular Flask Backend:** Separate route modules for weather and favourite-city operations.
- **External Weather API:** Integrates with the OpenWeather service.

> Note: Confirm each feature works in your local environment before treating it as production-ready.

## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Weather Data:** OpenWeather API
- **Database:** MySQL (if configured in your local setup)
- **Configuration:** Environment variables using a `.env` file

## Project Structure

```text
OpenWeather_Hub/
├── routes/
│   ├── __init__.py
│   ├── favorites_create.py
│   ├── favorites_read.py
│   ├── favorites_update.py
│   ├── favorites_delete.py
│   ├── weather_current.py
│   └── weather_forecast.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── database.py
├── errors.py
├── requirements.txt
├── weather_service.py
└── README.md
```

## Prerequisites

Before running the application, install:

- Python 3.10 or a compatible version supported by your dependencies
- pip
- An OpenWeather API key
- MySQL, if required by your database configuration

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/divyanayanasri/OpenWeather_Dashboard.git
cd OpenWeather_Dashboard
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

Add your own OpenWeather API key and database credentials as required by `config.py`.

**Never commit your `.env` file, API keys, or passwords to GitHub.**

### 5. Run the application

```bash
python app.py
```

Open the local URL printed by Flask in your browser. The default is often `http://127.0.0.1:5000/`, unless your application is configured to use another host or port.

## API Endpoints

WeatherHub exposes REST API endpoints through Flask Blueprints. Weather data is retrieved from the OpenWeather service using the selected city's coordinates.

### 1. Get Current Weather

**Endpoint:** `GET /api/weather/current`

Retrieves current weather conditions for a specified location.

**Query parameters**

| Parameter | Required | Description |
|---|---|---|
| `city` | Verify in `get_location_from_request()` | City name |
| `country` | Verify in `get_location_from_request()` | Country code or name, if supported |

**Successful response:** `200 OK`

```json
{
  "status": "success",
  "data": {
    "city": "London",
    "country": "GB",
    "latitude": 51.5072,
    "longitude": -0.1276,
    "temperature_c": 18.5,
    "feels_like_c": 18.0,
    "minimum_temperature_c": 16.0,
    "maximum_temperature_c": 20.0,
    "humidity_percent": 70,
    "pressure_hpa": 1012,
    "wind_speed_mps": 3.5,
    "visibility_m": 10000,
    "description": "scattered clouds",
    "icon": "03d",
    "sunrise": 1790000000,
    "sunset": 1790040000,
    "observed_at": 1790020000
  }
}
```

*The values above are illustrative examples of the response structure, not live weather data. Optional fields may be `null`.*

### 2. Get Weather Forecast

**Endpoint:** `GET /api/weather/forecast`

Retrieves forecast information for the selected location, including temperature, humidity, weather conditions, wind speed, and precipitation probability.

**Successful response:** `200 OK`

```json
{
  "status": "success",
  "data": {
    "city": "London",
    "country": "GB",
    "timezone_offset_seconds": 0,
    "forecast_count": 1,
    "forecast": [
      {
        "forecast_time_utc": "2026-10-28 12:00:00",
        "temperature_c": 18.5,
        "feels_like_c": 18.0,
        "humidity_percent": 70,
        "description": "scattered clouds",
        "icon": "03d",
        "wind_speed_mps": 3.5,
        "precipitation_probability_percent": 20
      }
    ]
  }
}
```

*The example shows one forecast item for readability. The actual response may contain multiple forecast entries.*

### Error Handling

The application uses a shared `APIError` mechanism for errors raised while processing weather-service responses. The HTTP status and error response body depend on the implementation in `errors.py` and `weather_service.py`.

Common scenarios to handle include:

- Missing or invalid location parameters
- Unknown city or geocoding failures
- Invalid or missing OpenWeather API credentials
- Weather-service timeouts or rate limits
- Unexpected responses from the weather service

Check the application's error handlers for the exact error response format and status codes.
## Configuration

Store environment-specific values in `.env`. Use `.env.example` to document the required variable names without including real credentials.

## Testing

Automated tests are planned. Once a test suite is added, run it with:

```bash
python -m pytest
```

## Security Notes

- Keep credentials out of source control.
- Validate incoming request data on the server.
- Use request timeouts when calling external APIs.
- Disable Flask debug mode in production.
- Handle API and database errors without exposing secrets or internal details.

## Future Improvements

- Automated tests and continuous integration
- Weather-data caching
- Temperature unit conversion
- Recent search history
- Weather charts and visualizations
- Production deployment with a live demo

## Author

**Divya Nayana Sri**

GitHub: [divyanayanasri](https://github.com/divyanayanasri)

## License

A license has not yet been selected for this project.
