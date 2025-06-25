# emailer.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")


def send_winner_email(recipient, username):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = "🎉 Kamu Menang di Skematik!"

    body = f"Halo {username},\n\nSelamat! Kamu berhasil menebak gambar dengan benar dalam game Skematik! 🏆\n\nTerima kasih sudah bermain!\n\n- Tim Skematik"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"[EMAIL SENT] Sent to {recipient}")