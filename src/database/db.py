import sqlite3
import logging
from pathlib import Path
from src.utils.config import config

logger = logging.getLogger('fresha_automation')

db_dir = config.DB_PATH.parent
db_dir.mkdir(exist_ok=True)

def get_connection():
    return sqlite3.connect(str(config.DB_PATH))

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fresha_id TEXT UNIQUE,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            appointment_date DATETIME NOT NULL,
            service_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            email_type TEXT NOT NULL,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            error_message TEXT,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER UNIQUE,
            thank_you_sent_12pm BOOLEAN DEFAULT 0,
            thank_you_sent_7pm BOOLEAN DEFAULT 0,
            followup_sent BOOLEAN DEFAULT 0,
            followup_sent_date DATETIME,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    ''')
    
    # Initialize response tracking
    from src.database.response_tracking import ResponseTracker
    ResponseTracker.init_response_tracking()
    
    conn.commit()
    conn.close()
    logger.info('Database initialized')
