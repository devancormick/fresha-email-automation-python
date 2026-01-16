from typing import List, Dict
from src.database.db import get_connection
from src.database.models import Appointment
from datetime import datetime, timedelta

class CustomerSegmentation:
    """Customer segmentation based on appointment history and engagement"""
    
    @staticmethod
    def get_customer_segments() -> Dict[str, List[Dict]]:
        """Get customers segmented by engagement level"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all customers with their appointment counts
        cursor.execute('''
            SELECT 
                customer_email,
                customer_name,
                COUNT(*) as appointment_count,
                MAX(appointment_date) as last_appointment,
                MIN(appointment_date) as first_appointment
            FROM appointments
            GROUP BY customer_email, customer_name
        ''')
        
        customers = cursor.fetchall()
        conn.close()
        
        segments = {
            'vip': [],      # 5+ appointments
            'regular': [],   # 2-4 appointments
            'new': [],      # 1 appointment
            'inactive': []  # No appointments in last 90 days
        }
        
        cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
        
        for email, name, count, last_appt, first_appt in customers:
            customer = {
                'email': email,
                'name': name,
                'appointment_count': count,
                'last_appointment': last_appt,
                'first_appointment': first_appt
            }
            
            if count >= 5:
                segments['vip'].append(customer)
            elif count >= 2:
                segments['regular'].append(customer)
            else:
                segments['new'].append(customer)
            
            # Check if inactive
            if last_appt and last_appt < cutoff_date:
                segments['inactive'].append(customer)
        
        return segments
    
    @staticmethod
    def get_segment_stats() -> Dict:
        """Get statistics for each segment"""
        segments = CustomerSegmentation.get_customer_segments()
        
        return {
            'vip_count': len(segments['vip']),
            'regular_count': len(segments['regular']),
            'new_count': len(segments['new']),
            'inactive_count': len(segments['inactive']),
            'total_customers': sum(len(s) for s in segments.values())
        }
    
    @staticmethod
    def get_customers_by_segment(segment: str) -> List[Dict]:
        """Get customers in a specific segment"""
        segments = CustomerSegmentation.get_customer_segments()
        return segments.get(segment, [])
