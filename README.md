# AI News Aggregator

An intelligent news aggregator that scrapes articles and videos from multiple sources, generates AI-powered summaries, and delivers personalized email digests based on user interests.

## 🎯 Overview

This system automatically:
- **Scrapes** news articles from RSS feeds (OpenAI, Anthropic, etc.)
- **Collects** YouTube videos from configured channels
- **Stores** everything in a PostgreSQL database
- **Generates** AI summaries using OpenAI's GPT models
- **Ranks** content by relevance to each user's profile
- **Sends** personalized email digests daily

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│  RSS Feeds          │  YouTube Channels  │  Blog Posts          │
│  • OpenAI           │  • CNBC            │  • Custom URLs       │
│  • Anthropic        │  • Your Channels    │                      │
└──────────┬──────────┴──────────┬─────────┴──────────┬───────────┘
           │                      │                    │
           ▼                      ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPING LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ RSS Scrapers │  │ YouTube      │  │ Markdown     │         │
│  │              │  │ Service      │  │ Converter    │         │
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘         │
└─────────┼──────────────────┼─────────────────┼──────────────────┘
          │                  │                 │
          └──────────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Sources  │  │ Articles │  │ Videos   │  │ Digests  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼──────────────┼──────────────┼─────────────┼────────────┘
        │              │              │             │
        └──────────────┴──────────────┴─────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI PROCESSING LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Digest       │  │ News Anchor  │  │ Email        │         │
│  │ Agent        │  │ Agent        │  │ Agent        │         │
│  │ (Summaries)  │  │ (Ranking)     │  │ (Formatting) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼─────────────────┼──────────────────┘
          │                  │                 │
          └──────────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL DELIVERY                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Personalized HTML/Text Emails with Ranked Content        │  │
│  │  • Top 10 articles/videos                                │  │
│  │  • AI-generated introductions                             │  │
│  │  • Clickable YouTube thumbnails                           │  │
│  │  • "Read more" buttons                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL (via Docker or local installation)
- OpenAI API key
- Gmail account with app password (for email sending)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-news-aggregator
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   # Start PostgreSQL container
   cd docker
   docker-compose up -d
   cd ..
   ```

5. **Configure environment**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and add your credentials:
   # - OPENAI_API_KEY
   # - SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL
   ```

6. **Initialize database**
   ```bash
   python scripts/create_tables.py
   ```

7. **Run the pipeline**
   ```bash
   python scripts/daily_runner.py
   ```

## ⚙️ Configuration

### 1. News Sources

Edit `app/config.py` to add/remove sources:

**YouTube Channels:**
```python
YOUTUBE_CHANNELS = [
    {"username": "CNBCtelevision", "name": "CNBC Television"},
    {"username": "@anotherchannel", "name": "Display Name"},
]
```

**RSS Feeds:**
```python
RSS_FEEDS = {
    "openai": "https://openai.com/news/rss",
    "source_name": "https://example.com/rss.xml",
}
```

### 2. Environment Variables

Create `.env` file in project root:

```bash
# Database (for local development)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_aggregator
DB_USER=postgres
DB_PASSWORD=postgres

# Or use DATABASE_URL (for production/Render)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Gmail SMTP (for email sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
FROM_EMAIL=your_email@gmail.com

# Optional: YouTube Proxy
YOUTUBE_PROXY_USERNAME=your_proxy_username
YOUTUBE_PROXY_PASSWORD=your_proxy_password
```

### 3. User Profiles

Create user profiles for personalized ranking:

```bash
python scripts/manage_profile.py create \
  user@example.com \
  "John Doe" \
  "Software engineer with 10 years experience" \
  "AI, machine learning, Python, web development"
```

## 📖 Usage

### Daily Pipeline (Complete Flow)

Run the complete pipeline (scrape → digest → email):

```bash
python scripts/daily_runner.py
```

**Options:**
- `--hours 48` - Look back 48 hours instead of 24
- `--text` - Send plain text emails instead of HTML
- `--skip-scraping` - Skip scraping step (useful for testing)

### Individual Steps

**1. Scrape and save content:**
```bash
python scripts/run_aggregator.py 24
```

**2. Generate digests for new items:**
```bash
python scripts/process_digests.py
```

**3. Send email digest to a user:**
```bash
python scripts/send_email_digest.py user@example.com 24 html
```

**4. Rank digests for a user:**
```bash
python scripts/rank_digests.py user@example.com 24
```

### Utility Scripts

**Check database status:**
```bash
python scripts/check_videos.py      # Check video/transcript status
python scripts/check_digests.py      # Check digest status
python scripts/test_database.py      # Test database operations
```

**Fetch missing data:**
```bash
python scripts/fetch_markdown_batch.py    # Get markdown for articles
python scripts/fetch_transcripts_batch.py # Get transcripts for videos
```

**Test email sending:**
```bash
python scripts/test_smtp.py recipient@example.com
```

## 🏗️ Project Structure

```
ai-news-aggregator/
├── app/                          # Main application code
│   ├── agents/                   # AI agents
│   │   ├── digest_agent.py      # Generates summaries
│   │   ├── news_anchor_agent.py # Ranks content
│   │   └── email_agent.py       # Formats emails
│   ├── config.py                 # Source configuration
│   ├── database/                 # Database layer
│   │   ├── connection.py         # DB connection
│   │   ├── models.py             # SQLAlchemy models
│   │   └── repository.py         # CRUD operations
│   ├── profiles/                 # User profile management
│   ├── scrapers/                 # Content scrapers
│   │   ├── anthropic_news_scraper.py
│   │   ├── openai_news_scraper.py
│   │   └── youtube_scraper.py    # Deprecated - use youtube_service.py
│   ├── services/                 # External services
│   │   ├── youtube_service.py    # YouTube API (use this instead of youtube_scraper)
│   │   └── smtp_service.py       # Email sending
│   └── runner.py                 # Main aggregator
├── docker/                        # Docker configuration
│   └── docker-compose.yml         # PostgreSQL setup
├── scripts/                       # Utility scripts
│   ├── daily_runner.py           # Complete pipeline
│   ├── run_aggregator.py         # Scraping only
│   ├── process_digests.py        # Digest generation
│   ├── send_email_digest.py      # Email sending
│   └── manage_profile.py         # User management
├── docs/                          # Documentation
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔄 Pipeline Flow

### Step 1: Scraping
- Fetches articles from RSS feeds (OpenAI, Anthropic)
- Collects videos from YouTube channels
- Filters by time window (default: last 24 hours)
- Saves to PostgreSQL database
- Excludes YouTube Shorts automatically

### Step 2: Digest Generation
- Finds articles/videos without digests
- Uses OpenAI to generate 2-3 sentence summaries
- Creates engaging titles
- Stores digests with original publish date

### Step 3: Email Delivery
- Retrieves digests from specified time window
- Ranks content by user profile relevance
- Generates personalized email with:
  - Personalized greeting (if name provided)
  - AI-generated introduction
  - Top 10 ranked items
  - YouTube video thumbnails
  - "Read more" buttons
- Sends via Gmail SMTP

## 🎨 Features

### Content Sources
- **RSS Feeds**: OpenAI, Anthropic (news, engineering, research)
- **YouTube Channels**: Configurable channel list
- **Markdown Conversion**: Full article content extraction
- **Transcript Fetching**: YouTube video transcripts

### AI Features
- **Smart Summaries**: GPT-4o-mini powered 2-3 sentence summaries
- **Personalized Ranking**: Content ranked by user interests
- **Email Generation**: AI-crafted introductions

### Email Features
- **HTML & Text**: Dual-format email support
- **YouTube Thumbnails**: Clickable video previews
- **Clean Design**: Professional, readable layout
- **Personalization**: User name, interests, background

## 🚢 Deployment

### Local Development

1. Use Docker for PostgreSQL:
   ```bash
   cd docker && docker-compose up -d
   ```

2. Run daily pipeline manually or schedule with cron:
   ```bash
   # Add to crontab
   0 8 * * * cd /path/to/project && /path/to/venv/bin/python scripts/daily_runner.py
   ```

### Render Deployment (Quickest Method)

**Prerequisites:**
- Render account (free tier available)
- GitHub repository with your code

**Steps:**

1. **Push code to GitHub** (if not already done)
   ```bash
   git push origin main
   ```

2. **Connect Render to GitHub**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Set Environment Variables** (in Render dashboard)
   After services are created, go to each service → Environment tab:
   - **Cron Job service:**
     - `OPENAI_API_KEY` - Your OpenAI API key
     - `SMTP_USERNAME` - Your Gmail address
     - `SMTP_PASSWORD` - Your Gmail app password
     - `FROM_EMAIL` - Your Gmail address
     - `SMTP_HOST` - `smtp.gmail.com` (optional, default)
     - `SMTP_PORT` - `587` (optional, default)
   - **Note:** `DATABASE_URL` is automatically provided by PostgreSQL service

4. **Initialize Database** (one-time)
   - Option A: Via Render Shell
     - Go to Cron Job service → Shell tab
     - Run: `python scripts/create_tables.py`
   - Option B: Locally (if you have DATABASE_URL)
     ```bash
     export DATABASE_URL="postgresql://user:pass@host:port/dbname"
     python scripts/create_tables.py
     ```

5. **Done!** The cron job will run daily at 8 AM UTC.

**What Gets Created:**
- ✅ Managed PostgreSQL database (`news-aggregator-db`)
- ✅ Cron Job (`daily-news-runner`) that runs `daily_runner.py` daily

**Customizing Schedule:**
Edit `render.yaml` and change the `schedule` field:
- `"0 8 * * *"` - Daily at 8 AM UTC
- `"0 */6 * * *"` - Every 6 hours
- `"0 0 * * *"` - Daily at midnight UTC

**Manual Setup Alternative:**
If you prefer manual setup instead of `render.yaml`:
1. Create PostgreSQL service manually
2. Create Cron Job manually
3. Set environment variables manually
4. Same result, just more clicks

## 🧪 Testing

### Test Individual Components

```bash
# Test database
python scripts/test_database.py

# Test SMTP email
python scripts/test_smtp.py recipient@example.com

# Test scraping
python scripts/run_aggregator.py 24

# Test digest generation
python scripts/process_digests.py

# Test email generation
python scripts/generate_email.py user@example.com 24 html
```

### Test Complete Pipeline

```bash
# Test without scraping (uses existing data)
python scripts/daily_runner.py --skip-scraping

# Test with custom hours
python scripts/daily_runner.py --hours 168
```

## 📝 Key Concepts

### Sources
- Represents a news source (RSS feed or YouTube channel)
- Stored in `sources` table
- Links to articles/videos

### Articles
- News articles from RSS feeds
- Includes title, URL, description, publish date
- Optional markdown content

### Videos
- YouTube videos from configured channels
- Includes title, URL, video ID, description
- Optional transcript

### Digests
- AI-generated summaries of articles/videos
- Includes title and 2-3 sentence summary
- Linked to original article/video
- Uses original publish date for `created_at`

### User Profiles
- User preferences for personalized ranking
- Includes name, background, interests
- Used by News Anchor Agent for ranking

## 🔧 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `docker ps`
- Check `.env` file has correct credentials
- Test connection: `python scripts/test_database.py`

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check Gmail app password is correct
- Test SMTP: `python scripts/test_smtp.py`

### No Content Found
- Check RSS feed URLs are accessible
- Verify YouTube channel usernames are correct
- Increase time window: `--hours 168`

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set
- Check API quota/billing
- Test with: `python scripts/process_digests.py`

### Missing Transcripts/Markdown
- Run batch scripts:
  ```bash
  python scripts/fetch_transcripts_batch.py
  python scripts/fetch_markdown_batch.py
  ```

## 📚 Documentation

- [Daily Runner Guide](docs/DAILY_RUNNER.md) - Complete pipeline documentation
- [Gmail SMTP Setup](docs/GMAIL_SMTP_SETUP.md) - Email configuration
- [Database Setup](app/database/README.md) - Database models and usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for news feeds
- YouTube for video content
- All open-source contributors

---

**Need Help?** Check the [docs/](docs/) folder for detailed guides or open an issue on GitHub.
