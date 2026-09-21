import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(receiver_email, otp):
    message = EmailMessage()

    message["Subject"] = "Nexgile WealthAgent - Email Verification"
    message["From"] = os.getenv("MAIL_USERNAME")
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

Your Nexgile WealthAgent email verification OTP is:

{otp}

This OTP expires in 10 minutes.

Please do not share this OTP with anyone.

Regards,
Nexgile WealthAgent Team
"""
    )

    try:
        with smtplib.SMTP(
            os.getenv("MAIL_SERVER"),
            int(os.getenv("MAIL_PORT"))
        ) as server:

            server.starttls()

            server.login(
                os.getenv("MAIL_USERNAME"),
                os.getenv("MAIL_PASSWORD")
            )

            server.send_message(message)

        return True

    except Exception as error:
        print("EMAIL ERROR:", error)
        return False