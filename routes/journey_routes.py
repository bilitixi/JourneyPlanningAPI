from flask import Blueprint, request, jsonify
from models.journey import Journey
from db import get_db
from middleware.jwt_auth import token_required
from sqlalchemy.orm import Session
from datetime import datetime

journey_bp = Blueprint('journey', __name__)


@journey_bp.route('/', methods=['GET'])
@token_required
def get_all_journeys(payload):
    """
    Get all journeys belonging to the authenticated user.
    
    Returns:
        JSON response with list of journeys
    """
    try:
        user_id = payload.get('user_id')
        db: Session = next(get_db())
        
        journeys = db.query(Journey).filter(Journey.user_id == user_id).all()
        
        return jsonify({
            'journeys': [journey.to_dict() for journey in journeys]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@journey_bp.route('/<int:journey_id>', methods=['GET'])
@token_required
def get_journey(payload, journey_id):
    """
    Get a specific journey by ID.
    
    Args:
        journey_id: ID of the journey
        
    Returns:
        JSON response with journey details
    """
    try:
        user_id = payload.get('user_id')
        db: Session = next(get_db())
        
        journey = db.query(Journey).filter(
            Journey.journey_id == journey_id,
            Journey.user_id == user_id
        ).first()
        
        if not journey:
            return jsonify({'error': 'Journey not found or access denied'}), 404
        
        return jsonify(journey.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@journey_bp.route('/', methods=['POST'])
@token_required
def create_journey(payload):
    """
    Create a new journey.
    
    Returns:
        JSON response with created journey
    """
    try:
        user_id = payload.get('user_id')
        data = request.get_json()
        db: Session = next(get_db())
        
        # Validate required fields
        required_fields = ['destination', 'start_date', 'end_date', 'budget', 'people']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create journey
        journey = Journey(
            user_id=user_id,
            destination=data['destination'],
            start_date=start_date,
            end_date=end_date,
            budget=data['budget'],
            people=data['people'],
            notes=data.get('notes')
        )
        
        db.add(journey)
        db.commit()
        db.refresh(journey)
        
        return jsonify(journey.to_dict()), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


@journey_bp.route('/<int:journey_id>', methods=['PUT'])
@token_required
def update_journey(payload, journey_id):
    """
    Update an existing journey.
    
    Args:
        journey_id: ID of the journey
        
    Returns:
        JSON response with updated journey
    """
    try:
        user_id = payload.get('user_id')
        data = request.get_json()
        db: Session = next(get_db())
        
        journey = db.query(Journey).filter(
            Journey.journey_id == journey_id,
            Journey.user_id == user_id
        ).first()
        
        if not journey:
            return jsonify({'error': 'Journey not found or access denied'}), 404
        
        # Update fields if provided
        if 'destination' in data:
            journey.destination = data['destination']
        if 'start_date' in data:
            try:
                journey.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        if 'end_date' in data:
            try:
                journey.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        if 'budget' in data:
            journey.budget = data['budget']
        if 'people' in data:
            journey.people = data['people']
        if 'notes' in data:
            journey.notes = data['notes']
        
        db.commit()
        db.refresh(journey)
        
        return jsonify(journey.to_dict()), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


@journey_bp.route('/<int:journey_id>', methods=['DELETE'])
@token_required
def delete_journey(payload, journey_id):
    """
    Delete a journey.
    
    Args:
        journey_id: ID of the journey
        
    Returns:
        JSON response confirming deletion
    """
    try:
        user_id = payload.get('user_id')
        db: Session = next(get_db())
        
        journey = db.query(Journey).filter(
            Journey.journey_id == journey_id,
            Journey.user_id == user_id
        ).first()
        
        if not journey:
            return jsonify({'error': 'Journey not found or access denied'}), 404
        
        db.delete(journey)
        db.commit()
        
        return jsonify({'message': 'Journey deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
