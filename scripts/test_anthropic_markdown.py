"""Test markdown conversion for Anthropic articles"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.anthropic_news_scraper import (
    AnthropicNewsScraper,
    get_url_content_as_markdown,
    get_anthropic_articles
)


def test_markdown_conversion():
    """Test markdown conversion with Anthropic articles"""
    print("=" * 70)
    print("Testing Anthropic Markdown Conversion")
    print("=" * 70)
    
    scraper = AnthropicNewsScraper()
    
    # Get some recent articles
    print("\nFetching recent articles...")
    articles = scraper.get_articles(hours=24 * 30)  # Last 30 days
    
    if not articles:
        print("No articles found. Testing with a known URL...")
        test_url = "https://www.anthropic.com/news/claude-opus-4-5"
    else:
        # Use the first article
        test_url = articles[0].url
        print(f"\nTesting with article: {articles[0].title}")
        print(f"URL: {test_url}")
    
    print(f"\n--- Testing Class Method ---")
    try:
        markdown = scraper.get_content_as_markdown(test_url)
        
        if markdown:
            print(f"✓ Successfully converted to markdown")
            print(f"  Length: {len(markdown)} characters")
            print(f"  Lines: {len(markdown.split(chr(10)))}")
            
            print(f"\nFirst 500 characters:")
            print("-" * 70)
            print(markdown[:500])
            print("-" * 70)
            
            # Show some stats
            lines = markdown.split('\n')
            non_empty = [l for l in lines if l.strip()]
            print(f"\nMarkdown stats:")
            print(f"  Total lines: {len(lines)}")
            print(f"  Non-empty lines: {len(non_empty)}")
            print(f"  Headers (#): {len([l for l in lines if l.strip().startswith('#')])}")
        else:
            print("✗ Failed to convert to markdown")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test convenience function
    print(f"\n--- Testing Convenience Function ---")
    try:
        markdown = get_url_content_as_markdown(test_url)
        
        if markdown:
            print(f"✓ Successfully converted using convenience function")
            print(f"  Length: {len(markdown)} characters")
        else:
            print("✗ Failed to convert using convenience function")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_articles():
    """Test converting multiple articles"""
    print("\n" + "=" * 70)
    print("Testing Multiple Articles")
    print("=" * 70)
    
    scraper = AnthropicNewsScraper()
    articles = scraper.get_articles(hours=24 * 30)
    
    if not articles:
        print("No articles found to test")
        return
    
    print(f"\nTesting markdown conversion for first 3 articles:")
    
    for i, article in enumerate(articles[:3], 1):
        print(f"\n{i}. [{article.feed_type}] {article.title}")
        print(f"   URL: {article.url}")
        
        try:
            markdown = scraper.get_content_as_markdown(article.url)
            if markdown:
                print(f"   ✓ Converted: {len(markdown)} characters")
            else:
                print(f"   ✗ Failed to convert")
        except Exception as e:
            print(f"   ✗ Error: {e}")


if __name__ == "__main__":
    try:
        test_markdown_conversion()
        test_multiple_articles()
        
        print("\n" + "=" * 70)
        print("All tests completed!")
        print("=" * 70)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

