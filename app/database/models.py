"""SQLAlchemy database models"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.database.connection import Base


class SourceType(enum.Enum):
    """Source type enumeration"""
    BLOG = "blog"
    YOUTUBE = "youtube"
    NEWS = "news"
    SEC = "sec"
    RSS = "rss"


class Source(Base):
    """Source model for news sources"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True, index=True)
    source_type = Column(Enum(SourceType), nullable=False, index=True)
    youtube_channel_id = Column(String(100), nullable=True, unique=True, index=True)
    youtube_username = Column(String(100), nullable=True, unique=True, index=True)
    rss_url = Column(String(500), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type={self.source_type.value})>"


class Article(Base):
    """Article model for news articles and blog posts"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scraped_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Additional fields for different source types
    feed_type = Column(String(50), nullable=True)  # For Anthropic: news, engineering, research, red
    markdown_content = Column(Text, nullable=True)  # Full markdown content if fetched
    markdown_fetched_at = Column(DateTime(timezone=True), nullable=True)  # Timestamp when markdown was fetched
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"


class Video(Base):
    """Video model for YouTube videos"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    video_id = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scraped_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    transcript_fetched_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    source = relationship("Source")
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title[:50]}...', video_id={self.video_id})>"


class UserSettings(Base):
    """User settings model"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    system_prompt = Column(Text, nullable=True)
    # User profile fields
    name = Column(String(255), nullable=True)  # User's name
    background = Column(Text, nullable=True)  # User's background/profession
    interests = Column(Text, nullable=True)  # User's interests (comma-separated or JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<UserSettings(id={self.id}, email='{self.email}')>"


class Digest(Base):
    """Digest model for summarized content"""
    __tablename__ = "digests"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True, index=True)
    url = Column(String(1000), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=False)  # 2-3 sentence summary
    content_type = Column(String(50), nullable=False)  # 'article' or 'video'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    article = relationship("Article")
    video = relationship("Video")
    
    def __repr__(self):
        return f"<Digest(id={self.id}, title='{self.title[:50]}...', content_type={self.content_type})>"

