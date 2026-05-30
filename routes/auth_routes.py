from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

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
