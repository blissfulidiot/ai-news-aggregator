"""Email agent for generating personalized email digests"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file (checks project root, then app directory)
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file if env_file.exists() else None)


class EmailIntroduction(BaseModel):
    """Structured output for email introduction"""
    introduction: str = Field(..., description="A brief, engaging introduction (2-3 sentences) summarizing what's coming in the top articles")


class ArticleSection(BaseModel):
    """A single article section in the email"""
    rank: int = Field(..., description="Rank position (1 = most relevant)")
    header: str = Field(..., description="Section header/title for the article")
    summary: str = Field(..., description="Summary of the article")
    url: str = Field(..., description="URL to the article")
    relevance_score: float = Field(..., description="Relevance score from 0.0 to 100.0")
    content_type: str = Field(..., description="Type of content: 'article' or 'video'")


class EmailContent(BaseModel):
    """Complete email content structure with sections"""
    greeting: str = Field(..., description="Personalized greeting with user's name")
    date_line: str = Field(..., description="Formatted date line (e.g., 'Friday, November 28th')")
    introduction: str = Field(..., description="Introduction summary of the top articles")
    sections: List[ArticleSection] = Field(..., description="List of article sections with headers, ordered by rank")


class EmailAgent:
    """
    Agent for generating personalized email digests from ranked news articles.
    
    Uses OpenAI's Responses API with gpt-4o-mini model to create engaging
    email introductions and structure personalized daily digests.
    """
    
    SYSTEM_PROMPT = """You are a professional email writer for a personalized news digest service. Your role is to:
1. Create engaging, personalized introductions that summarize the key themes from the top articles
2. Write in a friendly, conversational tone
3. Highlight the most interesting or important aspects of the articles
4. Keep introductions concise (2-3 sentences)
5. Make readers excited to read the articles

Your introductions should give readers a quick overview of what's coming while maintaining their interest."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the email agent
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _format_date(self, date: Optional[datetime] = None) -> str:
        """
        Format date in a readable format (e.g., "Friday, November 28th")
        
        Args:
            date: Date to format (defaults to today)
            
        Returns:
            Formatted date string
        """
        if date is None:
            date = datetime.now()
        
        # Format: "Friday, November 28th"
        day_name = date.strftime("%A")
        month_name = date.strftime("%B")
        day = date.day
        
        # Add ordinal suffix
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        
        return f"{day_name}, {month_name} {day}{suffix}"
    
    def generate_introduction(self, ranked_items: List[dict]) -> str:
        """
        Generate an introduction summary for the top ranked articles
        
        Args:
            ranked_items: List of ranked digest items (top 10)
            
        Returns:
            Introduction text summarizing the articles
        """
        if not ranked_items:
            return "Here's your personalized news digest for today."
        
        # Prepare context for the introduction
        articles_context = "\n\n".join([
            f"{i+1}. {item['title']}\n   {item.get('summary', '')[:200]}"
            for i, item in enumerate(ranked_items[:10])  # Top 10
        ])
        
        user_prompt = f"""Based on these top {len(ranked_items[:10])} ranked articles, create a brief, engaging introduction (2-3 sentences) that summarizes the key themes and highlights what makes these articles interesting or important.

Articles:
{articles_context}

Write an introduction that gives readers a quick overview and makes them excited to read more."""
        
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            text_format=EmailIntroduction,
        )
        
        return response.output_parsed.introduction
    
    def generate_email_content(self, user_name: Optional[str], ranked_items: List[dict], 
                              date: Optional[datetime] = None) -> EmailContent:
        """
        Generate complete email content structure
        
        Args:
            user_name: User's name for personalization (None or empty to skip greeting)
            ranked_items: List of ranked digest items (will use top 10)
            date: Date for the email (defaults to today)
            
        Returns:
            EmailContent with greeting, date, introduction, and sections
        """
        # Take top 10 items
        top_items = ranked_items[:10]
        
        if not top_items:
            raise ValueError("No ranked items provided")
        
        # Generate greeting (skip if no name provided)
        if user_name and user_name.strip():
            greeting = f"Hey {user_name},"
        else:
            greeting = ""
        
        # Format date
        date_line = self._format_date(date)
        
        # Generate introduction
        introduction = self.generate_introduction(top_items)
        
        # Create article sections with headers
        sections = [
            ArticleSection(
                rank=item.get("rank", i+1),
                header=item.get("title", ""),
                summary=item.get("summary", ""),
                url=item.get("url", ""),
                relevance_score=item.get("relevance_score", 0.0),
                content_type=item.get("content_type", "unknown")
            )
            for i, item in enumerate(top_items)
        ]
        
        return EmailContent(
            greeting=greeting,
            date_line=date_line,
            introduction=introduction,
            sections=sections
        )
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None if not a YouTube URL
        """
        if 'youtube.com/watch?v=' in url:
            return url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0]
        return None
    
    def format_email_html(self, email_content: EmailContent) -> str:
        """
        Format email content as HTML
        
        Args:
            email_content: EmailContent object
            
        Returns:
            HTML formatted email string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            border-bottom: 2px solid #4A90E2;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .greeting {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .date {{
            color: #666;
            font-size: 14px;
        }}
        .introduction {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 15px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #ffffff;
            border-left: 4px solid #4A90E2;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .rank-badge {{
            display: inline-block;
            background-color: #4A90E2;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-right: 15px;
            min-width: 45px;
            text-align: center;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin: 0;
            flex: 1;
        }}
        .section-title a {{
            color: #4A90E2;
            text-decoration: none;
        }}
        .section-title a:hover {{
            text-decoration: underline;
        }}
        .section-summary {{
            color: #555;
            margin: 15px 0;
            line-height: 1.7;
            font-size: 15px;
        }}
        .read-more-button {{
            display: inline-block;
            background-color: #4A90E2;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 15px;
            font-size: 14px;
        }}
        .read-more-button:hover {{
            background-color: #357ABD;
        }}
        .youtube-video {{
            margin-top: 15px;
            text-align: center;
        }}
        .youtube-thumbnail {{
            display: inline-block;
            position: relative;
            max-width: 100%;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .youtube-thumbnail img {{
            width: 100%;
            max-width: 560px;
            height: auto;
            display: block;
        }}
        .youtube-play-button {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 68px;
            height: 48px;
            background-color: rgba(23, 35, 34, 0.9);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .youtube-play-button::before {{
            content: '';
            border-style: solid;
            border-width: 12px 0 12px 20px;
            border-color: transparent transparent transparent white;
            margin-left: 4px;
        }}
        .youtube-link {{
            text-decoration: none;
            color: inherit;
        }}
        .content-type-badge {{
            display: inline-block;
            background-color: #e8e8e8;
            color: #666;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin-left: 10px;
            text-transform: uppercase;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #999;
            font-size: 12px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        {f'<div class="greeting">{email_content.greeting}</div>' if email_content.greeting else ''}
        <div class="date">Here is your daily news for {email_content.date_line}</div>
    </div>
    
    <div class="introduction">
        {email_content.introduction}
    </div>
    
    <div class="sections">
"""
        
        for section in email_content.sections:
            # Check if it's a YouTube video
            youtube_video_id = self._extract_youtube_video_id(section.url) if section.content_type == 'video' else None
            
            html += f"""
        <div class="section">
            <div class="section-header">
                <span class="rank-badge">#{section.rank}</span>
                <h2 class="section-title">
                    <a href="{section.url}" target="_blank">{section.header}</a>
                    <span class="content-type-badge">{section.content_type}</span>
                </h2>
            </div>
            <div class="section-summary">{section.summary}</div>"""
            
            # Add YouTube video thumbnail if it's a video
            if youtube_video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{youtube_video_id}/maxresdefault.jpg"
                html += f"""
            <div class="youtube-video">
                <a href="{section.url}" target="_blank" class="youtube-link">
                    <div class="youtube-thumbnail">
                        <img src="{thumbnail_url}" alt="{section.header}" />
                        <div class="youtube-play-button"></div>
                    </div>
                </a>
            </div>"""
            else:
                # Add "Read more" button only for articles (not videos)
                html += f"""
            <a href="{section.url}" target="_blank" class="read-more-button">Read more →</a>"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
    
    <div class="footer">
        <p>This is your personalized news digest, ranked by relevance to your interests.</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def format_email_text(self, email_content: EmailContent) -> str:
        """
        Format email content as plain text
        
        Args:
            email_content: EmailContent object
            
        Returns:
            Plain text formatted email string
        """
        greeting_line = f"{email_content.greeting}\n" if email_content.greeting else ""
        text = f"""{greeting_line}Here is your daily news for {email_content.date_line}

{email_content.introduction}

"""
        
        for section in email_content.sections:
            text += f"""
{'='*70}
#{section.rank} {section.header}
{'='*70}
[{section.content_type.upper()}]

{section.summary}

Read more: {section.url}

"""
        
        text += "\n" + "="*70 + "\n"
        text += "This is your personalized news digest, ranked by relevance to your interests."
        
        return text
    
    def send_email(self, to: str, email_content: EmailContent, 
                   use_html: bool = True) -> bool:
        """
        Send email using SMTP (Gmail with app password)
        
        Args:
            to: Recipient email address
            email_content: EmailContent object with email structure
            use_html: Whether to send HTML email (default: True)
            
        Returns:
            True if email sent successfully
        """
        from app.services.smtp_service import SMTPService
        
        # Format email content
        body_text = self.format_email_text(email_content)
        body_html = self.format_email_html(email_content) if use_html else None
        
        # Create subject line
        subject = f"Your Daily News Digest - {email_content.date_line}"
        
        # Send via SMTP
        smtp_service = SMTPService()
        return smtp_service.send_email(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )

