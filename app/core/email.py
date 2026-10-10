import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_verification_email(to_email: str, otp: str):
    if not settings.MAIL_HOST or not settings.MAIL_PASS:
        print(f"Mock Email to {to_email}: Your OTP is {otp}")
        return True

    message = EmailMessage()
    message["From"] = settings.MAIL_FROM
    message["To"] = to_email
    message["Subject"] = "Verify your Essor Nova Account"
    
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Essor Nova!</h2>
            <p>Your verification code is: <strong>{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
        </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            use_tls=False,
            start_tls=True
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
