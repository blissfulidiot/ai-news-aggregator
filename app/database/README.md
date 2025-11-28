# Database Setup

## Quick Start

1. **Start PostgreSQL container:**
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Create tables:**
   ```bash
   python scripts/create_tables.py
   ```

4. **Test database:**
   ```bash
   python scripts/test_database.py
   ```

## Database Models

### Source
- Stores news sources (RSS feeds, YouTube channels, etc.)
- Fields: name, url, source_type, youtube_channel_id, youtube_username, rss_url

### Article
- Stores news articles and blog posts
- Fields: title, url, description, content, published_at, feed_type, markdown_content
- Linked to Source via source_id

### Video
- Stores YouTube videos
- Fields: title, url, video_id, description, transcript, published_at
- Linked to Source via source_id
- Transcript can be fetched separately

### UserSettings
- Stores user preferences
- Fields: email, system_prompt

## Repository Usage

```python
from app.database.connection import get_db_session
from app.database.repository import SourceRepository, ArticleRepository
from app.database.models import SourceType

# Get database session
db_gen = get_db_session()
db = next(db_gen)

# Create source
source = SourceRepository.create(
    db,
    name="Anthropic",
    url="https://www.anthropic.com",
    source_type=SourceType.RSS,
    rss_url="https://anthropic.com/rss.xml"
)

# Create article
article = ArticleRepository.create(
    db,
    source_id=source.id,
    title="Article Title",
    url="https://example.com/article",
    published_at=datetime.now(timezone.utc),
    description="Article description"
)

# Get recent articles
recent = ArticleRepository.get_recent(db, hours=24)

db.close()
```

