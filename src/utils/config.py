import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    FRESHA_EMAIL = os.getenv('FRESHA_EMAIL', '')
    FRESHA_PASSWORD = os.getenv('FRESHA_PASSWORD', '')
    
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Nail Salon')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    
    ALERT_EMAIL = os.getenv('ALERT_EMAIL', '')
    TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
    
    DB_PATH = Path(__file__).parent.parent.parent / 'db' / 'fresha.db'

config = Config()
