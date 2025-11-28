"""Script to create database tables"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import init_db, engine
from app.database.models import Base


def main():
    """Create all database tables"""
    print("=" * 70)
    print("Creating Database Tables")
    print("=" * 70)
    
    try:
        # Create all tables
        print("\nInitializing database...")
        init_db()
        
        print("✓ Tables created successfully!")
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        print("\n" + "=" * 70)
        print("Database initialization complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

