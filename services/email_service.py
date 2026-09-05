import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService:
    def __init__(self):
        self.server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        self.port = int(os.getenv("MAIL_PORT", 587))
        self.username = os.getenv("MAIL_USERNAME")
        self.password = os.getenv("MAIL_PASSWORD")
        self.use_tls = os.getenv("MAIL_USE_TLS", "true").lower() != "false"
        self.sender = os.getenv("MAIL_DEFAULT_SENDER", self.username)

    def _send_email(self, to_email, subject, text_body, html_body=None):
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"Journey Planning <{self.sender}>"
            message["To"] = to_email

            message.attach(MIMEText(text_body, "plain"))
            message.attach(MIMEText(html_body or text_body, "html"))

            with smtplib.SMTP(self.server, self.port) as smtp:
                if self.use_tls:
                    smtp.starttls()
                smtp.login(self.username, self.password)
                smtp.sendmail(self.sender, [to_email], message.as_string())

            return True

        except Exception as e:
            print("SMTP error:", e)
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
