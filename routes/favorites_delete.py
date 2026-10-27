from flask import Blueprint, jsonify
from mysql.connector import Error

from database import get_connection
from routes.favorites_read import format_row

favorites_delete_bp = Blueprint(
    "favorites_delete", __name__, url_prefix="/api/favorites"
)


# Final URL  ->  DELETE /api/favorites/3
@favorites_delete_bp.route("/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: read the row first so we can return what was deleted
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

        if row is None:
            cursor.close()
            return jsonify({
                "status": "error",
                "message": "Favorite not found."
            }), 404

        # Step 2: delete it
        cursor.execute("DELETE FROM favorites WHERE id = %s", (favorite_id,))
        conn.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Favorite deleted.",
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