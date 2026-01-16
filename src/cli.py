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
    from src.database.response_tracking import ResponseTracker
    from src.database.segmentation import CustomerSegmentation
    
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
    
    # Response tracking
    response_stats = ResponseTracker.get_response_stats()
    
    # Segmentation
    segment_stats = CustomerSegmentation.get_segment_stats()
    
    conn.close()
    
    click.echo('\n=== Statistics ===')
    click.echo(f'Total Appointments: {total_appointments}')
    click.echo(f"Today's Appointments: {today_appointments}")
    click.echo(f'Emails Sent (24h): {recent_emails}')
    click.echo('\nEmail Status Breakdown:')
    for status, count in email_stats.items():
        click.echo(f'  {status}: {count}')
    
    click.echo('\n=== Customer Segmentation ===')
    click.echo(f'VIP Customers (5+ visits): {segment_stats["vip_count"]}')
    click.echo(f'Regular Customers (2-4 visits): {segment_stats["regular_count"]}')
    click.echo(f'New Customers (1 visit): {segment_stats["new_count"]}')
    click.echo(f'Inactive Customers (90+ days): {segment_stats["inactive_count"]}')
    
    click.echo('\n=== Email Engagement ===')
    click.echo(f'Open Rate: {response_stats["open_rate"]:.1f}%')
    click.echo(f'Click Rate: {response_stats["click_rate"]:.1f}%')
    click.echo(f'Reply Rate: {response_stats["reply_rate"]:.1f}%')

@cli.command()
@click.option('--segment', type=click.Choice(['vip', 'regular', 'new', 'inactive']), help='Filter by segment')
def segments(segment):
    """Show customer segments"""
    from src.database.segmentation import CustomerSegmentation
    
    if segment:
        customers = CustomerSegmentation.get_customers_by_segment(segment)
        click.echo(f'\n=== {segment.upper()} Customers ({len(customers)}) ===')
        for customer in customers[:20]:  # Show first 20
            click.echo(f"  {customer['name']} ({customer['email']}) - {customer['appointment_count']} appointments")
        if len(customers) > 20:
            click.echo(f'  ... and {len(customers) - 20} more')
    else:
        stats = CustomerSegmentation.get_segment_stats()
        click.echo('\n=== Customer Segments ===')
        click.echo(f'VIP: {stats["vip_count"]}')
        click.echo(f'Regular: {stats["regular_count"]}')
        click.echo(f'New: {stats["new_count"]}')
        click.echo(f'Inactive: {stats["inactive_count"]}')
        click.echo(f'Total: {stats["total_customers"]}')

@cli.command()
def engagement():
    """Show email engagement metrics"""
    from src.database.response_tracking import ResponseTracker
    
    stats = ResponseTracker.get_response_stats()
    
    click.echo('\n=== Email Engagement Metrics ===')
    click.echo(f'Total Emails Sent: {stats["total_emails"]}')
    click.echo(f'Opened: {stats["opened"]} ({stats["open_rate"]:.1f}%)')
    click.echo(f'Clicked: {stats["clicked"]} ({stats["click_rate"]:.1f}%)')
    click.echo(f'Replied: {stats["replied"]} ({stats["reply_rate"]:.1f}%)')

if __name__ == '__main__':
    cli()
