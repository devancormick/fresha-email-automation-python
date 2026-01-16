from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils.config import config
from src.utils.logger import logger
from src.scheduler.script1_thankyou import send_thank_you_emails
from src.scheduler.script2_followup import send_followup_emails

def start_scheduler():
    scheduler = BlockingScheduler(timezone=config.TIMEZONE)
    
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
    
    scheduler.add_job(
        send_followup_emails,
        CronTrigger(hour=10, minute=0),
        id='followup_7day',
        name='7-day follow-up emails'
    )
    
    logger.info('Scheduler started')
    logger.info('Thank-you emails scheduled: 12pm and 7pm daily')
    logger.info('Follow-up emails scheduled: 10am daily')
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Scheduler stopped')
        scheduler.shutdown()

if __name__ == '__main__':
    start_scheduler()
