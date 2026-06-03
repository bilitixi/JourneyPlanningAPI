import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta
from models.user import User
from db import get_db
from sqlalchemy.orm import Session
import os
from services.email_service import EmailService

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
email_service = EmailService()


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
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Create new user
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                password_hash=password_hash,
                role='user',
                is_verified=False,
                verification_token=verification_token,
                verification_expires=verification_expires
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Send verification email
            email_service.send_verification_email(new_user.email, verification_token)
            
            return {'message': 'User registered successfully. Please check your email to verify your account.', 'user_id': new_user.id}, 201
            
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
            
            # Check if email is verified
            if not user.is_verified:
                return {'error': 'Please verify your email before logging in'}, 403
            
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
    
    def verify_email(self, token):
        """
        Verify user's email using verification token.
        
        Args:
            token: Verification token from email
            
        Returns:
            dict with success message or error
        """
        db = get_db()
        try:
            # Find user by verification token
            user = db.query(User).filter(User.verification_token == token).first()
            
            if not user:
                return {'error': 'Invalid verification token'}, 400
            
            # Check if token is expired
            if user.verification_expires < datetime.utcnow():
                return {'error': 'Verification token has expired'}, 400
            
            # Mark user as verified
            user.is_verified = True
            user.verification_token = None
            user.verification_expires = None
            
            db.commit()
            
            return {'message': 'Email verified successfully'}, 200
            
        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
    
    def resend_verification_email(self, email):
        """
        Resend verification email to user.
        
        Args:
            email: User's email address
            
        Returns:
            dict with success message or error
        """
        db = get_db()
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                return {'error': 'User not found'}, 404
            
            # Check if already verified
            if user.is_verified:
                return {'error': 'Email is already verified'}, 400
            
            # Generate new verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            user.verification_token = verification_token
            user.verification_expires = verification_expires
            
            db.commit()
            
            # Send verification email
            email_service.send_verification_email(user.email, verification_token)
            
            return {'message': 'Verification email sent successfully'}, 200
            
        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
    
    def forgot_password(self, email):
        """
        Initiate password reset by sending reset email.
        
        Args:
            email: User's email address
            
        Returns:
            dict with success message or error
        """
        db = get_db()
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Don't reveal if user exists or not for security
                return {'message': 'If the email exists, a password reset link has been sent'}, 200
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            user.reset_token = reset_token
            user.reset_expires = reset_expires
            
            db.commit()
            
            # Send reset email
            email_service.send_password_reset_email(user.email, reset_token)
            
            return {'message': 'If the email exists, a password reset link has been sent'}, 200
            
        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
    
    def reset_password(self, token, new_password):
        """
        Reset user's password using reset token.
        
        Args:
            token: Reset token from email
            new_password: New password
            
        Returns:
            dict with success message or error
        """
        db = get_db()
        try:
            # Find user by reset token
            user = db.query(User).filter(User.reset_token == token).first()
            
            if not user:
                return {'error': 'Invalid reset token'}, 400
            
            # Check if token is expired
            if user.reset_expires < datetime.utcnow():
                return {'error': 'Reset token has expired'}, 400
            
            # Hash new password
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update password and clear reset token
            user.password_hash = password_hash
            user.reset_token = None
            user.reset_expires = None
            
            db.commit()
            
            return {'message': 'Password reset successfully'}, 200
            
        except Exception as e:
            db.rollback()
            return {'error': str(e)}, 500
        finally:
            db.close()
