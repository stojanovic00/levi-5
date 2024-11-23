import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.email_host = os.getenv("EMAIL_HOST")
        self.email_port = int(os.getenv("EMAIL_PORT"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.to_email = os.getenv("TO_EMAIL")

    def send_match_email(self, match):
        # Kreiranje email poruke
        subject = f"Odigran meč: {match.id}"
        body = f"""
        Detalji meča:
        - Meč ID: {match.id}
        - Igrači: {', '.join(match.players)}
        - Rezultat: {match.result}
        """
        message = MIMEMultipart()
        message["From"] = self.email_user
        message["To"] = self.to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Slanje emaila
        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
                print(f"Email uspešno poslat na {self.to_email}")
        except Exception as e:
            print(f"Greška pri slanju emaila: {e}")