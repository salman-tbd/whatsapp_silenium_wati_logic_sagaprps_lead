#!/usr/bin/env python3
"""
WhatsApp Lead Automation - Production Runner
============================================

This script runs the WhatsApp lead automation with real leads from the API.
Make sure to:
1. Update your .env file with correct API tokens
2. Ensure WhatsApp Web is accessible
3. Be ready to scan QR code if needed

Usage: python run_whatsapp_automation.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Import the main automation class
from lead_automation_selenium_whatsapp import EnhancedLeadAutomation, opt_logger

def main():
    """Run WhatsApp lead automation with real leads"""
    print("🚀 WHATSAPP LEAD AUTOMATION - PRODUCTION MODE")
    print("=" * 55)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify configuration
    api_token = os.getenv('LEAD_API_TOKEN', '')
    if not api_token or api_token == 'Token your_token_here':
        print("❌ ERROR: Please update LEAD_API_TOKEN in your .env file")
        print("   Get your token from the lead management system")
        return False
    
    print("🔧 Configuration:")
    print(f"   📊 Lead API: {os.getenv('LEAD_API_URL', 'Not set')}")
    print(f"   📝 Log API: {os.getenv('LEAD_LOG_API_URL', 'Not set')}")
    print(f"   🔒 API Token: {'✅ Set' if api_token else '❌ Missing'}")
    print(f"   🧪 Test Mode: {'✅ ON' if os.getenv('USE_TEST_NUMBER', 'false').lower() == 'true' else '❌ OFF (Production)'}")
    print()
    
    # Initialize automation
    try:
        print("🔧 Initializing WhatsApp automation...")
        automation = EnhancedLeadAutomation()
        
        print("🌐 Starting WhatsApp Web session...")
        print("📱 Be ready to scan QR code if prompted!")
        print()
        
        # Start automation
        success = automation.start_automation()
        
        if success:
            print("\n🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            print("📊 Check the logs for detailed results")
        else:
            print("\n❌ AUTOMATION FAILED!")
            print("🔧 Check the logs for error details")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 AUTOMATION STOPPED BY USER")
        return False
    except Exception as e:
        print(f"\n❌ AUTOMATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("WhatsApp Lead Automation")
    print("=" * 25)
    print()
    
    # Warning message
    print("⚠️  PRODUCTION MODE WARNING:")
    print("   - This will send messages to REAL leads")
    print("   - Make sure your API credentials are correct")
    print("   - Ensure WhatsApp Web access is ready")
    print()
    
    # Confirmation
    confirm = input("Continue with production automation? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    else:
        print("🛑 Automation cancelled by user")
        sys.exit(0)
