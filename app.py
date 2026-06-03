from flask import Flask
from routes.auth_routes import auth_bp
from routes.weather_routes import weather_bp
from routes.journey_routes import journey_bp
from routes.recommendation_routes import ai_bp
from flask_cors import CORS

from services.auth_service import email_service
from services.email_service import mail
import os

from db import init_db
import models
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
"http://127.0.0.1:3000"
        ]
    }
})

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@journeyplanning.com')

# Initialize Flask-Mail
mail.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(journey_bp)
app.register_blueprint(ai_bp)
@app.route("/test-email")
def test_email():
    success = email_service.send_verification_email(
        email="bilitixi@gmail.com",  # change this
        verification_token="test-token-123"
    )

    return {
        "email_sent": success
    }
@app.route('/')
def hello_world():
    return 'Hello World!'
print(app.url_map)

if __name__ == '__main__':

    init_db()
    app.run(host='0.0.0.0', port=5000)
