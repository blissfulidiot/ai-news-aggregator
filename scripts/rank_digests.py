"""Script to rank digests based on user profile"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import DigestRepository
from app.agents.news_anchor_agent import NewsAnchorAgent
from app.profiles.user_profile import UserProfile


def rank_digests_for_user(email: str, hours: int = 24):
    """
    Rank digests for a user based on their profile
    
    Args:
        email: User's email address
        hours: Number of hours to look back for digests (default: 24)
    """
    print("=" * 70)
    print(f"Ranking Digests for User: {email}")
    print("=" * 70)
    
    # Get user profile
    profile = UserProfile.get_profile(email)
    if not profile:
        print(f"\n✗ User profile not found for {email}")
        print("Please create a user profile first using:")
        print("  python scripts/manage_profile.py")
        return
    
    if not profile.get("name") or not profile.get("background") or not profile.get("interests"):
        print(f"\n✗ User profile incomplete for {email}")
        print("Please update profile with name, background, and interests")
        return
    
    print(f"\nUser Profile:")
    print(f"  Name: {profile['name']}")
    print(f"  Background: {profile['background']}")
    print(f"  Interests: {profile['interests']}")
    
    # Get recent digests
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        digests = DigestRepository.get_recent(db, hours=hours)
        
        if not digests:
            print(f"\n✓ No digests found in the last {hours} hours")
            return
        
        print(f"\nFound {len(digests)} digests from the last {hours} hours")
        
        # Initialize news anchor agent
        try:
            agent = NewsAnchorAgent()
            print("✓ News anchor agent initialized")
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            return
        
        # Prepare digest data for ranking
        digest_data = [
            {
                "id": d.id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "content_type": d.content_type
            }
            for d in digests
        ]
        
        print(f"\nRanking {len(digest_data)} digests...")
        
        # Rank digests
        ranking = agent.rank_digests(
            digests=digest_data,
            name=profile['name'],
            background=profile['background'],
            interests=profile['interests']
        )
        
        print("\n" + "=" * 70)
        print("Ranked Digests (Most Relevant First)")
        print("=" * 70)
        
        for item in ranking.ranked_items:
            print(f"\nRank {item.rank} (Score: {item.relevance_score:.1f}/100)")
            print(f"  Title: {item.title}")
            print(f"  Reason: {item.relevance_reason}")
            print(f"  URL: {item.url}")
        
        print("\n" + "=" * 70)
        print("Ranking Complete!")
        print("=" * 70)
        
        return ranking
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/rank_digests.py <email> [hours]")
        print("Example: python scripts/rank_digests.py user@example.com 24")
        sys.exit(1)
    
    email = sys.argv[1]
    hours = 24
    
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
        except ValueError:
            print(f"Invalid hours value: {sys.argv[2]}. Using default: 24 hours")
    
    rank_digests_for_user(email, hours)


if __name__ == "__main__":
    main()

