from flask import Blueprint, request, jsonify
from models.journey import Journey
from db import get_db
from middleware.jwt_auth import token_required
from sqlalchemy.orm import Session
from datetime import datetime

journey_bp = Blueprint('journey', __name__, url_prefix='/api/journeys')


# =========================
# GET ALL JOURNEYS
# =========================
@journey_bp.route('', methods=['GET'])
@token_required
def get_all_journeys(payload):
    db: Session = next(get_db())
    user_id = payload.get('user_id')

    journeys = db.query(Journey).filter(Journey.user_id == user_id).all()

    return jsonify({
        "journeys": [j.to_dict() for j in journeys]
    }), 200


# =========================
# GET BY ID
# =========================
@journey_bp.route('/<int:journey_id>', methods=['GET'])
@token_required
def get_journey(payload, journey_id):
    db: Session = next(get_db())
    user_id = payload.get('user_id')

    journey = db.query(Journey).filter(
        Journey.journey_id == journey_id,
        Journey.user_id == user_id
    ).first()

    if not journey:
        return jsonify({"error": "Journey not found"}), 404

    return jsonify(journey.to_dict()), 200


# =========================
# CREATE JOURNEY (FIXED)
# =========================
@journey_bp.route('', methods=['POST'])
@token_required
def create_journey(payload):
    db: Session = next(get_db())
    user_id = payload.get('user_id')

    data = request.get_json()

    required = ['destination', 'start_date', 'end_date', 'budget', 'people']
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing required field: {f}"}), 400

    try:
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

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

    # IMPORTANT: ensure journey_id exists in response
    return jsonify(journey.to_dict()), 201


# =========================
# UPDATE JOURNEY
# =========================
@journey_bp.route('/<int:journey_id>', methods=['PUT'])
@token_required
def update_journey(payload, journey_id):
    db: Session = next(get_db())
    user_id = payload.get('user_id')

    journey = db.query(Journey).filter(
        Journey.journey_id == journey_id,
        Journey.user_id == user_id
    ).first()

    if not journey:
        return jsonify({"error": "Journey not found"}), 404

    data = request.get_json()

    if 'destination' in data:
        journey.destination = data['destination']

    if 'start_date' in data:
        try:
            journey.start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    if 'end_date' in data:
        try:
            journey.end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    if 'budget' in data:
        journey.budget = data['budget']

    if 'people' in data:
        journey.people = data['people']

    db.commit()
    db.refresh(journey)

    return jsonify(journey.to_dict()), 200


# =========================
# DELETE JOURNEY
# =========================
@journey_bp.route('/<int:journey_id>', methods=['DELETE'])
@token_required
def delete_journey(payload, journey_id):
    db: Session = next(get_db())
    user_id = payload.get('user_id')

    journey = db.query(Journey).filter(
        Journey.journey_id == journey_id,
        Journey.user_id == user_id
    ).first()

    if not journey:
        return jsonify({"error": "Journey not found"}), 404

    db.delete(journey)
    db.commit()

    return jsonify({"message": "deleted successfully"}), 200