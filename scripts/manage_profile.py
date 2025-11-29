"""Script to manage user profiles"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.profiles.user_profile import UserProfile


def create_profile(email: str, name: str, background: str, interests: str):
    """Create or update user profile"""
    print("=" * 70)
    print("Creating/Updating User Profile")
    print("=" * 70)
    
    profile = UserProfile.create_or_update(
        email=email,
        name=name,
        background=background,
        interests=interests
    )
    
    print(f"\n✓ Profile saved for {email}")
    print(f"\nProfile Details:")
    print(f"  Name: {profile['name']}")
    print(f"  Background: {profile['background']}")
    print(f"  Interests: {profile['interests']}")
    print("=" * 70)


def show_profile(email: str):
    """Show user profile"""
    profile = UserProfile.get_profile(email)
    
    if not profile:
        print(f"\n✗ Profile not found for {email}")
        return
    
    print("=" * 70)
    print(f"User Profile: {email}")
    print("=" * 70)
    print(f"  Name: {profile.get('name', 'Not set')}")
    print(f"  Background: {profile.get('background', 'Not set')}")
    print(f"  Interests: {profile.get('interests', 'Not set')}")
    print(f"  System Prompt: {profile.get('system_prompt', 'Not set')}")
    print("=" * 70)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Create/Update: python scripts/manage_profile.py create <email> <name> <background> <interests>")
        print("  Show: python scripts/manage_profile.py show <email>")
        print("\nExample:")
        print('  python scripts/manage_profile.py create john@example.com "John Doe" "Software engineer with 10 years experience" "AI, machine learning, Python, web development"')
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create" and len(sys.argv) >= 6:
        email = sys.argv[2]
        name = sys.argv[3]
        background = sys.argv[4]
        interests = sys.argv[5]
        create_profile(email, name, background, interests)
    elif command == "show" and len(sys.argv) >= 3:
        email = sys.argv[2]
        show_profile(email)
    else:
        print("Invalid command or missing arguments")
        print("Usage:")
        print("  Create: python scripts/manage_profile.py create <email> <name> <background> <interests>")
        print("  Show: python scripts/manage_profile.py show <email>")


if __name__ == "__main__":
    main()

