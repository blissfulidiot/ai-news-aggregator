"""Test script for SMTP email sending"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.smtp_service import SMTPService


def test_smtp_connection(test_recipient: str = None):
    """Test SMTP connection and credentials"""
    print("=" * 70)
    print("Testing SMTP Configuration")
    print("=" * 70)
    
    try:
        # Initialize SMTP service
        print("\n1. Initializing SMTP service...")
        smtp_service = SMTPService()
        print(f"   ✓ SMTP Host: {smtp_service.smtp_host}")
        print(f"   ✓ SMTP Port: {smtp_service.smtp_port}")
        print(f"   ✓ From Email: {smtp_service.from_email}")
        print(f"   ✓ Username: {smtp_service.smtp_username}")
        
        # Check if credentials are placeholders
        if "your_email@gmail.com" in smtp_service.smtp_username or "your_email@gmail.com" in smtp_service.from_email:
            print("\n   ⚠ Warning: Using placeholder credentials from .env.example")
            print("   Please update your .env file with actual Gmail credentials")
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease add SMTP credentials to your .env file:")
        print("  SMTP_USERNAME=your_email@gmail.com")
        print("  SMTP_PASSWORD=your_app_password")
        print("  FROM_EMAIL=your_email@gmail.com")
        print("  SMTP_HOST=smtp.gmail.com")
        print("  SMTP_PORT=587")
        return False
    
    # Test sending email if recipient provided
    if test_recipient:
        print(f"\n2. Testing email send to {test_recipient}...")
        try:
            result = smtp_service.send_email(
                to=test_recipient,
                subject="Test Email from News Aggregator",
                body_text="This is a test email to verify SMTP configuration.",
                body_html="<html><body><h1>Test Email</h1><p>This is a test email to verify SMTP configuration.</p></body></html>"
            )
            
            if result:
                print(f"\n✓ Test email sent successfully to {test_recipient}!")
                print("   Please check your inbox (and spam folder).")
                return True
            else:
                print("\n✗ Failed to send test email")
                return False
                
        except Exception as e:
            print(f"\n✗ Error sending test email: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("\n2. Skipping email send test (no recipient provided)")
        print("\n✓ SMTP configuration looks good!")
        print("   To test sending, run: python scripts/test_smtp.py <recipient_email>")
        return True


def main():
    """Main entry point"""
    test_recipient = None
    if len(sys.argv) > 1:
        test_recipient = sys.argv[1]
    
    success = test_smtp_connection(test_recipient)
    
    if success:
        print("\n" + "=" * 70)
        print("SMTP Test Complete!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("SMTP Test Failed - Please check configuration")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

