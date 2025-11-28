#!/usr/bin/env python3
"""Test script for unified YouTube service"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.youtube_service import YouTubeService, get_channel_videos, get_transcript


def test_channel_scraping():
    """Test channel video scraping"""
    print("=" * 60)
    print("1. Testing Channel Video Scraping")
    print("=" * 60)
    
    service = YouTubeService()
    
    # Test single channel
    print("\nFetching videos from CNBCtelevision...")
    videos = service.get_channel_videos("CNBCtelevision", hours=24)
    
    print(f"Found {len(videos)} videos\n")
    for i, video in enumerate(videos[:3], 1):
        print(f"{i}. {video.title}")
        print(f"   URL: {video.url}")
        print(f"   Published: {video.published_at}")
        print(f"   Transcript: {'Yes' if video.transcript else 'No'}")
        if video.transcript:
            print(f"   Transcript preview: {video.transcript[:100]}...")
        print()


def test_multiple_channels():
    """Test multiple channel scraping"""
    print("=" * 60)
    print("2. Testing Multiple Channels")
    print("=" * 60)
    
    service = YouTubeService()
    
    channels = [
        {'username': 'CNBCtelevision', 'name': 'CNBC'},
        # Add more channels here
    ]
    
    videos = service.get_multiple_channels(channels, hours=24)
    print(f"\nFound {len(videos)} total videos from {len(channels)} channels\n")
    
    for i, video in enumerate(videos[:3], 1):
        print(f"{i}. [{video.channel_name}] {video.title}")
        print(f"   {video.url}\n")


def test_transcript_fetching():
    """Test transcript fetching"""
    print("=" * 60)
    print("3. Testing Transcript Fetching")
    print("=" * 60)
    
    service = YouTubeService()
    
    # Test with video URL
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\nFetching transcript for: {video_url}")
    
    transcript = service.get_transcript(video_url)
    if transcript:
        print(f"✓ Success! Transcript length: {len(transcript.text)} characters")
        print(f"Preview: {transcript.text[:200]}...")
        print(f"Type: {type(transcript).__name__}")
    else:
        print("✗ No transcript available")
    
    # Test with video ID
    print(f"\nFetching transcript with timestamps for video ID: dQw4w9WgXcQ")
    transcript_data = service.get_transcript_with_timestamps("dQw4w9WgXcQ")
    if transcript_data:
        print(f"✓ Success! Found {len(transcript_data)} segments")
        print(f"First segment: {transcript_data[0]}")


def test_convenience_functions():
    """Test convenience functions"""
    print("=" * 60)
    print("4. Testing Convenience Functions")
    print("=" * 60)
    
    # Using convenience function for channel videos
    print("\nUsing convenience function for channel videos...")
    videos = get_channel_videos("CNBCtelevision", hours=24)
    print(f"Found {len(videos)} videos")
    
    # Using convenience function for transcript
    if videos:
        print(f"\nUsing convenience function for transcript...")
        transcript = get_transcript(videos[0].url)
        if transcript:
            print(f"✓ Got transcript: {len(transcript.text)} characters")
            print(f"Type: {type(transcript).__name__}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Quick test with a video URL
        video_url = sys.argv[1]
        service = YouTubeService()
        transcript = service.get_transcript(video_url)
        if transcript:
            print(f"Transcript ({len(transcript.text)} chars):")
            print(transcript.text)
        else:
            print("No transcript available")
    else:
        test_channel_scraping()
        test_multiple_channels()
        test_transcript_fetching()
        test_convenience_functions()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

