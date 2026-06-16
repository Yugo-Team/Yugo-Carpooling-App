import os

import httpx

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_URL = "https://api.resend.com/emails"
FROM_ADDRESS = os.environ.get("RESEND_FROM", "Yugo <onboarding@resend.dev>")


def send_email(to: str, subject: str, html: str) -> None:
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY must be set in .env")

    resp = httpx.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_ADDRESS,
            "to": [to],
            "subject": subject,
            "html": html,
        },
        timeout=15.0,
    )
    #return resend message for diagnostic 
    if resp.is_error:
        raise RuntimeError(
            f"Resend send failed ({resp.status_code}) for {to}: {resp.text}"
        )


def send_verification_code(to: str, code: str) -> None:
    html = f"""
    <html>
      <body>
        <h1>Welcome to Yugo</h1>
        <p>Hi there,</p>
        <p>Your 4-digit verification code is:</p>
        <h2>{code}</h2>
        <p>This code expires in 10 minutes.</p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        <hr>
        <small>Yugo - rides for college students</small>
      </body>
    </html>
    """
    send_email(to=to, subject="Your Yugo verification code", html=html)
