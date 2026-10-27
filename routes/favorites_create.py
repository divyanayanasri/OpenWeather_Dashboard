from flask import Blueprint, jsonify, request
from mysql.connector import Error

from database import get_connection

favorites_create_bp = Blueprint(
    "favorites_create", __name__, url_prefix="/api/favorites"
)


def parse_coordinate(value, minimum, maximum):
    """Return a float within range, None if empty, or raise ValueError."""
    if value is None or value == "":
        return None
    number = float(value)
    if not (minimum <= number <= maximum):
        raise ValueError("out of range")
    return number


# Final URL  ->  POST /api/favorites
@favorites_create_bp.route("", methods=["POST"], strict_slashes=False)
def create_favorite():

    # Read the JSON body
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be valid JSON."
        }), 400

    city = str(data.get("city") or "").strip()
    country = str(data.get("country") or "").strip().upper()
    note = data.get("note")

    # Validate city
    if not city:
        return jsonify({
            "status": "error",
            "message": "Please provide a city name."
        }), 400

    if len(city) > 100:
        return jsonify({
            "status": "error",
            "message": "City name must be 100 characters or fewer."
        }), 400

    # Validate country (optional, 2 letters)
    if country and not (len(country) == 2 and country.isalpha()):
        return jsonify({
            "status": "error",
            "message": "Country must be a 2-letter code, for example IN."
        }), 400

    # Validate note (optional)
    if note is not None:
        note = str(note).strip() or None
        if note and len(note) > 255:
            return jsonify({
                "status": "error",
                "message": "Note must be 255 characters or fewer."
            }), 400

    # Validate coordinates (optional)
    try:
        latitude = parse_coordinate(data.get("latitude"), -90, 90)
        longitude = parse_coordinate(data.get("longitude"), -180, 180)
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Latitude must be -90 to 90 and longitude -180 to 180."
        }), 400

    # Save to MySQL
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # %s placeholders keep user input out of the SQL string
        cursor.execute(
            """
            INSERT INTO favorites (city, country, latitude, longitude, note)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (city, country, latitude, longitude, note)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "City added to favorites.",
            "data": {
                "id": new_id,
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "note": note
            }
        }), 201

    except Error as err:
        # 1062 = duplicate entry (city + country already saved)
        if err.errno == 1062:
            return jsonify({
                "status": "error",
                "message": "This city is already in your favorites."
            }), 409

        return jsonify({
            "status": "error",
            "message": "Database error. Please try again later."
        }), 500

    finally:
        if conn is not None and conn.is_connected():
            conn.close()