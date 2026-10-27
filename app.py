from flask import Flask, jsonify, render_template

from routes.weather_current import weather_current_bp
from routes.weather_forecast import weather_forecast_bp
from routes.favorites_create import favorites_create_bp
from routes.favorites_read import favorites_read_bp
from routes.favorites_update import favorites_update_bp
from routes.favorites_delete import favorites_delete_bp
from errors import register_error_handlers
app = Flask(__name__)
register_error_handlers(app)
app.register_blueprint(weather_current_bp)
app.register_blueprint(weather_forecast_bp)
app.register_blueprint(favorites_create_bp)
app.register_blueprint(favorites_read_bp)
app.register_blueprint(favorites_update_bp)
app.register_blueprint(favorites_delete_bp)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "WeatherHub backend is running"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)