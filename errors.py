from flask import jsonify, request
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Raise this anywhere to send a JSON error to the client."""

    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def error_response(message, status_code):
    return jsonify({"status": "error", "message": message}), status_code


def register_error_handlers(app):

    @app.errorhandler(APIError)
    def handle_api_error(err):
        return error_response(err.message, err.status_code)

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        # Only API paths get JSON; the normal pages keep Flask's default
        if not request.path.startswith("/api/"):
            return err

        messages = {
            404: "The requested endpoint was not found.",
            405: "This method is not allowed for this endpoint.",
        }
        return error_response(messages.get(err.code, err.description), err.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        # Log the real error for you, show a safe message to the client
        app.logger.exception("Unhandled error: %s", err)

        if request.path.startswith("/api/"):
            return error_response("Something went wrong on the server.", 500)
        return "Internal Server Error", 500