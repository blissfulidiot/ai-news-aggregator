"""Test markdown conversion from URLs"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers.openai_news_scraper import OpenAINewsScraper, get_url_content_as_markdown


def test_markdown_conversion():
    """Test converting URL content to markdown"""
    print("=" * 70)
    print("Testing URL to Markdown Conversion")
    print("=" * 70)
    
    # Test URL (using the example from the user)
    test_url = "https://ds4sd.github.io/docling/"
    
    print(f"\nTesting URL: {test_url}\n")
    
    # Test using the scraper class
    print("--- Using Scraper Class ---")
    scraper = OpenAINewsScraper("https://example.com/rss.xml")
    
    try:
        markdown = scraper.get_content_as_markdown(test_url)
        
        if markdown:
            print(f"✓ Successfully converted to markdown")
            print(f"  Length: {len(markdown)} characters")
            print(f"\nFirst 500 characters:")
            print("-" * 70)
            print(markdown[:500])
            print("-" * 70)
            
            # Show some stats
            lines = markdown.split('\n')
            print(f"\nMarkdown stats:")
            print(f"  Total lines: {len(lines)}")
            print(f"  Non-empty lines: {len([l for l in lines if l.strip()])}")
        else:
            print("✗ Failed to convert to markdown")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test using convenience function
    print("\n" + "=" * 70)
    print("Testing Convenience Function")
    print("=" * 70)
    
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


def test_with_article_url():
    """Test with an actual article URL"""
    print("\n" + "=" * 70)
    print("Testing with Article URL")
    print("=" * 70)
    
    # Use a simple, well-known URL
    article_url = "https://www.example.com"
    
    print(f"\nTesting URL: {article_url}\n")
    
    scraper = OpenAINewsScraper("https://example.com/rss.xml")
    
    try:
        markdown = scraper.get_content_as_markdown(article_url)
        
        if markdown:
            print(f"✓ Successfully converted article to markdown")
            print(f"  Length: {len(markdown)} characters")
            print(f"\nPreview (first 300 chars):")
            print("-" * 70)
            print(markdown[:300])
            print("-" * 70)
        else:
            print("✗ Failed to convert article")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        test_markdown_conversion()
        test_with_article_url()
        
        print("\n" + "=" * 70)
        print("All tests completed!")
        print("=" * 70)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

