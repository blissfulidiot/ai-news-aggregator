#!/usr/bin/env python3
"""Test script to verify transcripts are returned correctly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.youtube_service import YouTubeService, ChannelVideo, Transcript


def test_transcript_model():
    """Test that transcript model is returned correctly"""
    print("=" * 60)
    print("Testing Transcript Model")
    print("=" * 60)
    
    service = YouTubeService()
    
    # Test with a known video that has transcripts
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\nFetching transcript for: {video_url}")
    
    transcript = service.get_transcript(video_url)
    
    if transcript:
        print(f"✓ Success! Got Transcript model")
        print(f"  Type: {type(transcript)}")
        print(f"  Is Transcript instance: {isinstance(transcript, Transcript)}")
        print(f"  Text length: {len(transcript.text)} characters")
        print(f"  Text preview: {transcript.text[:200]}...")
        print(f"\n  Model fields: {transcript.model_fields.keys()}")
        print(f"  Model dict: {transcript.model_dump().keys()}")
    else:
        print("✗ No transcript returned")


def test_channel_videos_with_transcripts():
    """Test that channel videos include transcripts"""
    print("\n" + "=" * 60)
    print("Testing Channel Videos with Transcripts")
    print("=" * 60)
    
    service = YouTubeService()
    
    print("\nFetching videos from CNBCtelevision...")
    videos = service.get_channel_videos("CNBCtelevision", hours=24)
    
    print(f"Found {len(videos)} videos\n")
    
    videos_with_transcripts = 0
    videos_without_transcripts = 0
    
    for i, video in enumerate(videos[:5], 1):
        print(f"{i}. {video.title}")
        print(f"   Type: {type(video)}")
        print(f"   Is ChannelVideo instance: {isinstance(video, ChannelVideo)}")
        print(f"   URL: {video.url}")
        
        if video.transcript:
            videos_with_transcripts += 1
            print(f"   ✓ Has transcript ({len(video.transcript)} chars)")
            print(f"   Preview: {video.transcript[:100]}...")
        else:
            videos_without_transcripts += 1
            print(f"   ✗ No transcript available")
        print()
    
    print(f"\nSummary:")
    print(f"  Videos with transcripts: {videos_with_transcripts}")
    print(f"  Videos without transcripts: {videos_without_transcripts}")


def test_model_validation():
    """Test Pydantic model validation"""
    print("\n" + "=" * 60)
    print("Testing Model Validation")
    print("=" * 60)
    
    # Test Transcript model
    print("\n1. Testing Transcript model:")
    try:
        transcript = Transcript(text="This is a test transcript")
        print(f"   ✓ Created Transcript: {transcript.text[:50]}...")
        print(f"   Model dict: {transcript.model_dump()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test ChannelVideo model
    print("\n2. Testing ChannelVideo model:")
    try:
        from datetime import datetime, timezone
        video = ChannelVideo(
            title="Test Video",
            url="https://www.youtube.com/watch?v=test123",
            video_id="test123",
            published_at=datetime.now(timezone.utc),
            description="Test description",
            transcript="Test transcript text",
            channel_name="Test Channel",
            channel_id="UCtest123"
        )
        print(f"   ✓ Created ChannelVideo: {video.title}")
        print(f"   Has transcript: {video.transcript is not None}")
        print(f"   Model fields: {list(video.model_fields.keys())}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == "__main__":
    test_transcript_model()
    test_channel_videos_with_transcripts()
    test_model_validation()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

