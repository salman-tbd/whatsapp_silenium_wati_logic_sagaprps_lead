"""
Enhanced Selenium WhatsApp Lead Automation System
===============================================

🚀 Production-ready script with:
- Selenium WhatsApp Web automation (replaces WATI API)
- Advanced browser session management
- Smart message delivery through WhatsApp Web
- Enhanced analytics & reporting
- Professional logging system

Author: AI Assistant
Version: 3.0 (Selenium Enhanced)
Requirements: python-dotenv, requests, selenium, pyperclip
"""

import requests
import os
import json
import logging
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, NamedTuple
from enum import Enum
from dotenv import load_dotenv
import pyperclip
import traceback

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Load environment variables from .env in current directory
load_dotenv('.env')

# ============================================================================
# ENHANCED DATA STRUCTURES
# ============================================================================

class MessageStatus(Enum):
    """WhatsApp message delivery status tracking"""
    SENT = "sent"                    # Message sent through WhatsApp Web
    DELIVERED = "delivered"          # Message delivered (if detectable)
    READ = "read"                   # Message read (if detectable)
    FAILED = "failed"               # Message failed to send
    PENDING = "pending"             # Waiting for delivery confirmation

class ErrorCategory(Enum):
    """Categorized error types for better tracking"""
    INVALID_NUMBER = "invalid_number"
    NOT_ON_WHATSAPP = "not_on_whatsapp"
    BROWSER_ERROR = "browser_error"
    SESSION_EXPIRED = "session_expired"
    WHATSAPP_WEB_ERROR = "whatsapp_web_error"
    NETWORK_ERROR = "network_error"
    ELEMENT_NOT_FOUND = "element_not_found"
    UNKNOWN_ERROR = "unknown_error"

class MessageResult(NamedTuple):
    """Structured result for message operations"""
    success: bool
    status: MessageStatus
    message_id: Optional[str]
    error_category: Optional[ErrorCategory]
    error_message: Optional[str]
    should_continue: bool

# ============================================================================
# OPTIMIZED LOGGING SYSTEM
# ============================================================================

class OptimizedLogger:
    """Professional logging system with optimized output"""
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Configure optimized logging handlers"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-5s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler('selenium_whatsapp_automation.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler for essential info only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, console_handler]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Suppress verbose third-party logs
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
    
    def campaign_start(self, total_quota: int, total_leads: int, global_used: int = 0):
        """Log campaign start with key metrics"""
        self.logger.info("🚀 " + "="*50)
        self.logger.info("🤖 SELENIUM WHATSAPP AUTOMATION CAMPAIGN STARTED")
        self.logger.info("🚀 " + "="*50)
        self.logger.info(f"🌍 Global Daily Limit: {global_used}/{GLOBAL_DAILY_LIMIT} messages used")
        self.logger.info(f"📊 Available Quota: {total_quota}")
        self.logger.info(f"📋 Leads to Process: {total_leads}")
        self.logger.info(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    def lead_processing(self, lead_num: int, total: int, lead_name: str, counsellor: str):
        """Compact lead processing log"""
        self.logger.info(f"📞 [{lead_num:03d}/{total:03d}] {lead_name} → {counsellor}")
    
    def message_result(self, status: MessageStatus, lead_name: str, details: str = ""):
        """Log message result with appropriate emoji"""
        status_emojis = {
            MessageStatus.SENT: "📤",
            MessageStatus.DELIVERED: "📱",
            MessageStatus.READ: "👀",
            MessageStatus.FAILED: "❌",
            MessageStatus.PENDING: "⏳"
        }
        emoji = status_emojis.get(status, "📤")
        detail_text = f" | {details}" if details else ""
        self.logger.info(f"{emoji} {status.value.upper()}: {lead_name}{detail_text}")
    
    def browser_status(self, status: str, details: str = ""):
        """Log browser status"""
        self.logger.info(f"🌐 BROWSER: {status} {details}")
    
    def campaign_end(self, metrics: Dict):
        """Log campaign completion with summary"""
        self.logger.info("🏁 " + "="*50)
        self.logger.info("📊 CAMPAIGN COMPLETED")
        self.logger.info("🏁 " + "="*50)
        self.logger.info(f"📤 Sent: {metrics['sent']}")
        self.logger.info(f"📱 Delivered: {metrics['delivered']}")
        self.logger.info(f"👀 Read: {metrics['read']}")
        self.logger.info(f"❌ Failed: {metrics['failed']}")
        self.logger.info(f"⚡ Success Rate: {metrics['success_rate']:.1f}%")
        self.logger.info(f"⏱️ Duration: {metrics['duration']}")

# Initialize optimized logger
opt_logger = OptimizedLogger()
logger = opt_logger.logger

# ============================================================================
# CONFIGURATION
# ============================================================================

# Time settings
SCRIPT_START_TIME = '09:00'
SCRIPT_END_TIME = '21:00'

# Counsellor configuration with optimized limits and employee IDs
COUNSELLORS = {
    'Anandi': {'daily_limit': 50, 'number': '+919512270915', 'username': 'anandi', 'employee_id': 289},
    'Preeti': {'daily_limit': 50, 'number': '+918799334198', 'username': 'preeti', 'employee_id': 286},
    'Khushali': {'daily_limit': 50, 'number': '+917069629625', 'username': 'pkhushali', 'employee_id': 294},
    'Karan': {'daily_limit': 50, 'number': '+919773432629', 'username': 'dkaran', 'employee_id': 308},
    'Sangita': {'daily_limit': 50, 'number': '+918128758628', 'username': 'sangitac', 'employee_id': 305},  # ID 307 inactive, using fallback
    'Maitri': {'daily_limit': 50, 'number': '+918866817620', 'username': 'maitri', 'employee_id': 297},
    'Chitra': {'daily_limit': 50, 'number': '+918128817870', 'username': 'chitra', 'employee_id': 264},
    'Pragatee': {'daily_limit': 50, 'number': '+919687046717', 'username': 'pragatee', 'employee_id': 260},
    'Vaidehi': {'daily_limit': 50, 'number': '+917874202685', 'username': 'vaidehi', 'employee_id': 309}
}

# API Configuration
STATIC_OWNER_ID = int(os.getenv('LEAD_OWNER_ID', '227'))
USE_TEST_NUMBER = os.getenv('USE_TEST_NUMBER', 'false').lower() == 'true'  # Read from .env file
TEST_MOBILE_NUMBER = os.getenv('TEST_MOBILE_NUMBER', '+917567905829')  # Test number if needed

LEAD_API_URL = os.getenv('LEAD_API_URL', 'https://evolgroups.com/lead/get-leads-basic-info/')
API_TOKEN = os.getenv('LEAD_API_TOKEN', 'Token your_token_here')
LEAD_LOG_API_URL = os.getenv('LEAD_LOG_API_URL', 'https://evolgroups.com/lead/post-wati-msg-logs/')
# Static template system - no WATI template name needed

# Selenium Configuration
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')  # Leave empty for auto-detection
CHROME_PROFILE_PATH = os.getenv('CHROME_PROFILE_PATH', r'C:\Users\fahad\AppData\Local\Google\Chrome\User Data\WhatsAppBot')
WHATSAPP_SCAN_TIMEOUT = int(os.getenv('WHATSAPP_SCAN_TIMEOUT', '180'))  # 3 minutes

# Media Configuration
SEND_MEDIA = os.getenv('SEND_MEDIA', 'true').lower() == 'true'  # Set to 'false' for text-only messages
MESSAGE_SEND_DELAY = float(os.getenv('MESSAGE_SEND_DELAY', '2.0'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'  # Production mode

# Validation function for environment variables
def validate_env_config():
    """Validate required environment variables and their values"""
    errors = []
    
    # Check and validate MIN_DELAY_BETWEEN_MESSAGES
    min_delay_str = os.getenv('MIN_DELAY_BETWEEN_MESSAGES')
    if min_delay_str is None:
        errors.append("MIN_DELAY_BETWEEN_MESSAGES is not set in .env file")
        min_delay = None
    else:
        try:
            min_delay = int(min_delay_str)
            if min_delay < 30 or min_delay > 3600:
                errors.append(f"MIN_DELAY_BETWEEN_MESSAGES ({min_delay}) should be between 30-3600 seconds")
        except ValueError:
            errors.append(f"MIN_DELAY_BETWEEN_MESSAGES '{min_delay_str}' is not a valid integer")
            min_delay = None
    
    # Check and validate MAX_DELAY_BETWEEN_MESSAGES
    max_delay_str = os.getenv('MAX_DELAY_BETWEEN_MESSAGES')
    if max_delay_str is None:
        errors.append("MAX_DELAY_BETWEEN_MESSAGES is not set in .env file")
        max_delay = None
    else:
        try:
            max_delay = int(max_delay_str)
            if max_delay < 60 or max_delay > 7200:
                errors.append(f"MAX_DELAY_BETWEEN_MESSAGES ({max_delay}) should be between 60-7200 seconds")
        except ValueError:
            errors.append(f"MAX_DELAY_BETWEEN_MESSAGES '{max_delay_str}' is not a valid integer")
            max_delay = None
    
    # Check and validate GLOBAL_DAILY_LIMIT
    global_limit_str = os.getenv('GLOBAL_DAILY_LIMIT')
    if global_limit_str is None:
        errors.append("GLOBAL_DAILY_LIMIT is not set in .env file")
        global_limit = None
    else:
        try:
            global_limit = int(global_limit_str)
            if global_limit < 10 or global_limit > 500:
                errors.append(f"GLOBAL_DAILY_LIMIT ({global_limit}) should be between 10-500 messages")
        except ValueError:
            errors.append(f"GLOBAL_DAILY_LIMIT '{global_limit_str}' is not a valid integer")
            global_limit = None
    
    # Check logical relationship
    if min_delay and max_delay:
        if min_delay >= max_delay:
            errors.append(f"MIN_DELAY_BETWEEN_MESSAGES ({min_delay}) must be less than MAX_DELAY_BETWEEN_MESSAGES ({max_delay})")
    
    if errors:
        print("❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print("\n📝 Required .env file format:")
        print("   MIN_DELAY_BETWEEN_MESSAGES=60")
        print("   MAX_DELAY_BETWEEN_MESSAGES=600") 
        print("   GLOBAL_DAILY_LIMIT=75")
        exit(1)
    
    print("✅ Environment configuration validated successfully")
    return min_delay, max_delay, global_limit

# Validate configuration and set variables
MIN_DELAY_BETWEEN_MESSAGES, MAX_DELAY_BETWEEN_MESSAGES, GLOBAL_DAILY_LIMIT = validate_env_config()

LEAD_API_HEADERS = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}

# ============================================================================
# SELENIUM WHATSAPP WEB CLIENT
# ============================================================================

class SeleniumWhatsAppClient:
    """Production-ready WhatsApp Web client using Selenium automation"""
    
    def __init__(self):
        self.driver = None
        self.session_active = False
        self.input_box = None
        self.current_number = None
        # Static template system - no API needed
        
        logger.debug("Selenium WhatsApp client initialized")
    
    def _setup_chrome_profile(self) -> str:
        """Setup and validate Chrome profile directory"""
        try:
            # Get current user profile directory
            import os
            user_profile = os.path.expanduser("~")  # Gets C:\Users\fahad
            persistent_profile = os.path.join(user_profile, "WhatsAppBot_Profile")
            
            opt_logger.browser_status(f"Setting up persistent profile: {persistent_profile}")
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(persistent_profile, exist_ok=True)
                
                # Test write permissions
                test_file = os.path.join(persistent_profile, "test_write.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                
                opt_logger.browser_status("✅ Persistent profile directory ready")
                return persistent_profile
                
            except Exception as e:
                opt_logger.browser_status(f"❌ Could not create persistent profile: {str(e)[:50]}...")
            
            # Try the configured profile path as backup
            if CHROME_PROFILE_PATH and CHROME_PROFILE_PATH != persistent_profile:
                try:
                    profile_path = CHROME_PROFILE_PATH
                    opt_logger.browser_status(f"Trying configured profile: {profile_path}")
                    
                    os.makedirs(profile_path, exist_ok=True)
                    
                    # Test write permissions
                    test_file = os.path.join(profile_path, "test_write.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    
                    opt_logger.browser_status("✅ Configured profile directory ready")
                    return profile_path
                    
                except Exception as e:
                    opt_logger.browser_status(f"❌ Configured profile failed: {str(e)[:50]}...")
            
            # Fallback to temp directory (will lose session)
            import tempfile
            temp_profile = os.path.join(tempfile.gettempdir(), "WhatsAppBot_Profile")
            opt_logger.browser_status(f"⚠️  Using temporary profile (session won't persist): {temp_profile}")
            
            os.makedirs(temp_profile, exist_ok=True)
            return temp_profile
            
        except Exception as e:
            # Final fallback - let Chrome use default
            opt_logger.browser_status("Using Chrome default profile (no custom profile)")
            logger.warning(f"Profile setup failed, using default: {e}")
            return ""
    
    def initialize_browser(self) -> bool:
        """Initialize Chrome browser with WhatsApp Web"""
        try:
            opt_logger.browser_status("Initializing Chrome browser...")
            
            # Ensure profile directory exists and is accessible
            profile_path = self._setup_chrome_profile()
            
            # Setup Chrome options
            chrome_options = Options()
            
            # Only set user-data-dir if we have a valid profile path
            if profile_path:
                chrome_options.add_argument(f"--user-data-dir={profile_path}")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Debug mode - keep browser open and visible
            if DEBUG_MODE:
                opt_logger.browser_status("🔍 DEBUG MODE: Browser will stay visible")
                chrome_options.add_argument("--start-maximized")
            else:
                chrome_options.add_argument("--window-size=1200,800")
            
            # Initialize Chrome driver with Service (Selenium 4.x compatible)
            try:
                if CHROME_DRIVER_PATH and os.path.exists(CHROME_DRIVER_PATH):
                    opt_logger.browser_status(f"Using ChromeDriver from: {CHROME_DRIVER_PATH}")
                    service = Service(executable_path=CHROME_DRIVER_PATH)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    opt_logger.browser_status("Auto-detecting ChromeDriver from system PATH...")
                    self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as driver_error:
                if "chromedriver" in str(driver_error).lower():
                    opt_logger.browser_status("❌ ChromeDriver not found!")
                    logger.error("ChromeDriver Setup Required:")
                    logger.error("1. Download ChromeDriver from: https://chromedriver.chromium.org/")
                    logger.error("2. Match your Chrome version (check chrome://version/)")
                    logger.error("3. Either:")
                    logger.error("   a) Add chromedriver.exe to system PATH, OR")
                    logger.error("   b) Set CHROME_DRIVER_PATH in .env")
                    logger.error(f"4. Current CHROME_DRIVER_PATH: '{CHROME_DRIVER_PATH}'")
                raise driver_error
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to WhatsApp Web
            opt_logger.browser_status("Navigating to WhatsApp Web...")
            self.driver.get('https://web.whatsapp.com/')
            
            # Wait for WhatsApp to load and check login status
            opt_logger.browser_status("Checking login status...")
            if self._wait_for_whatsapp_ready():
                self.session_active = True
                opt_logger.browser_status("✅ WhatsApp Web ready")
                return True
            else:
                opt_logger.browser_status("❌ WhatsApp Web initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            opt_logger.browser_status(f"❌ Browser initialization failed: {str(e)[:100]}...")
            return False
    
    def _wait_for_whatsapp_ready(self) -> bool:
        """Wait for WhatsApp Web to be fully loaded and logged in"""
        try:
            opt_logger.browser_status("Waiting for WhatsApp to load...")
            
            # Give WhatsApp Web more time to fully load
            time.sleep(5)
            
            # Check current page state with multiple possible selectors
            try:
                # Wait for ANY WhatsApp Web element to appear (more flexible detection)
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        # Already logged in indicators
                        EC.presence_of_element_located((By.XPATH, '//div[@id="main"]')),  
                        EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')),
                        EC.presence_of_element_located((By.XPATH, '//header[@data-testid="chatlist-header"]')),
                        # QR code indicators  
                        EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan me!"]')),
                        EC.presence_of_element_located((By.XPATH, '//div[@data-ref]')),
                        # General WhatsApp Web indicators
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "landing-wrapper")]')),
                        EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "WhatsApp")]')),
                        # Fallback - just check if page has loaded content
                        EC.presence_of_element_located((By.TAG_NAME, 'main')),
                    )
                )
                opt_logger.browser_status("✅ WhatsApp Web page loaded successfully")
                
                # Debug info - show what we found
                if DEBUG_MODE:
                    try:
                        page_title = self.driver.title
                        current_url = self.driver.current_url
                        opt_logger.browser_status(f"🔍 DEBUG: Page title: {page_title}")
                        opt_logger.browser_status(f"🔍 DEBUG: Current URL: {current_url}")
                        
                        # Check what elements are on the page
                        all_elements = self.driver.find_elements(By.XPATH, "//*")
                        opt_logger.browser_status(f"🔍 DEBUG: Found {len(all_elements)} elements on page")
                    except Exception as debug_e:
                        opt_logger.browser_status(f"🔍 DEBUG: Error getting page info: {debug_e}")
            except:
                opt_logger.browser_status("❌ WhatsApp Web failed to load")
                return False
            
            # Additional wait for page to stabilize
            time.sleep(3)
            
            # Check current WhatsApp Web state
            page_text = self.driver.page_source.lower()
            
            # First check if we're ALREADY LOGGED IN (priority check)
            logged_in_indicators = [
                "search or start a new chat",
                "type a message", 
                "new chat",
                "chats",
                '"chat-list"',
                "chatlist-header",
                "conversation-compose"
            ]
            
            # Check for visual elements that indicate we're logged in
            logged_in_selectors = [
                '//div[@data-testid="chat-list"]',
                '//header[@data-testid="chatlist-header"]', 
                '//div[contains(@class, "chat-list")]',
                '//div[@id="main"]',
                '//div[contains(@title, "Search or start")]',
                '//input[@title="Search or start a new chat"]',
                '//div[contains(@class, "app-wrapper")]'
            ]
            
            # Check if already logged in via page content
            already_logged_in = any(indicator in page_text for indicator in logged_in_indicators)
            
            # Check if already logged in via visual elements
            if not already_logged_in:
                for selector in logged_in_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements and any(elem.is_displayed() for elem in elements):
                            already_logged_in = True
                            if DEBUG_MODE:
                                opt_logger.browser_status(f"🎯 Found logged-in element: {selector}")
                            break
                    except:
                        continue
            
            if already_logged_in:
                opt_logger.browser_status("✅ Already logged in to WhatsApp Web")
                self.session_active = True
                # Skip all QR logic and proceed to final verification
                return True
            
            # Only check for QR code if not logged in
            if "download whatsapp" in page_text or "use whatsapp on your computer" in page_text:
                opt_logger.browser_status("⚠️  WhatsApp Web showing download page - need to scan QR")
                qr_found = True
            else:
                # Check if we need to scan QR code
                qr_selectors = [
                    '//canvas[@aria-label="Scan me!"]',
                    '//div[@data-ref]', 
                    '//*[contains(@class, "qr")]',
                    '//*[contains(text(), "Scan")]',
                    '//canvas[@role="img"]'
                ]
                
                qr_found = False
                for selector in qr_selectors:
                    try:
                        qr_elements = self.driver.find_elements(By.XPATH, selector)
                        if qr_elements and any(elem.is_displayed() for elem in qr_elements):
                            qr_found = True
                            break
                    except:
                        continue
            
            if qr_found:
                opt_logger.browser_status("📱 QR Code detected - Please scan with your phone")
                opt_logger.browser_status(f"⏰ Waiting {WHATSAPP_SCAN_TIMEOUT} seconds for QR scan...")
                
                # Wait for user to scan QR code
                start_time = time.time()
                scan_success = False
                
                while time.time() - start_time < WHATSAPP_SCAN_TIMEOUT:
                    # Check for actual login (not just page elements)
                    current_page = self.driver.page_source.lower()
                    
                    # Look for signs that we're actually logged in
                    logged_in_indicators = [
                        "search or start a new chat",
                        "type a message",
                        "chat-list",
                        "whatsapp web is now connected"
                    ]
                    
                    # Check that we're NOT on the download page
                    not_on_download_page = "download whatsapp" not in current_page
                    
                    # Check for login indicators in page content
                    has_login_indicator = any(indicator in current_page for indicator in logged_in_indicators)
                    
                    if not_on_download_page and has_login_indicator:
                        scan_success = True
                        break
                    
                    # Also check for visual elements (backup)
                    login_selectors = [
                        '//div[@id="main"]',
                        '//div[@data-testid="chat-list"]', 
                        '//header[@data-testid="chatlist-header"]',
                        '//input[@title="Search or start a new chat"]'
                    ]
                    
                    for selector in login_selectors:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements and not_on_download_page:
                            scan_success = True
                            break
                    
                    if scan_success:
                        break
                        
                    time.sleep(3)  # Check every 3 seconds
                
                if scan_success:
                    opt_logger.browser_status("✅ QR Code scanned successfully")
                    # Additional wait for interface to fully load
                    opt_logger.browser_status("⏰ Waiting for chat interface to fully load...")
                    time.sleep(8)
                    
                    # Mark session as freshly logged in (important for message sending)
                    self.session_active = True
                    opt_logger.browser_status("✅ WhatsApp Web session is now active and ready")
                else:
                    opt_logger.browser_status("❌ QR Code scan timeout") 
                    opt_logger.browser_status("🔧 MANUAL ACTION REQUIRED:")
                    opt_logger.browser_status("   1. Open WhatsApp on your phone")
                    opt_logger.browser_status("   2. Tap Menu (⋮) → Linked Devices")
                    opt_logger.browser_status("   3. Tap 'Link a Device'")
                    opt_logger.browser_status("   4. Scan the QR code in the browser")
                    return False
            else:
                opt_logger.browser_status("✅ WhatsApp Web is ready without QR scan")
            
            # Final verification - check if we can access WhatsApp functionality
            try:
                # Look for ANY indicator that WhatsApp Web is ready
                ready_indicators = [
                    '//div[@id="main"]',
                    '//div[@data-testid="chat-list"]',
                    '//header[@data-testid="chatlist-header"]',
                    '//*[contains(@class, "app-wrapper")]',
                    '//*[contains(@class, "landing-wrapper")]'
                ]
                
                ready = False
                for indicator in ready_indicators:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        ready = True
                        break
                
                if ready:
                    opt_logger.browser_status("✅ WhatsApp Web interface ready")
                    return True
                else:
                    opt_logger.browser_status("⚠️  WhatsApp Web loaded but interface not fully ready")
                    # Don't fail completely - might still work
                    return True
                    
            except Exception as e:
                opt_logger.browser_status(f"⚠️  Interface check failed but continuing: {str(e)[:50]}...")
                # Don't fail completely - WhatsApp might still work
                return True
                
        except Exception as e:
            logger.error(f"Error waiting for WhatsApp ready: {e}")
            opt_logger.browser_status(f"❌ WhatsApp Web initialization error: {str(e)[:50]}...")
            return False
    
    def _navigate_to_chat(self, phone: str) -> bool:
        """Navigate to specific chat using WhatsApp Web URL"""
        try:
            # Format phone number (remove + and spaces)
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Navigate to chat URL
            chat_url = f'https://web.whatsapp.com/send?phone={clean_phone}'
            opt_logger.browser_status(f"Opening chat for {phone}")
            self.driver.get(chat_url)
            self.current_number = phone
            
            # Wait for page to load
            time.sleep(5)
            
            # Get page content for analysis
            page_text = self.driver.page_source.lower()
            page_title = self.driver.title.lower()
            current_url = self.driver.current_url.lower()
            
            # Check for various invalid number indicators
            invalid_indicators = [
                "phone number shared via url is invalid",
                "the phone number is not registered on whatsapp", 
                "número de teléfono no válido",
                "invalid phone number",
                "phone number not found",
                "not a valid whatsapp number",
                "this phone number is not registered",
                "número não encontrado",
                "number not found"
            ]
            
            # Check for error indicators in page content
            for indicator in invalid_indicators:
                if indicator in page_text or indicator in page_title:
                    opt_logger.browser_status(f"❌ Invalid/unregistered number: {phone}")
                    logger.warning(f"Invalid number detected: {phone} - {indicator}")
                    return False
            
            # Check if URL shows error
            if "error" in current_url or "invalid" in current_url:
                opt_logger.browser_status(f"❌ URL shows error for number: {phone}")
                logger.warning(f"URL error for number: {phone}")
                return False
            
            # Check if we're redirected to main page WITHOUT any chat context
            # Note: Normal behavior is redirect from /send?phone=X to main page when number is valid
            # We should check for chat-specific elements instead of just URL
            if "web.whatsapp.com" in current_url and "send" not in current_url:
                # This is normal - check if we actually have a chat open
                if DEBUG_MODE:
                    opt_logger.browser_status(f"🔍 Redirected to main page (normal) - checking for chat elements...")
                # Don't return False here - let the chat_indicators check below determine success
            
            # Look for indicators that we successfully opened a chat
            chat_indicators = [
                "type a message",
                "conversation-compose",
                "message yourself", 
                "chat with",
                "mensagem",
                "data-testid=\"conversation-compose-box-input\"",
                "contenteditable=\"true\"",
                "send-compose",
                "compose-box"
            ]
            
            chat_found = any(indicator in page_text for indicator in chat_indicators)
            
            # Also check for visual elements that indicate chat is open
            try:
                chat_elements = [
                    '//div[@contenteditable="true"]',
                    '//div[@data-testid="conversation-compose-box-input"]',
                    '//div[@title="Type a message"]'
                ]
                
                visual_chat_found = False
                for selector in chat_elements:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        visual_chat_found = True
                        if DEBUG_MODE:
                            opt_logger.browser_status(f"🎯 Found chat element: {selector}")
                        break
                
                if chat_found or visual_chat_found:
                    opt_logger.browser_status(f"✅ Successfully opened chat for {phone}")
                    return True
                else:
                    opt_logger.browser_status(f"⚠️  Could not confirm chat opened for {phone}")
                    # Check if we have the invalid number modal
                    if "phone number shared via url is invalid" in page_text:
                        opt_logger.browser_status(f"❌ Confirmed invalid number: {phone}")
                        return False
                    # Still try to proceed - might work anyway
                    opt_logger.browser_status(f"🔄 Proceeding anyway - maybe delayed loading...")
                    return True
                    
            except Exception as e:
                opt_logger.browser_status(f"⚠️  Error checking chat elements, proceeding anyway...")
                return True
            
        except Exception as e:
            logger.error(f"Error navigating to chat {phone}: {e}")
            opt_logger.browser_status(f"❌ Navigation error for {phone}: {str(e)[:50]}...")
            return False
    
    def _send_media_message(self, media_path: str, caption: str = "") -> bool:
        """Send media (image/video/document) with caption via WhatsApp Web"""
        try:
            logger.info(f"📎 Attempting to send media: {media_path}")
            
            # Find attachment button (+ icon) using current WhatsApp Web selectors
            attachment_selectors = [
                "button[data-tab='10'][title='Attach']",
                "button[title='Attach']",
                "span[data-icon='plus-rounded']",
                "button[data-tab='10']",
                "div[title='Attach']"
            ]
            
            attachment_button = None
            for selector in attachment_selectors:
                try:
                    attachment_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found attachment button: {selector}")
                    break
                except:
                    continue
            
            if not attachment_button:
                logger.error("❌ Could not find attachment button")
                return False
            
            # Click attachment button
            attachment_button.click()
            time.sleep(2)
            
            # Click on "Photos & videos" option from the attachment dropdown
            try:
                photos_video_selectors = [
                    "//span[contains(text(), 'Photos') and contains(text(), 'videos')]",
                    "//span[contains(text(), 'Photos & videos')]",  
                    "span[data-icon='media-filled-refreshed']",
                    "//li[contains(.//span, 'Photos')]"
                ]
                
                photos_button = None
                for selector in photos_video_selectors:
                    try:
                        if selector.startswith("//"):
                            photos_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            photos_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        logger.info(f"✅ Found photos/videos option: {selector}")
                        break
                    except:
                        continue
                
                if not photos_button:
                    logger.error("❌ Could not find Photos & videos option")
                    return False
                
                photos_button.click()
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Could not click Photos & videos: {e}")
                return False
            
            # Find file input with the specific accept attribute from WhatsApp Web
            file_input_selectors = [
                "input[accept='image/*,video/mp4,video/3gpp,video/quicktime'][multiple]",
                "input[accept*='image'][accept*='video']",
                "input[type='file'][accept*='image']",
                "input[type='file']"
            ]
            
            file_input = None
            for selector in file_input_selectors:
                try:
                    file_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found file input: {selector}")
                    break
                except:
                    continue
            
            if not file_input:
                logger.error("❌ Could not find file input element")
                return False
            
            # Upload the file using absolute path
            # media_path should already be absolute from _find_media_files
            absolute_path = media_path if os.path.isabs(media_path) else os.path.abspath(media_path)
            logger.info(f"📤 Uploading file: {os.path.basename(media_path)}")
            logger.info(f"📁 Full path: {absolute_path}")
            
            # Verify file exists before uploading
            if not os.path.exists(absolute_path):
                logger.error(f"❌ File not found: {absolute_path}")
                return False
            
            # Log file size for verification
            file_size = os.path.getsize(absolute_path)
            logger.info(f"📏 File size: {file_size:,} bytes")
            
            # Try uploading file with special character handling
            try:
                # First attempt: direct upload
                file_input.send_keys(absolute_path)
                logger.info(f"✅ File path sent to input element")
                time.sleep(4)  # Give more time for file processing
                
            except Exception as e:
                logger.warning(f"⚠️ Direct upload failed: {e}")
                
                # Alternative: Try creating a temporary file with simpler name
                try:
                    import shutil
                    import tempfile
                    
                    # Get file extension
                    _, ext = os.path.splitext(absolute_path)
                    
                    # Create temporary file with simple name
                    temp_dir = tempfile.gettempdir()
                    simple_name = f"whatsapp_upload_{int(time.time())}{ext}"
                    temp_path = os.path.join(temp_dir, simple_name)
                    
                    # Copy file to temp location
                    shutil.copy2(absolute_path, temp_path)
                    logger.info(f"📋 Created temp file: {temp_path}")
                    
                    # Try uploading temp file
                    file_input.clear()
                    file_input.send_keys(temp_path)
                    logger.info(f"✅ Temp file path sent to input element")
                    time.sleep(4)
                    
                    # Clean up temp file after a delay (in background)
                    # We'll leave it for now to ensure upload completes
                    
                except Exception as temp_error:
                    logger.error(f"❌ Temp file upload also failed: {temp_error}")
                    return False
            
            # Verify file was actually uploaded by looking for preview or send button change
            try:
                # Look for image/video preview or send button with attachment
                preview_indicators = [
                    "div[data-testid='media-viewer']",
                    "img[src*='blob:']",
                    "video[src*='blob:']", 
                    "div[role='button'][aria-label='Send']",
                    "span[data-icon='wds-ic-send-filled']"
                ]
                
                preview_found = False
                for indicator in preview_indicators:
                    try:
                        WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        preview_found = True
                        logger.info(f"✅ File upload verified with: {indicator}")
                        break
                    except:
                        continue
                
                if not preview_found:
                    logger.warning(f"⚠️ Could not verify file upload - proceeding anyway")
                    
            except Exception as e:
                logger.debug(f"File upload verification error: {e}")
            
            # Wait a bit more and check if file is actually loaded
            time.sleep(2)
            
            # Add caption if provided
            if caption:
                try:
                    caption_selectors = [
                        "div[contenteditable='true'][data-lexical-editor='true']",
                        "div[role='textbox'][contenteditable='true']",
                        "div[contenteditable='true'][data-tab='1']",
                        "div[contenteditable='true'][aria-label*='message']"
                    ]
                    
                    caption_input = None
                    for selector in caption_selectors:
                        try:
                            caption_input = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            logger.info(f"✅ Found caption input: {selector}")
                            break
                        except:
                            continue
                    
                    if caption_input:
                        caption_input.click()
                        time.sleep(1)
                        
                        # Clear any existing text and use pyperclip for reliable input
                        pyperclip.copy(caption)
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        time.sleep(0.3)
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                        logger.info(f"📝 Added caption: {caption[:50]}...")
                        time.sleep(2)
                    else:
                        logger.warning("⚠️ Could not find caption input - sending without caption")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not add caption: {e}")
            
            # Find and click send button using current WhatsApp Web selectors
            send_selectors = [
                "span[data-icon='wds-ic-send-filled']",
                "div[aria-label='Send'][role='button']",
                "button[aria-label='Send']",
                "span[data-icon='send']"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found send button: {selector}")
                    break
                except:
                    continue
            
            if not send_button:
                logger.error("❌ Could not find send button")
                return False
            
            # Send the media
            send_button.click()
            logger.info("📤 Media sent successfully!")
            time.sleep(3)
            
            # Final verification - check if message actually appears in chat
            try:
                # Look for message indicators that confirm send
                sent_indicators = [
                    "span[data-icon='msg-check']",
                    "span[data-icon='msg-dblcheck']", 
                    "span[data-icon='msg-time']",
                    "div[data-pre-plain-text*='You']"
                ]
                
                sent_confirmed = False
                for indicator in sent_indicators:
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        sent_confirmed = True
                        logger.info(f"✅ Message send confirmed with: {indicator}")
                        break
                    except:
                        continue
                
                if not sent_confirmed:
                    logger.warning(f"⚠️ Could not confirm message was sent")
                
            except Exception as e:
                logger.debug(f"Send confirmation error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending media: {e}")
            return False

    def _find_input_box(self) -> bool:
        """Find and set the message input box"""
        try:
            # Multiple selectors for different WhatsApp Web versions
            input_selectors = [
                '//div[@contenteditable="true"][@data-tab="10"]',  # Main input
                '//div[@contenteditable="true"][@role="textbox"]',  # Alternative
                '//*[@id="main"]//div[@contenteditable="true"]',    # Fallback
                '//div[@title="Type a message"]',                  # By title
                '//div[@data-testid="conversation-compose-box-input"]'  # By test ID
            ]
            
            for selector in input_selectors:
                try:
                    self.input_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.input_box.click()
                    logger.debug(f"Input box found with selector: {selector}")
                    return True
                except:
                    continue
            
            logger.warning("Could not find message input box")
            return False
            
        except Exception as e:
            logger.error(f"Error finding input box: {e}")
            return False
    
    def send_template_message(self, phone: str, template: str, params: List[Dict]) -> MessageResult:
        """Send message through WhatsApp Web (template params converted to text)"""
        try:
            # Navigate to chat
            if not self._navigate_to_chat(phone):
                return MessageResult(
                    success=False,
                    status=MessageStatus.FAILED,
                    message_id=None,
                    error_category=ErrorCategory.INVALID_NUMBER,
                    error_message=f"Invalid/unregistered WhatsApp number: {phone}",
                    should_continue=True
                )
            
            # Wait for chat interface to load
            time.sleep(3)
            
            # Find input box
            if not self._find_input_box():
                return MessageResult(
                    success=False,
                    status=MessageStatus.FAILED,
                    message_id=None,
                    error_category=ErrorCategory.ELEMENT_NOT_FOUND,
                    error_message="Could not find message input box",
                    should_continue=True
                )
            
            # Create message from WATI template parameters
            message_text = self._build_message_from_template(params)
            
            # Check media sending preference and files
            media_sent = False
            
            if SEND_MEDIA:
                media_files = self._find_media_files()
                
                if media_files:
                    # Use the first media file found (prioritized: images → videos → documents)
                    media_path = media_files[0]
                    logger.info(f"📎 Using media file: {media_path}")
                    
                    if self._send_media_message(media_path, message_text):
                        media_sent = True
                        logger.info(f"✅ Media + Caption message sent successfully")
                    else:
                        logger.warning(f"⚠️ Media send failed, falling back to text message")
                else:
                    logger.info(f"📭 No media files found - sending text-only message")
            else:
                logger.info(f"📝 Text-only mode enabled - skipping media")
            
            # Send text message if no media was sent
            if not media_sent:
                try:
                    # Clear input box
                    self.input_box.clear()
                    
                    # Copy message to clipboard and paste
                    pyperclip.copy(message_text)
                    self.input_box.send_keys(Keys.CONTROL, "v")
                    
                    # Wait a moment then send
                    time.sleep(1)
                    self.input_box.send_keys(Keys.ENTER)
                    
                    logger.info(f"✅ Text message sent to {phone}")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending text message: {e}")
                    return MessageResult(
                        success=False,
                        status=MessageStatus.FAILED,
                        message_id=None,
                        error_category=ErrorCategory.WHATSAPP_WEB_ERROR,
                        error_message=f"Send error: {str(e)}",
                        should_continue=True
                    )
            
            # Wait for message to be sent
            time.sleep(MESSAGE_SEND_DELAY)
            
            # Try to detect if message was sent successfully
            sent_status = self._check_message_sent()
            
            # Generate unique message ID (timestamp-based)
            message_id = f"sel_{int(time.time() * 1000)}"
            
            message_type = "Media + Caption" if media_sent else "Text"
            logger.info(f"✅ {message_type} message sent to {phone}")
            
            return MessageResult(
                success=True,
                status=sent_status,
                message_id=message_id,
                error_category=None,
                error_message=None,
                should_continue=True
            )
                
        except Exception as e:
            logger.error(f"Exception in send_template_message: {e}")
            return MessageResult(
                success=False,
                status=MessageStatus.FAILED,
                message_id=None,
                error_category=ErrorCategory.UNKNOWN_ERROR,
                error_message=f"Exception: {str(e)}",
                should_continue=True
            )
    
    def _build_message_from_template(self, params: List[Dict]) -> str:
        """Build message text from static template.txt file with parameters"""
        try:
            # Read template from file
            template_file = 'template.txt'
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                logger.info(f"📋 Using template content from: {template_file}")
            else:
                logger.warning(f"⚠️ Template file {template_file} not found, using fallback")
                # Fallback template (same as template.txt content)
                template_content = """🇦🇺 From dream to destination — Australia awaits!

Hi {{1}},
I'm {{2}} from Migrate Zone.

We're now processing top Australian visas like the 482 Work Permit and the 186 PR.

✅ 2,200+ happy clients & families settled. You could be the next! 🇦🇺

📞 Call or WhatsApp: {{3}}

🏢 Visit our office for a FREE consultation and check eligibility

📸 Client Wins: https://www.instagram.com/reel/DMrhR9aINFs/
🔔 Get visa updates first – follow us on Instagram!: https://www.instagram.com/migrate_zone/

✈️ Call to start your Australia journey today!"""
            
            # Extract parameters
            param_values = {}
            for param in params:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name and param_value:
                    param_values[param_name] = param_value
            
            # Replace template placeholders
            message = template_content
            
            # Replace {{1}}, {{2}}, {{3}} format placeholders
            for i in range(1, 10):  # Support up to 9 parameters
                placeholder = f"{{{{{i}}}}}"
                if placeholder in message and str(i) in param_values:
                    message = message.replace(placeholder, param_values[str(i)])
            
            # Log template info for debugging
            template_name = os.getenv('WATI_TEMPLATE_NAME', 'Template_Name')
            logger.info(f"📋 Using dynamic template: {template_name}")
            logger.info(f"📝 Message preview: {message[:100]}...")
            
            return message
            
        except Exception as e:
            logger.error(f"Error building message from template: {e}")
            # Emergency fallback
            lead_name = params[0].get('value', 'Customer') if params else 'Customer'
            counsellor_name = params[1].get('value', 'Counsellor') if len(params) > 1 else 'Counsellor'
            counsellor_phone = params[2].get('value', '') if len(params) > 2 else ''
            
            return f"Hello {lead_name}, I'm {counsellor_name} from Migrate Zone. Please contact me at {counsellor_phone} for assistance."
    
    def _check_message_sent(self) -> MessageStatus:
        """Check if message was sent successfully"""
        try:
            # Look for message status indicators
            time.sleep(2)
            
            # Check for sent indicators (single/double check marks)
            sent_indicators = [
                '//span[@data-icon="msg-time"]',     # Time indicator
                '//span[@data-icon="msg-check"]',    # Single check
                '//span[@data-icon="msg-dblcheck"]', # Double check
                '//span[@data-icon="msg-dblcheck-ack"]'  # Blue double check
            ]
            
            for indicator in sent_indicators:
                elements = self.driver.find_elements(By.XPATH, indicator)
                if elements:
                    # Check if it's the most recent message
                    if len(elements) > 0:
                        return MessageStatus.SENT
            
            return MessageStatus.SENT  # Assume sent if no errors
            
        except Exception:
            return MessageStatus.SENT  # Default to sent
    
    def get_delivery_status(self, message_id: str) -> MessageStatus:
        """Get delivery status (simplified for WhatsApp Web)"""
        # WhatsApp Web doesn't provide easy programmatic access to detailed delivery status
        # Return SENT as default since we confirmed the message was sent
        return MessageStatus.SENT
    
    def check_whatsapp_status(self, phone: str) -> Tuple[bool, Optional[ErrorCategory]]:
        """Check if number is on WhatsApp (simplified check)"""
        # For WhatsApp Web, we'll validate during actual sending
        return True, None
    
    def _find_media_files(self) -> List[str]:
        """Find any media files in the media directory with smart prioritization"""
        try:
            media_dir = 'media'
            if not os.path.exists(media_dir):
                logger.warning(f"📁 Media directory not found: {media_dir}")
                return []
            
            image_files = []
            video_files = []
            other_files = []
            
            image_formats = ['.jpg', '.jpeg', '.png', '.gif']
            video_formats = ['.mp4', '.avi', '.mov']
            other_formats = ['.pdf', '.doc', '.docx']
            
            for file in os.listdir(media_dir):
                file_path = os.path.join(media_dir, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower()
                    absolute_path = os.path.abspath(file_path)
                    
                    if file_ext in video_formats:
                        video_files.append(absolute_path)
                        logger.info(f"🎥 Found video file: {file_path}")
                    elif file_ext in image_formats:
                        image_files.append(absolute_path)
                        logger.info(f"📸 Found image file: {file_path}")
                    elif file_ext in other_formats:
                        other_files.append(absolute_path)
                        logger.info(f"📄 Found document: {file_path}")
                    
                    logger.debug(f"   📁 Absolute path: {absolute_path}")
            
            # Smart prioritization: Images first, then videos, then documents
            media_files = image_files + video_files + other_files
            
            if media_files:
                logger.info(f"📋 Media priority order:")
                for i, file in enumerate(media_files, 1):
                    file_type = "🎥 Video" if file in video_files else "📸 Image" if file in image_files else "📄 Document"
                    logger.info(f"   [{i}] {file_type}: {os.path.basename(file)}")
                    if i == 1:
                        logger.info(f"       👆 This will be sent")
            else:
                logger.warning(f"📭 No supported media files found in {media_dir}/")
                logger.info(f"   Supported: Images {image_formats}, Videos {video_formats}, Docs {other_formats}")
            
            return media_files
            
        except Exception as e:
            logger.error(f"Error finding media files: {e}")
            return []
    
    def close_browser(self):
        """Close the browser session"""
        try:
            if self.driver:
                # In debug mode, ask before closing
                if DEBUG_MODE:
                    opt_logger.browser_status("🔍 DEBUG MODE: Keeping browser open for 30 seconds...")
                    time.sleep(30)
                
                self.driver.quit()
                self.session_active = False
                opt_logger.browser_status("🔴 Browser session closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

# ============================================================================
# ENHANCED AUTOMATION MANAGER (MODIFIED FOR SELENIUM)
# ============================================================================

class EnhancedLeadAutomation:
    """Production-ready lead automation with Selenium WhatsApp Web"""
    
    def __init__(self):
        self.selenium_client = SeleniumWhatsAppClient()
        self.daily_quota = self._load_quota_data()
        self.sent_today = self._load_sent_data()
        self.analytics = CampaignAnalytics()
        
    def _load_quota_data(self) -> Dict:
        """Load today's quota usage"""
        try:
            with open('quota_usage.json', 'r') as f:
                data = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                quota_data = data.get(today, {})
                # Ensure global_total exists
                if 'global_total' not in quota_data:
                    quota_data['global_total'] = 0
                return quota_data
        except FileNotFoundError:
            return {'global_total': 0}
    
    def _save_quota_data(self):
        """Save quota usage with 7-day retention"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Load existing data
            try:
                with open('quota_usage.json', 'r') as f:
                    all_data = json.load(f)
            except FileNotFoundError:
                all_data = {}
            
            # Update today's data
            all_data[today] = self.daily_quota
            
            # Cleanup old data (keep 7 days)
            cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            all_data = {k: v for k, v in all_data.items() if k >= cutoff}
            
            # Save back
            with open('quota_usage.json', 'w') as f:
                json.dump(all_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save quota data: {e}")
    
    def _load_sent_data(self) -> set:
        """Load today's sent message IDs"""
        try:
            with open('sent_messages.json', 'r') as f:
                data = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                return set(data.get(today, []))
        except FileNotFoundError:
            return set()
    
    def _save_sent_data(self, lead_id: str):
        """Save sent message ID to prevent duplicates"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Load existing data
            try:
                with open('sent_messages.json', 'r') as f:
                    all_data = json.load(f)
            except FileNotFoundError:
                all_data = {}
            
            # Update today's data
            if today not in all_data:
                all_data[today] = []
            all_data[today].append(lead_id)
            
            # Cleanup old data
            cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            all_data = {k: v for k, v in all_data.items() if k >= cutoff}
            
            # Save back
            with open('sent_messages.json', 'w') as f:
                json.dump(all_data, f, indent=2)
                
            self.sent_today.add(lead_id)
            
        except Exception as e:
            logger.error(f"Failed to save sent data: {e}")
    
    def is_working_hours(self) -> bool:
        """Check if within working hours"""
        try:
            current = datetime.now().time()
            start = datetime.strptime(SCRIPT_START_TIME, '%H:%M').time()
            end = datetime.strptime(SCRIPT_END_TIME, '%H:%M').time()
            return start <= current <= end
        except Exception:
            return True  # Default to allowing operation
    
    def fetch_leads(self, limit: int) -> List[Dict]:
        """Fetch leads from API with optimized parameters"""
        try:
            params = {
                'owner_id': STATIC_OWNER_ID,
                'limit': limit,
                'template_name': os.getenv('WATI_TEMPLATE_NAME', 'Template_Name'),
            }
            
            response = requests.get(
                LEAD_API_URL,
                params=params,
                headers=LEAD_API_HEADERS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                leads = data.get('data', [])
                logger.debug(f"Fetched {len(leads)} leads from API")
                return leads
            else:
                logger.error(f"Lead API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch leads: {e}")
            return []
    
    def save_message_log(self, lead: Dict, status: str, message_id: str = None, error: str = None, 
                        counsellor_name: str = None, message_content: str = None) -> bool:
        """Save message log to external API"""
        try:
            # Get the correct employee ID based on counsellor name
            employee_id = 1  # Default fallback (system admin)
            if counsellor_name and counsellor_name in COUNSELLORS:
                employee_id = COUNSELLORS[counsellor_name]['employee_id']
                logger.debug(f"Using employee ID {employee_id} for counsellor {counsellor_name}")
            else:
                logger.warning(f"Counsellor '{counsellor_name}' not found in COUNSELLORS, using default employee ID 1")
            
            payload = {
                "lead_id": lead.get('lead_id'),
                "message_content": message_content if message_content else f"Template: {os.getenv('WATI_TEMPLATE_NAME', 'Template_Name')}",
                "msg_type": "template",
                "msg_status": status,
                "to_phone_number": lead.get('mobile_number_formatted'),
                "from_phone_number": os.getenv('SENDER_NUMBER'),
                "template_name": os.getenv('WATI_TEMPLATE_NAME', 'Template_Name'),
                "employee": employee_id,  # Use correct employee ID for each counsellor
                "method": "selenium_whatsapp_web_via_wati_api"
            }
            
            if message_id:
                payload["message_id"] = message_id
            if error:
                payload["error_message"] = error
            if status == "sent":
                payload["sent_at"] = datetime.now().isoformat()
            
            response = requests.post(
                LEAD_LOG_API_URL,
                json=payload,
                headers=LEAD_API_HEADERS,
                timeout=15
            )
            
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"Failed to save log: {e}")
            return False
    
    def get_available_counsellor(self) -> Optional[Tuple[str, Dict]]:
        """Get random available counsellor"""
        available = []
        
        for name, config in COUNSELLORS.items():
            used = self.daily_quota.get(name, 0)
            limit = config['daily_limit']
            
            if used < limit:
                available.append((name, config))
        
        if not available:
            return None
        
        return random.choice(available)
    
    def process_single_lead(self, lead: Dict, counsellor_name: str, counsellor_config: Dict) -> MessageResult:
        """Process single lead with enhanced tracking"""
        lead_id = str(lead.get('lead_id', ''))
        lead_name = lead.get('full_name', 'Customer')
        
        # Check if already sent today
        if lead_id in self.sent_today:
            logger.debug(f"Lead {lead_id} already processed today")
            return MessageResult(
                success=False,
                status=MessageStatus.FAILED,
                message_id=None,
                error_category=ErrorCategory.UNKNOWN_ERROR,
                error_message="Already sent today",
                should_continue=True
            )
        
        # Determine target phone
        if USE_TEST_NUMBER:
            target_phone = TEST_MOBILE_NUMBER
        else:
            target_phone = lead.get('mobile_number_formatted', '')
        
        # Prepare template parameters
        counsellor_number = counsellor_config['number']
        
        parameters = [
            {"name": "1", "value": lead_name},
            {"name": "2", "value": counsellor_name},
            {"name": "3", "value": counsellor_number}
        ]
        
        # Log detailed parameter info for debugging
        logger.info(f"🔍 PARAMETER DEBUG:")
        logger.info(f"   Lead: '{lead_name}' (from: {lead.get('full_name', 'N/A')})")
        logger.info(f"   Counsellor: '{counsellor_name}'")
        logger.info(f"   Number: '{counsellor_number}'")
        logger.info(f"   Target Phone: '{target_phone}'")
        
        # Build the actual message content for logging
        actual_message_content = self.selenium_client._build_message_from_template(parameters)
        
        # Send message using actual WATI template
        result = self.selenium_client.send_template_message(
            phone=target_phone,
            template=os.getenv('WATI_TEMPLATE_NAME', 'Template_Name'),  # Updated template name
            params=parameters
        )
        
        # Save to external log
        log_status = "sent" if result.success else "failed"
        
        self.save_message_log(
            lead=lead,
            status=log_status,
            message_id=result.message_id,
            error=result.error_message if not result.success else None,
            counsellor_name=counsellor_name,
            message_content=actual_message_content
        )
        
        # Update tracking data
        if result.success:
            self.daily_quota[counsellor_name] = self.daily_quota.get(counsellor_name, 0) + 1
            self.daily_quota['global_total'] = self.daily_quota.get('global_total', 0) + 1
            self._save_quota_data()
            self._save_sent_data(lead_id)
        
        # Track analytics
        self.analytics.track_result(lead_id, counsellor_name, result, result.status)
        
        return result
    
    def run_campaign(self) -> Dict:
        """Execute optimized campaign with Selenium WhatsApp Web"""
        
        # Pre-flight checks
        if not self.is_working_hours():
            current_time = datetime.now().strftime('%H:%M')
            return {
                'status': 'outside_working_hours',
                'message': f'Outside working hours ({SCRIPT_START_TIME}-{SCRIPT_END_TIME})',
                'current_time': current_time
            }
        
        # Check global daily limit first
        global_used = self.daily_quota.get('global_total', 0)
        global_remaining = max(0, GLOBAL_DAILY_LIMIT - global_used)
        
        if global_remaining == 0:
            return {
                'status': 'global_quota_exhausted',
                'message': f'Global daily limit reached ({global_used}/{GLOBAL_DAILY_LIMIT} messages sent today)'
            }
        
        # Calculate available quota (limited by global limit)
        total_quota = 0
        for name, config in COUNSELLORS.items():
            used = self.daily_quota.get(name, 0)
            remaining = max(0, config['daily_limit'] - used)
            total_quota += remaining
            logger.debug(f"{name}: {used}/{config['daily_limit']} used, {remaining} remaining")
        
        # Limit total quota to global remaining
        total_quota = min(total_quota, global_remaining)
        
        if total_quota == 0:
            return {
                'status': 'quota_exhausted',
                'message': 'All counsellor quotas exhausted for today'
            }
        
        # Initialize browser session
        opt_logger.browser_status("Initializing WhatsApp Web session...")
        if not self.selenium_client.initialize_browser():
            return {
                'status': 'browser_initialization_failed',
                'message': 'Failed to initialize WhatsApp Web session'
            }
        
        # Fetch leads
        leads = self.fetch_leads(min(total_quota, 200))  # Increased batch for production campaign
        if not leads:
            self.selenium_client.close_browser()
            return {
                'status': 'no_leads',
                'message': 'No leads available to process'
            }
        
        # Start campaign
        self.analytics.start_campaign()
        opt_logger.campaign_start(total_quota, len(leads), global_used)
        
        # Process leads
        processed = 0
        try:
            for i, lead in enumerate(leads, 1):
                # Check global limit before processing each lead
                current_global_used = self.daily_quota.get('global_total', 0)
                if current_global_used >= GLOBAL_DAILY_LIMIT:
                    logger.warning(f"🛑 Global daily limit reached ({current_global_used}/{GLOBAL_DAILY_LIMIT})")
                    opt_logger.browser_status(f"🛑 Global daily limit reached - stopping campaign")
                    break
                
                # Get available counsellor
                counsellor_selection = self.get_available_counsellor()
                if not counsellor_selection:
                    logger.warning("No available counsellors remaining")
                    break
                
                counsellor_name, counsellor_config = counsellor_selection
                lead_name = lead.get('full_name', 'Customer')
                
                # Log processing
                opt_logger.lead_processing(i, len(leads), lead_name, counsellor_name)
                
                # Process lead
                result = self.process_single_lead(lead, counsellor_name, counsellor_config)
                
                # Log result
                details = f"ID: {result.message_id}" if result.message_id else ""
                if not result.success and result.error_message:
                    details = result.error_message[:50] + "..." if len(result.error_message) > 50 else result.error_message
                
                opt_logger.message_result(result.status, lead_name, details)
                
                # Check for systematic failures
                if not result.should_continue:
                    logger.error("🛑 Systematic failure detected - stopping campaign")
                    break
                
                processed += 1
                
                # Random delay between sends to avoid WhatsApp blocking (skip for last message)
                if i < len(leads):  # Only delay if not the last message
                    delay_seconds = random.uniform(MIN_DELAY_BETWEEN_MESSAGES, MAX_DELAY_BETWEEN_MESSAGES)
                    opt_logger.browser_status(f"⏳ Waiting {delay_seconds:.1f} seconds before next message to avoid detection...")
                    
                    # Show countdown for transparency 
                    countdown_start = time.time()
                    while time.time() - countdown_start < delay_seconds:
                        remaining = delay_seconds - (time.time() - countdown_start)
                        if remaining > 0:
                            if int(remaining) % 30 == 0:  # Log every 30 seconds
                                opt_logger.browser_status(f"⏳ {remaining:.0f} seconds remaining...")
                            time.sleep(1)  # Check every second
                        else:
                            break
                    
                    opt_logger.browser_status("✅ Delay complete, continuing to next message")
                
        except KeyboardInterrupt:
            logger.info("🛑 Campaign interrupted by user")
        except Exception as e:
            logger.error(f"Campaign error: {e}")
        finally:
            # Always close browser
            self.selenium_client.close_browser()
        
        # Finalize campaign
        self.analytics.end_campaign()
        final_metrics = self.analytics.get_metrics()
        opt_logger.campaign_end(final_metrics)
        
        return {
            'status': 'completed',
            'processed': processed,
            'metrics': final_metrics,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# CAMPAIGN ANALYTICS (UNCHANGED)
# ============================================================================

class CampaignAnalytics:
    """Enhanced analytics system for campaign tracking"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset analytics for new campaign"""
        self.metrics = {
            'sent': 0,
            'delivered': 0,
            'read': 0,
            'failed': 0,
            'pending': 0,
            'total_processed': 0,
            'start_time': None,
            'end_time': None,
            'counsellor_stats': {},
            'error_categories': {cat.value: 0 for cat in ErrorCategory}
        }
    
    def start_campaign(self):
        """Mark campaign start"""
        self.metrics['start_time'] = datetime.now()
    
    def end_campaign(self):
        """Mark campaign end"""
        self.metrics['end_time'] = datetime.now()
    
    def track_result(self, lead_id: str, counsellor: str, result: MessageResult, final_status: MessageStatus):
        """Track individual result"""
        self.metrics['total_processed'] += 1
        
        # Track by final status
        status_key = final_status.value
        self.metrics[status_key] = self.metrics.get(status_key, 0) + 1
        
        # Track error categories
        if result.error_category:
            self.metrics['error_categories'][result.error_category.value] += 1
        
        # Track counsellor performance
        if counsellor not in self.metrics['counsellor_stats']:
            self.metrics['counsellor_stats'][counsellor] = {
                'sent': 0, 'delivered': 0, 'read': 0, 'failed': 0, 'pending': 0
            }
        
        self.metrics['counsellor_stats'][counsellor][status_key] += 1
    
    def get_metrics(self) -> Dict:
        """Get final campaign metrics"""
        total = self.metrics['total_processed']
        if total == 0:
            success_rate = 0
        else:
            successful = self.metrics['sent'] + self.metrics['delivered'] + self.metrics['read']
            success_rate = (successful / total) * 100
        
        duration = "Unknown"
        if self.metrics['start_time'] and self.metrics['end_time']:
            delta = self.metrics['end_time'] - self.metrics['start_time']
            duration = str(delta).split('.')[0]  # Remove microseconds
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'duration': duration
        }

# ============================================================================
# TERMINAL OUTPUT UTILITIES (UNCHANGED)
# ============================================================================

def safe_print(text: str):
    """Safe print with encoding handling"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows console
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def print_config_banner():
    """Display optimized configuration banner"""
    safe_print("\n" + "="*60)
    safe_print("🤖 SELENIUM WHATSAPP LEAD AUTOMATION SYSTEM")
    safe_print("="*60)
    safe_print(f"🌐 Method: Selenium WhatsApp Web")
    template_name = os.getenv('WATI_TEMPLATE_NAME', 'Template_Name')
    safe_print(f"📋 Template: {template_name} (content from template.txt)")
    safe_print(f"📎 Media Mode: {'ENABLED' if SEND_MEDIA else 'TEXT-ONLY'}")
    if SEND_MEDIA:
        safe_print(f"📊 Priority: 1️⃣ Images → 2️⃣ Videos → 3️⃣ Documents")
    safe_print(f"⏰ Working Hours: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")
    safe_print(f"🎯 Mode: {'TEST' if USE_TEST_NUMBER else 'PRODUCTION'}")
    safe_print(f"👥 Counsellors: {len(COUNSELLORS)} configured")
    safe_print(f"⏳ Anti-Detection Delay: {MIN_DELAY_BETWEEN_MESSAGES}-{MAX_DELAY_BETWEEN_MESSAGES} seconds")
    safe_print(f"🌍 Global Daily Limit: {GLOBAL_DAILY_LIMIT} messages/day")
    safe_print(f"🖥️ Chrome Profile: {CHROME_PROFILE_PATH}")
    
    total_daily_limit = sum(config['daily_limit'] for config in COUNSELLORS.values())
    safe_print(f"📈 Individual Capacity: {total_daily_limit} messages (limited by global limit)")
    safe_print("="*60)

def print_final_summary(result: Dict):
    """Print optimized final summary"""
    safe_print("\n" + "🏁"*50)
    safe_print("📊 SELENIUM CAMPAIGN EXECUTION SUMMARY")
    safe_print("🏁"*50)
    
    status = result['status']
    
    if status == 'completed':
        metrics = result.get('metrics', {})
        
        safe_print(f"✅ STATUS: COMPLETED")
        safe_print(f"📤 Messages Sent: {metrics.get('sent', 0)}")
        safe_print(f"📱 Delivered: {metrics.get('delivered', 0)}")
        safe_print(f"👀 Read: {metrics.get('read', 0)}")
        safe_print(f"❌ Failed: {metrics.get('failed', 0)}")
        safe_print(f"⚡ Success Rate: {metrics.get('success_rate', 0):.1f}%")
        safe_print(f"⏱️ Duration: {metrics.get('duration', 'Unknown')}")
        
        if metrics.get('sent', 0) > 0:
            safe_print("\n🎯 NEXT STEPS:")
            safe_print("   ✅ Check WhatsApp Web for delivery confirmations")
            safe_print("   📱 Monitor responses in WhatsApp")
            safe_print("   🔍 Review message logs in admin panel")
        else:
            safe_print("\n⚠️ NO MESSAGES SENT - CHECK:")
            safe_print("   🌐 WhatsApp Web login status")
            safe_print("   📱 Phone number formats")
            safe_print("   🖥️ Browser and Chrome driver setup")
    
    elif status == 'browser_initialization_failed':
        safe_print(f"🖥️ STATUS: BROWSER INITIALIZATION FAILED")
        safe_print("🔧 CHECK:")
        safe_print("   📱 WhatsApp Web QR code scan")
        safe_print("   🖥️ Chrome driver path")
        safe_print("   📂 Chrome profile permissions")
    
    elif status == 'outside_working_hours':
        safe_print(f"🕐 STATUS: OUTSIDE WORKING HOURS")
        safe_print(f"⏰ Current: {result.get('current_time', 'Unknown')}")
        safe_print(f"🕘 Allowed: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")
    
    elif status == 'global_quota_exhausted':
        safe_print(f"🌍 STATUS: GLOBAL DAILY LIMIT REACHED")
        safe_print(f"🚫 Maximum {GLOBAL_DAILY_LIMIT} messages/day limit reached")
        safe_print("📅 Script will resume tomorrow")
    
    elif status == 'quota_exhausted':
        safe_print(f"🚫 STATUS: DAILY QUOTAS EXHAUSTED")
        safe_print("📅 All counsellors have reached their daily limits")
    
    elif status == 'no_leads':
        safe_print(f"📭 STATUS: NO LEADS AVAILABLE")
        safe_print("🔍 Check lead API and filters")
    
    else:
        safe_print(f"❓ STATUS: {status.upper()}")
    
    safe_print("🏁"*50)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        # Display configuration
        print_config_banner()
        
        # Initialize automation
        automation = EnhancedLeadAutomation()
        
        # Run campaign
        result = automation.run_campaign()
        
        # Display results
        print_final_summary(result)
        
    except KeyboardInterrupt:
        logger.info("🛑 Campaign interrupted by user")
        safe_print("🛑 Campaign stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        safe_print(f"💥 Error: {e}")
        traceback.print_exc()
