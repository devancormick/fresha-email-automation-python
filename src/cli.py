import click
from src.database.db import init_database
from src.utils.health_check import HealthCheck
from src.utils.db_backup import backup_database, restore_database
from src.utils.logger import logger
from src.scheduler.script1_thankyou import send_thank_you_emails
from src.scheduler.script2_followup import send_followup_emails
from src.scraper.fresha_scraper import FreshaScraper
from pathlib import Path
import json

@click.group()
def cli():
    """Fresha Email Automation CLI"""
    pass

@cli.command()
def init():
    """Initialize the database"""
    click.echo('Initializing database...')
    try:
        init_database()
        click.echo('✓ Database initialized successfully')
    except Exception as e:
        click.echo(f'✗ Failed to initialize database: {e}', err=True)
        raise click.Abort()

@cli.command()
def health():
    """Check system health"""
    click.echo('Checking system health...')
    health_check = HealthCheck()
    health_status = health_check.get_full_health()
    
    click.echo('\n' + json.dumps(health_status, indent=2))
    
    overall = health_status['overall']
    if overall == 'healthy':
        click.echo('\n✓ System is healthy')
    else:
        click.echo('\n✗ System has issues', err=True)
        raise click.Abort()

@cli.command()
def backup():
    """Backup the database"""
    click.echo('Creating database backup...')
    try:
        backup_path = backup_database()
        click.echo(f'✓ Backup created: {backup_path}')
    except Exception as e:
        click.echo(f'✗ Backup failed: {e}', err=True)
        raise click.Abort()

@cli.command()
@click.argument('backup_file', type=click.Path(exists=True))
def restore(backup_file):
    """Restore database from backup"""
    click.echo(f'Restoring database from {backup_file}...')
    if click.confirm('This will overwrite the current database. Continue?'):
        try:
            if restore_database(Path(backup_file)):
                click.echo('✓ Database restored successfully')
            else:
                click.echo('✗ Restore failed', err=True)
                raise click.Abort()
        except Exception as e:
            click.echo(f'✗ Restore failed: {e}', err=True)
            raise click.Abort()

@cli.command()
@click.option('--time-slot', type=click.Choice(['12pm', '7pm']), default='12pm')
def send_thankyou(time_slot):
    """Send thank-you emails"""
    click.echo(f'Sending thank-you emails for {time_slot}...')
    try:
        send_thank_you_emails(time_slot)
        click.echo('✓ Thank-you emails sent successfully')
    except Exception as e:
        click.echo(f'✗ Failed to send emails: {e}', err=True)
        raise click.Abort()

@cli.command()
def send_followup():
    """Send 7-day follow-up emails"""
    click.echo('Sending follow-up emails...')
    try:
        send_followup_emails()
        click.echo('✓ Follow-up emails sent successfully')
    except Exception as e:
        click.echo(f'✗ Failed to send emails: {e}', err=True)
        raise click.Abort()

@cli.command()
def scrape():
    """Scrape appointments from Fresha"""
    click.echo('Scraping appointments from Fresha...')
    scraper = FreshaScraper()
    try:
        scraper.initialize()
        scraper.login()
        appointments = scraper.scrape_appointments()
        scraper.save_appointments(appointments)
        click.echo(f'✓ Scraped {len(appointments)} appointments')
    except Exception as e:
        click.echo(f'✗ Scraping failed: {e}', err=True)
        raise click.Abort()
    finally:
        scraper.close()

@cli.command()
def stats():
    """Show statistics"""
    from src.database.models import get_appointments_by_date
    from datetime import datetime
    from src.database.db import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total appointments
    cursor.execute('SELECT COUNT(*) FROM appointments')
    total_appointments = cursor.fetchone()[0]
    
    # Today's appointments
    today = datetime.now().strftime('%Y-%m-%d')
    today_appointments = len(get_appointments_by_date(today))
    
    # Email stats
    cursor.execute('SELECT status, COUNT(*) FROM email_logs GROUP BY status')
    email_stats = dict(cursor.fetchall())
    
    # Recent activity
    cursor.execute('''
        SELECT COUNT(*) FROM email_logs 
        WHERE sent_at > datetime('now', '-24 hours')
    ''')
    recent_emails = cursor.fetchone()[0]
    
    conn.close()
    
    click.echo('\n=== Statistics ===')
    click.echo(f'Total Appointments: {total_appointments}')
    click.echo(f"Today's Appointments: {today_appointments}")
    click.echo(f'Emails Sent (24h): {recent_emails}')
    click.echo('\nEmail Status Breakdown:')
    for status, count in email_stats.items():
        click.echo(f'  {status}: {count}')

if __name__ == '__main__':
    cli()
