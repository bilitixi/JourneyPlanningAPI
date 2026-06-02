from flask import Flask
from routes.auth_routes import auth_bp
from routes.weather_routes import weather_bp
from routes.journey_routes import journey_bp
from routes.recommendation_routes import ai_bp
from flask_cors import CORS

from db import init_db
import models
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(journey_bp)
app.register_blueprint(ai_bp)

@app.route('/')
def hello_world():
    return 'Hello World!'
print(app.url_map)

if __name__ == '__main__':

    init_db()
    app.run(host='0.0.0.0', port=5000)
