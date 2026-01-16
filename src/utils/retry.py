from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from src.utils.logger import logger
import smtplib
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((smtplib.SMTPException, ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def retry_email_operation(func, *args, **kwargs):
    """Retry decorator for email operations"""
    return func(*args, **kwargs)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def retry_scraper_operation(func, *args, **kwargs):
    """Retry decorator for scraper operations"""
    return func(*args, **kwargs)

import logging
