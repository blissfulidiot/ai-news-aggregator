"""Configuration for news aggregator sources"""

# YouTube channels to scrape
# Format: List of dictionaries with 'username' and optional 'name'
YOUTUBE_CHANNELS = [
    {"username": "CNBCtelevision", "name": "CNBC Television"},
    # Add more channels here as needed
    # Example: {"username": "@channelname", "name": "Display Name"},
]

# RSS feed URLs for news sources
RSS_FEEDS = {
    "openai": "https://openai.com/news/rss",
    # Add more RSS feeds here
    # Example: "source_name": "https://example.com/rss.xml",
}

