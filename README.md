# AI News Aggregator

An intelligent news aggregator that scrapes articles and videos from multiple sources, generates AI-powered summaries, and delivers personalized email digests.

## What It Does

1. **Scrapes** news from RSS feeds (OpenAI, Anthropic) and YouTube channels
2. **Stores** everything in PostgreSQL
3. **Generates** AI summaries using OpenAI
4. **Ranks** content by your interests
5. **Sends** personalized email digests daily

## Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL (Docker recommended)
- OpenAI API key
- Gmail account with app password

### Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-news-aggregator
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start database
cd docker && docker-compose up -d && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL

# 5. Initialize database
python scripts/create_tables.py

# 6. Run it!
python scripts/daily_runner.py
```

## Configuration

### Add News Sources

Edit `app/config.py`:

```python
# YouTube Channels
YOUTUBE_CHANNELS = [
    {"username": "CNBCtelevision", "name": "CNBC Television"},
]

# RSS Feeds
RSS_FEEDS = {
    "openai": "https://openai.com/news/rss",
}
```

### Environment Variables

Create `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_aggregator
DB_USER=postgres
DB_PASSWORD=postgres

# OpenAI
OPENAI_API_KEY=your_key_here

# Gmail SMTP
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
```

### Create User Profile

```bash
python scripts/manage_profile.py create \
  user@example.com \
  "Your Name" \
  "Your background" \
  "Your interests"
```

## Usage

### Run Complete Pipeline
```bash
python scripts/daily_runner.py
```

**Options:**
- `--hours 48` - Look back 48 hours
- `--text` - Plain text emails
- `--skip-scraping` - Skip scraping step

### Individual Steps
```bash
python scripts/run_aggregator.py 24        # Scrape content
python scripts/process_digests.py         # Generate summaries
python scripts/send_email_digest.py user@example.com 24 html
```

## Deployment (Optional)

### Local Development
Run manually or schedule with cron:
```bash
0 8 * * * cd /path/to/project && /path/to/venv/bin/python scripts/daily_runner.py
```

### Render Cloud Deployment (Optional)

Deploy to Render for automatic daily runs:

1. **Push to GitHub** (use `deployment` branch)
   ```bash
   git push origin deployment
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - New → Blueprint → Select your repo
   - Render detects `render.yaml` automatically

3. **Set Environment Variables** in Render dashboard:
   - `OPENAI_API_KEY`
   - `SMTP_USERNAME`, `SMTP_PASSWORD`, `FROM_EMAIL`
   - `DATABASE_URL` is auto-provided

4. **Initialize Database** (one-time)
   - Render Shell: `python scripts/create_tables.py`

**What Gets Created:**
- PostgreSQL database (managed)
- Cron job (runs daily at 8 AM UTC)

See [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md) for detailed instructions.

## Project Structure

```
app/
├── agents/          # AI agents (digest, ranking, email)
├── database/        # Database models and CRUD
├── scrapers/        # RSS and YouTube scrapers
├── services/       # YouTube, SMTP services
└── runner.py        # Main aggregator

scripts/
├── daily_runner.py  # Complete pipeline
├── run_aggregator.py
├── process_digests.py
└── send_email_digest.py
```

## How It Works

1. **Scraping**: Fetches articles/videos from configured sources (last 24 hours)
2. **Digest Generation**: Creates AI summaries for new content
3. **Email Delivery**: Ranks content by user profile and sends personalized emails

## Troubleshooting

**Database issues?**
```bash
docker ps  # Check PostgreSQL is running
python scripts/test_database.py
```

**Email not sending?**
```bash
python scripts/test_smtp.py recipient@example.com
# Check Gmail app password (not regular password)
```

**No content found?**
- Check RSS feed URLs are accessible
- Verify YouTube usernames in `app/config.py`
- Try: `python scripts/daily_runner.py --hours 168`

**OpenAI errors?**
- Verify `OPENAI_API_KEY` in `.env`
- Check API quota/billing

## Documentation

- [Daily Runner Guide](docs/DAILY_RUNNER.md)
- [Gmail SMTP Setup](docs/GMAIL_SMTP_SETUP.md)
- [Render Deployment](docs/RENDER_DEPLOYMENT.md)
- [Database Setup](app/database/README.md)

---

**Need Help?** Check the `docs/` folder or open an issue on GitHub.
