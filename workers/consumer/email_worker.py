import logging
from .email_service import EmailService
from core.database import AsyncSessionLocal
from helpers.enums import AlertStatus, ConditionEnum
from workers.shared.worker_alert_service import WorkerAlertService


logger = logging.getLogger("EmailWorker")
email_service = EmailService()


async def send_email_task(_, alert_id: int, user_email: str, symbol: str, target_price: str, current_price: str, condition: ConditionEnum) -> bool:
    logger.info(f"Processing email for alert {alert_id}")
    
    try:
        alert_service = WorkerAlertService(AsyncSessionLocal)

        await email_service.send(
            email=user_email,
            alert_id=alert_id,
            price=float(current_price),
            condition=condition,
            ticker=symbol,
            target_price=target_price
        )
        await alert_service.update_alert_status(alert_id, AlertStatus.SENT.value)
        
        logger.info(f"Email sent and status updated for {alert_id}")
        return True
        
    except Exception as e:
        await alert_service.update_alert_status(alert_id, )
        
        logger.error(f"Failed to send email for {alert_id}: {str(e)}")
        raise e
