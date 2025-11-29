# Daily Runner - Complete Pipeline

The `daily_runner.py` script combines all pipeline steps into a single executable that can be scheduled to run daily.

## Pipeline Steps

1. **Scrape Content** - Fetches articles and videos from all sources and saves to database
2. **Generate Digests** - Creates AI summaries for new items without digests
3. **Send Emails** - Sends personalized email digests to all users in the database

## Usage

### Basic Usage

Run the complete pipeline (scrapes last 24 hours):

```bash
python scripts/daily_runner.py
```

### Options

```bash
# Look back 48 hours instead of 24
python scripts/daily_runner.py --hours 48

# Send plain text emails instead of HTML
python scripts/daily_runner.py --text

# Skip scraping step (useful for testing email sending)
python scripts/daily_runner.py --skip-scraping
```

### Command Line Arguments

- `--hours HOURS`: Number of hours to look back for content (default: 24)
- `--text`: Send plain text emails instead of HTML
- `--skip-scraping`: Skip the scraping step (useful for testing)

## Scheduling

### Cron (Linux/Mac)

Add to crontab to run daily at 8 AM:

```bash
crontab -e
```

Add this line:

```
0 8 * * * cd /path/to/ai-news-aggregator && /path/to/venv/bin/python scripts/daily_runner.py >> logs/daily_runner.log 2>&1
```

### Systemd Timer (Linux)

Create `/etc/systemd/system/news-aggregator.service`:

```ini
[Unit]
Description=Daily News Aggregator Pipeline
After=network.target postgresql.service

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/ai-news-aggregator
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python scripts/daily_runner.py
```

Create `/etc/systemd/system/news-aggregator.timer`:

```ini
[Unit]
Description=Run News Aggregator Daily
Requires=news-aggregator.service

[Timer]
OnCalendar=daily
OnCalendar=08:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable news-aggregator.timer
sudo systemctl start news-aggregator.timer
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 AM
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `scripts\daily_runner.py`
7. Start in: `C:\path\to\ai-news-aggregator`

## Output

The script provides detailed output for each step:

```
======================================================================
DAILY NEWS AGGREGATOR PIPELINE
======================================================================
Started at: 2025-11-29 08:00:00
Looking back: 24 hours

======================================================================
STEP 1: Scraping Content and Saving to Database
======================================================================
✓ Scraping complete:
  Articles found: 15
  Videos found: 8

======================================================================
STEP 2: Generating Digests
======================================================================
✓ Digest agent initialized
Found 5 articles and 3 videos to process
✓ Digest generation complete:
  Successful: 8
  Failed: 0

======================================================================
STEP 3: Sending Email Digests
======================================================================
Found 3 user(s) to send emails to
✓ Agents initialized
Found 23 digests from the last 24 hours
✓ Email sending complete:
  Sent: 3
  Failed: 0
  Total users: 3

======================================================================
PIPELINE COMPLETE
======================================================================
Duration: 0:05:23
Summary:
  Articles scraped: 15
  Videos scraped: 8
  Digests generated: 8
  Emails sent: 3/3
======================================================================
```

## Error Handling

The pipeline continues even if individual steps fail:

- **Scraping errors**: Pipeline stops (no data to process)
- **Digest generation errors**: Continues (some digests may be missing)
- **Email sending errors**: Continues (sends to remaining users)

## Logging

For production use, redirect output to a log file:

```bash
python scripts/daily_runner.py >> logs/daily_runner.log 2>&1
```

Or use Python logging:

```python
import logging
logging.basicConfig(
    filename='logs/daily_runner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Requirements

- Database connection configured
- OpenAI API key set (for digest generation)
- SMTP credentials configured (for email sending)
- Users added to database (use `scripts/manage_profile.py`)

## Testing

Test individual steps:

```bash
# Test email sending only (skip scraping and digest generation)
python scripts/daily_runner.py --skip-scraping --hours 168

# Test with shorter time window
python scripts/daily_runner.py --hours 1
```

## Troubleshooting

### No users found
Add users using:
```bash
python scripts/manage_profile.py create user@example.com "Name" "Background" "Interests"
```

### No digests found
- Check if scraping ran successfully
- Verify digest generation completed
- Check database for digest entries

### Email sending fails
- Verify SMTP credentials in `.env`
- Check Gmail app password is correct
- Ensure 2-factor authentication is enabled

