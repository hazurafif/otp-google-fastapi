import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


async def send_otp_email(recipient: str, otp: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = recipient
    message["Subject"] = "Your OTP Code"
    message.set_content(f"Your OTP code is: {otp}. It expires in 5 minutes.")

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )
