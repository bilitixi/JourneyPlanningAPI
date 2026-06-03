import os
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


class EmailService:
    def __init__(self):
        pass

    def send_verification_email(self, email, verification_token):
        """
        Send email verification email to user.
        
        Args:
            email: User's email address
            verification_token: Token for email verification
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
            
            msg = Message(
                'Verify Your Email',
                recipients=[email],
                sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@journeyplanning.com')
            )
            
            msg.body = f"""
            Please verify your email address by clicking the link below:
            
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you did not create an account, please ignore this email.
            """
            
            msg.html = f"""
            <h2>Verify Your Email</h2>
            <p>Please verify your email address by clicking the button below:</p>
            <p>
                <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
            </p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not create an account, please ignore this email.</p>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            return False

    def send_password_reset_email(self, email, reset_token):
        """
        Send password reset email to user.
        
        Args:
            email: User's email address
            reset_token: Token for password reset
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            
            msg = Message(
                'Reset Your Password',
                recipients=[email],
                sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@journeyplanning.com')
            )
            
            msg.body = f"""
            You have requested to reset your password. Click the link below to proceed:
            
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you did not request a password reset, please ignore this email.
            """
            
            msg.html = f"""
            <h2>Reset Your Password</h2>
            <p>You have requested to reset your password. Click the button below to proceed:</p>
            <p>
                <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
            </p>
            <p>This link will expire in 1 hour.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            return False
