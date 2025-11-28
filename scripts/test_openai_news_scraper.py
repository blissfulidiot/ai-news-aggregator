"""Test script for OpenAI news scraper"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.openai_news_scraper import OpenAINewsScraper, get_openai_articles


def test_rss_structure(rss_url: str):
    """Explore RSS feed structure"""
    print("=" * 60)
    print(f"Exploring RSS Feed: {rss_url}")
    print("=" * 60)
    
    import feedparser
    feed = feedparser.parse(rss_url)
    
    print(f"\nFeed Title: {feed.feed.get('title', 'N/A')}")
    print(f"Feed Link: {feed.feed.get('link', 'N/A')}")
    print(f"Entries: {len(feed.entries)}")
    
    if feed.entries:
        entry = feed.entries[0]
        print(f"\nFirst Entry Keys: {list(entry.keys())}")
        print(f"Title: {entry.get('title', 'N/A')}")
        print(f"Link: {entry.get('link', 'N/A')}")
        print(f"Published: {entry.get('published', 'N/A')}")
        print(f"Description: {entry.get('description', 'N/A')[:100]}...")


def test_get_articles(rss_url: str):
    """Test getting articles"""
    print("\n" + "=" * 60)
    print("Testing get_articles()")
    print("=" * 60)
    
    scraper = OpenAINewsScraper(rss_url)
    articles = scraper.get_articles(hours=24 * 7)  # Last 7 days
    
    print(f"\nFound {len(articles)} articles from last 7 days\n")
    
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article.title}")
        print(f"   URL: {article.url}")
        print(f"   Published: {article.published_at}")
        print(f"   Description: {article.description[:100]}...")
        print()


def test_convenience_function(rss_url: str):
    """Test convenience function"""
    print("\n" + "=" * 60)
    print("Testing convenience function")
    print("=" * 60)
    
    articles = get_openai_articles(rss_url, hours=24 * 3)
    
    print(f"\nFound {len(articles)} articles from last 3 days\n")
    
    for i, article in enumerate(articles[:3], 1):
        print(f"{i}. {article.title}")
        print(f"   Published: {article.published_at}")
        print()


if __name__ == "__main__":
    # Test with OpenAI RSS feed (user should provide actual URL)
    rss_url = "https://openai.com/rss.xml"
    
    try:
        test_rss_structure(rss_url)
        test_get_articles(rss_url)
        test_convenience_function(rss_url)
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
