from flask import Blueprint, request, jsonify
from services.weather_service import WeatherService
from models.journey import Journey
from db import get_db
from middleware.jwt_auth import token_required
from sqlalchemy.orm import Session

weather_bp = Blueprint('weather', __name__)
weather_service = WeatherService()


@weather_bp.route('/<int:journey_id>', methods=['GET'])
@token_required
def get_weather_forecast(payload, journey_id):
    """
    Get weather forecast for a journey.
    
    Args:
        journey_id: ID of the journey
        
    Returns:
        JSON response with weather forecast data
    """
    try:
        user_id = payload.get('user_id')
        db: Session = next(get_db())
        
        # Get the journey and verify it belongs to the user
        journey = db.query(Journey).filter(
            Journey.journey_id == journey_id,
            Journey.user_id == user_id
        ).first()
        
        if not journey:
            return jsonify({'error': 'Journey not found or access denied'}), 404
        
        # Get weather forecast from service
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
