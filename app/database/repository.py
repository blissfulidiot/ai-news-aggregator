"""CRUD repository for database operations"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database.models import Source, Article, Video, UserSettings, Digest, SourceType
from app.database.connection import get_db_session


class SourceRepository:
    """Repository for Source operations"""
    
    @staticmethod
    def create(db: Session, name: str, url: str, source_type: SourceType, 
               youtube_channel_id: Optional[str] = None,
               youtube_username: Optional[str] = None,
               rss_url: Optional[str] = None) -> Source:
        """Create a new source"""
        source = Source(
            name=name,
            url=url,
            source_type=source_type,
            youtube_channel_id=youtube_channel_id,
            youtube_username=youtube_username,
            rss_url=rss_url
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source
    
    @staticmethod
    def get_by_id(db: Session, source_id: int) -> Optional[Source]:
        """Get source by ID"""
        return db.query(Source).filter(Source.id == source_id).first()
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Source]:
        """Get source by URL"""
        return db.query(Source).filter(Source.url == url).first()
    
    @staticmethod
    def get_by_youtube_channel_id(db: Session, channel_id: str) -> Optional[Source]:
        """Get source by YouTube channel ID"""
        return db.query(Source).filter(Source.youtube_channel_id == channel_id).first()
    
    @staticmethod
    def get_by_youtube_username(db: Session, username: str) -> Optional[Source]:
        """Get source by YouTube username"""
        return db.query(Source).filter(Source.youtube_username == username).first()
    
    @staticmethod
    def get_by_rss_url(db: Session, rss_url: str) -> Optional[Source]:
        """Get source by RSS URL"""
        return db.query(Source).filter(Source.rss_url == rss_url).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Source]:
        """Get all sources"""
        return db.query(Source).all()
    
    @staticmethod
    def get_by_type(db: Session, source_type: SourceType) -> List[Source]:
        """Get sources by type"""
        return db.query(Source).filter(Source.source_type == source_type).all()
    
    @staticmethod
    def update(db: Session, source_id: int, **kwargs) -> Optional[Source]:
        """Update source"""
        source = SourceRepository.get_by_id(db, source_id)
        if source:
            for key, value in kwargs.items():
                setattr(source, key, value)
            source.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(source)
        return source
    
    @staticmethod
    def delete(db: Session, source_id: int) -> bool:
        """Delete source"""
        source = SourceRepository.get_by_id(db, source_id)
        if source:
            db.delete(source)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_or_create(db: Session, name: str, url: str, source_type: SourceType,
                     youtube_channel_id: Optional[str] = None,
                     youtube_username: Optional[str] = None,
                     rss_url: Optional[str] = None) -> Source:
        """Get existing source or create a new one"""
        # Try to find existing source by URL first (most reliable)
        source = SourceRepository.get_by_url(db, url)
        if source:
            return source
        
        # For RSS sources, also check RSS URL
        if source_type == SourceType.RSS and rss_url:
            source = SourceRepository.get_by_rss_url(db, rss_url)
            if source:
                return source
        
        # For YouTube sources, check channel ID and username
        if source_type == SourceType.YOUTUBE:
            if youtube_channel_id:
                source = SourceRepository.get_by_youtube_channel_id(db, youtube_channel_id)
                if source:
                    return source
            if youtube_username:
                source = SourceRepository.get_by_youtube_username(db, youtube_username)
                if source:
                    return source
        
        # Create new source if not found
        return SourceRepository.create(
            db, name, url, source_type,
            youtube_channel_id=youtube_channel_id,
            youtube_username=youtube_username,
            rss_url=rss_url
        )


class ArticleRepository:
    """Repository for Article operations"""
    
    @staticmethod
    def create(db: Session, source_id: int, title: str, url: str, 
               published_at: datetime, description: Optional[str] = None,
               content: Optional[str] = None, feed_type: Optional[str] = None,
               markdown_content: Optional[str] = None) -> Article:
        """Create a new article"""
        article = Article(
            source_id=source_id,
            title=title,
            url=url,
            description=description,
            content=content,
            published_at=published_at,
            feed_type=feed_type,
            markdown_content=markdown_content,
            scraped_at=datetime.now(timezone.utc)
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        return article
    
    @staticmethod
    def get_by_id(db: Session, article_id: int) -> Optional[Article]:
        """Get article by ID"""
        return db.query(Article).filter(Article.id == article_id).first()
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Article]:
        """Get article by URL"""
        return db.query(Article).filter(Article.url == url).first()
    
    @staticmethod
    def get_by_source(db: Session, source_id: int, limit: Optional[int] = None) -> List[Article]:
        """Get articles by source"""
        query = db.query(Article).filter(Article.source_id == source_id).order_by(Article.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_recent(db: Session, hours: int = 24, limit: Optional[int] = None) -> List[Article]:
        """Get recent articles within specified hours"""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = db.query(Article).filter(Article.published_at >= cutoff).order_by(Article.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_all(db: Session, limit: Optional[int] = None) -> List[Article]:
        """Get all articles"""
        query = db.query(Article).order_by(Article.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update(db: Session, article_id: int, **kwargs) -> Optional[Article]:
        """Update article"""
        article = ArticleRepository.get_by_id(db, article_id)
        if article:
            for key, value in kwargs.items():
                setattr(article, key, value)
            db.commit()
            db.refresh(article)
        return article
    
    @staticmethod
    def delete(db: Session, article_id: int) -> bool:
        """Delete article"""
        article = ArticleRepository.get_by_id(db, article_id)
        if article:
            db.delete(article)
            db.commit()
            return True
        return False
    
    @staticmethod
    def exists_by_url(db: Session, url: str) -> bool:
        """Check if article exists by URL"""
        return db.query(Article).filter(Article.url == url).first() is not None
    
    @staticmethod
    def get_without_markdown(db: Session, limit: Optional[int] = None) -> List[Article]:
        """Get articles without markdown content"""
        query = db.query(Article).filter(Article.markdown_content.is_(None)).order_by(Article.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update_markdown(db: Session, article_id: int, markdown_content: str) -> Optional[Article]:
        """Update article markdown content"""
        article = ArticleRepository.get_by_id(db, article_id)
        if article:
            article.markdown_content = markdown_content
            article.markdown_fetched_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(article)
        return article


class VideoRepository:
    """Repository for Video operations"""
    
    @staticmethod
    def create(db: Session, source_id: int, title: str, url: str, video_id: str,
               published_at: datetime, description: Optional[str] = None,
               transcript: Optional[str] = None) -> Video:
        """Create a new video"""
        video = Video(
            source_id=source_id,
            title=title,
            url=url,
            video_id=video_id,
            description=description,
            transcript=transcript,
            published_at=published_at,
            scraped_at=datetime.now(timezone.utc),
            transcript_fetched_at=datetime.now(timezone.utc) if transcript else None
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video
    
    @staticmethod
    def get_by_id(db: Session, video_id: int) -> Optional[Video]:
        """Get video by ID"""
        return db.query(Video).filter(Video.id == video_id).first()
    
    @staticmethod
    def get_by_video_id(db: Session, video_id: str) -> Optional[Video]:
        """Get video by YouTube video ID"""
        return db.query(Video).filter(Video.video_id == video_id).first()
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Video]:
        """Get video by URL"""
        return db.query(Video).filter(Video.url == url).first()
    
    @staticmethod
    def get_by_source(db: Session, source_id: int, limit: Optional[int] = None) -> List[Video]:
        """Get videos by source"""
        query = db.query(Video).filter(Video.source_id == source_id).order_by(Video.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_recent(db: Session, hours: int = 24, limit: Optional[int] = None) -> List[Video]:
        """Get recent videos within specified hours"""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = db.query(Video).filter(Video.published_at >= cutoff).order_by(Video.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_without_transcript(db: Session, limit: Optional[int] = None) -> List[Video]:
        """Get videos without transcripts"""
        query = db.query(Video).filter(Video.transcript.is_(None)).order_by(Video.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_all(db: Session, limit: Optional[int] = None) -> List[Video]:
        """Get all videos"""
        query = db.query(Video).order_by(Video.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update_transcript(db: Session, video_id: int, transcript: str) -> Optional[Video]:
        """Update video transcript"""
        video = VideoRepository.get_by_id(db, video_id)
        if video:
            video.transcript = transcript
            video.transcript_fetched_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def update(db: Session, video_id: int, **kwargs) -> Optional[Video]:
        """Update video"""
        video = VideoRepository.get_by_id(db, video_id)
        if video:
            for key, value in kwargs.items():
                setattr(video, key, value)
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def delete(db: Session, video_id: int) -> bool:
        """Delete video"""
        video = VideoRepository.get_by_id(db, video_id)
        if video:
            db.delete(video)
            db.commit()
            return True
        return False
    
    @staticmethod
    def exists_by_video_id(db: Session, video_id: str) -> bool:
        """Check if video exists by YouTube video ID"""
        return db.query(Video).filter(Video.video_id == video_id).first() is not None


class UserSettingsRepository:
    """Repository for UserSettings operations"""
    
    @staticmethod
    def create(db: Session, email: str, system_prompt: Optional[str] = None,
               name: Optional[str] = None, background: Optional[str] = None,
               interests: Optional[str] = None) -> UserSettings:
        """Create user settings"""
        user_settings = UserSettings(
            email=email,
            system_prompt=system_prompt,
            name=name,
            background=background,
            interests=interests
        )
        db.add(user_settings)
        db.commit()
        db.refresh(user_settings)
        return user_settings
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[UserSettings]:
        """Get user settings by ID"""
        return db.query(UserSettings).filter(UserSettings.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserSettings]:
        """Get user settings by email"""
        return db.query(UserSettings).filter(UserSettings.email == email).first()
    
    @staticmethod
    def get_all(db: Session) -> List[UserSettings]:
        """Get all user settings"""
        return db.query(UserSettings).all()
    
    @staticmethod
    def update(db: Session, user_id: int, **kwargs) -> Optional[UserSettings]:
        """Update user settings"""
        user_settings = UserSettingsRepository.get_by_id(db, user_id)
        if user_settings:
            for key, value in kwargs.items():
                setattr(user_settings, key, value)
            user_settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user_settings)
        return user_settings
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Delete user settings"""
        user_settings = UserSettingsRepository.get_by_id(db, user_id)
        if user_settings:
            db.delete(user_settings)
            db.commit()
            return True
        return False


class DigestRepository:
    """Repository for Digest operations"""
    
    @staticmethod
    def create(db: Session, url: str, title: str, summary: str, content_type: str,
               article_id: Optional[int] = None, video_id: Optional[int] = None,
               published_at: Optional[datetime] = None) -> Digest:
        """
        Create a new digest
        
        Args:
            db: Database session
            url: Content URL
            title: Digest title
            summary: Digest summary
            content_type: Content type ('article' or 'video')
            article_id: Optional article ID
            video_id: Optional video ID
            published_at: Original publish date (will be used for created_at)
        """
        digest = Digest(
            article_id=article_id,
            video_id=video_id,
            url=url,
            title=title,
            summary=summary,
            content_type=content_type,
            created_at=published_at if published_at else datetime.now(timezone.utc)
        )
        db.add(digest)
        db.commit()
        db.refresh(digest)
        return digest
    
    @staticmethod
    def get_by_id(db: Session, digest_id: int) -> Optional[Digest]:
        """Get digest by ID"""
        return db.query(Digest).filter(Digest.id == digest_id).first()
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Digest]:
        """Get digest by URL"""
        return db.query(Digest).filter(Digest.url == url).first()
    
    @staticmethod
    def get_by_article_id(db: Session, article_id: int) -> Optional[Digest]:
        """Get digest by article ID"""
        return db.query(Digest).filter(Digest.article_id == article_id).first()
    
    @staticmethod
    def get_by_video_id(db: Session, video_id: int) -> Optional[Digest]:
        """Get digest by video ID"""
        return db.query(Digest).filter(Digest.video_id == video_id).first()
    
    @staticmethod
    def get_all(db: Session, limit: Optional[int] = None) -> List[Digest]:
        """Get all digests"""
        query = db.query(Digest).order_by(Digest.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_recent(db: Session, hours: int = 24, limit: Optional[int] = None) -> List[Digest]:
        """Get recent digests within specified hours"""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = db.query(Digest).filter(Digest.created_at >= cutoff).order_by(Digest.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def exists_by_url(db: Session, url: str) -> bool:
        """Check if digest exists by URL"""
        return db.query(Digest).filter(Digest.url == url).first() is not None
    
    @staticmethod
    def delete(db: Session, digest_id: int) -> bool:
        """Delete digest"""
        digest = DigestRepository.get_by_id(db, digest_id)
        if digest:
            db.delete(digest)
            db.commit()
            return True
        return False

