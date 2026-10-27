from flask import Blueprint, jsonify, request
from mysql.connector import Error

from database import get_connection

favorites_read_bp = Blueprint(
    "favorites_read", __name__, url_prefix="/api/favorites"
)


def format_row(row):
    """Convert a database row into JSON-friendly values.

    MySQL returns DECIMAL and TIMESTAMP objects, so turn them into
    plain floats and ISO date strings.
    """
    return {
        "id": row["id"],
        "city": row["city"],
        "country": row["country"],
        "latitude": float(row["latitude"]) if row["latitude"] is not None else None,
        "longitude": float(row["longitude"]) if row["longitude"] is not None else None,
        "note": row["note"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


# Final URL  ->  GET /api/favorites
# Optional search:  GET /api/favorites?city=Vij
@favorites_read_bp.route("", methods=["GET"], strict_slashes=False)
def get_favorites():

    search = request.args.get("city", "").strip()

    conn = None
    try:
        conn = get_connection()
        # dictionary=True returns each row as {"column": value}
        cursor = conn.cursor(dictionary=True)

        if search:
            cursor.execute(
                """
                SELECT id, city, country, latitude, longitude, note,
                       created_at, updated_at
                FROM favorites
                WHERE city LIKE %s
                ORDER BY created_at DESC, id DESC
                """,
                (f"%{search}%",)
            )
        else:
            cursor.execute(
                """
                SELECT id, city, country, latitude, longitude, note,
                       created_at, updated_at
                FROM favorites
                ORDER BY created_at DESC, id DESC
                """
            )

        rows = cursor.fetchall()
        cursor.close()

        favorites = [format_row(row) for row in rows]

        return jsonify({
            "status": "success",
            "count": len(favorites),
            "data": favorites
        }), 200

    except Error:
        return jsonify({
            "status": "error",
            "message": "Database error. Please try again later."
        }), 500

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


# Final URL  ->  GET /api/favorites/3
@favorites_read_bp.route("/<int:favorite_id>", methods=["GET"])
def get_favorite(favorite_id):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

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

        if row is None:
            return jsonify({
                "status": "error",
                "message": "Favorite not found."
            }), 404

        return jsonify({
            "status": "success",
            "data": format_row(row)
        }), 200

    except Error:
        return jsonify({
            "status": "error",
            "message": "Database error. Please try again later."
        }), 500

    finally:
        if conn is not None and conn.is_connected():
            conn.close()