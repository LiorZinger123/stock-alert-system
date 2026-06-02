import aiosmtplib
from email.message import EmailMessage
from .email_settings import email_settings


class EmailService:
    async def send(self, email: str, alert_id: int, price: float, condition: str, ticker: str, target_price: str):
        msg = EmailMessage()
        msg["Subject"] = f"Alert Triggered for {ticker}"
        msg["To"] = email
        msg["From"] = email_settings.SMTP_USER
        
        content = (
            f"Hello,\n\n"
            f"Alert #{alert_id} has been triggered.\n\n"
            f"Alert Details:\n"
            f"- Asset: {ticker}\n"
            f"- Current Price: {price}\n"
            f"- Target Price: {target_price}\n"
            f"- Condition: {condition}\n\n"
            f"Regards,\nAutomated Notification System"
        )
        msg.set_content(content)
        
        await aiosmtplib.send(
            msg, 
            hostname=email_settings.SMTP_SERVER, 
            port=email_settings.SMTP_PORT, 
            username=email_settings.SMTP_USER, 
            password=email_settings.SMTP_PASSWORD, 
            start_tls=True
        )
