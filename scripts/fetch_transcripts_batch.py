"""Script to fetch transcripts for videos in the database that don't have them"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import VideoRepository
from app.services.youtube_service import YouTubeService
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Constant for unavailable transcripts
TRANSCRIPT_UNAVAILABLE = "transcript is not available"


def fetch_transcripts_batch(limit: int = None, batch_size: int = 10):
    """
    Fetch transcripts for videos that don't have them
    
    Args:
        limit: Maximum number of videos to process (None for all)
        batch_size: Number of videos to process before showing progress
    """
    print("=" * 70)
    print("Fetching Transcripts for Videos")
    print("=" * 70)
    
    # Get database session
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get videos without transcripts
        videos = VideoRepository.get_without_transcript(db, limit=limit)
        total_count = len(videos)
        
        if total_count == 0:
            print("\n✓ All videos already have transcripts!")
            return
        
        print(f"\nFound {total_count} videos without transcripts")
        print(f"Processing in batches of {batch_size}...\n")
        
        youtube_service = YouTubeService()
        successful = 0
        failed = 0
        unavailable = 0
        
        for i, video in enumerate(videos, 1):
            try:
                print(f"[{i}/{total_count}] Processing: {video.title[:60]}...")
                print(f"  Video ID: {video.video_id}")
                print(f"  URL: {video.url}")
                
                # Fetch transcript
                transcript_obj = youtube_service.get_transcript(video.video_id)
                
                if transcript_obj and transcript_obj.text:
                    # Update video in database
                    VideoRepository.update_transcript(db, video.id, transcript_obj.text)
                    successful += 1
                    print(f"  ✓ Successfully fetched transcript ({len(transcript_obj.text)} chars)")
                else:
                    # Transcript not available - store placeholder to prevent retry loops
                    VideoRepository.update_transcript(db, video.id, TRANSCRIPT_UNAVAILABLE)
                    unavailable += 1
                    print(f"  ✗ Transcript not available (stored placeholder)")
                
                # Show progress every batch_size videos
                if i % batch_size == 0:
                    print(f"\n  Progress: {successful} successful, {unavailable} unavailable, {failed} errors\n")
                    
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                # Transcript is explicitly disabled or not found - store placeholder
                VideoRepository.update_transcript(db, video.id, TRANSCRIPT_UNAVAILABLE)
                unavailable += 1
                print(f"  ✗ Transcript not available: {type(e).__name__}")
                db.commit()  # Commit the placeholder
                continue
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
        print(f"✗ Unavailable: {unavailable}")
        print(f"✗ Errors: {failed}")
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
            print(f"Invalid limit value: {sys.argv[1]}. Processing all videos.")
    
    fetch_transcripts_batch(limit=limit)


if __name__ == "__main__":
    main()

