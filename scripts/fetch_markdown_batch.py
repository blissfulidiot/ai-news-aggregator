"""Script to fetch markdown content for articles in the database that don't have it"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import ArticleRepository
from app.scrapers.openai_news_scraper import get_url_content_as_markdown


def fetch_markdown_batch(limit: int = None, batch_size: int = 10):
    """
    Fetch markdown content for articles that don't have it
    
    Args:
        limit: Maximum number of articles to process (None for all)
        batch_size: Number of articles to process before showing progress
    """
    print("=" * 70)
    print("Fetching Markdown Content for Articles")
    print("=" * 70)
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get articles without markdown
        articles = ArticleRepository.get_without_markdown(db, limit=limit)
        total_count = len(articles)
        
        if total_count == 0:
            print("\n✓ All articles already have markdown content!")
            return
        
        print(f"\nFound {total_count} articles without markdown content")
        print(f"Processing in batches of {batch_size}...\n")
        
        successful = 0
        failed = 0
        
        for i, article in enumerate(articles, 1):
            try:
                print(f"[{i}/{total_count}] Processing: {article.title[:60]}...")
                print(f"  URL: {article.url}")
                
                # Fetch markdown content
                markdown_content = get_url_content_as_markdown(article.url)
                
                if markdown_content:
                    # Update article in database
                    ArticleRepository.update_markdown(db, article.id, markdown_content)
                    successful += 1
                    print(f"  ✓ Successfully fetched markdown ({len(markdown_content)} chars)")
                else:
                    failed += 1
                    print(f"  ✗ Failed to fetch markdown content")
                
                # Show progress every batch_size articles
                if i % batch_size == 0:
                    print(f"\n  Progress: {successful} successful, {failed} failed\n")
                    
            except Exception as e:
                failed += 1
                print(f"  ✗ Error: {e}")
                db.rollback()  # Rollback on error
                continue
        
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print(f"Total processed: {total_count}")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Main entry point"""
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit value: {sys.argv[1]}. Processing all articles.")
    
    fetch_markdown_batch(limit=limit)


if __name__ == "__main__":
    main()

