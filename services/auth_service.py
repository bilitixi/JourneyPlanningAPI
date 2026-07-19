import bcrypt
import jwt
from datetime import datetime, timedelta
from models.user import User
from models.journey import Journey
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

    def update_user(self, user_id, data):
        """
        Update the authenticated user's own profile.

        Args:
            user_id: id of the authenticated user (from JWT payload)
            data: dict that may contain first_name, last_name, email,
                  password, current_password

        Returns:
            dict with updated user info or error
        """
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {'error': 'User not found'}, 404

            changing_credentials = 'email' in data or 'password' in data

            if changing_credentials:
                current_password = data.get('current_password')
                if not current_password or not bcrypt.checkpw(
                    current_password.encode('utf-8'), user.password_hash.encode('utf-8')
                ):
                    return {'error': 'current_password is required and must be correct to change email or password'}, 401

            if 'email' in data and data['email'] != user.email:
                existing_user = db.query(User).filter(
                    User.email == data['email'], User.id != user_id
                ).first()
                if existing_user:
                    return {'error': 'Email already registered'}, 400
                user.email = data['email']

            if 'first_name' in data:
                user.first_name = data['first_name']

            if 'last_name' in data:
                user.last_name = data['last_name']

            if 'password' in data:
                user.password_hash = bcrypt.hashpw(
                    data['password'].encode('utf-8'), bcrypt.gensalt()
                ).decode('utf-8')

            db.commit()
            db.refresh(user)

            return {'message': 'User updated successfully', 'user': user.to_dict()}, 200

        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()

    def delete_user(self, user_id, data):
        """
        Delete the authenticated user's own account.

        Args:
            user_id: id of the authenticated user (from JWT payload)
            data: dict that must contain current_password

        Returns:
            dict with success message or error
        """
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {'error': 'User not found'}, 404

            current_password = data.get('current_password') if data else None
            if not current_password or not bcrypt.checkpw(
                current_password.encode('utf-8'), user.password_hash.encode('utf-8')
            ):
                return {'error': 'current_password is required and must be correct to delete this account'}, 401

            # Remove the user's journeys first to satisfy the foreign key constraint
            db.query(Journey).filter(Journey.user_id == user_id).delete()
            db.delete(user)
            db.commit()

            return {'message': 'Account deleted successfully'}, 200

        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
