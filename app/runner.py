"""Main runner for news aggregator"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.scrapers.openai_news_scraper import OpenAINewsScraper, NewsArticle as OpenAINewsArticle
from app.scrapers.anthropic_news_scraper import AnthropicNewsScraper, NewsArticle as AnthropicNewsArticle
from app.services.youtube_service import YouTubeService, ChannelVideo
from app.config import YOUTUBE_CHANNELS, RSS_FEEDS


class NewsAggregator:
    """Main aggregator that combines all news sources"""
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.anthropic_scraper = AnthropicNewsScraper()
        self.openai_scrapers = {}
        
        # Initialize OpenAI scrapers for each RSS feed
        for source_name, rss_url in RSS_FEEDS.items():
            self.openai_scrapers[source_name] = OpenAINewsScraper(rss_url)
    
    def run(self, hours: int = 24, fetch_transcripts: bool = False) -> Dict:
        """
        Run the aggregator and collect all content
        
        Args:
            hours: Number of hours to look back (default: 24)
            fetch_transcripts: Whether to fetch transcripts immediately (default: False)
            
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
        
        # Get Anthropic articles
        print(f"Fetching Anthropic articles (last {hours} hours)...")
        anthropic_articles = self.anthropic_scraper.get_articles(hours=hours)
        results["articles"].extend(anthropic_articles)
        results["summary"]["anthropic"] = len(anthropic_articles)
        print(f"  ✓ Found {len(anthropic_articles)} Anthropic articles")
        
        # Get OpenAI articles from all RSS feeds
        for source_name, scraper in self.openai_scrapers.items():
            print(f"Fetching {source_name} articles (last {hours} hours)...")
            try:
                articles = scraper.get_articles(hours=hours)
                results["articles"].extend(articles)
                results["summary"][source_name] = len(articles)
                print(f"  ✓ Found {len(articles)} {source_name} articles")
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


def run_aggregator(hours: int = 24, fetch_transcripts: bool = False) -> Dict:
    """
    Convenience function to run the aggregator
    
    Args:
        hours: Number of hours to look back (default: 24)
        fetch_transcripts: Whether to fetch transcripts immediately (default: False)
        
    Returns:
        Dictionary with aggregated results
    """
    aggregator = NewsAggregator()
    return aggregator.run(hours=hours, fetch_transcripts=fetch_transcripts)


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

