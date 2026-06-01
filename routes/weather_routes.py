from flask import Blueprint, jsonify
from services.weather_service import WeatherService
from models.journey import Journey
from db import get_db
from middleware.jwt_auth import token_required
from sqlalchemy.orm import Session

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/<int:journey_id>', methods=['GET'])
@token_required
def get_weather_forecast(payload, journey_id):
    """
    Get weather forecast for a journey.
    """
    try:
        user_id = payload.get('user_id')
        db: Session = next(get_db())

        # Get journey for user
        journey = db.query(Journey).filter(
            Journey.journey_id == journey_id,
            Journey.user_id == user_id
        ).first()

        if not journey:
            return jsonify({'error': 'Journey not found or access denied'}), 404

        # ✅ Create service HERE (not at import time)
        weather_service = WeatherService()

        result, status_code = weather_service.get_weather_forecast(
            destination=journey.destination,
            start_date=journey.start_date,
            end_date=journey.end_date
        )

        return jsonify(result), status_code

    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500