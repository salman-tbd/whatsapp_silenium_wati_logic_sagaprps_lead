#!/usr/bin/env python3
"""
WhatsApp Automation Runner Script
Simple wrapper to run the main WhatsApp automation script
"""

import sys
import os
import subprocess

def main():
    """Run the main WhatsApp automation script"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the main automation script
        main_script = os.path.join(script_dir, 'lead_automation_selenium_whatsapp.py')
        
        if not os.path.exists(main_script):
            print("❌ ERROR: Main automation script not found!")
            print(f"   Looking for: {main_script}")
            print("   Make sure lead_automation_selenium_whatsapp.py is in the same directory")
            input("Press Enter to exit...")
            return 1
        
        print("🚀 Starting WhatsApp Multi-Team Automation...")
        print(f"📂 Script location: {main_script}")
        print("=" * 60)
        
        # Run the main script
        result = subprocess.run([sys.executable, main_script], 
                              cwd=script_dir,
                              check=False)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️ Automation stopped by user")
        return 0
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
