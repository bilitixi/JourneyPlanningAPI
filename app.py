from flask import Flask, jsonify
from routes.auth_routes import auth_bp
from routes.weather_routes import weather_bp
from routes.journey_routes import journey_bp
from routes.recommendation_routes import ai_bp
from flask_cors import CORS
import os

from db import init_db
import models

from services.email_service import EmailService

app = Flask(__name__)

# CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://journeyplanninguidraft.vercel.app"
        ]
    }
})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(journey_bp)
app.register_blueprint(ai_bp)

# =========================
# Email Service INIT
# =========================
email_service = EmailService()


# =========================
# TEST EMAIL ROUTE
# =========================
@app.route("/test-email", methods=["GET"])
def test_email():
    try:
        print("🔥 TEST EMAIL TRIGGERED")

        success = email_service.send_verification_email(
            email="your_email@gmail.com",   # CHANGE THIS
            token="test-token-123"
        )

        return jsonify({
            "email_sent": success
        }), 200

    except Exception as e:
        import traceback
        print("❌ TEST EMAIL FAILED")
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# ROOT ROUTE
# =========================
@app.route('/')
def hello_world():
    return 'Hello World!'


print(app.url_map)


# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)