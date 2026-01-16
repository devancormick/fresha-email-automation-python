from src.database.db import get_connection
from datetime import datetime
from typing import Optional, Dict, List

class ResponseTracker:
    """Track customer responses and engagement"""
    
    @staticmethod
    def init_response_tracking():
        """Initialize response tracking table"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                customer_email TEXT NOT NULL,
                email_type TEXT NOT NULL,
                opened BOOLEAN DEFAULT 0,
                clicked BOOLEAN DEFAULT 0,
                replied BOOLEAN DEFAULT 0,
                feedback TEXT,
                response_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_email_open(appointment_id: int, email_type: str, customer_email: str):
        """Record email open (via tracking pixel)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO customer_responses 
            (appointment_id, customer_email, email_type, opened, response_date)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(appointment_id, email_type) DO UPDATE SET opened = 1, response_date = ?
        ''', (appointment_id, customer_email, email_type, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_email_click(appointment_id: int, email_type: str, customer_email: str):
        """Record email link click"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customer_responses 
            SET clicked = 1, response_date = ?
            WHERE appointment_id = ? AND email_type = ? AND customer_email = ?
        ''', (datetime.now().isoformat(), appointment_id, email_type, customer_email))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO customer_responses 
                (appointment_id, customer_email, email_type, clicked, response_date)
                VALUES (?, ?, ?, 1, ?)
            ''', (appointment_id, customer_email, email_type, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_feedback(appointment_id: int, email_type: str, customer_email: str, feedback: str):
        """Record customer feedback"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customer_responses 
            SET replied = 1, feedback = ?, response_date = ?
            WHERE appointment_id = ? AND email_type = ? AND customer_email = ?
        ''', (feedback, datetime.now().isoformat(), appointment_id, email_type, customer_email))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO customer_responses 
                (appointment_id, customer_email, email_type, replied, feedback, response_date)
                VALUES (?, ?, ?, 1, ?, ?)
            ''', (appointment_id, customer_email, email_type, feedback, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_response_stats() -> Dict:
        """Get response statistics"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM customer_responses WHERE opened = 1')
        opened = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customer_responses WHERE clicked = 1')
        clicked = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customer_responses WHERE replied = 1')
        replied = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customer_responses')
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_emails': total,
            'opened': opened,
            'clicked': clicked,
            'replied': replied,
            'open_rate': (opened / total * 100) if total > 0 else 0,
            'click_rate': (clicked / total * 100) if total > 0 else 0,
            'reply_rate': (replied / total * 100) if total > 0 else 0
        }
    
    @staticmethod
    def get_customer_engagement(customer_email: str) -> Dict:
        """Get engagement metrics for a specific customer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_emails,
                SUM(opened) as opened_count,
                SUM(clicked) as clicked_count,
                SUM(replied) as replied_count
            FROM customer_responses
            WHERE customer_email = ?
        ''', (customer_email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total, opened, clicked, replied = result
            return {
                'total_emails': total,
                'opened': opened or 0,
                'clicked': clicked or 0,
                'replied': replied or 0,
                'engagement_score': ((opened or 0) * 1 + (clicked or 0) * 2 + (replied or 0) * 3) / (total * 3) * 100
            }
        
        return {
            'total_emails': 0,
            'opened': 0,
            'clicked': 0,
            'replied': 0,
            'engagement_score': 0
        }
