"""Test script for Anthropic news scraper"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.anthropic_news_scraper import (
    AnthropicNewsScraper,
    get_anthropic_articles,
    get_anthropic_articles_by_feed
)


def test_all_feeds():
    """Test getting articles from all feeds"""
    print("=" * 70)
    print("Testing All Anthropic Feeds Combined")
    print("=" * 70)
    
    scraper = AnthropicNewsScraper()
    articles = scraper.get_articles(hours=24 * 30)  # Last 30 days
    
    print(f"\nTotal articles found: {len(articles)}")
    
    # Group by feed type
    by_feed = {}
    for article in articles:
        feed_type = article.feed_type
        if feed_type not in by_feed:
            by_feed[feed_type] = []
        by_feed[feed_type].append(article)
    
    print(f"\nArticles by feed type:")
    for feed_type, feed_articles in sorted(by_feed.items()):
        print(f"  {feed_type}: {len(feed_articles)} articles")
    
    print(f"\n--- Sample Articles (first 10) ---")
    for i, article in enumerate(articles[:10], 1):
        print(f"\n{i}. {article.title}")
        print(f"   Feed: {article.feed_type}")
        print(f"   URL: {article.url}")
        print(f"   Published: {article.published_at}")
        print(f"   Description: {article.description[:100]}...")


def test_individual_feeds():
    """Test getting articles from individual feeds"""
    print("\n" + "=" * 70)
    print("Testing Individual Feeds")
    print("=" * 70)
    
    scraper = AnthropicNewsScraper()
    
    for feed_type in ["news", "engineering", "research", "red"]:
        print(f"\n--- {feed_type.upper()} Feed ---")
        try:
            articles = scraper.get_articles_by_feed(feed_type, hours=24 * 30)
            print(f"Found {len(articles)} articles")
            
            if articles:
                print(f"\nSample articles:")
                for i, article in enumerate(articles[:3], 1):
                    print(f"  {i}. {article.title}")
                    print(f"     Published: {article.published_at}")
                    print(f"     URL: {article.url[:60]}...")
        except Exception as e:
            print(f"Error: {e}")


def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "=" * 70)
    print("Testing Convenience Functions")
    print("=" * 70)
    
    # Test get_anthropic_articles
    print("\n--- get_anthropic_articles() ---")
    articles = get_anthropic_articles(hours=24 * 7)
    print(f"Found {len(articles)} articles from last 7 days")
    
    if articles:
        print(f"\nFirst article:")
        article = articles[0]
        print(f"  Title: {article.title}")
        print(f"  Feed: {article.feed_type}")
        print(f"  Published: {article.published_at}")
    
    # Test get_anthropic_articles_by_feed
    print("\n--- get_anthropic_articles_by_feed('engineering') ---")
    eng_articles = get_anthropic_articles_by_feed("engineering", hours=24 * 30)
    print(f"Found {len(eng_articles)} engineering articles")


def test_date_filtering():
    """Test date filtering"""
    print("\n" + "=" * 70)
    print("Testing Date Filtering")
    print("=" * 70)
    
    scraper = AnthropicNewsScraper()
    
    for hours in [24, 24 * 7, 24 * 30]:
        articles = scraper.get_articles(hours=hours)
        print(f"\nLast {hours // 24} day(s): {len(articles)} articles")
        
        if articles:
            print(f"  Oldest: {articles[-1].published_at}")
            print(f"  Newest: {articles[0].published_at}")


if __name__ == "__main__":
    try:
        test_all_feeds()
        test_individual_feeds()
        test_convenience_functions()
        test_date_filtering()
        
        print("\n" + "=" * 70)
        print("All tests completed!")
        print("=" * 70)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

