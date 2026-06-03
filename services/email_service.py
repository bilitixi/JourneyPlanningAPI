import os
from mailersend import emails

class EmailService:
    def __init__(self):
        self.mailer = emails.NewEmail(os.environ["MAILERSEND_API_KEY"])

    def send_verification_email(self, email, token):
        try:
            verification_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"

            mail_body = {}

            mail_from = {
                "name": "Journey Planning",
                "email": os.getenv("MAILERSEND_SENDER", "noreply@yourdomain.com"),
            }

            recipients = [
                {"name": "User", "email": email},
            ]

            self.mailer.set_mail_from(mail_from, mail_body)
            self.mailer.set_mail_to(recipients, mail_body)
            self.mailer.set_subject("Verify Your Email", mail_body)
            self.mailer.set_html_content(
                f"""
                <h2>Verify Your Email</h2>
                <p>Click below to verify:</p>
                <a href="{verification_url}">Verify Email</a>
                """,
                mail_body
            )
            self.mailer.set_plaintext_content(
                f"Verify your email: {verification_url}",
                mail_body
            )

            self.mailer.send(mail_body)
            return True

        except Exception as e:
            print("MailerSend error:", e)
            return False

    def send_password_reset_email(self, email, token):
        try:
            reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"

            mail_body = {}

            mail_from = {
                "name": "Journey Planning",
                "email": os.getenv("MAILERSEND_SENDER", "noreply@yourdomain.com"),
            }

            recipients = [
                {"name": "User", "email": email},
            ]

            self.mailer.set_mail_from(mail_from, mail_body)
            self.mailer.set_mail_to(recipients, mail_body)
            self.mailer.set_subject("Reset Your Password", mail_body)
            self.mailer.set_html_content(
                f"""
                <h2>Reset Password</h2>
                <p>Click below to reset:</p>
                <a href="{reset_url}">Reset Password</a>
                """,
                mail_body
            )
            self.mailer.set_plaintext_content(
                f"Reset your password: {reset_url}",
                mail_body
            )

            self.mailer.send(mail_body)
            return True

        except Exception as e:
            print("MailerSend error:", e)
            return False