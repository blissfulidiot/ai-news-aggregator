"""Script to generate email content from ranked digests"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db_session
from app.database.repository import DigestRepository
from app.agents.news_anchor_agent import NewsAnchorAgent
from app.agents.email_agent import EmailAgent
from app.profiles.user_profile import UserProfile


def generate_email_for_user(email: str, hours: int = 24, output_format: str = "text"):
    """
    Generate email content for a user based on their ranked digests
    
    Args:
        email: User's email address
        hours: Number of hours to look back for digests (default: 24)
        output_format: Output format - 'text', 'html', or 'both' (default: 'text')
    """
    print("=" * 70)
    print(f"Generating Email Digest for User: {email}")
    print("=" * 70)
    
    # Get user profile
    profile = UserProfile.get_profile(email)
    if not profile:
        print(f"\n✗ User profile not found for {email}")
        print("Please create a user profile first using:")
        print("  python scripts/manage_profile.py create <email> <name> <background> <interests>")
        return
    
    if not profile.get("name"):
        print(f"\n✗ User name not set in profile for {email}")
        print("Please update profile with name")
        return
    
    user_name = profile['name']
    print(f"\nUser: {user_name} ({email})")
    
    # Get recent digests
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        digests = DigestRepository.get_recent(db, hours=hours)
        
        if not digests:
            print(f"\n✓ No digests found in the last {hours} hours")
            return
        
        print(f"\nFound {len(digests)} digests from the last {hours} hours")
        
        # Initialize agents
        try:
            ranking_agent = NewsAnchorAgent()
            email_agent = EmailAgent()
            print("✓ Agents initialized")
        except Exception as e:
            print(f"✗ Error initializing agents: {e}")
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
        ranking = ranking_agent.rank_digests(
            digests=digest_data,
            name=profile['name'],
            background=profile['background'] or "",
            interests=profile['interests'] or ""
        )
        
        # Prepare ranked items for email (include all needed fields)
        ranked_items = [
            {
                "rank": item.rank,
                "title": item.title,
                "summary": next((d['summary'] for d in digest_data if d['url'] == item.url), ""),
                "url": item.url,
                "relevance_score": item.relevance_score,
                "content_type": next((d['content_type'] for d in digest_data if d['url'] == item.url), "unknown")
            }
            for item in ranking.ranked_items[:10]  # Top 10
        ]
        
        print(f"✓ Ranked {len(ranked_items)} top digests")
        
        # Generate email content
        print("\nGenerating email content...")
        email_content = email_agent.generate_email_content(
            user_name=user_name,
            ranked_items=ranked_items,
            date=datetime.now()
        )
        
        print("✓ Email content generated")
        
        # Output based on format
        if output_format == "html" or output_format == "both":
            html_content = email_agent.format_email_html(email_content)
            print("\n" + "=" * 70)
            print("HTML Email Content")
            print("=" * 70)
            print(html_content)
            
            # Save to file
            html_file = f"email_digest_{email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n✓ HTML email saved to: {html_file}")
        
        if output_format == "text" or output_format == "both":
            text_content = email_agent.format_email_text(email_content)
            print("\n" + "=" * 70)
            print("Plain Text Email Content")
            print("=" * 70)
            print(text_content)
            
            # Save to file
            text_file = f"email_digest_{email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"\n✓ Text email saved to: {text_file}")
        
        print("\n" + "=" * 70)
        print("Email Generation Complete!")
        print("=" * 70)
        
        return email_content
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_email.py <email> [hours] [format]")
        print("Example: python scripts/generate_email.py user@example.com 24 html")
        print("\nFormats: text (default), html, both")
        sys.exit(1)
    
    email = sys.argv[1]
    hours = 24
    output_format = "text"
    
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
        except ValueError:
            print(f"Invalid hours value: {sys.argv[2]}. Using default: 24 hours")
    
    if len(sys.argv) > 3:
        output_format = sys.argv[3].lower()
        if output_format not in ["text", "html", "both"]:
            print(f"Invalid format: {output_format}. Using default: text")
            output_format = "text"
    
    generate_email_for_user(email, hours, output_format)


if __name__ == "__main__":
    main()

