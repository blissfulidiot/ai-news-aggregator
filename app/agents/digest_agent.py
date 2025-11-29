"""Digest agent for creating summaries of articles and videos using OpenAI"""

import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file (checks project root, then app directory)
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file if env_file.exists() else None)


class DigestOutput(BaseModel):
    """Structured output for digest generation"""
    title: str = Field(..., description="A concise, engaging title for the content")
    summary: str = Field(..., description="A 2-3 sentence summary of the key points")


class DigestAgent:
    """
    Agent for generating digests (summaries) of articles and videos.
    
    Uses OpenAI's Responses API with gpt-4o-mini model and Pydantic models
    for structured outputs to generate consistent summaries with titles.
    """
    
    SYSTEM_PROMPT = """You are a professional content summarizer. Your role is to:
1. Create concise, engaging titles that capture the essence of the content
2. Write clear 2-3 sentence summaries that highlight the key points
3. Focus on the most important information and insights
4. Maintain accuracy and avoid adding information not present in the content
5. Write in a clear, professional tone suitable for a news digest

Your summaries should be informative, concise, and help readers quickly understand the main points without reading the full content."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the digest agent
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
                   Note: Responses API may require specific model versions
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_digest(self, content: str, content_type: str = "article") -> DigestOutput:
        """
        Generate a digest (title + summary) for given content
        
        Args:
            content: The content to summarize (article text, video transcript, etc.)
            content_type: Type of content ('article' or 'video')
            
        Returns:
            DigestOutput with title and summary
        """
        user_prompt = f"""Please create a digest for this {content_type}:

{content}

Provide a concise title and a 2-3 sentence summary that captures the key points."""
        
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            text_format=DigestOutput,
        )
        return response.output_parsed
    
    def generate_digest_from_article(self, title: str, description: str, 
                                     markdown_content: Optional[str] = None) -> DigestOutput:
        """
        Generate digest from article data
        
        Args:
            title: Article title
            description: Article description
            markdown_content: Optional full markdown content
            
        Returns:
            DigestOutput with title and summary
        """
        # Use markdown content if available, otherwise use description
        content = markdown_content if markdown_content else description
        
        # Include title for context
        full_content = f"Title: {title}\n\n{content}"
        
        return self.generate_digest(full_content, content_type="article")
    
    def generate_digest_from_video(self, title: str, description: str, 
                                   transcript: Optional[str] = None) -> DigestOutput:
        """
        Generate digest from video data
        
        Args:
            title: Video title
            description: Video description
            transcript: Optional video transcript
            
        Returns:
            DigestOutput with title and summary
        """
        # Use transcript if available, otherwise use description
        content = transcript if transcript else description
        
        # Include title for context
        full_content = f"Title: {title}\n\n{content}"
        
        return self.generate_digest(full_content, content_type="video")

