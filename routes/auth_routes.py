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


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify user's email using verification token.
    
    Request body:
    {
        "token": "verification_token_from_email"
    }
    """
    try:
        data = request.get_json()
        
        if 'token' not in data:
            return jsonify({'error': 'Missing required field: token'}), 400
        
        result, status_code = auth_service.verify_email(data['token'])
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend verification email to user.
    
    Request body:
    {
        "email": "john@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Missing required field: email'}), 400
        
        result, status_code = auth_service.resend_verification_email(data['email'])
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiate password reset by sending reset email.
    
    Request body:
    {
        "email": "john@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Missing required field: email'}), 400
        
        result, status_code = auth_service.forgot_password(data['email'])
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset user's password using reset token.
    
    Request body:
    {
        "token": "reset_token_from_email",
        "new_password": "NewPassword123"
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result, status_code = auth_service.reset_password(data['token'], data['new_password'])
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_me(payload):
    """
    Update the authenticated user's own profile.
    All fields are optional - only provided fields are updated.
    `current_password` is required when changing `email` or `password`.

    Request body:
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "new-email@example.com",
        "password": "NewPassword123",
        "current_password": "OldPassword123"
    }
    """
    try:
        data = request.get_json()
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
    Requires password confirmation. Cascades to delete the user's journeys.

    Request body:
    {
        "current_password": "Password123"
    }
    """
    try:
        data = request.get_json()
        user_id = payload.get('user_id')

        result, status_code = auth_service.delete_user(user_id, data)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500
