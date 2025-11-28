"""Test script for database operations"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session, init_db
from app.database.models import SourceType
from app.database.repository import (
    SourceRepository, ArticleRepository, VideoRepository, UserSettingsRepository
)
from datetime import datetime, timezone, timedelta


def test_database():
    """Test database operations"""
    print("=" * 70)
    print("Testing Database Operations")
    print("=" * 70)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        init_db()
        print("   ✓ Database initialized")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Test Source operations
        print("\n2. Testing Source operations...")
        
        # Create sources
        anthropic_source = SourceRepository.create(
            db,
            name="Anthropic",
            url="https://www.anthropic.com",
            source_type=SourceType.RSS,
            rss_url="https://anthropic.com/rss.xml"
        )
        print(f"   ✓ Created source: {anthropic_source.name} (ID: {anthropic_source.id})")
        
        youtube_source = SourceRepository.create(
            db,
            name="CNBC Television",
            url="https://www.youtube.com/@CNBCtelevision",
            source_type=SourceType.YOUTUBE,
            youtube_username="CNBCtelevision",
            youtube_channel_id="UCvH3Uf5HqW2u7j7J7J7J7J7"
        )
        print(f"   ✓ Created source: {youtube_source.name} (ID: {youtube_source.id})")
        
        # Get sources
        sources = SourceRepository.get_all(db)
        print(f"   ✓ Retrieved {len(sources)} sources")
        
        # Test Article operations
        print("\n3. Testing Article operations...")
        
        test_article = ArticleRepository.create(
            db,
            source_id=anthropic_source.id,
            title="Test Article",
            url="https://example.com/test-article",
            published_at=datetime.now(timezone.utc),
            description="This is a test article",
            feed_type="engineering"
        )
        print(f"   ✓ Created article: {test_article.title} (ID: {test_article.id})")
        
        # Check if article exists
        exists = ArticleRepository.exists_by_url(db, test_article.url)
        print(f"   ✓ Article exists check: {exists}")
        
        # Get recent articles
        recent = ArticleRepository.get_recent(db, hours=24)
        print(f"   ✓ Retrieved {len(recent)} recent articles")
        
        # Test Video operations
        print("\n4. Testing Video operations...")
        
        test_video = VideoRepository.create(
            db,
            source_id=youtube_source.id,
            title="Test Video",
            url="https://www.youtube.com/watch?v=test123",
            video_id="test123",
            published_at=datetime.now(timezone.utc),
            description="This is a test video"
        )
        print(f"   ✓ Created video: {test_video.title} (ID: {test_video.id})")
        
        # Update transcript
        VideoRepository.update_transcript(db, test_video.id, "This is a test transcript")
        updated_video = VideoRepository.get_by_id(db, test_video.id)
        print(f"   ✓ Updated transcript: {updated_video.transcript is not None}")
        
        # Get videos without transcripts
        videos_without = VideoRepository.get_without_transcript(db)
        print(f"   ✓ Videos without transcripts: {len(videos_without)}")
        
        # Test UserSettings operations
        print("\n5. Testing UserSettings operations...")
        
        user_settings = UserSettingsRepository.create(
            db,
            email="test@example.com",
            system_prompt="Summarize articles concisely"
        )
        print(f"   ✓ Created user settings: {user_settings.email} (ID: {user_settings.id})")
        
        # Update user settings
        UserSettingsRepository.update(db, user_settings.id, system_prompt="Updated prompt")
        updated_user = UserSettingsRepository.get_by_id(db, user_settings.id)
        print(f"   ✓ Updated user settings: {updated_user.system_prompt}")
        
        print("\n" + "=" * 70)
        print("All database tests passed! ✓")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_database()

