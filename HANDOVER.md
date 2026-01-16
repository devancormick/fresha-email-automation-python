# Handover Video Guide

This document outlines what to cover in the handover video walkthrough for the Fresha Email Automation project.

## Video Structure (15-20 minutes)

### 1. Introduction (2 minutes)
- Project overview
- What the system does
- Key features

### 2. Project Setup (3 minutes)
- Repository structure
- Key files and directories
- Configuration files

### 3. Installation & Configuration (4 minutes)
- Installing dependencies
- Setting up environment variables
- Database initialization
- Testing the setup

### 4. Core Functionality (5 minutes)
- Running the scraper
- Sending emails manually
- Viewing statistics
- Health checks

### 5. Deployment Options (3 minutes)
- Docker deployment
- Systemd service
- Cloud deployment options

### 6. Monitoring & Maintenance (2 minutes)
- Dashboard access
- Logs location
- Backup procedures
- Troubleshooting

### 7. Q&A & Next Steps (1 minute)
- Common questions
- Support resources

---

## Detailed Script

### Section 1: Introduction

**Say:**
"Welcome to the Fresha Email Automation handover. This system automates thank-you and follow-up emails for your nail salon appointments managed through Fresha."

**Show:**
- Project README
- Key features list

**Highlight:**
- Same-day thank-you emails (12pm & 7pm)
- 7-day follow-up emails
- Duplicate prevention
- Comprehensive logging

---

### Section 2: Project Setup

**Show:**
```
fresha-email-automation-python/
├── src/
│   ├── scraper/      # Fresha automation
│   ├── email/        # Email service
│   ├── scheduler/    # Automated jobs
│   ├── database/     # Data models
│   └── monitoring/   # Dashboard
├── config/           # Configuration
├── db/              # Database files
├── logs/            # Log files
└── scripts/         # Deployment scripts
```

**Explain:**
- Source code organization
- Configuration location
- Database storage
- Log files

---

### Section 3: Installation & Configuration

**Demonstrate:**

1. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Configure environment:**
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials
```

3. **Initialize database:**
```bash
python -m src.cli init
```

4. **Verify setup:**
```bash
python -m src.cli health
```

**Show:**
- Environment variables needed
- Where to get credentials
- Health check output

---

### Section 4: Core Functionality

**Demonstrate:**

1. **Scrape appointments:**
```bash
python -m src.cli scrape
```

2. **Send thank-you emails:**
```bash
python -m src.cli send-thankyou --time-slot 12pm
```

3. **View statistics:**
```bash
python -m src.cli stats
```

4. **Check customer segments:**
```bash
python -m src.cli segments
python -m src.cli segments --segment vip
```

5. **View engagement:**
```bash
python -m src.cli engagement
```

**Explain:**
- What each command does
- Expected output
- Error handling

---

### Section 5: Deployment Options

**Show Docker deployment:**
```bash
docker-compose up -d
```

**Show systemd service:**
- Service file location
- How to enable/start
- Status checking

**Mention:**
- Cloud deployment options
- Scaling considerations
- Backup strategies

---

### Section 6: Monitoring & Maintenance

**Show dashboard:**
```bash
python -m src.monitoring.dashboard
# Access at http://localhost:8080
```

**Show:**
- Dashboard interface
- Health metrics
- Statistics display
- API endpoints

**Explain:**
- Log file locations
- Backup procedures
- Common issues and fixes

---

### Section 7: Q&A & Next Steps

**Common Questions:**

1. **How do I update credentials?**
   - Edit `config/.env`
   - Restart service

2. **How do I check if it's working?**
   - Run `python -m src.cli health`
   - Check dashboard
   - Review logs

3. **What if emails fail?**
   - Check SMTP settings
   - Review error logs
   - Check alert emails

4. **How do I backup?**
   - Automatic: Daily at 2am
   - Manual: `python -m src.cli backup`

**Next Steps:**
- Review documentation
- Test with real data
- Set up monitoring
- Schedule regular backups

---

## Key Points to Emphasize

1. **Security:**
   - Never commit `.env` file
   - Use strong passwords
   - Enable 2FA on email accounts

2. **Monitoring:**
   - Check health regularly
   - Review logs weekly
   - Monitor email success rates

3. **Maintenance:**
   - Database backups are automatic
   - Logs rotate automatically
   - Update dependencies quarterly

4. **Support:**
   - Check logs first
   - Review TEST_RESULTS.md
   - See DEPLOYMENT.md for issues

---

## Video Recording Tips

1. **Screen Recording:**
   - Use clear resolution (1080p+)
   - Show terminal and code clearly
   - Use zoom for small text

2. **Audio:**
   - Clear microphone
   - Minimal background noise
   - Speak clearly and slowly

3. **Editing:**
   - Add timestamps/chapters
   - Highlight important commands
   - Add text overlays for file paths

4. **Delivery:**
   - Upload to YouTube (unlisted) or cloud storage
   - Provide download link
   - Include in project documentation

---

## Checklist for Handover Video

- [ ] Project overview and features
- [ ] Installation steps
- [ ] Configuration walkthrough
- [ ] Database initialization
- [ ] Running scraper
- [ ] Sending emails
- [ ] Viewing statistics
- [ ] Health checks
- [ ] Dashboard demonstration
- [ ] Docker deployment
- [ ] Systemd service setup
- [ ] Backup procedures
- [ ] Troubleshooting tips
- [ ] Q&A section

---

## Additional Resources to Reference

- README.md - Main documentation
- DEPLOYMENT.md - Deployment guide
- TEST_RESULTS.md - Test validation
- CHANGELOG.md - Version history
- .env.example - Configuration template
