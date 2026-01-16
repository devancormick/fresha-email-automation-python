from datetime import datetime
from src.database.db import get_connection
from src.email.email_service import EmailService
from src.utils.config import config
from src.utils.logger import logger
import sqlite3

class HealthCheck:
    def __init__(self):
        self.email_service = EmailService()
    
    def check_database(self) -> dict:
        """Check database connectivity and integrity"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM appointments')
            appointment_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM email_logs')
            log_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                'status': 'healthy',
                'appointments': appointment_count,
                'email_logs': log_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'Database health check failed: {e}')
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_smtp(self) -> dict:
        """Check SMTP connectivity"""
        try:
            is_connected = self.email_service.verify_connection()
            return {
                'status': 'healthy' if is_connected else 'unhealthy',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'SMTP health check failed: {e}')
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_recent_errors(self) -> dict:
        """Check for recent errors in email logs"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM email_logs 
                WHERE status = 'failed' 
                AND sent_at > datetime('now', '-1 hour')
            ''')
            recent_errors = cursor.fetchone()[0]
            conn.close()
            
            return {
                'status': 'healthy' if recent_errors < 10 else 'warning',
                'recent_errors': recent_errors,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'Error check failed: {e}')
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_full_health(self) -> dict:
        """Get comprehensive health status"""
        return {
            'overall': 'healthy',
            'checks': {
                'database': self.check_database(),
                'smtp': self.check_smtp(),
                'recent_errors': self.check_recent_errors()
            },
            'timestamp': datetime.now().isoformat()
        }
