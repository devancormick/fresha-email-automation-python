from src.database.db import init_database
from src.utils.logger import logger
from src.scheduler.scheduler import start_scheduler

def main():
    try:
        init_database()
        logger.info('Fresha Email Automation started')
        logger.info('Schedulers running:')
        logger.info('  - Thank-you emails: 12pm and 7pm daily')
        logger.info('  - Follow-up emails: 10am daily')
        start_scheduler()
    except Exception as error:
        logger.error(f'Failed to start application: {error}')
        import sys
        sys.exit(1)

if __name__ == '__main__':
    main()
