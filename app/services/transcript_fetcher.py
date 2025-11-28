"""Service for fetching YouTube video transcripts in batch"""

from typing import List, Optional
from app.services.youtube_service import YouTubeService, ChannelVideo


class TranscriptFetcher:
    """Service for fetching transcripts for YouTube videos"""
    
    def __init__(self):
        self.youtube_service = YouTubeService()
    
    def fetch_transcript(self, video: ChannelVideo) -> Optional[str]:
        """
        Fetch transcript for a single video
        
        Args:
            video: ChannelVideo object
            
        Returns:
            Transcript text or None
        """
        return self.youtube_service.fetch_transcript_for_video(video)
    
    def fetch_transcripts_batch(self, videos: List[ChannelVideo], max_workers: int = 5) -> List[ChannelVideo]:
        """
        Fetch transcripts for multiple videos
        
        Args:
            videos: List of ChannelVideo objects
            max_workers: Maximum concurrent transcript fetches (default: 5, not used currently)
            
        Returns:
            List of ChannelVideo objects with transcripts populated
        """
        return self.youtube_service.fetch_transcripts_batch(videos)
    
    def fetch_transcripts_for_videos_without(self, videos: List[ChannelVideo]) -> List[ChannelVideo]:
        """
        Fetch transcripts only for videos that don't have them yet
        
        Args:
            videos: List of ChannelVideo objects
            
        Returns:
            List of ChannelVideo objects with transcripts populated
        """
        videos_without_transcripts = [v for v in videos if v.transcript is None]
        if not videos_without_transcripts:
            return videos
        
        updated = self.fetch_transcripts_batch(videos_without_transcripts)
        
        # Merge back with videos that already had transcripts
        result = []
        updated_dict = {v.video_id: v for v in updated}
        
        for video in videos:
            if video.video_id in updated_dict:
                result.append(updated_dict[video.video_id])
            else:
                result.append(video)
        
        return result


def fetch_transcripts_for_videos(videos: List[ChannelVideo]) -> List[ChannelVideo]:
    """Convenience function to fetch transcripts for videos"""
    fetcher = TranscriptFetcher()
    return fetcher.fetch_transcripts_for_videos_without(videos)

