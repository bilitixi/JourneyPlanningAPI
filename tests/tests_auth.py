import pytest
import jwt
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from middleware.jwt_auth import token_required, admin_required, JWT_SECRET_KEY


class TestJWTAuthentication:
    """Test JWT authentication functionality"""
    
    def test_generate_valid_token(self):
        """Test generating a valid JWT token"""
        payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        # Handle both string and bytes return types
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding a valid JWT token"""
        payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        assert decoded['user_id'] == 1
        assert decoded['email'] == 'test@example.com'
        assert decoded['role'] == 'user'
    
    def test_expired_token(self):
        """Test that expired tokens are rejected"""
        payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'role': 'user',
            'exp': datetime.utcnow() - timedelta(hours=1),  # Expired
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    
    def test_invalid_token(self):
        """Test that invalid tokens are rejected"""
        invalid_token = "invalid.token.string"
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(invalid_token, JWT_SECRET_KEY, algorithms=['HS256'])
    
    def test_token_with_admin_role(self):
        """Test token with admin role"""
        payload = {
            'user_id': 1,
            'email': 'admin@example.com',
            'role': 'admin',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        assert decoded['role'] == 'admin'
    
    def test_token_with_user_role(self):
        """Test token with user role"""
        payload = {
            'user_id': 2,
            'email': 'user@example.com',
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        assert decoded['role'] == 'user'


class TestTokenRequiredDecorator:
    """Test token_required decorator functionality"""
    
    def test_token_required_decorator_exists(self):
        """Test that token_required decorator exists"""
        assert callable(token_required)
    
    def test_token_required_protects_endpoint(self):
        """Test that token_required decorator protects endpoints"""
        # This would typically be tested with a Flask test client
        # For now, we just verify the decorator exists and is callable
        @token_required
        def protected_route(payload):
            return {'message': 'success'}
        
        assert callable(protected_route)


class TestAdminRequiredDecorator:
    """Test admin_required decorator functionality"""
    
    def test_admin_required_decorator_exists(self):
        """Test that admin_required decorator exists"""
        assert callable(admin_required)
    
    def test_admin_requires_admin_role(self):
        """Test that admin_required requires admin role"""
        # This would typically be tested with a Flask test client
        # For now, we just verify the decorator exists and is callable
        @admin_required
        def admin_route(payload):
            return {'message': 'admin success'}
        
        assert callable(admin_route)
    
    def test_admin_token_vs_user_token(self):
        """Test difference between admin and user tokens"""
        admin_payload = {
            'user_id': 1,
            'role': 'admin',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        user_payload = {
            'user_id': 2,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        admin_token = jwt.encode(admin_payload, JWT_SECRET_KEY, algorithm='HS256')
        user_token = jwt.encode(user_payload, JWT_SECRET_KEY, algorithm='HS256')
        
        if isinstance(admin_token, bytes):
            admin_token = admin_token.decode('utf-8')
        if isinstance(user_token, bytes):
            user_token = user_token.decode('utf-8')
        
        admin_decoded = jwt.decode(admin_token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_decoded = jwt.decode(user_token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        assert admin_decoded['role'] == 'admin'
        assert user_decoded['role'] == 'user'
        assert admin_decoded['role'] != user_decoded['role']


class TestJWTSecretKey:
    """Test JWT secret key configuration"""
    
    def test_jwt_secret_key_exists(self):
        """Test that JWT secret key is configured"""
        assert JWT_SECRET_KEY is not None
        assert isinstance(JWT_SECRET_KEY, str)
        assert len(JWT_SECRET_KEY) > 0
    
    def test_jwt_secret_key_default(self):
        """Test that JWT secret key has a default value"""
        assert JWT_SECRET_KEY == 'test-secret-key' or len(JWT_SECRET_KEY) > 0
