"""Script to generate and send email digest via Gmail API"""

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


def send_email_digest(recipient_email: str, hours: int = 24, use_html: bool = True):
    """
    Generate and send email digest to a user
    
    Args:
        recipient_email: Email address to send the digest to
        hours: Number of hours to look back for digests (default: 24)
        use_html: Whether to send HTML email (default: True)
    """
    print("=" * 70)
    print(f"Sending Email Digest to: {recipient_email}")
    print("=" * 70)
    
    # Get user profile (use recipient email as profile lookup)
    profile = UserProfile.get_profile(recipient_email)
    if not profile:
        print(f"\n⚠ User profile not found for {recipient_email}")
        print("Using recipient email as profile lookup...")
        # Use recipient email as fallback
        user_name = recipient_email.split('@')[0].replace('.', ' ').title()
    else:
        user_name = profile.get('name') or recipient_email.split('@')[0].replace('.', ' ').title()
    
    print(f"\nUser: {user_name} ({recipient_email})")
    
    # Get recent digests
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        digests = DigestRepository.get_recent(db, hours=hours)
        
        if not digests:
            print(f"\n✓ No digests found in the last {hours} hours")
            print("Nothing to send.")
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
        
        # Rank digests (use profile if available, otherwise use defaults)
        if profile and profile.get('background') and profile.get('interests'):
            ranking = ranking_agent.rank_digests(
                digests=digest_data,
                name=user_name,
                background=profile.get('background', ''),
                interests=profile.get('interests', '')
            )
        else:
            # Default ranking without profile
            print("⚠ No profile found - using default ranking")
            ranking = ranking_agent.rank_digests(
                digests=digest_data,
                name=user_name,
                background="General interest",
                interests="Technology, news, current events"
            )
        
        # Prepare ranked items for email
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
        
        # Send email
        print(f"\nSending email to {recipient_email}...")
        try:
            result = email_agent.send_email(
                to=recipient_email,
                email_content=email_content,
                use_html=use_html
            )
            
            if result:
                print(f"✓ Email sent successfully!")
            else:
                print(f"✗ Failed to send email")
            
        except ValueError as e:
            print(f"\n✗ SMTP credentials not configured")
            print("Please set up Gmail SMTP credentials in your .env file:")
            print("1. Enable 2-factor authentication on your Gmail account")
            print("2. Generate an app password:")
            print("   - Go to https://myaccount.google.com/apppasswords")
            print("   - Select 'Mail' and 'Other (Custom name)'")
            print("   - Enter 'News Aggregator' as the name")
            print("   - Copy the generated 16-character app password")
            print("3. Add to your .env file:")
            print("   SMTP_USERNAME=your_email@gmail.com")
            print("   SMTP_PASSWORD=your_16_char_app_password")
            print("   FROM_EMAIL=your_email@gmail.com")
            print("   SMTP_HOST=smtp.gmail.com")
            print("   SMTP_PORT=587")
        except Exception as e:
            print(f"\n✗ Error sending email: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/send_email_digest.py <recipient_email> [hours] [html|text]")
        print("Example: python scripts/send_email_digest.py user@example.com 24 html")
        print("\nNote: First run will require Gmail API authentication")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    hours = 24
    use_html = True
    
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
        except ValueError:
            print(f"Invalid hours value: {sys.argv[2]}. Using default: 24 hours")
    
    if len(sys.argv) > 3:
        format_arg = sys.argv[3].lower()
        use_html = format_arg == "html"
    
    send_email_digest(recipient_email, hours, use_html)


if __name__ == "__main__":
    main()

