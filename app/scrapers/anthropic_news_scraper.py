"""Anthropic news scraper combining multiple RSS feeds"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from pydantic import BaseModel, Field
from docling.document_converter import DocumentConverter


class NewsArticle(BaseModel):
    """Model for RSS news article"""
    title: str
    url: str
    description: str = ""
    published_at: datetime
    source_name: str = "Anthropic"
    feed_type: str = ""  # e.g., "news", "engineering", "research", "red"
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AnthropicNewsScraper:
    """Scraper for Anthropic news combining multiple RSS feeds"""
    
    # Anthropic RSS feed URLs
    FEEDS = {
        "news": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "engineering": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "research": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
        "red": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_red.xml",
    }
    
    def __init__(self):
        self.source_name = "Anthropic"
        self.converter = DocumentConverter()
    
    def get_articles(self, hours: int = 24) -> List[NewsArticle]:
        """
        Get articles from all Anthropic feeds within the specified time frame
        
        Args:
            hours: Number of hours to look back (default: 24)
            
        Returns:
            Combined and sorted list of NewsArticle models from all feeds
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        all_articles = []
        
        for feed_type, feed_url in self.FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    continue
                
                for entry in feed.entries:
                    published_at = self._parse_date(entry)
                    if published_at and published_at >= cutoff:
                        all_articles.append(NewsArticle(
                            title=entry.get('title', '').strip(),
                            url=entry.get('link', ''),
                            description=self._get_description(entry),
                            published_at=published_at,
                            source_name=self.source_name,
                            feed_type=feed_type
                        ))
            except Exception as e:
                print(f"Error processing {feed_type} feed: {e}")
                continue
        
        # Sort by publication date (newest first)
        all_articles.sort(key=lambda x: x.published_at, reverse=True)
        return all_articles
    
    def get_articles_by_feed(self, feed_type: str, hours: int = 24) -> List[NewsArticle]:
        """
        Get articles from a specific feed type
        
        Args:
            feed_type: One of "news", "engineering", "research", "red"
            hours: Number of hours to look back (default: 24)
            
        Returns:
            List of NewsArticle models from the specified feed
        """
        if feed_type not in self.FEEDS:
            raise ValueError(f"Invalid feed_type. Must be one of: {list(self.FEEDS.keys())}")
        
        feed_url = self.FEEDS[feed_type]
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                return []
            
            for entry in feed.entries:
                published_at = self._parse_date(entry)
                if published_at and published_at >= cutoff:
                    articles.append(NewsArticle(
                        title=entry.get('title', '').strip(),
                        url=entry.get('link', ''),
                        description=self._get_description(entry),
                        published_at=published_at,
                        source_name=self.source_name,
                        feed_type=feed_type
                    ))
        except Exception as e:
            print(f"Error processing {feed_type} feed: {e}")
            return []
        
        articles.sort(key=lambda x: x.published_at, reverse=True)
        return articles
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse published date from RSS entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if hasattr(entry, 'published'):
            try:
                from dateutil import parser
                parsed = parser.parse(entry.published)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except:
                pass
        return None
    
    def _get_description(self, entry) -> str:
        """Extract description from RSS entry"""
        desc = entry.get('summary') or entry.get('description', '')
        return " ".join(desc.split()) if desc else ""
    
    def get_content_as_markdown(self, url: str) -> Optional[str]:
        """
        Fetch content from URL and convert to markdown
        
        Args:
            url: URL to fetch content from
            
        Returns:
            Markdown content as string, or None if conversion fails
        """
        try:
            result = self.converter.convert(url)
            document = result.document
            markdown_output = document.export_to_markdown()
            return markdown_output
        except Exception as e:
            print(f"Error converting {url} to markdown: {e}")
            return None


def get_anthropic_articles(hours: int = 24) -> List[NewsArticle]:
    """Get articles from all Anthropic feeds within time frame"""
    scraper = AnthropicNewsScraper()
    return scraper.get_articles(hours)


def get_anthropic_articles_by_feed(feed_type: str, hours: int = 24) -> List[NewsArticle]:
    """Get articles from a specific Anthropic feed"""
    scraper = AnthropicNewsScraper()
    return scraper.get_articles_by_feed(feed_type, hours)


def get_url_content_as_markdown(url: str) -> Optional[str]:
    """Get content from URL and convert to markdown"""
    converter = DocumentConverter()
    try:
        result = converter.convert(url)
        document = result.document
        markdown_output = document.export_to_markdown()
        return markdown_output
    except Exception as e:
        print(f"Error converting {url} to markdown: {e}")
        return None

