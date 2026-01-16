from playwright.sync_api import sync_playwright, Browser, Page
from src.utils.config import config
from src.utils.logger import logger
from src.database.db import init_database
from src.database.models import save_appointment, Appointment

class FreshaScraper:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None
    
    def initialize(self):
        init_database()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = context.new_page()
        logger.info('Browser initialized')
    
    def login(self):
        if not self.page:
            raise Exception('Page not initialized')
        
        try:
            logger.info('Navigating to Fresha login page')
            self.page.goto('https://www.fresha.com/login', wait_until='networkidle', timeout=30000)
            
            self.page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)
            
            email_input = self.page.query_selector('input[type="email"], input[name="email"]')
            password_input = self.page.query_selector('input[type="password"], input[name="password"]')
            
            if not email_input or not password_input:
                raise Exception('Login form not found')
            
            email_input.fill(config.FRESHA_EMAIL)
            password_input.fill(config.FRESHA_PASSWORD)
            
            login_button = self.page.query_selector('button[type="submit"], button:has-text("Sign in"), button:has-text("Log in")')
            if login_button:
                login_button.click()
            else:
                self.page.keyboard.press('Enter')
            
            self.page.wait_for_url('**/dashboard**', timeout=30000)
            logger.info('Successfully logged in to Fresha')
        except Exception as error:
            logger.error(f'Login failed: {error}')
            raise
    
    def scrape_appointments(self) -> list[Appointment]:
        if not self.page:
            raise Exception('Page not initialized')
        
        try:
            logger.info('Navigating to appointments page')
            self.page.goto('https://www.fresha.com/appointments', wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)
            
            appointments = []
            appointment_elements = self.page.query_selector_all('[data-appointment-id], .appointment-item, [class*="appointment"]')
            
            if not appointment_elements:
                logger.warn('No appointment elements found, trying alternative selectors')
                alt_elements = self.page.query_selector_all('tr, .calendar-event, [class*="booking"]')
                if alt_elements:
                    logger.info(f'Found {len(alt_elements)} potential appointment elements')
            
            for element in appointment_elements[:50]:
                try:
                    fresha_id = element.get_attribute('data-appointment-id') or \
                               element.get_attribute('id') or \
                               f'appt-{int(__import__("time").time() * 1000)}-{__import__("random").random()}'
                    
                    text = element.inner_text() or ''
                    import re
                    customer_name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                    
                    customer_name = customer_name_match.group(1) if customer_name_match else 'Unknown Customer'
                    customer_email = email_match.group(1) if email_match else ''
                    
                    if not customer_email:
                        logger.warn(f'Skipping appointment {fresha_id} - no email found')
                        continue
                    
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
                    appointment_date = date_match.group(1) if date_match else __import__('datetime').datetime.now().isoformat()
                    
                    appointment = Appointment(
                        fresha_id=fresha_id,
                        customer_name=customer_name,
                        customer_email=customer_email,
                        appointment_date=appointment_date,
                        service_type='Nail Service'
                    )
                    
                    appointments.append(appointment)
                except Exception as error:
                    logger.warn(f'Error parsing appointment element: {error}')
            
            logger.info(f'Scraped {len(appointments)} appointments')
            return appointments
        except Exception as error:
            logger.error(f'Error scraping appointments: {error}')
            raise
    
    def save_appointments(self, appointments: list[Appointment]):
        for appointment in appointments:
            try:
                save_appointment(appointment)
                logger.info(f'Saved appointment for {appointment.customer_name}')
            except Exception as error:
                logger.error(f'Failed to save appointment for {appointment.customer_name}: {error}')
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.browser = None
        self.page = None
        logger.info('Browser closed')

def main():
    scraper = FreshaScraper()
    try:
        scraper.initialize()
        scraper.login()
        appointments = scraper.scrape_appointments()
        scraper.save_appointments(appointments)
        logger.info(f'Successfully processed {len(appointments)} appointments')
    except Exception as error:
        logger.error(f'Scraper failed: {error}')
        import sys
        sys.exit(1)
    finally:
        scraper.close()

if __name__ == '__main__':
    main()
