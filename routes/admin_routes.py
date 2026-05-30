from flask import Blueprint, jsonify
from models.api_usage_log import APIUsageLog
from db import get_db
from sqlalchemy.orm import Session
from middleware.jwt_auth import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_api_logs(current_user):
    """
    Admin endpoint to retrieve API usage logs.
    Admin users can retrieve API usage logs.
    """
    try:
        db: Session = next(get_db())
        
        # Query all API usage logs
        logs = db.query(APIUsageLog).order_by(APIUsageLog.created_at.desc()).all()
        
        # Convert logs to dictionaries
        logs_list = [log.to_dict() for log in logs]
        
        return jsonify({
            'count': len(logs_list),
            'logs': logs_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
