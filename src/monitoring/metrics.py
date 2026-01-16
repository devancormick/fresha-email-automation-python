from datetime import datetime, timedelta
from src.database.db import get_connection
from src.utils.logger import logger

class MetricsCollector:
    """Collect and report system metrics"""
    
    @staticmethod
    def get_email_stats(hours: int = 24) -> dict:
        """Get email statistics for the last N hours"""
        conn = get_connection()
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT 
                status,
                email_type,
                COUNT(*) as count
            FROM email_logs
            WHERE sent_at > ?
            GROUP BY status, email_type
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'by_type': {}
        }
        
        for status, email_type, count in results:
            stats['total'] += count
            stats[status] = stats.get(status, 0) + count
            
            if email_type not in stats['by_type']:
                stats['by_type'][email_type] = {'sent': 0, 'failed': 0, 'skipped': 0}
            stats['by_type'][email_type][status] = count
        
        return stats
    
    @staticmethod
    def get_appointment_stats() -> dict:
        """Get appointment statistics"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM appointments')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE DATE(appointment_date) = DATE('now')
        ''')
        today = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE DATE(appointment_date) >= DATE('now', '-7 days')
        ''')
        week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'today': today,
            'last_7_days': week
        }
    
    @staticmethod
    def get_success_rate(hours: int = 24) -> float:
        """Calculate email success rate"""
        stats = MetricsCollector.get_email_stats(hours)
        if stats['total'] == 0:
            return 0.0
        return (stats['sent'] / stats['total']) * 100
    
    @staticmethod
    def get_report() -> dict:
        """Get comprehensive metrics report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'email_stats_24h': MetricsCollector.get_email_stats(24),
            'email_stats_7d': MetricsCollector.get_email_stats(168),
            'appointment_stats': MetricsCollector.get_appointment_stats(),
            'success_rate_24h': MetricsCollector.get_success_rate(24),
            'success_rate_7d': MetricsCollector.get_success_rate(168)
        }
