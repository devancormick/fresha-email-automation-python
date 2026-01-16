from datetime import datetime, timedelta
from src.email.email_service import EmailService
from src.utils.logger import logger

class AlertService:
    def __init__(self):
        self.email_service = EmailService()
        self.consecutive_failures = 0
        self.last_alert_time = None
        self.ALERT_COOLDOWN = timedelta(hours=1)
    
    def handle_failure(self, failure_type: str, error: Exception, context: dict = None):
        self.consecutive_failures += 1
        logger.error(f'Failure detected: {failure_type}', extra={'error': str(error), **(context or {})})
        
        if self.consecutive_failures >= 3:
            self._send_failure_alert(failure_type, error, context)
    
    def handle_success(self):
        if self.consecutive_failures > 0:
            logger.info('Service recovered from failures')
            self.consecutive_failures = 0
    
    def _send_failure_alert(self, failure_type: str, error: Exception, context: dict = None):
        now = datetime.now()
        if self.last_alert_time and (now - self.last_alert_time) < self.ALERT_COOLDOWN:
            return
        
        subject = f'{failure_type} - {self.consecutive_failures} Consecutive Failures'
        message = f"""
Failure Alert: {failure_type}

Error: {str(error)}
Type: {type(error).__name__}

Consecutive Failures: {self.consecutive_failures}
Time: {now.isoformat()}

Context:
{str(context) if context else 'None'}
        """.strip()
        
        self.email_service.send_alert_email(subject, message)
        self.last_alert_time = now
        logger.info(f'Failure alert sent: {failure_type}, consecutive failures: {self.consecutive_failures}')
    
    def send_critical_alert(self, subject: str, message: str):
        self.email_service.send_alert_email(subject, message)
        logger.info(f'Critical alert sent: {subject}')
