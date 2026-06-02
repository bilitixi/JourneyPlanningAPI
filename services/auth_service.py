import bcrypt
import jwt
from datetime import datetime, timedelta
from models.user import User
from db import get_db
from sqlalchemy.orm import Session
import os

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key')


class AuthService:
    def __init__(self):
        pass
    
    def register(self, user_data):
        """
        Register a new user.
        
        Args:
            user_data: dict with first_name, last_name, email, password
            
        Returns:
            dict with success message or error
        """
        db = get_db()
        try:

            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                return {'error': 'Email already registered'}, 400
            
            # Hash password
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create new user
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                password_hash=password_hash,
                role='user'
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {'message': 'User registered successfully', 'user_id': new_user.id}, 201
            
        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
    
    def login(self, credentials):
        """
        Authenticate user and return JWT token.
        
        Args:
            credentials: dict with email, password
            
        Returns:
            dict with access_token and user info or error
        """
        db = get_db()
        try:

            
            # Find user by email
            user = db.query(User).filter(User.email == credentials['email']).first()
            
            if not user:
                return {'error': 'Invalid email or password'}, 401
            
            # Verify password
            if not bcrypt.checkpw(credentials['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
                return {'error': 'Invalid email or password'}, 401
            
            # Generate JWT token
            payload = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            access_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
            
            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            db.close()
