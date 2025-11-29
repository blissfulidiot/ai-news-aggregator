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


class EmailContent(BaseModel):
    """Complete email content structure"""
    greeting: str = Field(..., description="Personalized greeting with user's name")
    date_line: str = Field(..., description="Formatted date line (e.g., 'Friday, November 28th')")
    introduction: str = Field(..., description="Introduction summary of the top articles")
    ranked_items: List[dict] = Field(..., description="List of ranked digest items with title, summary, url, and rank")


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
    
    def generate_email_content(self, user_name: str, ranked_items: List[dict], 
                              date: Optional[datetime] = None) -> EmailContent:
        """
        Generate complete email content structure
        
        Args:
            user_name: User's name for personalization
            ranked_items: List of ranked digest items (will use top 10)
            date: Date for the email (defaults to today)
            
        Returns:
            EmailContent with greeting, date, introduction, and ranked items
        """
        # Take top 10 items
        top_items = ranked_items[:10]
        
        if not top_items:
            raise ValueError("No ranked items provided")
        
        # Generate greeting
        greeting = f"Hey {user_name},"
        
        # Format date
        date_line = self._format_date(date)
        
        # Generate introduction
        introduction = self.generate_introduction(top_items)
        
        # Prepare ranked items for email (include rank, title, summary, url)
        email_items = [
            {
                "rank": item.get("rank", i+1),
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "url": item.get("url", ""),
                "relevance_score": item.get("relevance_score", 0.0),
                "content_type": item.get("content_type", "unknown")
            }
            for i, item in enumerate(top_items)
        ]
        
        return EmailContent(
            greeting=greeting,
            date_line=date_line,
            introduction=introduction,
            ranked_items=email_items
        )
    
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
        .article {{
            margin: 25px 0;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .rank {{
            display: inline-block;
            background-color: #4A90E2;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }}
        .title {{
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .title a {{
            color: #4A90E2;
            text-decoration: none;
        }}
        .title a:hover {{
            text-decoration: underline;
        }}
        .summary {{
            color: #555;
            margin: 10px 0;
            line-height: 1.6;
        }}
        .url {{
            color: #999;
            font-size: 12px;
            margin-top: 5px;
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
        <div class="greeting">{email_content.greeting}</div>
        <div class="date">Here is your daily news for {email_content.date_line}</div>
    </div>
    
    <div class="introduction">
        {email_content.introduction}
    </div>
    
    <div class="articles">
"""
        
        for item in email_content.ranked_items:
            html += f"""
        <div class="article">
            <span class="rank">#{item['rank']}</span>
            <div class="title">
                <a href="{item['url']}" target="_blank">{item['title']}</a>
            </div>
            <div class="summary">{item['summary']}</div>
            <div class="url">{item['url']}</div>
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
        text = f"""{email_content.greeting}
Here is your daily news for {email_content.date_line}

{email_content.introduction}

"""
        
        for item in email_content.ranked_items:
            text += f"""
#{item['rank']} {item['title']}
{item['summary']}
{item['url']}

"""
        
        text += "\n---\nThis is your personalized news digest, ranked by relevance to your interests."
        
        return text

