# Deployment Guide

## Quick Start

1. Run the deployment script:
```bash
./scripts/deploy.sh
```

2. Configure environment variables:
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials
```

3. Start the scheduler:
```bash
python -m src.main
```

## Manual Deployment

### 1. Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### 2. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configuration

Create `config/.env` from the example:
```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your credentials.

### 4. Initialize Database

```bash
python -m src.cli init
```

### 5. Verify Installation

```bash
python -m src.cli health
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/fresha-automation.service`:

```ini
[Unit]
Description=Fresha Email Automation
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/fresha-email-automation-python
Environment="PATH=/path/to/fresha-email-automation-python/venv/bin"
ExecStart=/path/to/fresha-email-automation-python/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=append:/var/log/fresha-automation.log
StandardError=append:/var/log/fresha-automation.error.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fresha-automation
sudo systemctl start fresha-automation
sudo systemctl status fresha-automation
```

### Supervisor

Create `/etc/supervisor/conf.d/fresha-automation.conf`:

```ini
[program:fresha-automation]
command=/path/to/venv/bin/python -m src.main
directory=/path/to/fresha-email-automation-python
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/fresha-automation.err.log
stdout_logfile=/var/log/fresha-automation.out.log
environment=PATH="/path/to/venv/bin:%(ENV_PATH)s"
```

Reload supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fresha-automation
```

## Monitoring

### Health Checks

Check system health:
```bash
python -m src.cli health
```

### Statistics

View statistics:
```bash
python -m src.cli stats
```

### Logs

View logs:
```bash
tail -f logs/combined.log
tail -f logs/error.log
```

## Backup and Restore

### Automatic Backups

Backups run daily at 2am automatically. Manual backup:
```bash
python -m src.cli backup
```

### Restore from Backup

```bash
python -m src.cli restore db/backups/fresha_20240115_020000.db
```

## Maintenance

### Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Database Maintenance

The database is automatically backed up daily. Old backups (beyond 10) are automatically removed.

### Troubleshooting

1. Check health status:
```bash
python -m src.cli health
```

2. Check logs:
```bash
tail -n 100 logs/error.log
```

3. Test email sending:
```bash
python -m src.cli send-thankyou 12pm
```

4. Test scraper:
```bash
python -m src.cli scrape
```

## Security Considerations

1. **Credentials**: Never commit `.env` file
2. **Permissions**: Ensure database and log files have proper permissions
3. **Firewall**: Restrict access to the server
4. **Updates**: Keep dependencies updated
5. **Monitoring**: Set up alerts for failures

## Scaling

For high-volume scenarios:

1. Use a message queue (Redis/RabbitMQ) for email sending
2. Run multiple scraper instances with different schedules
3. Use a production database (PostgreSQL) instead of SQLite
4. Implement horizontal scaling with load balancer
