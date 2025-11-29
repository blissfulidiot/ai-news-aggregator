"""OpenAI news scraper using RSS feeds"""

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
    source_name: str = "OpenAI"
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class OpenAINewsScraper:
    """Scraper for RSS news feeds"""
    
    def __init__(self, rss_url: str):
        self.rss_url = rss_url
        self.source_name = "OpenAI"
        self.converter = DocumentConverter()
    
    def get_articles(self, hours: int = 24) -> List[NewsArticle]:
        """Get articles published within the specified time frame"""
        feed = feedparser.parse(self.rss_url)
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        print(f"    Cutoff time: {cutoff}")
        print(f"    Feed entries found: {len(feed.entries) if feed.entries else 0}")
        
        if not feed.entries:
            if feed.bozo:
                print(f"    ⚠ RSS feed parsing warning: {feed.bozo_exception}")
            return []
        
        articles = []
        
        for entry in feed.entries:
            published_at = self._parse_date(entry)
            if published_at and published_at >= cutoff:
                articles.append(NewsArticle(
                    title=entry.get('title', '').strip(),
                    url=entry.get('link', ''),
                    description=self._get_description(entry),
                    published_at=published_at,
                    source_name=self.source_name
                ))
        
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


def get_openai_articles(rss_url: str, hours: int = 24) -> List[NewsArticle]:
    """Get articles from RSS feed within time frame"""
    scraper = OpenAINewsScraper(rss_url)
    return scraper.get_articles(hours)


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
