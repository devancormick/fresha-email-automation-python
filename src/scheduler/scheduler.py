from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from src.utils.config import config
from src.utils.logger import logger
from src.utils.health_check import HealthCheck
from src.utils.db_backup import backup_database
from src.scheduler.script1_thankyou import send_thank_you_emails
from src.scheduler.script2_followup import send_followup_emails

def job_listener(event):
    """Listen to job execution events"""
    if event.exception:
        logger.error(f'Job {event.job_id} failed: {event.exception}')
    else:
        logger.info(f'Job {event.job_id} completed successfully')

def start_scheduler():
    scheduler = BlockingScheduler(timezone=config.TIMEZONE)
    
    # Add event listener
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    # Daily backup at 2am
    scheduler.add_job(
        lambda: backup_database(),
        CronTrigger(hour=2, minute=0),
        id='daily_backup',
        name='Daily database backup'
    )
    
    # Health check every 6 hours
    scheduler.add_job(
        lambda: HealthCheck().get_full_health(),
        CronTrigger(hour='*/6', minute=0),
        id='health_check',
        name='System health check'
    )
    
    # Thank-you emails
    scheduler.add_job(
        lambda: send_thank_you_emails('12pm'),
        CronTrigger(hour=12, minute=0),
        id='thank_you_12pm',
        name='Thank-you emails at 12pm'
    )
    
    scheduler.add_job(
        lambda: send_thank_you_emails('7pm'),
        CronTrigger(hour=19, minute=0),
        id='thank_you_7pm',
        name='Thank-you emails at 7pm'
    )
    
    # Follow-up emails
    scheduler.add_job(
        send_followup_emails,
        CronTrigger(hour=10, minute=0),
        id='followup_7day',
        name='7-day follow-up emails'
    )
    
    logger.info('Scheduler started')
    logger.info('Thank-you emails scheduled: 12pm and 7pm daily')
    logger.info('Follow-up emails scheduled: 10am daily')
    logger.info('Daily backup scheduled: 2am')
    logger.info('Health checks scheduled: every 6 hours')
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Scheduler stopped')
        scheduler.shutdown()

if __name__ == '__main__':
    start_scheduler()
