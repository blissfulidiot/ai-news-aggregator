"""Test date handling in OpenAI news scraper"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.openai_news_scraper import OpenAINewsScraper, NewsArticle
import feedparser


def test_date_parsing():
    """Test parsing dates from RSS entries"""
    print("=" * 60)
    print("Testing Date Parsing")
    print("=" * 60)
    
    scraper = OpenAINewsScraper("https://example.com/rss.xml")
    
    # Create mock RSS entry with different date formats
    test_cases = [
        {
            'name': 'Entry with published_parsed',
            'entry': type('obj', (object,), {
                'published_parsed': (2024, 1, 15, 10, 30, 0, 0, 0, 0),
                'title': 'Test Article 1',
                'link': 'https://example.com/article1',
                'summary': 'Test description'
            })()
        },
        {
            'name': 'Entry with published string',
            'entry': type('obj', (object,), {
                'published': 'Mon, 15 Jan 2024 10:30:00 GMT',
                'title': 'Test Article 2',
                'link': 'https://example.com/article2',
                'summary': 'Test description'
            })()
        },
        {
            'name': 'Entry with ISO format',
            'entry': type('obj', (object,), {
                'published': '2024-01-15T10:30:00Z',
                'title': 'Test Article 3',
                'link': 'https://example.com/article3',
                'summary': 'Test description'
            })()
        },
        {
            'name': 'Entry without date',
            'entry': type('obj', (object,), {
                'title': 'Test Article 4',
                'link': 'https://example.com/article4',
                'summary': 'Test description'
            })()
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        parsed_date = scraper._parse_date(test_case['entry'])
        if parsed_date:
            print(f"  Parsed: {parsed_date}")
            print(f"  Timezone: {parsed_date.tzinfo}")
            print(f"  UTC: {parsed_date.isoformat()}")
        else:
            print(f"  Could not parse date (expected for some cases)")


def test_time_filtering():
    """Test filtering articles by time window"""
    print("\n" + "=" * 60)
    print("Testing Time Filtering")
    print("=" * 60)
    
    scraper = OpenAINewsScraper("https://example.com/rss.xml")
    
    # Create articles with different dates
    now = datetime.now(timezone.utc)
    
    articles_data = [
        {'published_at': now - timedelta(hours=12), 'title': '12 hours ago'},
        {'published_at': now - timedelta(hours=25), 'title': '25 hours ago'},
        {'published_at': now - timedelta(hours=48), 'title': '48 hours ago'},
        {'published_at': now - timedelta(days=7), 'title': '7 days ago'},
    ]
    
    print(f"\nCurrent time (UTC): {now}")
    print(f"\nTest articles:")
    for article_data in articles_data:
        print(f"  - {article_data['title']}: {article_data['published_at']}")
    
    # Test 24-hour filter
    print(f"\n--- Testing 24-hour filter ---")
    cutoff_24h = now - timedelta(hours=24)
    print(f"Cutoff: {cutoff_24h}")
    
    filtered_24h = [a for a in articles_data if a['published_at'] >= cutoff_24h]
    print(f"Articles within 24 hours: {len(filtered_24h)}")
    for article in filtered_24h:
        print(f"  ✓ {article['title']}")
    
    # Test 48-hour filter
    print(f"\n--- Testing 48-hour filter ---")
    cutoff_48h = now - timedelta(hours=48)
    print(f"Cutoff: {cutoff_48h}")
    
    filtered_48h = [a for a in articles_data if a['published_at'] >= cutoff_48h]
    print(f"Articles within 48 hours: {len(filtered_48h)}")
    for article in filtered_48h:
        print(f"  ✓ {article['title']}")


def test_real_rss_dates(rss_url: str):
    """Test date parsing from a real RSS feed"""
    print("\n" + "=" * 60)
    print("Testing Real RSS Feed Dates")
    print("=" * 60)
    
    print(f"\nFetching RSS feed: {rss_url}")
    
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"RSS feed error: {feed.bozo_exception}")
        return
    
    if not feed.entries:
        print("No entries found in RSS feed")
        return
    
    print(f"\nFound {len(feed.entries)} entries")
    
    scraper = OpenAINewsScraper(rss_url)
    
    print("\n--- First 5 entries date parsing ---")
    for i, entry in enumerate(feed.entries[:5], 1):
        print(f"\nEntry {i}:")
        print(f"  Title: {entry.get('title', 'N/A')[:60]}")
        print(f"  Published string: {entry.get('published', 'N/A')}")
        print(f"  Published parsed: {entry.get('published_parsed', 'N/A')}")
        
        parsed_date = scraper._parse_date(entry)
        if parsed_date:
            print(f"  ✓ Parsed date: {parsed_date}")
            print(f"  ✓ Timezone: {parsed_date.tzinfo}")
            print(f"  ✓ ISO format: {parsed_date.isoformat()}")
            
            # Check if it's timezone-aware
            if parsed_date.tzinfo:
                print(f"  ✓ Timezone-aware: Yes")
            else:
                print(f"  ✗ Timezone-aware: No (should be fixed)")
        else:
            print(f"  ✗ Could not parse date")


def test_timezone_awareness():
    """Test that all dates are timezone-aware"""
    print("\n" + "=" * 60)
    print("Testing Timezone Awareness")
    print("=" * 60)
    
    scraper = OpenAINewsScraper("https://example.com/rss.xml")
    
    # Test with different date formats
    test_entries = [
        type('obj', (object,), {
            'published_parsed': (2024, 1, 15, 10, 30, 0, 0, 0, 0),
            'title': 'Test',
            'link': 'https://example.com/test',
            'summary': 'Test'
        })(),
        type('obj', (object,), {
            'published': 'Mon, 15 Jan 2024 10:30:00 +0000',
            'title': 'Test',
            'link': 'https://example.com/test',
            'summary': 'Test'
        })(),
        type('obj', (object,), {
            'published': '2024-01-15T10:30:00Z',
            'title': 'Test',
            'link': 'https://example.com/test',
            'summary': 'Test'
        })(),
    ]
    
    print("\nTesting date parsing for timezone awareness:")
    all_timezone_aware = True
    
    for i, entry in enumerate(test_entries, 1):
        parsed_date = scraper._parse_date(entry)
        if parsed_date:
            is_aware = parsed_date.tzinfo is not None
            print(f"\nEntry {i}:")
            print(f"  Parsed: {parsed_date}")
            print(f"  Timezone-aware: {is_aware}")
            
            if not is_aware:
                all_timezone_aware = False
                print(f"  ✗ ERROR: Date is not timezone-aware!")
            else:
                print(f"  ✓ OK: Date is timezone-aware")
    
    if all_timezone_aware:
        print("\n✓ All dates are timezone-aware!")
    else:
        print("\n✗ Some dates are not timezone-aware - needs fixing!")


def test_article_model_dates():
    """Test NewsArticle model with dates"""
    print("\n" + "=" * 60)
    print("Testing NewsArticle Model with Dates")
    print("=" * 60)
    
    now = datetime.now(timezone.utc)
    
    article = NewsArticle(
        title="Test Article",
        url="https://example.com/test",
        description="Test description",
        published_at=now,
        source_name="Test Source"
    )
    
    print(f"\nCreated article:")
    print(f"  Title: {article.title}")
    print(f"  Published at: {article.published_at}")
    print(f"  Published at type: {type(article.published_at)}")
    print(f"  Timezone-aware: {article.published_at.tzinfo is not None}")
    print(f"  ISO format: {article.published_at.isoformat()}")
    
    # Test serialization
    print(f"\nModel dict:")
    article_dict = article.model_dump()
    print(f"  published_at in dict: {article_dict.get('published_at')}")
    
    print(f"\nModel JSON:")
    article_json = article.model_dump_json()
    print(f"  published_at in JSON: {article_json[:200]}...")


if __name__ == "__main__":
    try:
        test_date_parsing()
        test_time_filtering()
        test_timezone_awareness()
        test_article_model_dates()
        
        # Test with a real RSS feed if available
        # You can uncomment and provide a valid RSS URL
        # test_real_rss_dates("https://example.com/rss.xml")
        
        print("\n" + "=" * 60)
        print("All date tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

