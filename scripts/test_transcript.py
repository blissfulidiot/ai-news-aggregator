#!/usr/bin/env python3
"""Simple test for YouTube transcript service"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.youtube_transcript_service import YouTubeTranscriptService, get_transcript


def main():
    # Test with a real YouTube video URL
    # You can replace this with any YouTube video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example video
    
    print("Testing YouTube Transcript Service")
    print("=" * 60)
    print(f"Video URL: {test_url}\n")
    
    # Method 1: Using convenience function
    print("Method 1: Using convenience function")
    transcript = get_transcript(test_url)
    if transcript:
        print(f"✓ Success! Transcript length: {len(transcript)} characters")
        print(f"Preview: {transcript[:300]}...\n")
    else:
        print("✗ No transcript available\n")
    
    # Method 2: Using service class
    print("Method 2: Using service class")
    service = YouTubeTranscriptService()
    transcript = service.get_transcript(test_url)
    if transcript:
        print(f"✓ Success! Transcript length: {len(transcript)} characters")
        print(f"Preview: {transcript[:300]}...\n")
    else:
        print("✗ No transcript available\n")
    
    # Method 3: Get transcript with timestamps
    print("Method 3: Getting transcript with timestamps")
    transcript_data = service.get_transcript_with_timestamps(test_url)
    if transcript_data:
        print(f"✓ Success! Found {len(transcript_data)} segments")
        print(f"First 3 segments:")
        for i, segment in enumerate(transcript_data[:3], 1):
            print(f"  {i}. [{segment['start']:.1f}s] {segment['text']}")
    else:
        print("✗ No transcript available")


if __name__ == "__main__":
    # You can also pass a URL as command line argument
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"Testing with URL: {test_url}\n")
        service = YouTubeTranscriptService()
        transcript = service.get_transcript(test_url)
        if transcript:
            print(f"Transcript ({len(transcript)} chars):")
            print(transcript)
        else:
            print("No transcript available")
    else:
        main()


