import httpx
from app.core.config import settings

async def send_verification_email(to_email: str, otp: str):
    if not settings.BREVO_API_KEY:
        print(f"Mock Email to {to_email}: Your OTP is {otp}")
        return True

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": settings.SENDER_NAME,
            "email": settings.SENDER_EMAIL
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": "Verify your Essor Nova Account",
        "htmlContent": f"""
        <html>
            <body>
                <h2>Welcome to Essor Nova!</h2>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>This code will expire in 10 minutes.</p>
            </body>
        </html>
        """
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
