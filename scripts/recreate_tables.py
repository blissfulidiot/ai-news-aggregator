"""Script to drop and recreate database tables with new constraints"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import engine
from app.database.models import Base
from sqlalchemy.exc import SQLAlchemyError


def main():
    """Drop and recreate all database tables"""
    print("=" * 70)
    print("Recreating Database Tables")
    print("=" * 70)
    
    try:
        # Drop all tables
        print("\nDropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ Tables dropped successfully!")
        
        # Create all tables with new constraints
        print("\nCreating tables with new constraints...")
        Base.metadata.create_all(bind=engine)
        
        print("✓ Tables created successfully!")
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        print("\nUnique constraints added:")
        print("  - sources.url: UNIQUE")
        print("  - sources.rss_url: UNIQUE")
        print("  - sources.youtube_channel_id: UNIQUE")
        print("  - sources.youtube_username: UNIQUE")
        
        print("\nNew tables:")
        print("  - digests: Stores AI-generated summaries with title and summary")
        
        print("\n" + "=" * 70)
        print("Database recreation complete!")
        print("=" * 70)
        
    except SQLAlchemyError as e:
        print(f"\n✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

