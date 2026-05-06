import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 587)),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_FROM_NAME="Faculty Appraisal System",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, token: str):
    """
    Sends a verification email with a link to the local verify endpoint.
    """
    # Replace with the actual frontend or backend URL
    verify_url = f"{os.getenv('APP_URL', 'http://localhost:8000')}/api/v1/auth/verify-email?token={token}"
    
    html = f"""
    <h3>Welcome to the Faculty Appraisal System</h3>
    <p>Please verify your email address by clicking the link below:</p>
    <a href="{verify_url}">Verify Email Address</a>
    <br><br>
    <p>If you did not create an account, please ignore this email.</p>
    """
    
    message = MessageSchema(
        subject="Email Verification - Faculty Appraisal System",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
