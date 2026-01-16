def get_thank_you_email(customer_name: str, service_type: str = None) -> dict:
    service_text = service_type or 'nail service'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Thank You, {customer_name}!</h1>
            </div>
            <div class="content">
                <p>Dear {customer_name},</p>
                <p>Thank you for choosing us for your {service_text} today! We hope you had a wonderful experience.</p>
                <p>We truly appreciate your business and look forward to serving you again soon.</p>
                <p>If you have any questions or feedback, please don't hesitate to reach out to us.</p>
                <p>Best regards,<br>The Nail Salon Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Thank You, {customer_name}!
    
    Dear {customer_name},
    
    Thank you for choosing us for your {service_text} today! We hope you had a wonderful experience.
    
    We truly appreciate your business and look forward to serving you again soon.
    
    If you have any questions or feedback, please don't hesitate to reach out to us.
    
    Best regards,
    The Nail Salon Team
    
    ---
    This is an automated message. Please do not reply to this email.
    """
    
    return {
        'subject': 'Thank You for Your Visit!',
        'html': html,
        'text': text
    }

def get_followup_email(customer_name: str) -> dict:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Hi {customer_name}!</h1>
            </div>
            <div class="content">
                <p>Dear {customer_name},</p>
                <p>It's been a week since your visit, and we wanted to check in with you.</p>
                <p><strong>How are your nails doing? Are they lasting well?</strong></p>
                <p>We'd love to hear about your experience and any feedback you might have. Your satisfaction is our top priority!</p>
                <p>If you have any concerns or would like to schedule another appointment, please don't hesitate to contact us.</p>
                <p>Thank you for being a valued customer!</p>
                <p>Best regards,<br>The Nail Salon Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Hi {customer_name}!
    
    Dear {customer_name},
    
    It's been a week since your visit, and we wanted to check in with you.
    
    How are your nails doing? Are they lasting well?
    
    We'd love to hear about your experience and any feedback you might have. Your satisfaction is our top priority!
    
    If you have any concerns or would like to schedule another appointment, please don't hesitate to contact us.
    
    Thank you for being a valued customer!
    
    Best regards,
    The Nail Salon Team
    
    ---
    This is an automated message. Please do not reply to this email.
    """
    
    return {
        'subject': 'How Are Your Nails Doing?',
        'html': html,
        'text': text
    }
