# Fresha Email Automation (Python)

Automated email system for Fresha nail salon appointments. Sends same-day thank-you emails at 12pm and 7pm, and 7-day follow-up emails asking if nails lasted well.

## Features

- **Script 1**: Same-day thank-you emails at 12pm and 7pm
- **Script 2**: 7-day follow-up emails with duplicate prevention
- Headless browser automation with Playwright
- SQLite database for tracking and preventing duplicates
- Comprehensive logging (sent/skipped/failed)
- Failure alerts via email
- Secure credential handling
- **NEW**: Retry logic with exponential backoff
- **NEW**: Health check system
- **NEW**: CLI interface for management
- **NEW**: Metrics and statistics collection
- **NEW**: Automatic database backups
- **NEW**: Rate limiting protection
- **NEW**: Configuration validation

## Prerequisites

- Python 3.8+
- pip
- Playwright browsers (installed automatically)
- SMTP email account (Gmail, SendGrid, etc.)
- Fresha account credentials

## Installation

1. Clone the repository:
```bash
cd fresha-email-automation-python
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Set up environment variables:
```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your credentials:
- Fresha login credentials
- SMTP settings
- Alert email address

## Configuration

### Environment Variables

- `FRESHA_EMAIL`: Your Fresha login email
- `FRESHA_PASSWORD`: Your Fresha login password
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port (587 for TLS, 465 for SSL)
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_FROM_NAME`: Sender name
- `SMTP_FROM_EMAIL`: Sender email address
- `ALERT_EMAIL`: Email address for failure alerts
- `TIMEZONE`: Timezone (default: America/New_York)

## Usage

### CLI Commands

The project includes a comprehensive CLI interface:

```bash
# Initialize database
python -m src.cli init

# Check system health
python -m src.cli health

# View statistics
python -m src.cli stats

# Send thank-you emails manually
python -m src.cli send-thankyou --time-slot 12pm
python -m src.cli send-thankyou --time-slot 7pm

# Send follow-up emails manually
python -m src.cli send-followup

# Scrape appointments
python -m src.cli scrape

# Backup database
python -m src.cli backup

# Restore database
python -m src.cli restore db/backups/fresha_20240115_020000.db
```

### Development Mode

Run scripts individually:
```bash
python -m src.scheduler.script1_thankyou 12pm
python -m src.scheduler.script1_thankyou 7pm
python -m src.scheduler.script2_followup
```

Scrape appointments:
```bash
python -m src.scraper.fresha_scraper
```

### Production Mode

Start the scheduler:
```bash
python -m src.main
```

Or:
```bash
python src/main.py
```

The scheduler will automatically run:
- Thank-you emails at 12pm and 7pm daily
- Follow-up emails at 10am daily
- Daily database backups at 2am
- Health checks every 6 hours

## Deployment

### Option 1: Systemd Service

Create `/etc/systemd/system/fresha-automation.service`:
```ini
[Unit]
Description=Fresha Email Automation
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/fresha-email-automation-python
ExecStart=/usr/bin/python3 /path/to/fresha-email-automation-python/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fresha-automation
sudo systemctl start fresha-automation
```

### Option 2: Supervisor

Create `/etc/supervisor/conf.d/fresha-automation.conf`:
```ini
[program:fresha-automation]
command=/path/to/venv/bin/python /path/to/fresha-email-automation-python/src/main.py
directory=/path/to/fresha-email-automation-python
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/fresha-automation.err.log
stdout_logfile=/var/log/fresha-automation.out.log
```

Reload supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fresha-automation
```

### Option 3: Cloud Deployment

Deploy to services like:
- AWS EC2 with systemd
- Heroku
- DigitalOcean App Platform
- Railway
- Render

## Database

SQLite database is stored in `db/fresha.db`. The database tracks:
- Appointments from Fresha
- Email logs (sent/skipped/failed)
- Email tracking (prevents duplicates)

### Backup

Regularly backup the database:
```bash
cp db/fresha.db db/fresha.db.backup
```

## Monitoring

### Logs

Logs are stored in `logs/`:
- `combined.log`: All logs
- `error.log`: Error logs only

Logs are automatically rotated when they reach 10MB.

### Alerts

The system sends email alerts when:
- 3+ consecutive failures occur
- Critical errors happen
- Authentication fails

## Troubleshooting

### Playwright Issues

If browsers fail to install:
```bash
playwright install --force chromium
```

### SMTP Issues

Test SMTP connection:
```python
from src.email.email_service import EmailService
service = EmailService()
service.verify_connection()
```

### Database Issues

If database is corrupted, delete and recreate:
```bash
rm db/fresha.db
python -m src.main
```

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/fresha-email-automation-python
python -m src.main
```

Or add the project root to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/fresha-email-automation-python"
```

## Security

- Never commit `.env` file
- Use strong passwords
- Enable 2FA on email accounts
- Regularly rotate credentials
- Monitor logs for suspicious activity

## Support

For issues or questions, check the logs in `logs/` directory.
