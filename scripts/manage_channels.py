"""Helper script to manage YouTube channels"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import YOUTUBE_CHANNELS


def list_channels():
    """List all configured YouTube channels"""
    print("=" * 70)
    print("Configured YouTube Channels")
    print("=" * 70)
    
    if not YOUTUBE_CHANNELS:
        print("\nNo channels configured.")
        print("\nTo add channels, edit app/config.py and add entries to YOUTUBE_CHANNELS:")
        print('  YOUTUBE_CHANNELS = [')
        print('      {"username": "channelname", "name": "Display Name"},')
        print('  ]')
        return
    
    print(f"\nTotal channels: {len(YOUTUBE_CHANNELS)}\n")
    
    for i, channel in enumerate(YOUTUBE_CHANNELS, 1):
        username = channel.get('username', 'N/A')
        name = channel.get('name', username)
        print(f"{i}. {name}")
        print(f"   Username: {username}")
        print()


def show_instructions():
    """Show instructions for managing channels"""
    print("=" * 70)
    print("How to Manage YouTube Channels")
    print("=" * 70)
    
    print("""
To add or remove YouTube channels, edit the file:
  app/config.py

The YOUTUBE_CHANNELS list accepts channels in these formats:

1. Simple username:
   {"username": "CNBCtelevision"}

2. With display name:
   {"username": "CNBCtelevision", "name": "CNBC Television"}

3. With @ symbol:
   {"username": "@CNBCtelevision"}

4. Full URL (will extract username):
   {"username": "https://www.youtube.com/@CNBCtelevision"}

Examples:
  YOUTUBE_CHANNELS = [
      {"username": "CNBCtelevision", "name": "CNBC Television"},
      {"username": "@channelname", "name": "Display Name"},
      {"username": "anotherchannel"},
  ]

After editing config.py, restart the aggregator to use the new channels.
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        show_instructions()
    else:
        list_channels()
        print("\nRun 'python scripts/manage_channels.py help' for instructions")

