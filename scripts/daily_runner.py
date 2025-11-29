"""Daily runner script that combines all pipeline steps:
1. Scrape and save data to database
2. Generate digests for new items
3. Send email digests to all users
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.runner import run_aggregator
from app.database.connection import get_db_session
from app.database.repository import (
    ArticleRepository, VideoRepository, DigestRepository, UserSettingsRepository
)
from app.agents.digest_agent import DigestAgent
from app.agents.news_anchor_agent import NewsAnchorAgent
from app.agents.email_agent import EmailAgent
from app.profiles.user_profile import UserProfile


def scrape_and_save(hours: int = 24):
    """
    Step 1: Scrape content and save to database
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        Dictionary with scraping results
    """
    print("\n" + "=" * 70)
    print("STEP 1: Scraping Content and Saving to Database")
    print("=" * 70)
    
    try:
        results = run_aggregator(hours=hours, fetch_transcripts=False, save_to_db=True)
        
        print(f"\n✓ Scraping complete:")
        print(f"  Articles found: {len(results.get('articles', []))}")
        print(f"  Videos found: {len(results.get('videos', []))}")
        
        return results
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_digests(batch_size: int = 10):
    """
    Step 2: Generate digests for items without them
    
    Args:
        batch_size: Number of items to process before showing progress
        
    Returns:
        Tuple of (successful_count, failed_count)
    """
    print("\n" + "=" * 70)
    print("STEP 2: Generating Digests")
    print("=" * 70)
    
    # Initialize digest agent
    try:
        agent = DigestAgent()
        print("✓ Digest agent initialized")
    except Exception as e:
        print(f"✗ Error initializing digest agent: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")
        return (0, 0)
    
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        # Get items without digests
        articles = ArticleRepository.get_all(db)
        videos = VideoRepository.get_all(db)
        
        articles_to_process = [
            a for a in articles 
            if not DigestRepository.exists_by_url(db, a.url)
        ]
        videos_to_process = [
            v for v in videos 
            if not DigestRepository.exists_by_url(db, v.url)
        ]
        
        total_count = len(articles_to_process) + len(videos_to_process)
        
        if total_count == 0:
            print("\n✓ All items already have digests!")
            return (0, 0)
        
        print(f"\nFound {len(articles_to_process)} articles and {len(videos_to_process)} videos to process")
        print(f"Processing in batches of {batch_size}...\n")
        
        successful = 0
        failed = 0
        
        def process_item(item, item_type: str, item_id: int):
            nonlocal successful, failed
            processed = successful + failed + 1
            
            try:
                if processed % batch_size == 0 or processed == 1:
                    print(f"[{processed}/{total_count}] Processing {item_type}: {item.title[:60]}...")
                
                if item_type == "article":
                    digest_output = agent.generate_digest_from_article(
                        title=item.title,
                        description=item.description or "",
                        markdown_content=item.markdown_content
                    )
                    DigestRepository.create(
                        db, url=item.url, title=digest_output.title,
                        summary=digest_output.summary, content_type="article",
                        article_id=item_id, published_at=item.published_at
                    )
                else:  # video
                    digest_output = agent.generate_digest_from_video(
                        title=item.title,
                        description=item.description or "",
                        transcript=item.transcript
                    )
                    DigestRepository.create(
                        db, url=item.url, title=digest_output.title,
                        summary=digest_output.summary, content_type="video",
                        video_id=item_id, published_at=item.published_at
                    )
                
                successful += 1
                
                if processed % batch_size == 0:
                    print(f"  Progress: {successful} successful, {failed} failed\n")
                
            except Exception as e:
                failed += 1
                if processed % batch_size == 0:
                    print(f"  ✗ Error: {e}")
                db.rollback()
        
        for article in articles_to_process:
            process_item(article, "article", article.id)
        
        for video in videos_to_process:
            process_item(video, "video", video.id)
        
        print(f"\n✓ Digest generation complete:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        return (successful, failed)
        
    except Exception as e:
        print(f"\n✗ Error during digest generation: {e}")
        import traceback
        traceback.print_exc()
        return (0, 0)
    finally:
        db.close()


def send_email_digests(hours: int = 24, use_html: bool = True):
    """
    Step 3: Send email digests to all users
    
    Args:
        hours: Number of hours to look back for digests
        use_html: Whether to send HTML emails
        
    Returns:
        Dictionary with sending results
    """
    print("\n" + "=" * 70)
    print("STEP 3: Sending Email Digests")
    print("=" * 70)
    
    # Get all users from database
    db_gen = get_db_session()
    db = next(db_gen)
    
    try:
        users = UserSettingsRepository.get_all(db)
        
        if not users:
            print("\n⚠ No users found in database")
            print("Add users using: python scripts/manage_profile.py create <email> <name> <background> <interests>")
            return {"sent": 0, "failed": 0, "total": 0}
        
        print(f"\nFound {len(users)} user(s) to send emails to")
        
        # Initialize agents
        try:
            ranking_agent = NewsAnchorAgent()
            email_agent = EmailAgent()
            print("✓ Agents initialized")
        except Exception as e:
            print(f"✗ Error initializing agents: {e}")
            return {"sent": 0, "failed": 0, "total": len(users)}
        
        # Get recent digests
        digests = DigestRepository.get_recent(db, hours=hours)
        
        if not digests:
            print(f"\n⚠ No digests found in the last {hours} hours")
            print("Nothing to send.")
            return {"sent": 0, "failed": 0, "total": len(users)}
        
        print(f"Found {len(digests)} digests from the last {hours} hours")
        
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
        
        sent_count = 0
        failed_count = 0
        
        # Send email to each user
        for user in users:
            user_email = user.email
            print(f"\nProcessing user: {user_email}")
            
            try:
                # Get user profile
                profile = UserProfile.get_profile(user_email)
                user_name = None
                if profile:
                    user_name = profile.get('name') if profile.get('name') and profile.get('name').strip() else None
                
                # Rank digests
                if profile and profile.get('background') and profile.get('interests'):
                    ranking = ranking_agent.rank_digests(
                        digests=digest_data,
                        name=user_name or "",
                        background=profile.get('background', ''),
                        interests=profile.get('interests', '')
                    )
                else:
                    # Default ranking
                    ranking = ranking_agent.rank_digests(
                        digests=digest_data,
                        name=user_name or "",
                        background="General interest",
                        interests="Technology, news, current events"
                    )
                
                # Prepare ranked items
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
                
                # Generate email content
                email_content = email_agent.generate_email_content(
                    user_name=user_name,
                    ranked_items=ranked_items,
                    date=datetime.now()
                )
                
                # Send email
                result = email_agent.send_email(
                    to=user_email,
                    email_content=email_content,
                    use_html=use_html
                )
                
                if result:
                    sent_count += 1
                    print(f"  ✓ Email sent successfully")
                else:
                    failed_count += 1
                    print(f"  ✗ Failed to send email")
                    
            except Exception as e:
                failed_count += 1
                print(f"  ✗ Error sending email: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n✓ Email sending complete:")
        print(f"  Sent: {sent_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total users: {len(users)}")
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(users)
        }
        
    except Exception as e:
        print(f"\n✗ Error during email sending: {e}")
        import traceback
        traceback.print_exc()
        return {"sent": 0, "failed": 0, "total": 0}
    finally:
        db.close()


def run_daily_pipeline(hours: int = 24, use_html: bool = True, skip_scraping: bool = False):
    """
    Run the complete daily pipeline
    
    Args:
        hours: Number of hours to look back for content
        use_html: Whether to send HTML emails
        skip_scraping: Skip scraping step (useful for testing)
        
    Returns:
        Dictionary with pipeline results
    """
    start_time = datetime.now()
    
    print("=" * 70)
    print("DAILY NEWS AGGREGATOR PIPELINE")
    print("=" * 70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Looking back: {hours} hours")
    
    results = {
        "start_time": start_time,
        "scraping": None,
        "digests": None,
        "emails": None,
        "end_time": None,
        "success": False
    }
    
    # Step 1: Scrape and save
    if not skip_scraping:
        scraping_results = scrape_and_save(hours=hours)
        results["scraping"] = scraping_results
        if scraping_results is None:
            print("\n✗ Pipeline stopped due to scraping errors")
            return results
    else:
        print("\n" + "=" * 70)
        print("STEP 1: Scraping (SKIPPED)")
        print("=" * 70)
        print("✓ Skipping scraping step")
    
    # Step 2: Generate digests
    successful_digests, failed_digests = generate_digests()
    results["digests"] = {
        "successful": successful_digests,
        "failed": failed_digests
    }
    
    # Step 3: Send emails
    email_results = send_email_digests(hours=hours, use_html=use_html)
    results["emails"] = email_results
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    results["end_time"] = end_time
    results["success"] = True
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"Duration: {duration}")
    print(f"\nSummary:")
    if results["scraping"]:
        print(f"  Articles scraped: {len(results['scraping'].get('articles', []))}")
        print(f"  Videos scraped: {len(results['scraping'].get('videos', []))}")
    print(f"  Digests generated: {results['digests']['successful']}")
    print(f"  Emails sent: {results['emails']['sent']}/{results['emails']['total']}")
    print("=" * 70)
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily news aggregator pipeline")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back for content (default: 24)"
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Send plain text emails instead of HTML"
    )
    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip the scraping step (useful for testing)"
    )
    
    args = parser.parse_args()
    
    run_daily_pipeline(
        hours=args.hours,
        use_html=not args.text,
        skip_scraping=args.skip_scraping
    )


if __name__ == "__main__":
    main()

