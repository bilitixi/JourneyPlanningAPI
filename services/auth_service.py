import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta
from models.user import User
from models.journey import Journey
from db import get_db
import os
from services.email_service import EmailService

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
email_service = EmailService()


class AuthService:

    # =========================
    # REGISTER
    # =========================
    def register(self, user_data):
        db = get_db()
        try:
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                return {'error': 'Email already registered'}, 400

            password_hash = bcrypt.hashpw(
                user_data['password'].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(minutes=15)

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

            # ✅ EMAIL (FIXED)
            success = email_service.send_verification_email(
                new_user.email,
                verification_token
            )

            if not success:
                print("❌ Verification email failed")
                return {'error': 'User created but email failed'}, 500

            return {
                'message': 'User registered successfully. Please check your email.',
                'user_id': new_user.id
            }, 201

        except Exception as e:
            db.rollback()
            print("REGISTER ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # LOGIN
    # =========================
    def login(self, credentials):
        db = get_db()
        try:
            user = db.query(User).filter(User.email == credentials['email']).first()

            if not user:
                return {'error': 'Invalid email or password'}, 401

            if not bcrypt.checkpw(
                credentials['password'].encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                return {'error': 'Invalid email or password'}, 401

            if not user.is_verified:
                return {'error': 'Please verify your email'}, 403

            payload = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

            return {
                'access_token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, 200

        except Exception as e:
            print("LOGIN ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # VERIFY EMAIL
    # =========================
    def verify_email(self, token):
        db = get_db()
        try:
            user = db.query(User).filter(User.verification_token == token).first()

            if not user:
                return {'error': 'Invalid token'}, 400

            if user.verification_expires < datetime.utcnow():
                return {'error': 'Token expired'}, 400

            user.is_verified = True
            user.verification_token = None
            user.verification_expires = None

            db.commit()

            return {'message': 'Email verified successfully'}, 200

        except Exception as e:
            db.rollback()
            print("VERIFY ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # RESEND EMAIL
    # =========================
    def resend_verification_email(self, email):
        db = get_db()
        try:

            user = db.query(User).filter(User.email == email).first()

            if not user:
                return {'error': 'User not found'}, 404

            if user.is_verified:
                return {'error': 'Already verified'}, 400

            # Check if there's already a valid token (not expired)
            if user.verification_token and user.verification_expires:
                if user.verification_expires > datetime.utcnow():
                    return {'error': 'Please wait before requesting another verification email'}, 429

            token = secrets.token_urlsafe(32)
            user.verification_token = token
            user.verification_expires = datetime.utcnow() + timedelta(minutes=15)

            db.commit()
            print("➡️ RESEND START")
            print("Email:", user.email)
            print("Token:", user.verification_token)

            success = email_service.send_verification_email(user.email, token)

            if not success:
                return {'error': 'Email send failed'}, 500

            return {'message': 'Verification email sent'}, 200

        except Exception as e:
            db.rollback()
            print("RESEND ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            print("➡️ RESEND END")
            db.close()

    # =========================
    # FORGOT PASSWORD
    # =========================
    def forgot_password(self, email):
        db = get_db()
        try:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                return {'message': 'If email exists, reset sent'}, 200

            # Check if there's already a valid reset token (not expired)
            if user.reset_token and user.reset_expires:
                if user.reset_expires > datetime.utcnow():
                    return {'error': 'Please wait before requesting another password reset email'}, 429

            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_expires = datetime.utcnow() + timedelta(minutes=15)

            db.commit()

            success = email_service.send_password_reset_email(user.email, token)

            if not success:
                return {'error': 'Reset email failed'}, 500

            return {'message': 'Reset email sent'}, 200

        except Exception as e:
            db.rollback()
            print("FORGOT PASSWORD ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # RESET PASSWORD
    # =========================
    def reset_password(self, token, new_password):
        db = get_db()
        try:
            user = db.query(User).filter(User.reset_token == token).first()

            if not user:
                return {'error': 'Invalid token'}, 400

            if user.reset_expires < datetime.utcnow():
                return {'error': 'Token expired'}, 400

            hashed = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            user.password_hash = hashed
            user.reset_token = None
            user.reset_expires = None

            db.commit()

            return {'message': 'Password reset successful'}, 200

        except Exception as e:
            db.rollback()
            print("RESET ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # UPDATE USER
    # =========================
    def update_user(self, user_id, data):
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {'error': 'User not found'}, 404

            changing_email = 'email' in data and data['email'] != user.email
            changing_password = 'password' in data

            if changing_email or changing_password:
                current_password = data.get('current_password')
                if not current_password or not bcrypt.checkpw(
                    current_password.encode('utf-8'),
                    user.password_hash.encode('utf-8')
                ):
                    return {'error': 'Missing or incorrect current password'}, 401

            if changing_email:
                existing_user = db.query(User).filter(
                    User.email == data['email'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return {'error': 'Email already registered'}, 400
                user.email = data['email']

            if 'first_name' in data:
                user.first_name = data['first_name']

            if 'last_name' in data:
                user.last_name = data['last_name']

            if changing_password:
                user.password_hash = bcrypt.hashpw(
                    data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')

            db.commit()
            db.refresh(user)

            return {
                'message': 'User updated successfully',
                'user': user.to_dict()
            }, 200

        except Exception as e:
            db.rollback()
            print("UPDATE USER ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()

    # =========================
    # DELETE USER
    # =========================
    def delete_user(self, user_id, data):
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {'error': 'User not found'}, 404

            current_password = data.get('current_password')
            if not current_password or not bcrypt.checkpw(
                current_password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                return {'error': 'Missing or incorrect current password'}, 401

            db.query(Journey).filter(Journey.user_id == user_id).delete()
            db.delete(user)
            db.commit()

            return {'message': 'Account deleted successfully'}, 200

        except Exception as e:
            db.rollback()
            print("DELETE USER ERROR:", str(e))
            return {'error': str(e)}, 500
        finally:
            db.close()