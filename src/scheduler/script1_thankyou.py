import sys
from datetime import datetime
from src.database.db import init_database
from src.database.models import get_appointments_by_date, get_email_tracking, update_email_tracking, log_email, EmailTracking
from src.email.email_service import EmailService
from src.alerts.alert_service import AlertService
from src.utils.logger import logger

email_service = EmailService()
alert_service = AlertService()

def send_thank_you_emails(time_slot: str):
    try:
        init_database()
        
        today = datetime.now().strftime('%Y-%m-%d')
        appointments = get_appointments_by_date(today)
        
        logger.info(f'Processing {len(appointments)} appointments for {time_slot} thank-you emails')
        
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
                already_sent = False
                
                if time_slot == '12pm':
                    already_sent = tracking.thank_you_sent_12pm if tracking else False
                else:
                    already_sent = tracking.thank_you_sent_7pm if tracking else False
                
                if already_sent:
                    logger.info(f'Thank-you email already sent for {appointment.customer_email} at {time_slot}')
                    skipped += 1
                    log_email(
                        appointment.id,
                        f'thank_you_{time_slot}',
                        'skipped',
                        'Already sent'
                    )
                    continue
                
                email_service.send_thank_you_email(
                    appointment.customer_email,
                    appointment.customer_name,
                    appointment.service_type
                )
                
                if not tracking:
                    tracking = EmailTracking(appointment_id=appointment.id)
                
                if time_slot == '12pm':
                    tracking.thank_you_sent_12pm = True
                else:
                    tracking.thank_you_sent_7pm = True
                
                update_email_tracking(tracking)
                
                log_email(
                    appointment.id,
                    f'thank_you_{time_slot}',
                    'sent',
                    None
                )
                
                sent += 1
                logger.info(f'Thank-you email sent to {appointment.customer_email} at {time_slot}')
            except Exception as error:
                failed += 1
                error_message = str(error)
                logger.error(f'Failed to send thank-you email to {appointment.customer_email}', extra={'error': error_message})
                
                log_email(
                    appointment.id,
                    f'thank_you_{time_slot}',
                    'failed',
                    error_message
                )
                
                alert_service.handle_failure('Thank-You Email', error, {
                    'appointmentId': appointment.id,
                    'customerEmail': appointment.customer_email,
                    'timeSlot': time_slot
                })
        
        logger.info(f'Thank-you email job completed ({time_slot}): {sent} sent, {skipped} skipped, {failed} failed')
        
        if sent > 0 or skipped > 0:
            alert_service.handle_success()
    except Exception as error:
        logger.error('Thank-you email job failed', extra={'error': str(error)})
        alert_service.handle_failure('Thank-You Email Job', error)
        raise

if __name__ == '__main__':
    time_slot = sys.argv[1] if len(sys.argv) > 1 else '12pm'
    
    logger.info(f'Starting thank-you email script for {time_slot}')
    try:
        send_thank_you_emails(time_slot)
        logger.info('Script completed successfully')
        sys.exit(0)
    except Exception as error:
        logger.error('Script failed', extra={'error': str(error)})
        sys.exit(1)
