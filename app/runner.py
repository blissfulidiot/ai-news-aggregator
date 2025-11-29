"""Main runner for news aggregator"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.scrapers.openai_news_scraper import OpenAINewsScraper, NewsArticle as OpenAINewsArticle
from app.scrapers.anthropic_news_scraper import AnthropicNewsScraper, NewsArticle as AnthropicNewsArticle
from app.services.youtube_service import YouTubeService, ChannelVideo
from app.config import YOUTUBE_CHANNELS, RSS_FEEDS
from app.database.connection import get_db_session
from app.database.repository import (
    SourceRepository, ArticleRepository, VideoRepository
)
from app.database.models import SourceType


class NewsAggregator:
    """Main aggregator that combines all news sources"""
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.anthropic_scraper = AnthropicNewsScraper()
        self.openai_scrapers = {}
        
        # Initialize OpenAI scrapers for each RSS feed
        for source_name, rss_url in RSS_FEEDS.items():
            self.openai_scrapers[source_name] = OpenAINewsScraper(rss_url)
    
    def run(self, hours: int = 24, fetch_transcripts: bool = False, save_to_db: bool = True) -> Dict:
        """
        Run the aggregator and collect all content
        
        Args:
            hours: Number of hours to look back (default: 24)
            fetch_transcripts: Whether to fetch transcripts immediately (default: False)
            save_to_db: Whether to save results to database (default: True)
            
        Returns:
            Dictionary containing articles and videos from all sources
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hours": hours,
            "articles": [],
            "videos": [],
            "summary": {}
        }
        
        # Get database session if saving to DB
        db = None
        if save_to_db:
            db_gen = get_db_session()
            db = next(db_gen)
        
        try:
            # Get Anthropic articles
            print(f"Fetching Anthropic articles (last {hours} hours)...")
            anthropic_articles = self.anthropic_scraper.get_articles(hours=hours)
            results["articles"].extend(anthropic_articles)
            results["summary"]["anthropic"] = len(anthropic_articles)
            print(f"  ✓ Found {len(anthropic_articles)} Anthropic articles")
            
            # Save Anthropic articles to database
            if save_to_db and db and anthropic_articles:
                saved_count = self._save_anthropic_articles(db, anthropic_articles)
                print(f"  ✓ Saved {saved_count} Anthropic articles to database")
            
            # Get OpenAI articles from all RSS feeds
            for source_name, scraper in self.openai_scrapers.items():
                print(f"Fetching {source_name} articles (last {hours} hours)...")
                try:
                    articles = scraper.get_articles(hours=hours)
                    results["articles"].extend(articles)
                    results["summary"][source_name] = len(articles)
                    print(f"  ✓ Found {len(articles)} {source_name} articles")
                    
                    # Save OpenAI articles to database
                    if save_to_db and db and articles:
                        saved_count = self._save_openai_articles(db, source_name, scraper.rss_url, articles)
                        print(f"  ✓ Saved {saved_count} {source_name} articles to database")
                except Exception as e:
                    print(f"  ✗ Error fetching {source_name}: {e}")
                    results["summary"][source_name] = 0
            
            # Get YouTube videos
            if YOUTUBE_CHANNELS:
                print(f"Fetching YouTube videos (last {hours} hours)...")
                try:
                    videos = self.youtube_service.get_multiple_channels(YOUTUBE_CHANNELS, hours=hours)
                    
                    # Optionally fetch transcripts
                    if fetch_transcripts:
                        print("Fetching transcripts for videos...")
                        videos = self.fetch_transcripts_for_videos(videos)
                        transcripts_fetched = len([v for v in videos if v.transcript])
                        print(f"  ✓ Fetched transcripts for {transcripts_fetched} videos")
                    
                    results["videos"].extend(videos)
                    results["summary"]["youtube"] = len(videos)
                    print(f"  ✓ Found {len(videos)} YouTube videos")
                    
                    # Save YouTube videos to database
                    if save_to_db and db and videos:
                        saved_count = self._save_youtube_videos(db, videos)
                        print(f"  ✓ Saved {saved_count} YouTube videos to database")
                except Exception as e:
                    print(f"  ✗ Error fetching YouTube videos: {e}")
                    results["summary"]["youtube"] = 0
            else:
                results["summary"]["youtube"] = 0
            
            # Sort articles by date
            results["articles"].sort(key=lambda x: x.published_at, reverse=True)
            
            # Sort videos by date
            results["videos"].sort(key=lambda x: x.published_at, reverse=True)
            
            return results
            
        finally:
            if db:
                db.close()
    
    def _save_anthropic_articles(self, db, articles: List[AnthropicNewsArticle]) -> int:
        """Save Anthropic articles to database"""
        # Get or create Anthropic source
        source = SourceRepository.get_or_create(
            db,
            name="Anthropic",
            url="https://www.anthropic.com",
            source_type=SourceType.RSS,
            rss_url="https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml"
        )
        
        saved_count = 0
        for article in articles:
            try:
                # Check if article already exists
                if ArticleRepository.exists_by_url(db, article.url):
                    continue
                
                # Save article
                ArticleRepository.create(
                    db,
                    source_id=source.id,
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at,
                    description=article.description,
                    feed_type=article.feed_type
                )
                saved_count += 1
            except Exception as e:
                print(f"    ✗ Error saving article {article.title[:50]}: {e}")
                db.rollback()
                continue
        
        return saved_count
    
    def _save_openai_articles(self, db, source_name: str, rss_url: str, articles: List[OpenAINewsArticle]) -> int:
        """Save OpenAI articles to database"""
        # Get or create source
        source = SourceRepository.get_or_create(
            db,
            name=source_name,
            url=f"https://openai.com",  # Base URL
            source_type=SourceType.RSS,
            rss_url=rss_url
        )
        
        saved_count = 0
        for article in articles:
            try:
                # Check if article already exists
                if ArticleRepository.exists_by_url(db, article.url):
                    continue
                
                # Save article
                ArticleRepository.create(
                    db,
                    source_id=source.id,
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at,
                    description=article.description
                )
                saved_count += 1
            except Exception as e:
                print(f"    ✗ Error saving article {article.title[:50]}: {e}")
                db.rollback()
                continue
        
        return saved_count
    
    def _save_youtube_videos(self, db, videos: List[ChannelVideo]) -> int:
        """Save YouTube videos to database"""
        saved_count = 0
        
        # Create a mapping from channel_id to channel config
        channel_config_map = {}
        for channel_config in YOUTUBE_CHANNELS:
            username = channel_config.get('username', '').lstrip('@')
            channel_name = channel_config.get('name', username)
            # We'll match by channel_id when we have it
            channel_config_map[channel_name] = {
                'username': username,
                'name': channel_name
            }
        
        # Group videos by channel
        channels = {}
        for video in videos:
            channel_key = (video.channel_id, video.channel_name)
            if channel_key not in channels:
                channels[channel_key] = []
            channels[channel_key].append(video)
        
        # Save videos for each channel
        for (channel_id, channel_name), channel_videos in channels.items():
            # Get channel config
            channel_config = channel_config_map.get(channel_name, {
                'username': channel_name.replace('@', '').replace('CNBC Television', 'CNBCtelevision'),
                'name': channel_name
            })
            
            # Get or create source for this channel
            channel_url = f"https://www.youtube.com/@{channel_config['username']}"
            source = SourceRepository.get_or_create(
                db,
                name=channel_config['name'],
                url=channel_url,
                source_type=SourceType.YOUTUBE,
                youtube_channel_id=channel_id,
                youtube_username=channel_config['username']
            )
            
            # Save videos
            for video in channel_videos:
                try:
                    # Check if video already exists
                    existing_video = VideoRepository.get_by_video_id(db, video.video_id)
                    if existing_video:
                        continue
                    
                    # Save video (transcript will be fetched separately if needed)
                    VideoRepository.create(
                        db,
                        source_id=source.id,
                        title=video.title,
                        url=video.url,
                        video_id=video.video_id,
                        published_at=video.published_at,
                        description=video.description,
                        transcript=video.transcript  # May be None
                    )
                    saved_count += 1
                except Exception as e:
                    print(f"    ✗ Error saving video {video.title[:50]}: {e}")
                    db.rollback()
                    continue
        
        return saved_count
    
    def get_content_as_markdown(self, url: str) -> Optional[str]:
        """Get content from URL as markdown (uses Anthropic scraper's converter)"""
        return self.anthropic_scraper.get_content_as_markdown(url)
    
    def fetch_transcripts_for_videos(self, videos: List[ChannelVideo]) -> List[ChannelVideo]:
        """
        Fetch transcripts for videos (separate from initial scraping)
        
        Args:
            videos: List of ChannelVideo objects
            
        Returns:
            List of ChannelVideo objects with transcripts populated
        """
        from app.services.transcript_fetcher import TranscriptFetcher
        fetcher = TranscriptFetcher()
        return fetcher.fetch_transcripts_for_videos_without(videos)


def run_aggregator(hours: int = 24, fetch_transcripts: bool = False, save_to_db: bool = True) -> Dict:
    """
    Convenience function to run the aggregator
    
    Args:
        hours: Number of hours to look back (default: 24)
        fetch_transcripts: Whether to fetch transcripts immediately (default: False)
        save_to_db: Whether to save results to database (default: True)
        
    Returns:
        Dictionary with aggregated results
    """
    aggregator = NewsAggregator()
    return aggregator.run(hours=hours, fetch_transcripts=fetch_transcripts, save_to_db=save_to_db)


if __name__ == "__main__":
    import sys
    
    # Parse hours from command line if provided
    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Invalid hours value: {sys.argv[1]}. Using default: 24 hours")
    
    print("=" * 70)
    print(f"News Aggregator - Fetching content from last {hours} hours")
    print("=" * 70)
    
    results = run_aggregator(hours=hours)
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total articles: {len(results['articles'])}")
    print(f"Total videos: {len(results['videos'])}")
    print(f"\nBreakdown:")
    for source, count in results["summary"].items():
        print(f"  {source}: {count}")
    
    print("\n" + "=" * 70)
    print("Sample Articles (first 5)")
    print("=" * 70)
    for i, article in enumerate(results["articles"][:5], 1):
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source_name}")
        if hasattr(article, 'feed_type'):
            print(f"   Feed: {article.feed_type}")
        print(f"   Published: {article.published_at}")
        print(f"   URL: {article.url}")
    
    if results["videos"]:
        print("\n" + "=" * 70)
        print("Sample Videos (first 5)")
        print("=" * 70)
        for i, video in enumerate(results["videos"][:5], 1):
            print(f"\n{i}. {video.title}")
            print(f"   Channel: {video.channel_name}")
            print(f"   Published: {video.published_at}")
            print(f"   URL: {video.url}")

