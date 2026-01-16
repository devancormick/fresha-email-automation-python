import sys
from src.database.db import init_database
from src.database.models import get_appointments_7_days_ago, get_email_tracking, update_email_tracking, log_email, EmailTracking
from src.email.email_service import EmailService
from src.alerts.alert_service import AlertService
from src.utils.logger import logger
from datetime import datetime

email_service = EmailService()
alert_service = AlertService()

def send_followup_emails():
    try:
        init_database()
        
        appointments = get_appointments_7_days_ago()
        
        logger.info(f'Processing {len(appointments)} appointments for 7-day follow-up emails')
        
        sent = 0
        skipped = 0
        failed = 0
        
        for appointment in appointments:
            try:
                if not appointment.id:
                    logger.warn(f'Appointment missing ID, skipping', extra={'freshaId': appointment.fresha_id})
                    skipped += 1
                    continue
                
                tracking = get_email_tracking(appointment.id)
                
                if tracking and tracking.followup_sent:
                    logger.info(f'Follow-up email already sent for {appointment.customer_email}')
                    skipped += 1
                    log_email(
                        appointment.id,
                        'followup_7day',
                        'skipped',
                        'Already sent (duplicate prevention)'
                    )
                    continue
                
                email_service.send_followup_email(
                    appointment.customer_email,
                    appointment.customer_name
                )
                
                if not tracking:
                    tracking = EmailTracking(appointment_id=appointment.id)
                
                tracking.followup_sent = True
                tracking.followup_sent_date = datetime.now().isoformat()
                
                update_email_tracking(tracking)
                
                log_email(
                    appointment.id,
                    'followup_7day',
                    'sent',
                    None
                )
                
                sent += 1
                logger.info(f'Follow-up email sent to {appointment.customer_email}')
            except Exception as error:
                failed += 1
                error_message = str(error)
                logger.error(f'Failed to send follow-up email to {appointment.customer_email}', extra={'error': error_message})
                
                log_email(
                    appointment.id,
                    'followup_7day',
                    'failed',
                    error_message
                )
                
                alert_service.handle_failure('Follow-Up Email', error, {
                    'appointmentId': appointment.id,
                    'customerEmail': appointment.customer_email
                })
        
        logger.info(f'Follow-up email job completed: {sent} sent, {skipped} skipped, {failed} failed')
        
        if sent > 0 or skipped > 0:
            alert_service.handle_success()
    except Exception as error:
        logger.error('Follow-up email job failed', extra={'error': str(error)})
        alert_service.handle_failure('Follow-Up Email Job', error)
        raise

if __name__ == '__main__':
    logger.info('Starting 7-day follow-up email script')
    try:
        send_followup_emails()
        logger.info('Script completed successfully')
        sys.exit(0)
    except Exception as error:
        logger.error('Script failed', extra={'error': str(error)})
        sys.exit(1)
