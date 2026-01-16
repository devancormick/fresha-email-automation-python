from typing import Optional, List
from datetime import datetime
from src.database.db import get_connection
import logging

logger = logging.getLogger('fresha_automation')

class Appointment:
    def __init__(self, fresha_id: str, customer_name: str, customer_email: str, 
                 appointment_date: str, service_type: Optional[str] = None, 
                 id: Optional[int] = None):
        self.id = id
        self.fresha_id = fresha_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.appointment_date = appointment_date
        self.service_type = service_type

def save_appointment(appointment: Appointment) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO appointments 
        (fresha_id, customer_name, customer_email, appointment_date, service_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        appointment.fresha_id,
        appointment.customer_name,
        appointment.customer_email,
        appointment.appointment_date,
        appointment.service_type
    ))
    
    cursor.execute('SELECT id FROM appointments WHERE fresha_id = ?', (appointment.fresha_id,))
    result = cursor.fetchone()
    appointment_id = result[0] if result else cursor.lastrowid
    
    conn.commit()
    conn.close()
    return appointment_id

def get_appointments_by_date(date: str) -> List[Appointment]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM appointments WHERE DATE(appointment_date) = DATE(?)
    ''', (date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    appointments = []
    for row in rows:
        appointments.append(Appointment(
            id=row[0],
            fresha_id=row[1],
            customer_name=row[2],
            customer_email=row[3],
            appointment_date=row[4],
            service_type=row[5]
        ))
    return appointments

def get_appointments_7_days_ago() -> List[Appointment]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM appointments WHERE DATE(appointment_date) = DATE('now', '-7 days')
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    appointments = []
    for row in rows:
        appointments.append(Appointment(
            id=row[0],
            fresha_id=row[1],
            customer_name=row[2],
            customer_email=row[3],
            appointment_date=row[4],
            service_type=row[5]
        ))
    return appointments

def log_email(appointment_id: Optional[int], email_type: str, 
              status: str, error_message: Optional[str] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO email_logs (appointment_id, email_type, status, error_message)
        VALUES (?, ?, ?, ?)
    ''', (appointment_id, email_type, status, error_message))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

class EmailTracking:
    def __init__(self, appointment_id: int, thank_you_sent_12pm: bool = False,
                 thank_you_sent_7pm: bool = False, followup_sent: bool = False,
                 followup_sent_date: Optional[str] = None, id: Optional[int] = None):
        self.id = id
        self.appointment_id = appointment_id
        self.thank_you_sent_12pm = thank_you_sent_12pm
        self.thank_you_sent_7pm = thank_you_sent_7pm
        self.followup_sent = followup_sent
        self.followup_sent_date = followup_sent_date

def get_email_tracking(appointment_id: int) -> Optional[EmailTracking]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM email_tracking WHERE appointment_id = ?', (appointment_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return EmailTracking(
        id=row[0],
        appointment_id=row[1],
        thank_you_sent_12pm=bool(row[2]),
        thank_you_sent_7pm=bool(row[3]),
        followup_sent=bool(row[4]),
        followup_sent_date=row[5]
    )

def update_email_tracking(tracking: EmailTracking):
    conn = get_connection()
    cursor = conn.cursor()
    
    existing = get_email_tracking(tracking.appointment_id)
    
    if existing:
        cursor.execute('''
            UPDATE email_tracking 
            SET thank_you_sent_12pm = ?,
                thank_you_sent_7pm = ?,
                followup_sent = ?,
                followup_sent_date = ?
            WHERE appointment_id = ?
        ''', (
            tracking.thank_you_sent_12pm,
            tracking.thank_you_sent_7pm,
            tracking.followup_sent,
            tracking.followup_sent_date,
            tracking.appointment_id
        ))
    else:
        cursor.execute('''
            INSERT INTO email_tracking 
            (appointment_id, thank_you_sent_12pm, thank_you_sent_7pm, followup_sent, followup_sent_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            tracking.appointment_id,
            tracking.thank_you_sent_12pm,
            tracking.thank_you_sent_7pm,
            tracking.followup_sent,
            tracking.followup_sent_date
        ))
    
    conn.commit()
    conn.close()
