"""Unified YouTube service for scraping channels and fetching transcripts"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import os
import re
import requests
import feedparser
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Try to import proxy config (optional)
try:
    from youtube_transcript_api.proxies import WebshareProxyConfig
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False
    WebshareProxyConfig = None


# ==================== Pydantic Models ====================

class ChannelVideo(BaseModel):
    """Model for YouTube channel video data"""
    title: str = Field(..., description="Video title")
    url: str = Field(..., description="Video URL")
    video_id: str = Field(..., description="YouTube video ID")
    published_at: datetime = Field(..., description="Video publication date")
    description: str = Field(default="", description="Video description")
    transcript: Optional[str] = Field(default=None, description="Video transcript text")
    channel_name: str = Field(..., description="Channel name")
    channel_id: str = Field(..., description="YouTube channel ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Transcript(BaseModel):
    """Model for YouTube video transcript"""
    text: str = Field(..., description="Transcript text content")


class YouTubeService:
    """
    Unified service for YouTube channel scraping and transcript fetching.
    
    Features:
    - Scrape videos from YouTube channels using RSS feeds
    - Fetch transcripts for any YouTube video
    - Extract video IDs from URLs
    - Support for multiple channels
    - Optional proxy support for transcript fetching
    """
    
    def __init__(self, use_proxy: bool = None):
        """
        Initialize YouTube service
        
        Args:
            use_proxy: Whether to use proxy (None = auto-detect from env vars)
            
        Proxy Configuration:
            To use proxy for YouTube transcript fetching, set these environment variables:
            - YOUTUBE_PROXY_USERNAME: Your proxy username
            - YOUTUBE_PROXY_PASSWORD: Your proxy password
            
            Example in .env file:
                YOUTUBE_PROXY_USERNAME=your_proxy_username
                YOUTUBE_PROXY_PASSWORD=your_proxy_password
            
            If these are set, proxy will be used automatically. If not set, proxy is not used.
        """
        # Check if proxy should be used
        proxy_config = None
        if use_proxy is None:
            # Auto-detect from environment variables
            proxy_username = os.getenv("YOUTUBE_PROXY_USERNAME")
            proxy_password = os.getenv("YOUTUBE_PROXY_PASSWORD")
            if proxy_username and proxy_password and PROXY_AVAILABLE:
                proxy_config = WebshareProxyConfig(
                    proxy_username=proxy_username,
                    proxy_password=proxy_password
                )
        elif use_proxy and PROXY_AVAILABLE:
            # Explicitly use proxy
            proxy_username = os.getenv("YOUTUBE_PROXY_USERNAME")
            proxy_password = os.getenv("YOUTUBE_PROXY_PASSWORD")
            if proxy_username and proxy_password:
                proxy_config = WebshareProxyConfig(
                    proxy_username=proxy_username,
                    proxy_password=proxy_password
                )
        
        # Initialize transcript API with optional proxy
        if proxy_config:
            self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        else:
            self.transcript_api = YouTubeTranscriptApi()
    
    # ==================== Channel Scraping ====================
    
    def get_channel_videos(self, username: str, hours: int = 24, channel_name: str = None) -> List[ChannelVideo]:
        """
        Get latest videos from a YouTube channel
        
        Args:
            username: YouTube username/handle (e.g., 'CNBCtelevision', '@CNBCtelevision', 
                     or full URL 'https://www.youtube.com/@CNBCtelevision')
            hours: Number of hours to look back (default: 24)
            channel_name: Optional display name for the channel
            
        Returns:
            List of ChannelVideo models
        """
        username_clean = self._extract_username(username)
        channel_name = channel_name or username_clean
        channel_id = self._resolve_to_channel_id(username_clean)
        
        if not channel_id:
            raise ValueError(f"Could not resolve username '{username_clean}' to a channel ID")
        
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            feed = feedparser.parse(rss_url)
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            print(f"    Cutoff time: {cutoff_time}")
            print(f"    Feed entries found: {len(feed.entries) if feed.entries else 0}")
            
            if not feed.entries:
                if feed.bozo:
                    print(f"    ⚠ RSS feed parsing warning: {feed.bozo_exception}")
                return []
            
            videos = []
            
            for entry in feed.entries:
                video = self._extract_video_info(entry, cutoff_time, channel_name, channel_id)
                if video:
                    videos.append(ChannelVideo(**video))
            
            return videos
        except Exception as e:
            print(f"  ✗ Error fetching videos from {username}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_multiple_channels(self, channel_list: List[Dict], hours: int = 24) -> List[ChannelVideo]:
        """
        Get videos from multiple YouTube channels
        
        Args:
            channel_list: List of channel dictionaries with 'username' and optionally 'name'
            hours: Number of hours to look back
            
        Returns:
            Combined and sorted list of videos from all channels
        """
        all_videos = []
        
        for channel_info in channel_list:
            username = channel_info.get('username') or channel_info.get('channel_id') or channel_info.get('id')
            channel_name = channel_info.get('name') or channel_info.get('channel_name')
            
            if not username:
                continue
            
            try:
                videos = self.get_channel_videos(username, hours, channel_name)
                all_videos.extend(videos)
            except Exception as e:
                print(f"  ✗ Error processing channel {username}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        all_videos.sort(key=lambda x: x.published_at, reverse=True)
        return all_videos
    
    # ==================== Transcript Fetching ====================
    
    def get_transcript(self, video_url_or_id: str, languages: list = None) -> Optional[Transcript]:
        """
        Get transcript for a YouTube video
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            languages: List of language codes in priority order (default: ['en'])
            
        Returns:
            Transcript model with text, or None if unavailable
        """
        video_id = self.extract_video_id(video_url_or_id)
        
        if languages is None:
            languages = ['en']
        
        try:
            fetched_transcript = self.transcript_api.fetch(video_id, languages=languages)
            transcript_text = ' '.join([snippet.text for snippet in fetched_transcript])
            return Transcript(text=transcript_text)
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None
    
    def get_transcript_with_timestamps(self, video_url_or_id: str, languages: list = None) -> Optional[list]:
        """
        Get transcript with timestamps for a YouTube video
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            languages: List of language codes in priority order (default: ['en'])
            
        Returns:
            List of dictionaries with 'text', 'start', 'duration', or None if unavailable
        """
        video_id = self.extract_video_id(video_url_or_id)
        
        if languages is None:
            languages = ['en']
        
        try:
            fetched_transcript = self.transcript_api.fetch(video_id, languages=languages)
            return fetched_transcript.to_raw_data()
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None
    
    def fetch_transcript_for_video(self, video: ChannelVideo) -> Optional[str]:
        """
        Fetch transcript for a ChannelVideo object and update it
        
        Args:
            video: ChannelVideo object to fetch transcript for
            
        Returns:
            Transcript text if successful, None otherwise
        """
        transcript_obj = self.get_transcript(video.video_id)
        if transcript_obj:
            return transcript_obj.text
        return None
    
    def fetch_transcripts_batch(self, videos: List[ChannelVideo]) -> List[ChannelVideo]:
        """
        Fetch transcripts for multiple videos in batch
        
        Args:
            videos: List of ChannelVideo objects
            
        Returns:
            List of ChannelVideo objects with transcripts populated
        """
        updated_videos = []
        for video in videos:
            if video.transcript is None:  # Only fetch if not already fetched
                transcript_text = self.fetch_transcript_for_video(video)
                if transcript_text:
                    # Create new video object with transcript
                    video_dict = video.model_dump()
                    video_dict['transcript'] = transcript_text
                    updated_videos.append(ChannelVideo(**video_dict))
                else:
                    updated_videos.append(video)  # Keep original if transcript unavailable
            else:
                updated_videos.append(video)  # Already has transcript
        
        return updated_videos
    
    # ==================== Utility Methods ====================
    
    def extract_video_id(self, url_or_id: str) -> str:
        """
        Extract video ID from URL or return ID if already an ID
        
        Args:
            url_or_id: YouTube video URL or video ID
            
        Returns:
            Video ID string
        """
        if 'watch?v=' in url_or_id:
            return url_or_id.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in url_or_id:
            return url_or_id.split('youtu.be/')[-1].split('?')[0]
        return url_or_id
    
    # ==================== Private Methods ====================
    
    def _extract_username(self, identifier: str) -> str:
        """Extract username from URL, handle, or plain username"""
        if identifier.startswith('http') and '/@' in identifier:
            return identifier.split('/@')[-1].split('?')[0].split('/')[0].lstrip('@')
        return identifier.lstrip('@').strip()
    
    def _resolve_to_channel_id(self, handle: str) -> Optional[str]:
        """Resolve YouTube handle to channel ID"""
        url = f"https://www.youtube.com/@{handle.lstrip('@')}"
        
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            
            patterns = [
                r'"channelId":"(UC[a-zA-Z0-9_-]{22})"',
                r'"externalId":"(UC[a-zA-Z0-9_-]{22})"',
                r'/channel/(UC[a-zA-Z0-9_-]{22})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None
    
    def _extract_video_info(self, entry, cutoff_time: datetime, channel_name: str, channel_id: str) -> Optional[Dict]:
        """Extract video information from RSS entry"""
        title = entry.get('title', '').strip()
        url = entry.get('link', '')
        
        if not title or not url:
            return None

        # Filter out YouTube Shorts
        if '/shorts/' in url:
            return None

        video_id = self.extract_video_id(url)
        if not video_id:
            return None

        # Parse published date
        published_at = datetime.now(timezone.utc)
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'published'):
            try:
                from dateutil import parser
                parsed = parser.parse(entry.published)
                published_at = parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except:
                pass

        # Filter by time
        if published_at < cutoff_time:
            return None

        # Get description (transcript fetched separately)
        description = " ".join((entry.get('summary', '') or entry.get('description', '')).split())

        return {
            'title': title,
            'url': url,
            'video_id': video_id,
            'published_at': published_at,
            'description': description,
            'transcript': None,  # Transcripts fetched separately
            'channel_name': channel_name,
            'channel_id': channel_id
        }


# Convenience functions for simple use cases
def get_channel_videos(username: str, hours: int = 24) -> List[ChannelVideo]:
    """Quick function to get videos from a channel"""
    service = YouTubeService()
    return service.get_channel_videos(username, hours)

def get_transcript(video_url_or_id: str, languages: list = None) -> Optional[Transcript]:
    """Quick function to get transcript"""
    service = YouTubeService()
    return service.get_transcript(video_url_or_id, languages)

