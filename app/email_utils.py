import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

EMAIL_FROM = os.getenv("MAIL_FROM")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
EMAIL_SERVER = os.getenv("MAIL_SERVER")
EMAIL_PORT = int(os.getenv("MAIL_PORT", 587))

def send_email(to_email: str, subject: str, html_content: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
