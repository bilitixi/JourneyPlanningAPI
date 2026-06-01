from flask import Flask
from routes.auth_routes import auth_bp
from routes.weather_routes import weather_bp
from routes.journey_routes import journey_bp

from db import init_db
import models
app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(journey_bp)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
