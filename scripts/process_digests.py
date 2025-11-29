"""Script to process articles and videos and generate digests"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import (
    ArticleRepository, VideoRepository, DigestRepository
)
from app.agents.digest_agent import DigestAgent


def process_digests(limit: int = None, batch_size: int = 10):
    """
    Process articles and videos to generate digests
    
    Args:
        limit: Maximum number of items to process (None for all)
        batch_size: Number of items to process before showing progress
    """
    print("=" * 70)
    print("Processing Digests")
    print("=" * 70)
    
    # Initialize digest agent
    try:
        agent = DigestAgent()
        print("✓ Digest agent initialized")
    except Exception as e:
        print(f"✗ Error initializing digest agent: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")
        return
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get articles without digests
        articles = ArticleRepository.get_all(db, limit=limit)
        videos = VideoRepository.get_all(db, limit=limit)
        
        # Filter out items that already have digests
        articles_to_process = [a for a in articles if not DigestRepository.exists_by_url(db, a.url)]
        videos_to_process = [v for v in videos if not DigestRepository.exists_by_url(db, v.url)]
        
        total_count = len(articles_to_process) + len(videos_to_process)
        
        if total_count == 0:
            print("\n✓ All items already have digests!")
            return
        
        print(f"\nFound {len(articles_to_process)} articles and {len(videos_to_process)} videos to process")
        print(f"Processing in batches of {batch_size}...\n")
        
        successful = 0
        failed = 0
        
        # Helper function to process a single item
        def process_item(item, item_type: str, item_id: int):
            """Process a single article or video"""
            nonlocal successful, failed
            processed = successful + failed + 1
            
            try:
                print(f"[{processed}/{total_count}] Processing {item_type}: {item.title[:60]}...")
                print(f"  URL: {item.url}")
                
                # Generate digest based on type
                if item_type == "article":
                    digest_output = agent.generate_digest_from_article(
                        title=item.title,
                        description=item.description or "",
                        markdown_content=item.markdown_content
                    )
                    DigestRepository.create(
                        db, url=item.url, title=digest_output.title,
                        summary=digest_output.summary, content_type="article",
                        article_id=item_id, published_at=item.published_at
                    )
                else:  # video
                    digest_output = agent.generate_digest_from_video(
                        title=item.title,
                        description=item.description or "",
                        transcript=item.transcript
                    )
                    DigestRepository.create(
                        db, url=item.url, title=digest_output.title,
                        summary=digest_output.summary, content_type="video",
                        video_id=item_id, published_at=item.published_at
                    )
                
                successful += 1
                print(f"  ✓ Generated digest: {digest_output.title[:60]}...")
                
                # Show progress every batch_size items
                if processed % batch_size == 0:
                    print(f"\n  Progress: {successful} successful, {failed} failed\n")
                    
            except Exception as e:
                failed += 1
                print(f"  ✗ Error: {e}")
                db.rollback()
        
        # Process articles
        for article in articles_to_process:
            process_item(article, "article", article.id)
        
        # Process videos
        for video in videos_to_process:
            process_item(video, "video", video.id)
        
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
            print(f"Invalid limit value: {sys.argv[1]}. Processing all items.")
    
    process_digests(limit=limit)


if __name__ == "__main__":
    main()

