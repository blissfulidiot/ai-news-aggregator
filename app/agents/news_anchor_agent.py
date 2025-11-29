"""News anchor agent for ranking digests based on user profile"""

import os
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


class RankedItem(BaseModel):
    """Single ranked digest item"""
    digest_id: int = Field(..., description="ID of the digest")
    url: str = Field(..., description="URL of the content")
    title: str = Field(..., description="Title of the digest")
    relevance_score: float = Field(..., description="Relevance score from 0.0 to 100.0")
    rank: int = Field(..., description="Rank position (1 = most relevant)")
    relevance_reason: str = Field(..., description="Brief explanation of why this is relevant to the user")


class RankingOutput(BaseModel):
    """Structured output for digest ranking"""
    ranked_items: List[RankedItem] = Field(..., description="List of ranked digests ordered by relevance")


class NewsAnchorAgent:
    """
    Agent for ranking news digests based on user profile and interests.
    
    Uses OpenAI's Responses API with gpt-4o-mini model to rank digests
    according to user background and interests.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the news anchor agent
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _build_system_prompt(self, name: str, background: str, interests: str) -> str:
        """Build system prompt from user profile"""
        return f"""You are a personalized news anchor. Your role is to rank news articles and videos based on a user's profile and interests.

User Profile:
- Name: {name}
- Background: {background}
- Interests: {interests}

Your task:
1. Analyze each digest (title and summary) for relevance to the user's profile
2. Assign a relevance score from 0.0 to 100.0 (higher = more relevant)
3. Rank items from most relevant (rank 1) to least relevant
4. Provide a brief explanation for why each item is relevant to the user

Consider:
- How well the content matches the user's professional background
- Alignment with stated interests
- Potential value or usefulness to the user
- Overall relevance and importance

Be thoughtful and accurate in your ranking. Higher scores should reflect stronger alignment with the user's profile."""
    
    def rank_digests(self, digests: List[dict], name: str, background: str, interests: str) -> RankingOutput:
        """
        Rank digests based on user profile
        
        Args:
            digests: List of digest dictionaries with keys: id, url, title, summary, content_type
            name: User's name
            background: User's background/profession
            interests: User's interests
            
        Returns:
            RankingOutput with ranked items ordered by relevance
        """
        if not digests:
            return RankingOutput(ranked_items=[])
        
        # Build context for ranking
        digests_context = "\n\n".join([
            f"Digest {i+1}:\n"
            f"ID: {d['id']}\n"
            f"Title: {d['title']}\n"
            f"Summary: {d['summary']}\n"
            f"Type: {d.get('content_type', 'unknown')}\n"
            f"URL: {d['url']}"
            for i, d in enumerate(digests)
        ])
        
        user_prompt = f"""Please rank these {len(digests)} digests based on the user profile above.

{digests_context}

Rank them from most relevant (rank 1) to least relevant (rank {len(digests)}), assigning relevance scores from 0.0 to 100.0."""
        
        system_prompt = self._build_system_prompt(name, background, interests)
        
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            text_format=RankingOutput,
        )
        return response.output_parsed

