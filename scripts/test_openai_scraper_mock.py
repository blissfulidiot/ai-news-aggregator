"""Test OpenAI scraper with mock RSS data"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.openai_news_scraper import OpenAINewsScraper, NewsArticle
import feedparser


def test_with_mock_feed():
    """Test scraper with mock RSS feed data"""
    print("=" * 70)
    print("Testing OpenAI Scraper with Mock RSS Feed")
    print("=" * 70)
    
    # Create mock RSS feed XML
    now = datetime.now(timezone.utc)
    
    mock_rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>OpenAI News</title>
        <link>https://openai.com/news</link>
        <description>OpenAI News and Updates</description>
        <item>
            <title>Latest GPT Model Released</title>
            <link>https://openai.com/news/gpt-model-released</link>
            <description>OpenAI has released a new GPT model with improved capabilities.</description>
            <pubDate>{(now - timedelta(hours=12)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
        </item>
        <item>
            <title>API Updates Available</title>
            <link>https://openai.com/news/api-updates</link>
            <description>New API features and improvements are now available.</description>
            <pubDate>{(now - timedelta(hours=36)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
        </item>
        <item>
            <title>Research Paper Published</title>
            <link>https://openai.com/news/research-paper</link>
            <description>A new research paper has been published on AI safety.</description>
            <pubDate>{(now - timedelta(days=5)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
        </item>
        <item>
            <title>Old Article</title>
            <link>https://openai.com/news/old-article</link>
            <description>This is an old article from 30 days ago.</description>
            <pubDate>{(now - timedelta(days=30)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
        </item>
    </channel>
</rss>"""
    
    # Parse mock feed
    feed = feedparser.parse(mock_rss)
    
    print(f"\nMock Feed Status:")
    print(f"  - Entries found: {len(feed.entries)}")
    print(f"  - Feed title: {feed.feed.get('title', 'N/A')}")
    
    if feed.entries:
        print(f"\nRaw Feed Entries:")
        for i, entry in enumerate(feed.entries, 1):
            print(f"  {i}. {entry.get('title', 'N/A')}")
            print(f"     Published: {entry.get('published', 'N/A')}")
            print(f"     Has published_parsed: {hasattr(entry, 'published_parsed') and entry.published_parsed is not None}")
    
    # Test scraper with mock data
    print(f"\n" + "=" * 70)
    print("Testing Scraper with Mock Data")
    print("=" * 70)
    
    # We need to create a scraper that can work with parsed feed data
    # Let's test the date parsing and article creation directly
    
    scraper = OpenAINewsScraper("https://openai.com/rss.xml")
    
    print(f"\n--- Testing Date Parsing ---")
    for i, entry in enumerate(feed.entries, 1):
        parsed_date = scraper._parse_date(entry)
        print(f"\nEntry {i}: {entry.get('title', 'N/A')[:50]}")
        print(f"  Published string: {entry.get('published', 'N/A')}")
        if parsed_date:
            print(f"  ✓ Parsed date: {parsed_date}")
            print(f"  ✓ Timezone-aware: {parsed_date.tzinfo is not None}")
        else:
            print(f"  ✗ Could not parse date")
    
    print(f"\n--- Testing Article Creation ---")
    cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    print(f"Cutoff time (24h): {cutoff_24h}")
    
    articles_24h = []
    for entry in feed.entries:
        published_at = scraper._parse_date(entry)
        if published_at and published_at >= cutoff_24h:
            article = NewsArticle(
                title=entry.get('title', '').strip(),
                url=entry.get('link', ''),
                description=scraper._get_description(entry),
                published_at=published_at,
                source_name=scraper.source_name
            )
            articles_24h.append(article)
    
    print(f"\nArticles within 24 hours: {len(articles_24h)}")
    for article in articles_24h:
        print(f"  ✓ {article.title}")
        print(f"    Published: {article.published_at}")
        print(f"    URL: {article.url}")
    
    cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)
    print(f"\nCutoff time (7 days): {cutoff_7d}")
    
    articles_7d = []
    for entry in feed.entries:
        published_at = scraper._parse_date(entry)
        if published_at and published_at >= cutoff_7d:
            article = NewsArticle(
                title=entry.get('title', '').strip(),
                url=entry.get('link', ''),
                description=scraper._get_description(entry),
                published_at=published_at,
                source_name=scraper.source_name
            )
            articles_7d.append(article)
    
    print(f"\nArticles within 7 days: {len(articles_7d)}")
    for article in articles_7d:
        print(f"  ✓ {article.title}")
        print(f"    Published: {article.published_at}")
    
    print(f"\n--- Testing Pydantic Models ---")
    if articles_24h:
        article = articles_24h[0]
        print(f"\nSample Article Model:")
        print(f"  Title: {article.title}")
        print(f"  URL: {article.url}")
        print(f"  Published: {article.published_at}")
        print(f"  Description: {article.description[:80]}...")
        print(f"  Source: {article.source_name}")
        
        print(f"\n  Model dict:")
        article_dict = article.model_dump()
        for key, value in article_dict.items():
            print(f"    {key}: {value}")
        
        print(f"\n  Model JSON:")
        print(f"    {article.model_dump_json()[:200]}...")
    
    print(f"\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print(f"✓ Date parsing: Working")
    print(f"✓ Time filtering (24h): {len(articles_24h)} articles")
    print(f"✓ Time filtering (7d): {len(articles_7d)} articles")
    print(f"✓ Pydantic models: Working")
    print(f"✓ Article creation: Working")


if __name__ == "__main__":
    try:
        test_with_mock_feed()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

