import os
from mailersend import MailerSendClient, EmailParams

class EmailService:
    def __init__(self):
        self.client = MailerSendClient(
            api_key=os.getenv("MAILERSEND_API_KEY")
        )

    def send_verification_email(self, email, verification_token):
        try:
            verification_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={verification_token}"

            email_params = EmailParams(
                from_email=os.getenv("MAILERSEND_SENDER", "sandbox@yourdomain.com"),
                to=[email],
                subject="Verify Your Email",
                html=f"""
                <h2>Verify Your Email</h2>
                <p>Click below to verify:</p>
                <a href="{verification_url}">Verify Email</a>
                """
            )

            self.client.emails.send(email_params)
            return True

        except Exception as e:
            print("Email error:", e)
            return False

    def send_password_reset_email(self, email, reset_token):
        try:
            reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password?token={reset_token}"

            email_params = EmailParams(
                from_email=os.getenv("MAILERSEND_SENDER", "sandbox@yourdomain.com"),
                to=[email],
                subject="Reset Your Password",
                html=f"""
                <h2>Reset Password</h2>
                <p>Click below:</p>
                <a href="{reset_url}">Reset Password</a>
                """
            )

            self.client.emails.send(email_params)
            return True

        except Exception as e:
            print("Email error:", e)
            return False