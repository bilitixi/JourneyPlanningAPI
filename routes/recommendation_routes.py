from flask import Blueprint, jsonify
from sqlalchemy.orm import Session

from db import SessionLocal, get_db
from middleware.jwt_auth import token_required
from models.journey import Journey
from services.ai_service import AIService

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/api/recommendations")

ai_service = AIService()


@ai_bp.route('/<int:journey_id>', methods=['POST'])
@token_required
def generate_recommendations(payload, journey_id):
    db = get_db()
    try:
        # 1. Get journey from DB
        journey = db.query(Journey).filter(Journey.journey_id == journey_id).first()

        if not journey:
            return jsonify({"error": "Journey not found"}), 404

        # 2. Call AI service
        result = ai_service.generate_recommendations(
            destination=journey.destination,
            start_date=str(journey.start_date),
            end_date=str(journey.end_date),
            budget=float(journey.budget),
            people=journey.people
        )

        # 3. Return response
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to generate recommendations",
            "details": str(e)
        }), 500

    finally:
        db.close()