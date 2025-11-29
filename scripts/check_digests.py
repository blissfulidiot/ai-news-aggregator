"""Script to check digests in database"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import DigestRepository

def check_digests():
    """Check digests in database"""
    print("=" * 70)
    print("Checking Digests in Database")
    print("=" * 70)
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get all digests
        digests = DigestRepository.get_all(db)
        total_count = len(digests)
        
        print(f"\nTotal digests in database: {total_count}")
        
        if total_count == 0:
            print("\nNo digests found in database.")
            return
        
        # Group by content type
        articles = [d for d in digests if d.content_type == "article"]
        videos = [d for d in digests if d.content_type == "video"]
        
        print(f"\nBreakdown:")
        print(f"  Articles: {len(articles)}")
        print(f"  Videos: {len(videos)}")
        
        # Show sample digests
        print(f"\n" + "=" * 70)
        print("Sample Digests (first 10)")
        print("=" * 70)
        for i, digest in enumerate(digests[:10], 1):
            print(f"\n{i}. [{digest.content_type.upper()}] {digest.title}")
            print(f"   Summary: {digest.summary[:150]}...")
            print(f"   URL: {digest.url[:70]}...")
            if digest.article_id:
                print(f"   Article ID: {digest.article_id}")
            if digest.video_id:
                print(f"   Video ID: {digest.video_id}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_digests()

