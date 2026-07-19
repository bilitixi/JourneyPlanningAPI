from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from middleware.jwt_auth import token_required

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Smith", 
        "email": "john@example.com",
        "password": "Password123"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result, status_code = auth_service.register(data)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request body:
    {
        "email": "john@example.com",
        "password": "Password123"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result, status_code = auth_service.login(data)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_me(payload):
    """
    Update the authenticated user's own account.

    Request body (all fields optional):
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "new-email@example.com",
        "password": "NewPassword123",
        "current_password": "OldPassword123"
    }

    current_password is required only when changing email or password.
    """
    try:
        data = request.get_json() or {}
        user_id = payload.get('user_id')

        result, status_code = auth_service.update_user(user_id, data)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['DELETE'])
@token_required
def delete_me(payload):
    """
    Delete the authenticated user's own account.

    Request body:
    {
        "current_password": "Password123"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        user_id = payload.get('user_id')

        result, status_code = auth_service.delete_user(user_id, data)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500
