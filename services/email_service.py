import os
import requests


class EmailService:
    def __init__(self):
        self.api_key = os.getenv("MAILGUN_API_KEY")
        self.domain = os.getenv("MAILGUN_DOMAIN")

    def _send_email(self, to_email, subject, text_body, html_body=None):
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"Journey Planning <postmaster@{self.domain}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": text_body,
                    "html": html_body or text_body,
                },
            )

            response.raise_for_status()
            return True

        except Exception as e:
            print("Mailgun error:", e)
            return False

    def send_verification_email(self, email, token):
        verification_url = (
            f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
        )

        text_body = f"""
Verify your email address.

Click the link below:
{verification_url}
"""

        html_body = f"""
<h2>Verify Your Email</h2>
<p>Please click the link below to verify your account:</p>
<a href="{verification_url}">Verify Email</a>
"""

        return self._send_email(
            email,
            "Verify Your Email",
            text_body,
            html_body
        )

    def send_password_reset_email(self, email, token):
        reset_url = (
            f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
        )

        text_body = f"""
Reset your password.

Click the link below:
{reset_url}
"""

        html_body = f"""
<h2>Reset Password</h2>
<p>Please click the link below to reset your password:</p>
<a href="{reset_url}">Reset Password</a>
"""

        return self._send_email(
            email,
            "Reset Your Password",
            text_body,
            html_body
        )


email_service = EmailService()