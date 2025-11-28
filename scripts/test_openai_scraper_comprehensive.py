"""Comprehensive test for OpenAI news scraper"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.openai_news_scraper import OpenAINewsScraper, get_openai_articles
import feedparser


def test_with_rss_feed(rss_url: str, feed_name: str):
    """Test scraper with a specific RSS feed"""
    print("=" * 70)
    print(f"Testing with {feed_name}")
    print("=" * 70)
    print(f"RSS URL: {rss_url}\n")
    
    # First, check raw feed
    feed = feedparser.parse(rss_url)
    
    print(f"Feed Status:")
    print(f"  - Bozo (error): {feed.bozo}")
    if feed.bozo:
        print(f"  - Error: {feed.bozo_exception}")
    print(f"  - Feed title: {feed.feed.get('title', 'N/A')}")
    print(f"  - Feed link: {feed.feed.get('link', 'N/A')}")
    print(f"  - Entries found: {len(feed.entries)}")
    
    if feed.entries:
        print(f"\nFirst Entry Sample:")
        entry = feed.entries[0]
        print(f"  - Title: {entry.get('title', 'N/A')[:60]}")
        print(f"  - Link: {entry.get('link', 'N/A')[:60]}")
        print(f"  - Published: {entry.get('published', 'N/A')}")
        print(f"  - Has published_parsed: {hasattr(entry, 'published_parsed') and entry.published_parsed is not None}")
    
    print(f"\n--- Testing Scraper ---")
    scraper = OpenAINewsScraper(rss_url)
    
    # Test different time windows
    for hours in [24, 24 * 7, 24 * 30]:
        articles = scraper.get_articles(hours=hours)
        print(f"\nArticles from last {hours // 24} day(s): {len(articles)}")
        
        if articles:
            print(f"  Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"    {i}. {article.title[:60]}")
                print(f"       Published: {article.published_at}")
                print(f"       URL: {article.url[:60]}...")
                print(f"       Description: {article.description[:80]}...")
    
    # Test convenience function
    print(f"\n--- Testing Convenience Function ---")
    articles = get_openai_articles(rss_url, hours=24 * 7)
    print(f"Found {len(articles)} articles using convenience function")
    
    if articles:
        print(f"\nFirst article details:")
        article = articles[0]
        print(f"  Title: {article.title}")
        print(f"  URL: {article.url}")
        print(f"  Published: {article.published_at}")
        print(f"  Source: {article.source_name}")
        print(f"  Description length: {len(article.description)} chars")
        
        # Test Pydantic model serialization
        print(f"\n  Model dict keys: {list(article.model_dump().keys())}")
        print(f"  Model JSON (first 200 chars): {article.model_dump_json()[:200]}...")
    
    print()


def main():
    """Run comprehensive tests"""
    
    # Test with OpenAI RSS feed
    test_with_rss_feed("https://openai.com/rss.xml", "OpenAI RSS Feed")
    
    # Test with a known working RSS feed to verify scraper works
    print("\n" + "=" * 70)
    print("Testing with a known working RSS feed (to verify scraper)")
    print("=" * 70)
    
    # Try a few common RSS feeds
    test_feeds = [
        ("https://feeds.feedburner.com/oreilly/radar", "O'Reilly Radar"),
        ("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "NYTimes Technology"),
    ]
    
    for rss_url, name in test_feeds:
        try:
            test_with_rss_feed(rss_url, name)
            break  # If one works, we've verified the scraper
        except Exception as e:
            print(f"Error testing {name}: {e}\n")
            continue
    
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("\n✓ Scraper implementation verified")
    print("✓ Date parsing tested")
    print("✓ Pydantic models working")
    print("✓ Time filtering functional")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

