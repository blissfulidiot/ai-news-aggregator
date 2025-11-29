# AI News Aggregator

A news aggregator that pulls articles and videos from RSS feeds and YouTube channels, generates summaries using OpenAI, and sends personalized email digests.

## What It Does

The system scrapes content from multiple sources, stores it in a PostgreSQL database, creates AI summaries, ranks them based on your interests, and emails you a daily digest.

## Quick Start

### Prerequisites

You'll need:
- Python 3.13 or higher
- PostgreSQL (Docker works well for local development)
- An OpenAI API key
- A Gmail account with an app password set up

### Setup

Clone the repository and set up your environment:

```bash
git clone <repository-url>
cd ai-news-aggregator
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies using UV:

```bash
pip install uv
uv sync
```

Start the database:

```bash
cd docker && docker-compose up -d && cd ..
```

Set up your environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your `OPENAI_API_KEY`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `FROM_EMAIL`.

Initialize the database:

```bash
python scripts/create_tables.py
```

Run it:

```bash
python scripts/daily_runner.py
```

## Configuration

### Adding News Sources

Edit `app/config.py` to add YouTube channels or RSS feeds:

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

Copy `.env.example` to `.env` and configure it.

For the database, you have two options:

**Option 1: Production Database (Render/External)**

Set `DATABASE_URL` to your production database connection string. This takes priority over the individual database variables below.

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**Option 2: Local Development Database**

Comment out `DATABASE_URL` and use individual variables for local Docker PostgreSQL:

```bash
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=news_aggregator
# DB_USER=postgres
# DB_PASSWORD=postgres
```

The `DATABASE_URL` variable takes priority. If it's set, the individual `DB_*` variables are ignored. This makes it easy to switch between local and production.

You'll also need:

```bash
# OpenAI
OPENAI_API_KEY=your_key_here

# Gmail SMTP
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
```

### Creating a User Profile

Create a user profile so the system knows what content to prioritize:

```bash
python scripts/manage_profile.py create \
  user@example.com \
  "Your Name" \
  "Your background" \
  "Your interests"
```

## Usage

### Running the Complete Pipeline

Run everything at once:

```bash
python scripts/daily_runner.py
```

Options:
- `--hours 48` - Look back 48 hours instead of 24
- `--text` - Send plain text emails instead of HTML
- `--skip-scraping` - Skip the scraping step (useful for testing)

### Running Individual Steps

You can also run each step separately:

```bash
python scripts/run_aggregator.py 24        # Scrape content
python scripts/process_digests.py         # Generate summaries
python scripts/send_email_digest.py user@example.com 24 html
```

## Deployment

### Local Development

Run it manually or set up a cron job:

```bash
0 8 * * * cd /path/to/project && /path/to/venv/bin/python scripts/daily_runner.py
```

### Render Cloud Deployment

You can deploy to Render for automatic daily runs.

1. Push to GitHub (use the `deployment` branch):
   ```bash
   git push origin deployment
   ```

2. Connect to Render:
   - Go to the [Render Dashboard](https://dashboard.render.com)
   - Click New → Blueprint → Select your repository
   - Render will detect `render.yaml` automatically

3. Set environment variables in the Render dashboard:
   - `OPENAI_API_KEY`
   - `SMTP_USERNAME`, `SMTP_PASSWORD`, `FROM_EMAIL`
   - `DATABASE_URL` is automatically provided

4. Initialize the database (one-time):
   - Use Render Shell: `python scripts/create_tables.py`

This creates:
- A managed PostgreSQL database
- A cron job that runs daily at 8 AM UTC

See [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md) for more detailed instructions.

## Project Structure

```
app/
├── agents/          # AI agents (digest, ranking, email)
├── database/        # Database models and CRUD operations
├── scrapers/        # RSS scrapers (Anthropic, OpenAI)
├── services/        # YouTube service, SMTP service
└── runner.py        # Main aggregator

scripts/
├── daily_runner.py      # Complete pipeline
├── run_aggregator.py    # Scraping only
├── process_digests.py   # Generate summaries
├── send_email_digest.py # Send emails
└── manage_profile.py   # User management
```

## How It Works

1. Scraping: Fetches articles and videos from configured sources (defaults to last 24 hours)
2. Digest Generation: Creates AI summaries for new content
3. Email Delivery: Ranks content by user profile and sends personalized emails
4. Tracking: Tracks which digests have been sent to each user to prevent duplicates

## Features

### Digest Tracking

The system tracks which digests have been sent to each user, so you won't get duplicate emails. Each user only receives new digests they haven't seen yet. Digests are automatically marked as sent after successful email delivery.

### Database Switching

You can easily switch between local and production databases by setting or unsetting `DATABASE_URL`. The system automatically detects which database mode to use. Works seamlessly with Render PostgreSQL.

## Troubleshooting

**Database connection issues?**

Check which database you're connected to:
```bash
python3 -c "from app.database.connection import DB_MODE; print(f'Mode: {DB_MODE}')"
```

For local development, make sure Docker is running:
```bash
docker ps  # Check PostgreSQL is running
```

Test the connection:
```bash
python scripts/test_database.py
```

**Email not sending?**

Test SMTP configuration:
```bash
python scripts/test_smtp.py recipient@example.com
```

Make sure you're using a Gmail app password, not your regular password.

**No content found?**

- Check that RSS feed URLs are accessible
- Verify YouTube usernames in `app/config.py`
- Try looking back further: `python scripts/daily_runner.py --hours 168`

**OpenAI errors?**

- Verify `OPENAI_API_KEY` is set in your `.env` file
- Check your API quota and billing status

## Documentation

- [Daily Runner Guide](docs/DAILY_RUNNER.md)
- [Gmail SMTP Setup](docs/GMAIL_SMTP_SETUP.md)
- [Render Deployment](docs/RENDER_DEPLOYMENT.md)
- [Database Setup](app/database/README.md)

---

For more help, check the `docs/` folder or open an issue on GitHub.
