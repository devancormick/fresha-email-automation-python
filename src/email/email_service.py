import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.config import config
from src.utils.logger import logger
from src.email.templates import get_thank_you_email, get_followup_email

class EmailService:
    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.from_name = config.SMTP_FROM_NAME
        self.from_email = config.SMTP_FROM_EMAIL
    
    def send_thank_you_email(self, customer_email: str, customer_name: str, service_type: str = None) -> bool:
        try:
            template = get_thank_you_email(customer_name, service_type)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template['subject']
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = customer_email
            
            part1 = MIMEText(template['text'], 'plain')
            part2 = MIMEText(template['html'], 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f'Thank-you email sent to {customer_email}')
            return True
        except Exception as error:
            logger.error(f'Failed to send thank-you email to {customer_email}: {error}')
            raise
    
    def send_followup_email(self, customer_email: str, customer_name: str) -> bool:
        try:
            template = get_followup_email(customer_name)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template['subject']
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = customer_email
            
            part1 = MIMEText(template['text'], 'plain')
            part2 = MIMEText(template['html'], 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f'Follow-up email sent to {customer_email}')
            return True
        except Exception as error:
            logger.error(f'Failed to send follow-up email to {customer_email}: {error}')
            raise
    
    def send_alert_email(self, subject: str, message: str):
        if not config.ALERT_EMAIL:
            logger.warn('Alert email not configured, skipping alert')
            return
        
        try:
            msg = MIMEText(message)
            msg['Subject'] = f'[ALERT] {subject}'
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = config.ALERT_EMAIL
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f'Alert email sent: {subject}')
        except Exception as error:
            logger.error(f'Failed to send alert email: {error}')
    
    def verify_connection(self) -> bool:
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            logger.info('SMTP connection verified')
            return True
        except Exception as error:
            logger.error(f'SMTP connection verification failed: {error}')
            return False
