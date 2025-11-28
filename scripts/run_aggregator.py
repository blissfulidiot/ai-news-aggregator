"""Main script to run the news aggregator"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.runner import run_aggregator, NewsAggregator


def main():
    """Main entry point"""
    # Parse hours from command line if provided
    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Invalid hours value: {sys.argv[1]}. Using default: 24 hours")
            hours = 24
    
    print("=" * 70)
    print(f"News Aggregator - Fetching content from last {hours} hours")
    print("=" * 70)
    print()
    
    results = run_aggregator(hours=hours)
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total articles: {len(results['articles'])}")
    print(f"Total videos: {len(results['videos'])}")
    print(f"\nBreakdown:")
    for source, count in results["summary"].items():
        print(f"  {source}: {count}")
    
    if results["articles"]:
        print("\n" + "=" * 70)
        print("Sample Articles (first 5)")
        print("=" * 70)
        for i, article in enumerate(results["articles"][:5], 1):
            print(f"\n{i}. {article.title}")
            print(f"   Source: {article.source_name}")
            if hasattr(article, 'feed_type'):
                print(f"   Feed: {article.feed_type}")
            print(f"   Published: {article.published_at}")
            print(f"   URL: {article.url[:70]}...")
    
    if results["videos"]:
        print("\n" + "=" * 70)
        print("Sample Videos (first 5)")
        print("=" * 70)
        for i, video in enumerate(results["videos"][:5], 1):
            print(f"\n{i}. {video.title}")
            print(f"   Channel: {video.channel_name}")
            print(f"   Published: {video.published_at}")
            print(f"   URL: {video.url}")
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()

