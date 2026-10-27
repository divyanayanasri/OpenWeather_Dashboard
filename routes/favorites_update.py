from flask import Blueprint, jsonify, request
from mysql.connector import Error

from database import get_connection
from routes.favorites_create import parse_coordinate
from routes.favorites_read import format_row

favorites_update_bp = Blueprint(
    "favorites_update", __name__, url_prefix="/api/favorites"
)


def error(message, code):
    return jsonify({"status": "error", "message": message}), code


# Final URL  ->  PUT /api/favorites/3
@favorites_update_bp.route("/<int:favorite_id>", methods=["PUT", "PATCH"])
def update_favorite(favorite_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error("Request body must be valid JSON.", 400)

    # Only these columns can be changed
    allowed = {"city", "country", "latitude", "longitude", "note"}
    if not any(key in data for key in allowed):
        return error(
            "Send at least one field to update: "
            "city, country, latitude, longitude or note.", 400
        )

    # Collect validated changes as {column: value}
    changes = {}

    if "city" in data:
        city = str(data["city"] or "").strip()
        if not city:
            return error("City cannot be empty.", 400)
        if len(city) > 100:
            return error("City name must be 100 characters or fewer.", 400)
        changes["city"] = city

    if "country" in data:
        country = str(data["country"] or "").strip().upper()
        if country and not (len(country) == 2 and country.isalpha()):
            return error("Country must be a 2-letter code, for example IN.", 400)
        changes["country"] = country

    if "note" in data:
        note = data["note"]
        if note is not None:
            note = str(note).strip() or None
            if note and len(note) > 255:
                return error("Note must be 255 characters or fewer.", 400)
        changes["note"] = note

    try:
        if "latitude" in data:
            changes["latitude"] = parse_coordinate(data["latitude"], -90, 90)
        if "longitude" in data:
            changes["longitude"] = parse_coordinate(data["longitude"], -180, 180)
    except (ValueError, TypeError):
        return error("Latitude must be -90 to 90 and longitude -180 to 180.", 400)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: make sure the favorite exists
        cursor.execute("SELECT id FROM favorites WHERE id = %s", (favorite_id,))
        if cursor.fetchone() is None:
            cursor.close()
            return error("Favorite not found.", 404)

        # Step 2: build the UPDATE (column names come from the fixed
        # whitelist above, values go through %s placeholders)
        set_clause = ", ".join(f"{column} = %s" for column in changes)
        values = list(changes.values()) + [favorite_id]

        cursor.execute(
            f"UPDATE favorites SET {set_clause} WHERE id = %s", values
        )
        conn.commit()

        # Step 3: read the row back and return it
        cursor.execute(
            """
            SELECT id, city, country, latitude, longitude, note,
                   created_at, updated_at
            FROM favorites
            WHERE id = %s
            """,
            (favorite_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Favorite updated.",
            "data": format_row(row)
        }), 200

    except Error as err:
        # 1062 = this city + country already exists as another favorite
        if err.errno == 1062:
            return error("This city is already in your favorites.", 409)
        return error("Database error. Please try again later.", 500)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()