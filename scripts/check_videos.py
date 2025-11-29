"""Script to check videos in database and their transcript status"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import VideoRepository, SourceRepository
from app.database.models import SourceType

def check_videos():
    """Check videos in database and their transcript status"""
    print("=" * 70)
    print("Checking Videos in Database")
    print("=" * 70)
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get CNBC source
        cnbc_source = SourceRepository.get_by_url(db, "https://www.youtube.com/@CNBCtelevision")
        if not cnbc_source:
            print("\n✗ CNBC source not found in database")
            print("You may need to run the aggregator first to scrape videos.")
            return
        
        print(f"\nFound CNBC source: {cnbc_source.name} (ID: {cnbc_source.id})")
        
        # Get all videos from CNBC
        videos = VideoRepository.get_by_source(db, cnbc_source.id)
        print(f"\nTotal CNBC videos in database: {len(videos)}")
        
        if len(videos) == 0:
            print("\nNo videos found for CNBC channel.")
            print("You may need to run the aggregator to scrape videos first:")
            print("  python scripts/run_aggregator.py")
            return
        
        # Check transcript status
        with_transcript = [v for v in videos if v.transcript and v.transcript != "transcript is not available"]
        without_transcript = [v for v in videos if v.transcript is None]
        unavailable = [v for v in videos if v.transcript == "transcript is not available"]
        
        print(f"\nTranscript Status:")
        print(f"  ✓ With transcript: {len(with_transcript)}")
        print(f"  ✗ Without transcript (NULL): {len(without_transcript)}")
        print(f"  ✗ Unavailable (placeholder): {len(unavailable)}")
        
        # Show sample videos
        print(f"\n" + "=" * 70)
        print("Sample Videos (first 10)")
        print("=" * 70)
        for i, video in enumerate(videos[:10], 1):
            transcript_status = "✓ Has transcript" if video.transcript and video.transcript != "transcript is not available" else ("✗ Unavailable" if video.transcript == "transcript is not available" else "✗ No transcript")
            print(f"\n{i}. {video.title[:60]}...")
            print(f"   Video ID: {video.video_id}")
            print(f"   Published: {video.published_at}")
            print(f"   Status: {transcript_status}")
            if video.transcript and video.transcript != "transcript is not available":
                print(f"   Transcript length: {len(video.transcript)} chars")
        
        # Show videos without transcripts
        if without_transcript:
            print(f"\n" + "=" * 70)
            print(f"Videos Without Transcripts ({len(without_transcript)})")
            print("=" * 70)
            print("Run this to fetch transcripts:")
            print("  python scripts/fetch_transcripts_batch.py")
            print("\nFirst 5 videos needing transcripts:")
            for i, video in enumerate(without_transcript[:5], 1):
                print(f"  {i}. {video.title[:60]}... (ID: {video.video_id})")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_videos()

