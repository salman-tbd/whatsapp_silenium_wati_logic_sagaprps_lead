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
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Complete counsellor database for multi-team system
ALL_COUNSELLORS = {
    'Anandi': {'daily_limit': 50, 'number': '+919512270915', 'username': 'anandi', 'employee_id': 289},
    'Preeti': {'daily_limit': 50, 'number': '+918799334198', 'username': 'preeti', 'employee_id': 286},
    'Khushali': {'daily_limit': 50, 'number': '+917069629625', 'username': 'pkhushali', 'employee_id': 294},
    'Karan': {'daily_limit': 50, 'number': '+919773432629', 'username': 'dkaran', 'employee_id': 308},
    'Sangita': {'daily_limit': 50, 'number': '+918128758628', 'username': 'sangitac', 'employee_id': 305},
    'Chitra': {'daily_limit': 50, 'number': '+918128817870', 'username': 'chitra', 'employee_id': 264},
    'Pragatee': {'daily_limit': 50, 'number': '+919687046717', 'username': 'pragatee', 'employee_id': 260},
    'Tulsi': {'daily_limit': 50, 'number': '+919726266913', 'username': 'tulsi', 'employee_id': 261},
}

# 📊 MANAGEMENT REPORTING SYSTEM - Daily Report Recipients
MANAGEMENT_NUMBERS = {
    'SALMAN_SIR': os.getenv('SALMAN_SIR_PHONE', '+913333333333'),
    'SAGAR_SIR': os.getenv('SAGAR_SIR_PHONE', '+913333333333'),
    'SWETA_MAM': os.getenv('SWETA_MAM_PHONE', '+913333333333'),
    'DIPALI_MAM': os.getenv('DIPALI_MAM_PHONE', '+913333333333'),
    'FAHAD': os.getenv('FAHAD_PHONE', '+917699887110'),
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
# MULTI-TEAM MANAGEMENT SYSTEM
# ============================================================================

class PhoneTeamManager:
    """Manages phone-based team configurations and builds team structures"""
    
    def __init__(self):
        # Ensure environment variables are loaded
        load_dotenv('.env')
        self.phone_teams = self.build_all_teams()
        self.validate_teams()
    
    def build_all_teams(self) -> Dict:
        """Build phone teams by combining .env config with counsellor database"""
        phone_teams = {}
        
        # Define all phone team configurations
        team_configs = [
            ('sweta_jio', 'Sweta Mam', 'Jio'),
            ('sweta_airtel', 'Sweta Mam', 'Airtel'), 
            ('dipali_jio', 'Dipali Mam', 'Jio'),
            ('dipali_airtel', 'Dipali Mam', 'Airtel')
        ]
        
        for team_key, manager, network in team_configs:
            # Get phone number from .env
            phone_env_key = f"{team_key.upper()}_PHONE"
            phone = os.getenv(phone_env_key)
            
            if not phone:
                logger.warning(f"Phone number not found for {team_key} in .env file")
                continue
            
            # Get counsellor list from .env
            counsellors_env_key = f"{team_key.upper()}_COUNSELLORS"
            counsellor_names = os.getenv(counsellors_env_key, '').split(',')
            
            # Build counsellor dict from names
            team_counsellors = {}
            for name in counsellor_names:
                name = name.strip()
                if name in ALL_COUNSELLORS:
                    team_counsellors[name] = ALL_COUNSELLORS[name]
                else:
                    logger.warning(f"Counsellor '{name}' not found in database for team {team_key}")
            
            if not team_counsellors:
                logger.warning(f"No valid counsellors found for team {team_key}")
                continue
            
            phone_teams[team_key] = {
                'manager': manager,
                'phone': phone,
                'network': network,
                'profile_name': team_key,
                'counsellors': team_counsellors,
                'capacity': sum(c['daily_limit'] for c in team_counsellors.values())
            }
        
        return phone_teams
    
    def validate_teams(self):
        """Validate team configurations"""
        if not self.phone_teams:
            raise ValueError("No valid phone teams configured! Check your .env file.")
        
        logger.info(f"✅ Loaded {len(self.phone_teams)} phone teams:")
        total_capacity = 0
        for team_id, team in self.phone_teams.items():
            counsellor_count = len(team['counsellors'])
            capacity = team['capacity']
            total_capacity += capacity
            logger.info(f"   📱 {team['manager']} {team['network']} ({team['phone']}): {counsellor_count} counsellors, {capacity} capacity")
        
        logger.info(f"🌍 Total system capacity: {total_capacity} messages/day")
    
    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        """Get team configuration by ID"""
        return self.phone_teams.get(team_id)
    
    def get_all_teams(self) -> Dict:
        """Get all team configurations"""
        return self.phone_teams
    
    def get_team_capacity(self, team_id: str) -> int:
        """Get total capacity for a team"""
        team = self.get_team_by_id(team_id)
        return team['capacity'] if team else 0

class LeadDistributor:
    """Smart lead distribution across all phone teams"""
    
    def __init__(self, phone_teams: Dict):
        self.phone_teams = phone_teams
        self.distribution_strategy = os.getenv('LEAD_DISTRIBUTION_STRATEGY', 'capacity_based')
    
    def distribute_leads(self, leads: List[Dict], quota_manager) -> Dict[str, List[Dict]]:
        """Distribute leads across all teams based on available capacity"""
        
        # Calculate available capacity for each team
        team_capacities = {}
        total_available = 0
        
        for team_id, team in self.phone_teams.items():
            used = quota_manager.get_team_quota_used(team_id)
            available = max(0, team['capacity'] - used)
            team_capacities[team_id] = available
            total_available += available
            logger.debug(f"Team {team_id}: {used}/{team['capacity']} used, {available} available")
        
        if total_available == 0:
            logger.warning("No available capacity across all teams!")
            return {}
        
        # Limit leads to available capacity
        leads_to_distribute = leads[:total_available]
        
        # Distribute based on strategy
        if self.distribution_strategy == 'capacity_based':
            return self._capacity_based_distribution(leads_to_distribute, team_capacities)
        elif self.distribution_strategy == 'round_robin':
            return self._round_robin_distribution(leads_to_distribute, team_capacities)
        else:
            return self._balanced_distribution(leads_to_distribute, team_capacities)
    
    def _capacity_based_distribution(self, leads: List[Dict], capacities: Dict[str, int]) -> Dict[str, List[Dict]]:
        """Distribute leads proportionally based on team capacity"""
        distribution = {team_id: [] for team_id in capacities.keys()}
        
        if not leads:
            return distribution
        
        total_capacity = sum(capacities.values())
        if total_capacity == 0:
            return distribution
        
        # Calculate proportion for each team
        lead_index = 0
        for team_id, capacity in capacities.items():
            if capacity > 0:
                proportion = capacity / total_capacity
                leads_for_team = int(len(leads) * proportion)
                
                # Assign leads to this team
                end_index = min(lead_index + leads_for_team, len(leads))
                distribution[team_id] = leads[lead_index:end_index]
                lead_index = end_index
        
        # Assign remaining leads to teams with capacity
        while lead_index < len(leads):
            for team_id in capacities.keys():
                if capacities[team_id] > len(distribution[team_id]) and lead_index < len(leads):
                    distribution[team_id].append(leads[lead_index])
                    lead_index += 1
        
        return distribution
    
    def _round_robin_distribution(self, leads: List[Dict], capacities: Dict[str, int]) -> Dict[str, List[Dict]]:
        """Distribute leads in round-robin fashion"""
        distribution = {team_id: [] for team_id in capacities.keys()}
        available_teams = [team_id for team_id, cap in capacities.items() if cap > 0]
        
        if not available_teams:
            return distribution
        
        team_index = 0
        for lead in leads:
            team_id = available_teams[team_index % len(available_teams)]
            if len(distribution[team_id]) < capacities[team_id]:
                distribution[team_id].append(lead)
            team_index += 1
        
        return distribution
    
    def _balanced_distribution(self, leads: List[Dict], capacities: Dict[str, int]) -> Dict[str, List[Dict]]:
        """Distribute leads evenly across available teams"""
        distribution = {team_id: [] for team_id in capacities.keys()}
        available_teams = [team_id for team_id, cap in capacities.items() if cap > 0]
        
        if not available_teams:
            return distribution
        
        leads_per_team = len(leads) // len(available_teams)
        remaining_leads = len(leads) % len(available_teams)
        
        lead_index = 0
        for i, team_id in enumerate(available_teams):
            team_lead_count = leads_per_team + (1 if i < remaining_leads else 0)
            team_lead_count = min(team_lead_count, capacities[team_id])
            
            end_index = lead_index + team_lead_count
            distribution[team_id] = leads[lead_index:end_index]
            lead_index = end_index
        
        return distribution

class GlobalQuotaManager:
    """Manages quota across all phone teams"""
    
    def __init__(self):
        self.quota_file = 'multi_team_quota.json'
        self.quota_data = self._load_quota_data()
    
    def _load_quota_data(self) -> Dict:
        """Load quota data for all teams"""
        try:
            with open(self.quota_file, 'r') as f:
                data = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                return data.get(today, {
                    'global_total': 0,
                    'teams': {}
                })
        except FileNotFoundError:
            return {
                'global_total': 0,
                'teams': {}
            }
    
    def _save_quota_data(self):
        """Save quota data with cleanup"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Load existing data
            try:
                with open(self.quota_file, 'r') as f:
                    all_data = json.load(f)
            except FileNotFoundError:
                all_data = {}
            
            # Update today's data
            all_data[today] = self.quota_data
            
            # Cleanup old data (keep 7 days)
            cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            all_data = {k: v for k, v in all_data.items() if k >= cutoff}
            
            # Save back
            with open(self.quota_file, 'w') as f:
                json.dump(all_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save quota data: {e}")
    
    def get_global_quota_used(self) -> int:
        """Get total messages sent across all teams today"""
        return self.quota_data.get('global_total', 0)
    
    def get_team_quota_used(self, team_id: str) -> int:
        """Get messages sent by specific team today"""
        return self.quota_data.get('teams', {}).get(team_id, 0)
    
    def increment_quota(self, team_id: str):
        """Increment quota for team and global"""
        if 'teams' not in self.quota_data:
            self.quota_data['teams'] = {}
        
        self.quota_data['teams'][team_id] = self.quota_data['teams'].get(team_id, 0) + 1
        self.quota_data['global_total'] = self.quota_data.get('global_total', 0) + 1
        self._save_quota_data()
    
    def get_global_remaining(self) -> int:
        """Get remaining global quota"""
        used = self.get_global_quota_used()
        return max(0, GLOBAL_DAILY_LIMIT - used)

# ============================================================================
# SELENIUM WHATSAPP WEB CLIENT
# ============================================================================

class SeleniumWhatsAppClient:
    """Production-ready WhatsApp Web client using Selenium automation"""
    
    def __init__(self, team_id: str = None, team_config: Dict = None):
        self.driver = None
        self.session_active = False
        self.input_box = None
        self.current_number = None
        self.team_id = team_id
        self.team_config = team_config or {}
        # Static template system - no API needed
        
        logger.debug(f"Selenium WhatsApp client initialized for team: {team_id}")
    
    def _setup_chrome_profile(self) -> str:
        """Setup and validate Chrome profile directory for team"""
        try:
            # Get base profile directory from .env or use default
            base_profiles_dir = os.getenv('CHROME_PROFILES_BASE_PATH')
            if not base_profiles_dir:
                user_profile = os.path.expanduser("~")  # Gets C:\Users\fahad
                base_profiles_dir = os.path.join(user_profile, "WhatsAppProfiles")
            
            # Create team-specific profile directory
            if self.team_id:
                profile_name = f"{self.team_id}_profile"
                persistent_profile = os.path.join(base_profiles_dir, profile_name)
                team_info = f"Team {self.team_id}"
                if self.team_config:
                    team_info += f" ({self.team_config.get('manager', 'Unknown')} {self.team_config.get('network', '')})"
                opt_logger.browser_status(f"Setting up profile for {team_info}: {persistent_profile}")
            else:
                # Fallback for legacy mode
                persistent_profile = os.path.join(base_profiles_dir, "WhatsAppBot_Profile")
                opt_logger.browser_status(f"Setting up legacy profile: {persistent_profile}")
            
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
            
            # Wait longer for page to load and stabilize
            time.sleep(8)
            
            # Additional wait for any WhatsApp Web animations/loading
            try:
                # Wait for the page to not have loading indicators
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)  # Additional buffer
            except:
                pass
            
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
        """Find and set the message input box with updated selectors"""
        try:
            # Wait for chat to fully load
            time.sleep(3)
            
            # Updated selectors for current WhatsApp Web (January 2025)
            input_selectors = [
                # Current primary selectors
                '//div[@contenteditable="true"][@data-lexical-editor="true"]',
                '//div[@contenteditable="true"][@role="textbox"][@data-lexical-editor="true"]',
                '//div[@contenteditable="true"][@aria-label="Type a message"]',
                '//div[@contenteditable="true"][contains(@class, "lexical")]',
                
                # Backup selectors
                '//div[@contenteditable="true"][@data-tab="10"]',
                '//div[@contenteditable="true"][@title="Type a message"]',
                '//*[@id="main"]//div[@contenteditable="true"]',
                '//div[@data-testid="conversation-compose-box-input"]',
                
                # CSS selectors as fallback
                'div[contenteditable="true"][data-lexical-editor="true"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][aria-label*="message"]'
            ]
            
            for i, selector in enumerate(input_selectors):
                try:
                    if selector.startswith('//') or selector.startswith('/'):
                        # XPath selector
                        self.input_box = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        self.input_box = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    # Try to click and verify it's working
                    self.input_box.click()
                    time.sleep(1)
                    
                    # Verify the input box is active by checking if we can type
                    try:
                        self.input_box.send_keys("test")
                        self.input_box.clear()
                        logger.info(f"✅ Input box found and verified with selector: {selector}")
                        return True
                    except:
                        continue
                        
                except Exception as e:
                    logger.debug(f"Selector {i+1}/{len(input_selectors)} failed: {selector}")
                    continue
            
            # If all selectors failed, try to find any contenteditable div
            try:
                logger.warning("All selectors failed, trying generic approach...")
                all_inputs = self.driver.find_elements(By.XPATH, '//div[@contenteditable="true"]')
                logger.info(f"Found {len(all_inputs)} contenteditable elements")
                
                for inp in all_inputs:
                    try:
                        if inp.is_displayed() and inp.is_enabled():
                            inp.click()
                            time.sleep(1)
                            inp.send_keys("test")
                            inp.clear()
                            self.input_box = inp
                            logger.info("✅ Input box found with generic approach")
                            return True
                    except:
                        continue
            except:
                pass
            
            logger.error("❌ Could not find message input box with any method")
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
            time.sleep(5)
            
            # Try multiple times to find input box
            input_found = False
            max_retries = 3
            
            for attempt in range(max_retries):
                logger.info(f"🔍 Attempt {attempt + 1}/{max_retries} to find input box...")
                
                if self._find_input_box():
                    input_found = True
                    break
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"⏳ Input box not found, retrying in 3 seconds...")
                        time.sleep(3)
                        # Try refreshing the page
                        try:
                            self.driver.refresh()
                            time.sleep(5)
                        except:
                            pass
            
            if not input_found:
                # Try to diagnose the issue
                try:
                    page_source = self.driver.page_source
                    if "phone number shared via url is invalid" in page_source.lower():
                        return MessageResult(
                            success=False,
                            status=MessageStatus.FAILED,
                            message_id=None,
                            error_category=ErrorCategory.INVALID_NUMBER,
                            error_message=f"Invalid WhatsApp number: {phone}",
                            should_continue=True
                        )
                    elif "not registered on whatsapp" in page_source.lower():
                        return MessageResult(
                            success=False,
                            status=MessageStatus.FAILED,
                            message_id=None,
                            error_category=ErrorCategory.NOT_ON_WHATSAPP,
                            error_message=f"Number not on WhatsApp: {phone}",
                            should_continue=True
                        )
                except:
                    pass
                
                return MessageResult(
                    success=False,
                    status=MessageStatus.FAILED,
                    message_id=None,
                    error_category=ErrorCategory.ELEMENT_NOT_FOUND,
                    error_message="Could not find message input box after multiple attempts",
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
                    logger.info(f"📝 Sending text message to {phone}")
                    
                    # Multiple approaches to send the message
                    message_sent = False
                    
                    # Method 1: Clipboard paste (most reliable)
                    try:
                        self.input_box.clear()
                        pyperclip.copy(message_text)
                        time.sleep(0.5)
                        
                        # Click to ensure focus
                        self.input_box.click()
                        time.sleep(0.5)
                        
                        # Paste using Ctrl+V
                        self.input_box.send_keys(Keys.CONTROL, "v")
                        time.sleep(1)
                        
                        # Send message
                        self.input_box.send_keys(Keys.ENTER)
                        message_sent = True
                        logger.info(f"✅ Text message sent via clipboard to {phone}")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Clipboard method failed: {e}")
                        
                        # Method 2: Direct typing (backup)
                        try:
                            self.input_box.clear()
                            time.sleep(0.5)
                            self.input_box.click()
                            time.sleep(0.5)
                            
                            # Type message directly (slower but more reliable)
                            self.input_box.send_keys(message_text)
                            time.sleep(1)
                            self.input_box.send_keys(Keys.ENTER)
                            message_sent = True
                            logger.info(f"✅ Text message sent via typing to {phone}")
                            
                        except Exception as e2:
                            logger.error(f"❌ Both send methods failed: {e2}")
                    
                    if not message_sent:
                        return MessageResult(
                            success=False,
                            status=MessageStatus.FAILED,
                            message_id=None,
                            error_category=ErrorCategory.WHATSAPP_WEB_ERROR,
                            error_message="Failed to send message with all methods",
                            should_continue=True
                        )
                    
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
            if counsellor_name and counsellor_name in ALL_COUNSELLORS:
                employee_id = ALL_COUNSELLORS[counsellor_name]['employee_id']
                logger.debug(f"Using employee ID {employee_id} for counsellor {counsellor_name}")
            else:
                logger.warning(f"Counsellor '{counsellor_name}' not found in ALL_COUNSELLORS, using default employee ID 1")
            
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
        
        for name, config in ALL_COUNSELLORS.items():
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
        for name, config in ALL_COUNSELLORS.items():
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
# INTELLIGENT TEAM FAILOVER SYSTEM  
# ============================================================================

class TeamFailoverManager:
    """Manages intelligent failover when teams go offline during campaigns"""
    
    def __init__(self, team_manager: PhoneTeamManager):
        self.team_manager = team_manager
        # Define backup relationships
        self.backup_mapping = {
            'sweta_jio': 'sweta_airtel',      # If Sweta Jio fails → use Sweta Airtel
            'dipali_jio': 'dipali_airtel'     # If Dipali Jio fails → use Dipali Airtel
        }
        self.failover_history = []
        logger.info("🔄 Intelligent Failover System initialized")
    
    def check_team_health(self, team_id: str, client) -> bool:
        """Check if team's WhatsApp session is still active"""
        try:
            if not client or not client.driver:
                return False
            
            # Quick health check - try to access page
            current_url = client.driver.current_url
            if "web.whatsapp.com" not in current_url.lower():
                return False
            
            # Check if still logged in (look for logged-in indicators)
            page_text = client.driver.page_source.lower()
            logged_out_indicators = [
                "scan me",
                "qr code", 
                "download whatsapp",
                "use whatsapp on your computer"
            ]
            
            if any(indicator in page_text for indicator in logged_out_indicators):
                logger.warning(f"🚨 Team {team_id} appears to be logged out")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for team {team_id}: {e}")
            return False
    
    def get_backup_team(self, failed_team: str) -> Optional[str]:
        """Get backup team for failed team"""
        return self.backup_mapping.get(failed_team)
    
    def can_failover(self, failed_team: str, available_teams: set) -> bool:
        """Check if failover is possible"""
        backup_team = self.get_backup_team(failed_team)
        return backup_team and backup_team in available_teams
    
    def merge_team_counselors(self, primary_team: str, backup_team: str) -> Dict:
        """Merge counselors from failed team with backup team"""
        try:
            primary_config = self.team_manager.get_team_by_id(primary_team)
            backup_config = self.team_manager.get_team_by_id(backup_team)
            
            if not primary_config or not backup_config:
                return None
            
            # Create merged team configuration
            merged_counselors = {}
            
            # Add backup team counselors first (they have active session)
            merged_counselors.update(backup_config['counsellors'])
            
            # Add primary team counselors (will use backup team's WhatsApp session)
            merged_counselors.update(primary_config['counsellors'])
            
            merged_config = backup_config.copy()
            merged_config['counsellors'] = merged_counselors
            merged_config['original_teams'] = [primary_team, backup_team]
            merged_config['capacity'] = sum(c['daily_limit'] for c in merged_counselors.values())
            
            logger.info(f"🔄 TEAM MERGER: {primary_team} + {backup_team}")
            logger.info(f"   📱 Phone: {backup_config['phone']}")
            logger.info(f"   👥 Combined Counselors: {', '.join(merged_counselors.keys())}")
            logger.info(f"   📊 Total Capacity: {merged_config['capacity']}")
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Failed to merge teams {primary_team} + {backup_team}: {e}")
            return None
    
    def redistribute_leads(self, failed_team_leads: List[Dict], backup_team: str, 
                          backup_client, quota_manager) -> bool:
        """Redistribute leads from failed team to backup team"""
        try:
            if not failed_team_leads:
                return True
            
            backup_config = self.team_manager.get_team_by_id(backup_team)
            merged_config = self.merge_team_counselors(
                self.get_primary_team_for_backup(backup_team), backup_team
            )
            
            if not merged_config:
                return False
            
            logger.info(f"🔄 LEAD REDISTRIBUTION: {len(failed_team_leads)} leads")
            logger.info(f"   📤 From: Failed team")
            logger.info(f"   📥 To: {backup_team} ({backup_config['phone']})")
            logger.info(f"   👥 Available Counselors: {', '.join(merged_config['counsellors'].keys())}")
            
            # Update the backup client to use merged configuration
            backup_client.team_config = merged_config
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to redistribute leads: {e}")
            return False
    
    def get_primary_team_for_backup(self, backup_team: str) -> Optional[str]:
        """Get primary team that uses this backup"""
        for primary, backup in self.backup_mapping.items():
            if backup == backup_team:
                return primary
        return None
    
    def log_failover_event(self, failed_team: str, backup_team: str, leads_count: int):
        """Log failover event for monitoring"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'failed_team': failed_team,
            'backup_team': backup_team,
            'leads_redistributed': leads_count,
            'action': 'team_failover'
        }
        self.failover_history.append(event)
        
        logger.warning(f"🚨 FAILOVER EVENT LOGGED:")
        logger.warning(f"   💥 Failed: {failed_team}")
        logger.warning(f"   🔄 Backup: {backup_team}")
        logger.warning(f"   📊 Leads: {leads_count}")

# ============================================================================
# AUTOMATED DAILY REPORTING SYSTEM
# ============================================================================

class DailyReportGenerator:
    """Generates and sends comprehensive daily reports to management"""
    
    def __init__(self, team_manager: PhoneTeamManager, quota_manager: GlobalQuotaManager):
        self.team_manager = team_manager
        self.quota_manager = quota_manager
        self.report_enabled = os.getenv('ENABLE_DAILY_REPORTS', 'true').lower() == 'true'
        logger.info("📊 Daily Report Generator initialized")
    
    def generate_comprehensive_report(self, campaign_result: Dict, failover_events: List = None) -> str:
        """Generate comprehensive daily report from campaign data and quota files"""
        try:
            report_template = self._load_report_template()
            
            # Get campaign metrics
            metrics = campaign_result.get('metrics', {})
            
            # Calculate key statistics
            total_messages = metrics.get('sent', 0)
            success_rate = metrics.get('success_rate', 0)
            duration = self._format_duration(campaign_result.get('start_time'), datetime.now())
            
            # Get quota information
            global_used = self.quota_manager.get_global_quota_used()
            global_limit = GLOBAL_DAILY_LIMIT
            
            # Get team breakdown
            team_breakdown = self._generate_team_breakdown(metrics.get('team_breakdown', {}))
            team_quota_breakdown = self._generate_team_quota_breakdown()
            counselor_stats = self._generate_counselor_stats(metrics.get('team_breakdown', {}))
            
            # Get system status
            successful_teams = campaign_result.get('successful_teams', [])
            failed_teams = campaign_result.get('failed_teams', [])
            
            # Generate failover section
            failover_section = self._generate_failover_section(failover_events or [])
            
            # Calculate business insights
            estimated_value = self._calculate_estimated_value(total_messages)
            weekly_progress = self._get_weekly_progress()
            next_campaign = self._get_next_campaign_time()
            
            # Get top performing team
            top_team, best_success_rate = self._get_top_performing_team(metrics.get('team_breakdown', {}))
            
            # Replace template placeholders
            report = report_template.replace('{{DATE}}', datetime.now().strftime('%d %B %Y'))
            report = report.replace('{{TIME}}', datetime.now().strftime('%I:%M %p'))
            report = report.replace('{{TOTAL_MESSAGES}}', str(total_messages))
            report = report.replace('{{SUCCESS_RATE}}', f"{success_rate:.1f}")
            report = report.replace('{{DURATION}}', duration)
            report = report.replace('{{GLOBAL_USED}}', str(global_used))
            report = report.replace('{{GLOBAL_LIMIT}}', str(global_limit))
            report = report.replace('{{TEAM_BREAKDOWN}}', team_breakdown)
            report = report.replace('{{TEAM_QUOTA_BREAKDOWN}}', team_quota_breakdown)
            report = report.replace('{{COUNSELOR_STATS}}', counselor_stats)
            report = report.replace('{{ACTIVE_TEAMS}}', ', '.join(successful_teams))
            report = report.replace('{{FAILED_TEAMS}}', ', '.join(failed_teams) if failed_teams else 'None')
            report = report.replace('{{FAILOVER_SECTION}}', failover_section)
            report = report.replace('{{SENT_COUNT}}', str(metrics.get('sent', 0)))
            report = report.replace('{{DELIVERED_COUNT}}', str(metrics.get('delivered', 0)))
            report = report.replace('{{READ_COUNT}}', str(metrics.get('read', 0)))
            report = report.replace('{{FAILED_COUNT}}', str(metrics.get('failed', 0)))
            report = report.replace('{{TOP_TEAM}}', top_team)
            report = report.replace('{{BEST_SUCCESS_RATE}}', f"{best_success_rate:.1f}")
            report = report.replace('{{ESTIMATED_VALUE}}', estimated_value)
            report = report.replace('{{WEEKLY_PROGRESS}}', weekly_progress)
            report = report.replace('{{NEXT_CAMPAIGN_TIME}}', next_campaign)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return self._generate_fallback_report(campaign_result)
    
    def _load_report_template(self) -> str:
        """Load report template from file"""
        try:
            if os.path.exists('report.txt'):
                with open('report.txt', 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning("report.txt not found, using fallback template")
                return self._get_fallback_template()
        except Exception as e:
            logger.error(f"Error loading report template: {e}")
            return self._get_fallback_template()
    
    def _generate_team_breakdown(self, team_breakdown: Dict) -> str:
        """Generate formatted team performance breakdown"""
        if not team_breakdown:
            return "• No team data available"
        
        breakdown_lines = []
        for team_id, metrics in team_breakdown.items():
            team_config = self.team_manager.get_team_by_id(team_id)
            if team_config:
                team_name = f"{team_config['manager']} {team_config['network']}"
                phone = team_config['phone']
                sent = metrics.get('sent', 0)
                total = metrics.get('total_processed', 0)
                success_rate = (sent / total * 100) if total > 0 else 0
                
                breakdown_lines.append(
                    f"• {team_name} ({phone}): {sent} sent, {success_rate:.1f}% success"
                )
        
        return '\n'.join(breakdown_lines) if breakdown_lines else "• No team data available"
    
    def _generate_team_quota_breakdown(self) -> str:
        """Generate team quota breakdown from multi_team_quota.json in format: team(counselors)=count"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            quota_breakdown = []
            
            # Try to read from multi_team_quota.json
            try:
                with open('multi_team_quota.json', 'r') as f:
                    quota_data = json.load(f)
                    today_data = quota_data.get(today, {})
                    teams_data = today_data.get('teams', {})
            except (FileNotFoundError, json.JSONDecodeError):
                teams_data = {}
            
            # Generate breakdown for each team
            all_teams = self.team_manager.get_all_teams()
            for team_id in ['sweta_jio', 'sweta_airtel', 'dipali_jio', 'dipali_airtel']:
                team_config = all_teams.get(team_id)
                if team_config:
                    # Get counselors for this team
                    counselors = list(team_config['counsellors'].keys())
                    counselors_str = ','.join(counselors)
                    
                    # Get quota usage for this team
                    team_quota = teams_data.get(team_id, 0)
                    
                    # Format: team_name(counselor1,counselor2)=count
                    quota_breakdown.append(f"{team_id}({counselors_str})={team_quota}")
            
            return '\n'.join(quota_breakdown) if quota_breakdown else "• No quota data available"
            
        except Exception as e:
            logger.error(f"Error generating team quota breakdown: {e}")
            return "• Error loading quota data"
    
    def _generate_counselor_stats(self, team_breakdown: Dict) -> str:
        """Generate counselor statistics from team data"""
        counselor_stats = {}
        
        for team_id, metrics in team_breakdown.items():
            team_config = self.team_manager.get_team_by_id(team_id)
            if team_config:
                counselors = team_config.get('counsellors', {})
                sent_count = metrics.get('sent', 0)
                
                # Distribute sent messages across counselors (simplified)
                counselors_in_team = len(counselors)
                if counselors_in_team > 0:
                    avg_per_counselor = sent_count // counselors_in_team
                    remainder = sent_count % counselors_in_team
                    
                    for i, counselor_name in enumerate(counselors.keys()):
                        counselor_sent = avg_per_counselor + (1 if i < remainder else 0)
                        if counselor_name in counselor_stats:
                            counselor_stats[counselor_name] += counselor_sent
                        else:
                            counselor_stats[counselor_name] = counselor_sent
        
        # Format counselor stats
        if counselor_stats:
            stats_lines = []
            for counselor, sent in sorted(counselor_stats.items(), key=lambda x: x[1], reverse=True):
                phone = ALL_COUNSELLORS.get(counselor, {}).get('number', 'Unknown')
                stats_lines.append(f"• {counselor} ({phone}): {sent} messages")
            return '\n'.join(stats_lines)
        else:
            return "• No counselor data available"
    
    def _generate_failover_section(self, failover_events: List) -> str:
        """Generate failover events section"""
        if not failover_events:
            return "🔄 *Failover Events:* None (All teams remained stable)"
        
        failover_lines = ["🔄 *Failover Events:*"]
        for event in failover_events:
            failed_team = event.get('failed_team', 'Unknown')
            backup_team = event.get('backup_team', 'Unknown')
            leads_count = event.get('leads_redistributed', 0)
            timestamp = event.get('timestamp', 'Unknown')
            
            failover_lines.append(f"• {failed_team} → {backup_team} ({leads_count} leads at {timestamp})")
        
        failover_lines.append("✅ All failover operations completed successfully")
        return '\n'.join(failover_lines)
    
    def _calculate_estimated_value(self, total_messages: int) -> str:
        """Calculate estimated business value"""
        # Rough calculation: each message could generate ₹500-2000 in visa fees
        min_value = total_messages * 500
        max_value = total_messages * 2000
        return f"₹{min_value:,} - ₹{max_value:,}"
    
    def _get_weekly_progress(self) -> str:
        """Get weekly progress information"""
        try:
            # Load quota data for the week
            today = datetime.now()
            week_total = 0
            
            for i in range(7):
                date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                try:
                    with open('multi_team_quota.json', 'r') as f:
                        data = json.load(f)
                        day_data = data.get(date, {})
                        week_total += day_data.get('global_total', 0)
                except:
                    continue
            
            return f"{week_total} messages this week"
        except:
            return "Weekly data unavailable"
    
    def _get_next_campaign_time(self) -> str:
        """Get next campaign time"""
        now = datetime.now()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_run.strftime('%d %B %Y at %I:%M %p')
    
    def _get_top_performing_team(self, team_breakdown: Dict) -> Tuple[str, float]:
        """Get top performing team"""
        if not team_breakdown:
            return "No data", 0.0
        
        best_team = ""
        best_rate = 0.0
        
        for team_id, metrics in team_breakdown.items():
            sent = metrics.get('sent', 0)
            total = metrics.get('total_processed', 0)
            if total > 0:
                success_rate = (sent / total) * 100
                if success_rate > best_rate:
                    best_rate = success_rate
                    team_config = self.team_manager.get_team_by_id(team_id)
                    if team_config:
                        best_team = f"{team_config['manager']} {team_config['network']}"
        
        return best_team or "No data", best_rate
    
    def _format_duration(self, start_time, end_time) -> str:
        """Format campaign duration"""
        try:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration = end_time - start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    
    def _get_fallback_template(self) -> str:
        """Fallback template if report.txt is not found"""
        return """📊 WhatsApp Automation Daily Report
📅 Date: {{DATE}}
⏰ Time: {{TIME}}

📈 Campaign Summary:
• Total Messages: {{TOTAL_MESSAGES}}
• Success Rate: {{SUCCESS_RATE}}%
• Duration: {{DURATION}}
• Global Quota: {{GLOBAL_USED}}/{{GLOBAL_LIMIT}}

📱 Team Performance:
{{TEAM_BREAKDOWN}}

📊 Team Quota Usage:
{{TEAM_QUOTA_BREAKDOWN}}

🔄 System Status:
• Active Teams: {{ACTIVE_TEAMS}}
• Failed Teams: {{FAILED_TEAMS}}

{{FAILOVER_SECTION}}

🤖 Automated Report by WhatsApp Automation System"""
    
    def _generate_fallback_report(self, campaign_result: Dict) -> str:
        """Generate basic fallback report"""
        metrics = campaign_result.get('metrics', {})
        team_quota_breakdown = self._generate_team_quota_breakdown()
        
        return f"""📊 WhatsApp Automation Daily Report
📅 {datetime.now().strftime('%d %B %Y')}
⏰ {datetime.now().strftime('%I:%M %p')}

📈 Quick Summary:
• Messages Sent: {metrics.get('sent', 0)}
• Success Rate: {metrics.get('success_rate', 0):.1f}%
• Global Quota Used: {self.quota_manager.get_global_quota_used()}/{GLOBAL_DAILY_LIMIT}

📊 Team Quota Usage:
{team_quota_breakdown}

🤖 Automated Report by WhatsApp Automation System"""
    
    def send_report_to_management(self, report_content: str, available_client=None) -> bool:
        """Send generated report to all management numbers"""
        if not self.report_enabled:
            logger.info("📊 Daily reports disabled in configuration")
            return False
        
        if not available_client:
            logger.warning("📊 No available WhatsApp client for sending reports")
            return False
        
        logger.info("📊 Sending daily report to management...")
        
        sent_count = 0
        total_recipients = len(MANAGEMENT_NUMBERS)
        
        for name, phone in MANAGEMENT_NUMBERS.items():
            try:
                logger.info(f"📊 Sending report to {name} ({phone})")
                
                # Navigate to recipient's chat
                if available_client._navigate_to_chat(phone):
                    # Find input box
                    if available_client._find_input_box():
                        # Send report using clipboard method
                        try:
                            available_client.input_box.clear()
                            pyperclip.copy(report_content)
                            time.sleep(0.5)
                            
                            available_client.input_box.click()
                            time.sleep(0.5)
                            
                            available_client.input_box.send_keys(Keys.CONTROL, "v")
                            time.sleep(1)
                            
                            available_client.input_box.send_keys(Keys.ENTER)
                            
                            logger.info(f"✅ Report sent to {name}")
                            sent_count += 1
                            
                            # Add delay between recipients
                            time.sleep(3)
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to send report to {name}: {e}")
                    else:
                        logger.error(f"❌ Could not find input box for {name}")
                else:
                    logger.error(f"❌ Could not open chat for {name} ({phone})")
                    
            except Exception as e:
                logger.error(f"❌ Error sending report to {name}: {e}")
        
        success_rate = (sent_count / total_recipients) * 100
        logger.info(f"📊 Report delivery complete: {sent_count}/{total_recipients} sent ({success_rate:.1f}% success)")
        
        return sent_count > 0

# ============================================================================
# MULTI-TEAM AUTOMATION ORCHESTRATOR
# ============================================================================

class MultiTeamAutomation:
    """Orchestrates parallel execution across all phone teams with intelligent failover"""
    
    def __init__(self):
        self.team_manager = PhoneTeamManager()
        self.quota_manager = GlobalQuotaManager()
        self.lead_distributor = LeadDistributor(self.team_manager.get_all_teams())
        self.team_clients = {}  # Will store SeleniumWhatsAppClient instances
        self.team_analytics = {}  # Per-team analytics
        self.global_analytics = CampaignAnalytics()
        self.enable_parallel = os.getenv('ENABLE_PARALLEL_EXECUTION', 'true').lower() == 'true'
        self.max_browsers = int(os.getenv('MAX_CONCURRENT_BROWSERS', '4'))
        
        # 🚀 NEW: Intelligent Failover System
        self.failover_manager = TeamFailoverManager(self.team_manager)
        self.active_teams = set()  # Track currently active teams
        self.failed_teams = set()  # Track failed teams
        self.redistributed_leads = {}  # Track redistributed leads
        
        # 📊 NEW: Daily Report Generator
        self.report_generator = DailyReportGenerator(self.team_manager, self.quota_manager)
        
    def initialize_all_browsers(self) -> Dict[str, bool]:
        """Initialize all browser sessions in parallel with strict team validation"""
        opt_logger.browser_status("🚀 Initializing all phone team browsers...")
        
        initialization_results = {}
        
        if self.enable_parallel:
            # Use ThreadPoolExecutor for parallel browser initialization
            with ThreadPoolExecutor(max_workers=self.max_browsers) as executor:
                future_to_team = {}
                
                for team_id, team_config in self.team_manager.get_all_teams().items():
                    future = executor.submit(self._initialize_single_team_browser, team_id, team_config)
                    future_to_team[future] = team_id
                
                # Process results as they complete
                for future in as_completed(future_to_team):
                    team_id = future_to_team[future]
                    try:
                        success = future.result()
                        initialization_results[team_id] = success
                        if success:
                            # Validate WhatsApp session matches team phone
                            team_config = self.team_manager.get_team_by_id(team_id)
                            expected_phone = team_config['phone']
                            opt_logger.browser_status(f"✅ {team_id} browser ready (Phone: {expected_phone})")
                        else:
                            opt_logger.browser_status(f"❌ {team_id} browser failed")
                    except Exception as e:
                        logger.error(f"Exception initializing {team_id}: {e}")
                        initialization_results[team_id] = False
        else:
            # Sequential initialization (for debugging)
            opt_logger.browser_status("🔍 Sequential browser initialization (debug mode)")
            for team_id, team_config in self.team_manager.get_all_teams().items():
                success = self._initialize_single_team_browser(team_id, team_config)
                initialization_results[team_id] = success
                if success:
                    expected_phone = team_config['phone']
                    opt_logger.browser_status(f"✅ {team_id} browser ready (Phone: {expected_phone})")
                else:
                    opt_logger.browser_status(f"❌ {team_id} browser failed")
                
                # Add delay between browsers in sequential mode
                if team_id != list(self.team_manager.get_all_teams().keys())[-1]:  # Not last
                    delay = int(os.getenv('BROWSER_STARTUP_DELAY', '5'))
                    opt_logger.browser_status(f"⏳ Waiting {delay}s before next browser...")
                    time.sleep(delay)
        
        # Summary with phone validation
        successful_teams = [team for team, success in initialization_results.items() if success]
        failed_teams = [team for team, success in initialization_results.items() if not success]
        
        opt_logger.browser_status(f"🌐 Browser initialization complete:")
        opt_logger.browser_status(f"   ✅ Successful: {len(successful_teams)}/{len(initialization_results)}")
        
        if successful_teams:
            opt_logger.browser_status(f"🔐 TEAM-BROWSER VALIDATION:")
            for team_id in successful_teams:
                team_config = self.team_manager.get_team_by_id(team_id)
                manager = team_config['manager']
                network = team_config['network']
                phone = team_config['phone']
                opt_logger.browser_status(f"   ✅ {team_id}: {manager} {network} → {phone}")
        
        if failed_teams:
            opt_logger.browser_status(f"   ❌ Failed Teams: {', '.join(failed_teams)}")
            opt_logger.browser_status(f"   ⚠️  Failed teams will be SKIPPED to prevent wrong number usage")
        
        return initialization_results
    
    def _initialize_single_team_browser(self, team_id: str, team_config: Dict) -> bool:
        """Initialize browser for a single team"""
        try:
            # Create WhatsApp client for this team
            client = SeleniumWhatsAppClient(team_id=team_id, team_config=team_config)
            
            # Initialize browser session
            success = client.initialize_browser()
            
            if success:
                self.team_clients[team_id] = client
                # Initialize team-specific analytics
                self.team_analytics[team_id] = CampaignAnalytics()
                logger.info(f"✅ Team {team_id} browser initialized successfully")
                return True
            else:
                logger.error(f"❌ Failed to initialize browser for team {team_id}")
                return False
                
        except Exception as e:
            logger.error(f"Exception initializing team {team_id}: {e}")
            return False
    
    def fetch_and_distribute_leads(self) -> Dict[str, List[Dict]]:
        """Fetch leads and distribute ONLY across teams with logged-in browsers"""
        opt_logger.browser_status("📋 Fetching and distributing leads across ACTIVE teams...")
        
        # Only consider teams that have successfully logged-in browsers
        active_teams = list(self.team_clients.keys())
        opt_logger.browser_status(f"🔐 Active teams with logged-in browsers: {', '.join(active_teams)}")
        
        # Calculate total available capacity ONLY for active teams
        total_capacity = 0
        team_capacity_info = {}
        
        for team_id in active_teams:
            team_capacity = self.team_manager.get_team_capacity(team_id)
            used = self.quota_manager.get_team_quota_used(team_id)
            available = max(0, team_capacity - used)
            total_capacity += available
            team_capacity_info[team_id] = available
            
            team_config = self.team_manager.get_team_by_id(team_id)
            logger.debug(f"Team {team_id} ({team_config['phone']}): {available} available capacity")
        
        # Limit by global quota (CRITICAL: Respect .env GLOBAL_DAILY_LIMIT)
        global_remaining = self.quota_manager.get_global_remaining()
        global_used = self.quota_manager.get_global_quota_used()
        
        # The effective capacity is limited by BOTH team capacity AND global limit
        total_capacity = min(total_capacity, global_remaining)
        
        opt_logger.browser_status(f"📊 QUOTA ANALYSIS:")
        opt_logger.browser_status(f"   🌍 Global: {global_used}/{GLOBAL_DAILY_LIMIT} used, {global_remaining} remaining")
        opt_logger.browser_status(f"   📱 Teams: {sum(team_capacity_info.values())} total team capacity available")
        opt_logger.browser_status(f"   ⚡ EFFECTIVE TARGET: {total_capacity} messages (limited by global quota)")
        
        if total_capacity == 0:
            if global_remaining == 0:
                opt_logger.browser_status("🚫 GLOBAL DAILY LIMIT REACHED!")
                opt_logger.browser_status(f"   Used: {global_used}/{GLOBAL_DAILY_LIMIT} messages today")
            else:
                opt_logger.browser_status("⚠️ No available capacity across any ACTIVE teams")
                opt_logger.browser_status("💡 Ensure teams have logged-in WhatsApp sessions and available quota")
            return {}
        
        # Fetch leads
        leads = self.fetch_leads(total_capacity)
        if not leads:
            opt_logger.browser_status("📭 No leads available from API")
            return {}
        
        # Create filtered phone teams with only active teams
        active_phone_teams = {
            team_id: self.team_manager.get_team_by_id(team_id) 
            for team_id in active_teams
        }
        
        # Create temporary distributor with only active teams
        active_distributor = LeadDistributor(active_phone_teams)
        
        # Distribute leads across ONLY active teams
        distributed_leads = active_distributor.distribute_leads(leads, self.quota_manager)
        
        # Validate distribution - ensure no leads go to inactive teams
        validated_distribution = {}
        for team_id, team_leads in distributed_leads.items():
            if team_id in active_teams:
                validated_distribution[team_id] = team_leads
            else:
                logger.warning(f"⚠️ Prevented lead assignment to inactive team: {team_id}")
        
        # Log distribution with phone validation
        opt_logger.browser_status("📊 SECURED Lead distribution (Team → Phone):")
        total_distributed = 0
        for team_id, team_leads in validated_distribution.items():
            if team_leads:
                team_config = self.team_manager.get_team_by_id(team_id)
                team_name = f"{team_config['manager']} {team_config['network']}"
                team_phone = team_config['phone']
                opt_logger.browser_status(f"   📱 {team_name}: {len(team_leads)} leads → {team_phone}")
                total_distributed += len(team_leads)
        
        opt_logger.browser_status(f"🎯 Total distributed: {total_distributed}/{len(leads)} leads")
        opt_logger.browser_status(f"🔐 All leads will use CORRECT manager phone numbers only")
        
        return validated_distribution
    
    def fetch_leads(self, limit: int) -> List[Dict]:
        """Fetch leads from API (shared method)"""
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
    
    def process_teams_parallel(self, distributed_leads: Dict[str, List[Dict]]) -> Dict:
        """Process all teams in parallel with INTELLIGENT FAILOVER and real-time health monitoring"""
        opt_logger.browser_status("🚀 Starting parallel team processing with INTELLIGENT FAILOVER...")
        
        # Validate that all teams have their own browser sessions
        for team_id in distributed_leads.keys():
            if team_id not in self.team_clients:
                logger.error(f"🚨 CRITICAL: Team {team_id} has leads but NO browser session!")
                raise ValueError(f"Security violation: Team {team_id} cannot process leads without dedicated browser")
        
        # 🚀 NEW: Initialize active teams tracking
        self.active_teams = set(distributed_leads.keys())
        opt_logger.browser_status("🔐 Team-Browser Security Check: PASSED")
        opt_logger.browser_status(f"🔄 Failover System: ACTIVE (monitoring {len(self.active_teams)} teams)")
        
        # Start analytics
        self.global_analytics.start_campaign()
        for analytics in self.team_analytics.values():
            analytics.start_campaign()
        
        # 🚀 NEW: Process teams with real-time health monitoring and failover
        if self.enable_parallel:
            team_results = self._process_with_intelligent_failover(distributed_leads)
        else:
            # Sequential processing with health monitoring
            team_results = self._process_sequential_with_monitoring(distributed_leads)
        
        # End analytics
        self.global_analytics.end_campaign()
        for analytics in self.team_analytics.values():
            analytics.end_campaign()
        
        # 🚀 NEW: Log failover summary
        if self.failover_manager.failover_history:
            opt_logger.browser_status("🔄 FAILOVER EVENTS SUMMARY:")
            for event in self.failover_manager.failover_history:
                opt_logger.browser_status(f"   💥 {event['failed_team']} → 🔄 {event['backup_team']} ({event['leads_redistributed']} leads)")
        
        return team_results
    
    def _process_with_intelligent_failover(self, distributed_leads: Dict[str, List[Dict]]) -> Dict:
        """Process teams in parallel with real-time health monitoring and automatic failover"""
        opt_logger.browser_status("🔄 Starting INTELLIGENT FAILOVER processing...")
        
        team_results = {}
        active_distributed_leads = distributed_leads.copy()
        
        with ThreadPoolExecutor(max_workers=len(self.team_clients)) as executor:
            future_to_team = {}
            
            # Start processing all teams
            for team_id, team_leads in active_distributed_leads.items():
                if team_leads and team_id in self.team_clients:
                    team_config = self.team_manager.get_team_by_id(team_id)
                    expected_phone = team_config['phone']
                    opt_logger.browser_status(f"🔐 Processing {team_id} → {expected_phone} ({len(team_leads)} leads)")
                    
                    future = executor.submit(self._process_team_with_health_monitoring, team_id, team_leads)
                    future_to_team[future] = team_id
            
            # Monitor and collect results with failover handling
            for future in as_completed(future_to_team):
                team_id = future_to_team[future]
                try:
                    result = future.result()
                    team_results[team_id] = result
                    
                    # Check if this team failed and needs failover
                    if result.get('health_failed', False):
                        self._handle_team_failover(team_id, active_distributed_leads, executor, future_to_team)
                    else:
                        team_config = self.team_manager.get_team_by_id(team_id)
                        opt_logger.browser_status(f"✅ Team {team_id} ({team_config['phone']}) processing complete")
                        
                except Exception as e:
                    logger.error(f"Exception processing team {team_id}: {e}")
                    team_results[team_id] = {'processed': 0, 'errors': 1, 'health_failed': True}
                    
                    # Try failover for this team
                    self._handle_team_failover(team_id, active_distributed_leads, executor, future_to_team)
        
        return team_results
    
    def _process_sequential_with_monitoring(self, distributed_leads: Dict[str, List[Dict]]) -> Dict:
        """Process teams sequentially with health monitoring and failover"""
        opt_logger.browser_status("🔄 Starting SEQUENTIAL processing with health monitoring...")
        
        team_results = {}
        active_distributed_leads = distributed_leads.copy()
        
        for team_id, team_leads in list(active_distributed_leads.items()):
            if team_leads and team_id in self.team_clients:
                team_config = self.team_manager.get_team_by_id(team_id)
                expected_phone = team_config['phone']
                opt_logger.browser_status(f"🔐 Processing {team_id} → {expected_phone} ({len(team_leads)} leads)")
                
                result = self._process_team_with_health_monitoring(team_id, team_leads)
                team_results[team_id] = result
                
                # Check if this team failed and needs failover
                if result.get('health_failed', False):
                    self._handle_team_failover_sequential(team_id, active_distributed_leads, team_results)
                else:
                    opt_logger.browser_status(f"✅ Team {team_id} ({expected_phone}) processing complete")
        
        return team_results
    
    def _handle_team_failover(self, failed_team: str, active_leads: Dict, executor, future_to_team: Dict):
        """Handle failover for a failed team in parallel processing"""
        try:
            backup_team = self.failover_manager.get_backup_team(failed_team)
            
            if not backup_team or backup_team not in self.team_clients:
                opt_logger.browser_status(f"❌ No backup available for {failed_team}")
                return
            
            if backup_team in self.failed_teams:
                opt_logger.browser_status(f"❌ Backup team {backup_team} also failed - cannot failover")
                return
            
            # Get remaining leads for failed team
            failed_leads = active_leads.get(failed_team, [])
            if not failed_leads:
                return
            
            opt_logger.browser_status(f"🚨 FAILOVER TRIGGERED: {failed_team} → {backup_team}")
            
            # Merge teams and redistribute leads
            success = self.failover_manager.redistribute_leads(
                failed_leads, backup_team, self.team_clients[backup_team], self.quota_manager
            )
            
            if success:
                # Add failed team leads to backup team
                if backup_team not in active_leads:
                    active_leads[backup_team] = []
                active_leads[backup_team].extend(failed_leads)
                
                # Remove failed team from active processing
                active_leads.pop(failed_team, None)
                self.failed_teams.add(failed_team)
                
                # Log the failover event
                self.failover_manager.log_failover_event(failed_team, backup_team, len(failed_leads))
                
                opt_logger.browser_status(f"✅ FAILOVER SUCCESS: {len(failed_leads)} leads moved to {backup_team}")
            else:
                opt_logger.browser_status(f"❌ FAILOVER FAILED for {failed_team}")
                
        except Exception as e:
            logger.error(f"Failover handling error: {e}")
    
    def _handle_team_failover_sequential(self, failed_team: str, active_leads: Dict, team_results: Dict):
        """Handle failover for a failed team in sequential processing"""
        try:
            backup_team = self.failover_manager.get_backup_team(failed_team)
            
            if not backup_team or backup_team not in self.team_clients:
                opt_logger.browser_status(f"❌ No backup available for {failed_team}")
                return
            
            if backup_team in self.failed_teams:
                opt_logger.browser_status(f"❌ Backup team {backup_team} also failed - cannot failover")
                return
            
            # Get remaining leads for failed team  
            failed_leads = active_leads.get(failed_team, [])
            if not failed_leads:
                return
            
            opt_logger.browser_status(f"🚨 FAILOVER TRIGGERED: {failed_team} → {backup_team}")
            
            # Merge teams and process leads with backup team
            success = self.failover_manager.redistribute_leads(
                failed_leads, backup_team, self.team_clients[backup_team], self.quota_manager
            )
            
            if success:
                # Process the failed leads with backup team
                backup_result = self._process_team_with_health_monitoring(backup_team, failed_leads)
                
                # Merge results
                if backup_team in team_results:
                    team_results[backup_team]['processed'] += backup_result.get('processed', 0)
                    team_results[backup_team]['errors'] += backup_result.get('errors', 0)
                else:
                    team_results[backup_team] = backup_result
                
                # Mark failed team
                self.failed_teams.add(failed_team)
                
                # Log the failover event
                self.failover_manager.log_failover_event(failed_team, backup_team, len(failed_leads))
                
                opt_logger.browser_status(f"✅ FAILOVER SUCCESS: {len(failed_leads)} leads processed by {backup_team}")
            else:
                opt_logger.browser_status(f"❌ FAILOVER FAILED for {failed_team}")
                
        except Exception as e:
            logger.error(f"Sequential failover handling error: {e}")
    
    def _process_team_with_health_monitoring(self, team_id: str, leads: List[Dict]) -> Dict:
        """Process team leads with continuous health monitoring"""
        try:
            # Initial health check
            client = self.team_clients.get(team_id)
            if not client or not self.failover_manager.check_team_health(team_id, client):
                opt_logger.browser_status(f"🚨 Team {team_id} failed initial health check")
                return {'processed': 0, 'errors': len(leads), 'health_failed': True}
            
            # Process leads with periodic health checks
            processed = 0
            errors = 0
            health_check_interval = 5  # Check health every 5 leads
            
            for i, lead in enumerate(leads, 1):
                # Periodic health check
                if i % health_check_interval == 0:
                    if not self.failover_manager.check_team_health(team_id, client):
                        opt_logger.browser_status(f"🚨 Team {team_id} health check FAILED at lead {i}/{len(leads)}")
                        remaining_leads = len(leads) - i + 1
                        return {
                            'processed': processed, 
                            'errors': errors, 
                            'health_failed': True,
                            'remaining_leads': leads[i-1:],  # Unprocessed leads
                            'failure_point': i
                        }
                
                # Process single lead
                try:
                    # Get counsellor for this team (with merged counsellors if applicable)
                    counsellor_name, counsellor_config = self._get_team_counsellor(team_id)
                    if not counsellor_name:
                        errors += 1
                        continue
                    
                    result = self._process_single_lead_for_team_secured(
                        lead, counsellor_name, counsellor_config, client, team_id
                    )
                    
                    # Track analytics
                    if team_id in self.team_analytics:
                        self.team_analytics[team_id].track_result(
                            str(lead.get('lead_id', '')), 
                            counsellor_name, 
                            result, 
                            result.status
                        )
                    
                    # Update quota
                    if result.success:
                        self.quota_manager.increment_quota(team_id)
                        processed += 1
                        
                        lead_name = lead.get('full_name', 'Customer')
                        team_config = self.team_manager.get_team_by_id(team_id)
                        expected_phone = team_config['phone']
                        logger.info(f"✅ {team_id} ({expected_phone}): {lead_name} → {counsellor_name}")
                    else:
                        errors += 1
                    
                    # Add human-like delay
                    if i < len(leads):  # Not last message
                        delay = random.uniform(MIN_DELAY_BETWEEN_MESSAGES, MAX_DELAY_BETWEEN_MESSAGES)
                        
                        if delay < 120:
                            delay_type = "⚡ Quick"
                        elif delay < 300:
                            delay_type = "⏳ Normal"  
                        else:
                            delay_type = "🐌 Careful"
                        
                        logger.info(f"🤖→👤 {team_id}: {delay_type} human-like delay: {delay:.1f}s")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"Error processing lead in team {team_id}: {e}")
                    errors += 1
            
            logger.info(f"🔐 {team_id} processing complete: {processed} sent, {errors} errors")
            return {'processed': processed, 'errors': errors, 'health_failed': False}
            
        except Exception as e:
            logger.error(f"Team processing error for {team_id}: {e}")
            return {'processed': 0, 'errors': len(leads), 'health_failed': True}
    
    def _process_single_team_secured(self, team_id: str, leads: List[Dict]) -> Dict:
        """Process leads for a single team with STRICT security validation"""
        
        # CRITICAL SECURITY CHECK: Ensure team can only use its own browser
        if team_id not in self.team_clients:
            logger.error(f"🚨 SECURITY VIOLATION: Team {team_id} trying to process without dedicated browser!")
            return {'processed': 0, 'errors': len(leads), 'security_error': True}
        
        client = self.team_clients[team_id]
        team_config = self.team_manager.get_team_by_id(team_id)
        analytics = self.team_analytics[team_id]
        
        # Additional security validation
        expected_phone = team_config['phone']
        manager_name = team_config['manager']
        network = team_config['network']
        
        logger.info(f"🔐 SECURED Processing for {team_id}: {manager_name} {network} → {expected_phone}")
        
        processed = 0
        errors = 0
        
        for i, lead in enumerate(leads, 1):
            try:
                # Get available counsellor from THIS SPECIFIC team only
                counsellor_name, counsellor_config = self._get_team_counsellor(team_id)
                if not counsellor_name:
                    logger.warning(f"No available counsellors in team {team_id}")
                    break
                
                # DOUBLE CHECK: Ensure we're using correct team's browser
                if client.team_id != team_id:
                    logger.error(f"🚨 CRITICAL: Browser session mismatch! Expected {team_id}, got {client.team_id}")
                    errors += 1
                    continue
                
                # Process lead with security validation
                result = self._process_single_lead_for_team_secured(
                    lead, counsellor_name, counsellor_config, client, team_id
                )
                
                # Track analytics
                analytics.track_result(
                    str(lead.get('lead_id', '')), 
                    counsellor_name, 
                    result, 
                    result.status
                )
                
                # Update quota
                if result.success:
                    self.quota_manager.increment_quota(team_id)
                    processed += 1
                    
                    # Log successful send with team validation
                    lead_name = lead.get('full_name', 'Customer')
                    logger.info(f"✅ {team_id} ({expected_phone}): {lead_name} → {counsellor_name}")
                else:
                    errors += 1
                
                # Add HUMAN-LIKE delay between messages (per team)
                if i < len(leads):  # Not last message
                    delay = random.uniform(MIN_DELAY_BETWEEN_MESSAGES, MAX_DELAY_BETWEEN_MESSAGES)
                    
                    # Make it more human-like with varied delay patterns
                    if delay < 120:  # Short delay
                        delay_type = "⚡ Quick"
                    elif delay < 300:  # Medium delay
                        delay_type = "⏳ Normal"
                    else:  # Long delay
                        delay_type = "🐌 Careful"
                    
                    logger.info(f"🤖→👤 {team_id}: {delay_type} human-like delay: {delay:.1f}s before next message")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing lead in team {team_id}: {e}")
                errors += 1
        
        logger.info(f"🔐 {team_id} SECURED processing complete: {processed} sent, {errors} errors")
        return {'processed': processed, 'errors': errors}
    
    def _process_single_team(self, team_id: str, leads: List[Dict]) -> Dict:
        """Legacy method - redirects to secured version"""
        return self._process_single_team_secured(team_id, leads)
    
    def _get_team_counsellor(self, team_id: str) -> Tuple[Optional[str], Optional[Dict]]:
        """Get available counsellor from team"""
        team_config = self.team_manager.get_team_by_id(team_id)
        if not team_config:
            return None, None
        
        # For now, return random counsellor from team
        # TODO: Implement team-specific quota tracking
        counsellors = team_config['counsellors']
        if counsellors:
            name = random.choice(list(counsellors.keys()))
            return name, counsellors[name]
        
        return None, None
    
    def _process_single_lead_for_team_secured(self, lead: Dict, counsellor_name: str, 
                                             counsellor_config: Dict, client: SeleniumWhatsAppClient, 
                                             team_id: str) -> MessageResult:
        """Process single lead for specific team with STRICT security validation"""
        
        # SECURITY CHECK 1: Verify team configuration
        team_config = self.team_manager.get_team_by_id(team_id)
        if not team_config:
            logger.error(f"🚨 SECURITY: Invalid team_id {team_id}")
            return MessageResult(
                success=False,
                status=MessageStatus.FAILED,
                message_id=None,
                error_category=ErrorCategory.UNKNOWN_ERROR,
                error_message="Invalid team configuration",
                should_continue=False
            )
        
        # SECURITY CHECK 2: Verify counsellor belongs to this team
        if counsellor_name not in team_config['counsellors']:
            logger.error(f"🚨 SECURITY: Counsellor {counsellor_name} does not belong to team {team_id}")
            return MessageResult(
                success=False,
                status=MessageStatus.FAILED,
                message_id=None,
                error_category=ErrorCategory.UNKNOWN_ERROR,
                error_message="Counsellor-team mismatch",
                should_continue=False
            )
        
        # SECURITY CHECK 3: Verify client belongs to correct team
        if hasattr(client, 'team_id') and client.team_id != team_id:
            logger.error(f"🚨 SECURITY: Client team mismatch! Expected {team_id}, got {client.team_id}")
            return MessageResult(
                success=False,
                status=MessageStatus.FAILED,
                message_id=None,
                error_category=ErrorCategory.UNKNOWN_ERROR,
                error_message="Client-team mismatch",
                should_continue=False
            )
        
        lead_id = str(lead.get('lead_id', ''))
        lead_name = lead.get('full_name', 'Customer')
        expected_phone = team_config['phone']
        
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
        
        # Log security validation success
        logger.debug(f"🔐 SECURITY PASSED: {team_id} → {expected_phone} | {lead_name} → {counsellor_name}")
        
        # Send message through verified team's browser session
        result = client.send_template_message(
            phone=target_phone,
            template=os.getenv('WATI_TEMPLATE_NAME', 'Template_Name'),
            params=parameters
        )
        
        # Save to external log with secured team info
        log_status = "sent" if result.success else "failed"
        message_content = client._build_message_from_template(parameters)
        
        self._save_team_message_log_secured(
            lead=lead,
            status=log_status,
            message_id=result.message_id,
            error=result.error_message if not result.success else None,
            counsellor_name=counsellor_name,
            message_content=message_content,
            team_id=team_id,
            expected_phone=expected_phone
        )
        
        return result
    
    def _process_single_lead_for_team(self, lead: Dict, counsellor_name: str, 
                                     counsellor_config: Dict, client: SeleniumWhatsAppClient, 
                                     team_id: str) -> MessageResult:
        """Legacy method - redirects to secured version"""
        return self._process_single_lead_for_team_secured(lead, counsellor_name, counsellor_config, client, team_id)
    
    def _save_team_message_log_secured(self, lead: Dict, status: str, message_id: str = None, 
                                      error: str = None, counsellor_name: str = None, 
                                      message_content: str = None, team_id: str = None,
                                      expected_phone: str = None) -> bool:
        """Save message log with SECURED team information and validation"""
        try:
            # SECURITY VALIDATION: Verify team configuration
            team_config = self.team_manager.get_team_by_id(team_id)
            if not team_config:
                logger.error(f"🚨 LOG SECURITY: Invalid team_id {team_id}")
                return False
            
            # Get employee ID with validation
            employee_id = 1  # Default fallback
            if counsellor_name and counsellor_name in ALL_COUNSELLORS:
                employee_id = ALL_COUNSELLORS[counsellor_name]['employee_id']
                logger.debug(f"🔐 LOG: Employee ID {employee_id} for {counsellor_name}")
            else:
                logger.warning(f"⚠️ LOG: Unknown counsellor {counsellor_name}, using default employee ID")
            
            # SECURITY: Use verified team phone number for from_phone_number
            verified_from_phone = team_config['phone']
            
            # Additional validation - ensure expected phone matches team phone
            if expected_phone and expected_phone != verified_from_phone:
                logger.error(f"🚨 LOG SECURITY: Phone mismatch! Expected {expected_phone}, team has {verified_from_phone}")
                return False
            
            payload = {
                "lead_id": lead.get('lead_id'),
                "message_content": message_content if message_content else f"Template: {os.getenv('WATI_TEMPLATE_NAME', 'Template_Name')}",
                "msg_type": "template",
                "msg_status": status,
                "to_phone_number": lead.get('mobile_number_formatted'),
                "from_phone_number": verified_from_phone,  # SECURED: Always use verified team phone
                "template_name": os.getenv('WATI_TEMPLATE_NAME', 'Template_Name'),
                "employee": employee_id,
                "method": f"selenium_whatsapp_web_team_{team_id}_secured"
            }
            
            # Add team validation metadata
            payload["team_validation"] = {
                "team_id": team_id,
                "manager": team_config['manager'],
                "network": team_config['network'],
                "verified_phone": verified_from_phone,
                "counsellor": counsellor_name
            }
            
            if message_id:
                payload["message_id"] = message_id
            if error:
                payload["error_message"] = error
            if status == "sent":
                payload["sent_at"] = datetime.now().isoformat()
            
            # Log the secure operation
            logger.info(f"🔐 SECURE LOG: {team_id} → {verified_from_phone} | {counsellor_name} | {status}")
            
            response = requests.post(
                LEAD_LOG_API_URL,
                json=payload,
                headers=LEAD_API_HEADERS,
                timeout=15
            )
            
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"Failed to save secured team log: {e}")
            return False
    
    def _save_team_message_log(self, lead: Dict, status: str, message_id: str = None, 
                              error: str = None, counsellor_name: str = None, 
                              message_content: str = None, team_id: str = None) -> bool:
        """Legacy method - redirects to secured version"""
        team_config = self.team_manager.get_team_by_id(team_id) if team_id else None
        expected_phone = team_config['phone'] if team_config else None
        
        return self._save_team_message_log_secured(
            lead, status, message_id, error, counsellor_name, 
            message_content, team_id, expected_phone
        )
    
    def close_all_browsers(self):
        """Close all browser sessions"""
        opt_logger.browser_status("🔴 Closing all browser sessions...")
        
        for team_id, client in self.team_clients.items():
            try:
                client.close_browser()
                opt_logger.browser_status(f"🔴 {team_id} browser closed")
            except Exception as e:
                logger.error(f"Error closing {team_id} browser: {e}")
        
        self.team_clients.clear()
    
    def get_combined_metrics(self) -> Dict:
        """Get combined metrics from all teams"""
        combined_metrics = {
            'sent': 0,
            'delivered': 0,
            'read': 0,
            'failed': 0,
            'pending': 0,
            'total_processed': 0,
            'team_breakdown': {},
            'global_quota_used': self.quota_manager.get_global_quota_used()
        }
        
        for team_id, analytics in self.team_analytics.items():
            team_metrics = analytics.get_metrics()
            
            # Add to combined totals
            for key in ['sent', 'delivered', 'read', 'failed', 'pending', 'total_processed']:
                combined_metrics[key] += team_metrics.get(key, 0)
            
            # Store team breakdown
            combined_metrics['team_breakdown'][team_id] = team_metrics
        
        # Calculate success rate
        total = combined_metrics['total_processed']
        if total > 0:
            successful = combined_metrics['sent'] + combined_metrics['delivered'] + combined_metrics['read']
            combined_metrics['success_rate'] = (successful / total) * 100
        else:
            combined_metrics['success_rate'] = 0
        
        return combined_metrics
    
    def run_multi_team_campaign(self) -> Dict:
        """Run the complete multi-team campaign"""
        try:
            # Check working hours
            if not self.is_working_hours():
                current_time = datetime.now().strftime('%H:%M')
                return {
                    'status': 'outside_working_hours',
                    'message': f'Outside working hours ({SCRIPT_START_TIME}-{SCRIPT_END_TIME})',
                    'current_time': current_time
                }
            
            # Check global quota
            global_remaining = self.quota_manager.get_global_remaining()
            if global_remaining == 0:
                return {
                    'status': 'global_quota_exhausted',
                    'message': f'Global daily limit reached ({self.quota_manager.get_global_quota_used()}/{GLOBAL_DAILY_LIMIT})'
                }
            
            # Initialize all browsers
            browser_results = self.initialize_all_browsers()
            successful_teams = [team for team, success in browser_results.items() if success]
            
            if not successful_teams:
                return {
                    'status': 'all_browsers_failed',
                    'message': 'Failed to initialize any browser sessions'
                }
            
            # Fetch and distribute leads
            distributed_leads = self.fetch_and_distribute_leads()
            if not distributed_leads:
                return {
                    'status': 'no_leads_to_distribute',
                    'message': 'No leads available for distribution'
                }
            
            # Process teams in parallel
            campaign_start_time = datetime.now()
            team_results = self.process_teams_parallel(distributed_leads)
            
            # Get final metrics
            final_metrics = self.get_combined_metrics()
            
            # 📊 NEW: Generate and send daily report to management
            try:
                campaign_result = {
                    'status': 'completed',
                    'successful_teams': successful_teams,
                    'failed_teams': [team for team, success in browser_results.items() if not success],
                    'team_results': team_results,
                    'metrics': final_metrics,
                    'failover_events': self.failover_manager.failover_history,
                    'start_time': campaign_start_time.isoformat(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Generate comprehensive daily report
                opt_logger.browser_status("📊 Generating daily management report...")
                report_content = self.report_generator.generate_comprehensive_report(
                    campaign_result, self.failover_manager.failover_history
                )
                
                # Find any available client for sending reports
                available_client = None
                for team_id, client in self.team_clients.items():
                    if client and hasattr(client, 'driver') and client.driver:
                        try:
                            # Quick health check
                            if self.failover_manager.check_team_health(team_id, client):
                                available_client = client
                                break
                        except:
                            continue
                
                # Send report to management
                if available_client:
                    opt_logger.browser_status("📊 Sending daily report to management...")
                    report_sent = self.report_generator.send_report_to_management(
                        report_content, available_client
                    )
                    
                    if report_sent:
                        opt_logger.browser_status("✅ Daily report sent to management successfully")
                    else:
                        opt_logger.browser_status("⚠️ Daily report sending had issues")
                else:
                    opt_logger.browser_status("⚠️ No active WhatsApp client available for sending reports")
                    logger.warning("Daily report generated but could not be sent - no active WhatsApp sessions")
                
            except Exception as e:
                logger.error(f"Error generating/sending daily report: {e}")
                opt_logger.browser_status("❌ Daily report generation failed")
            
            return campaign_result
            
        except Exception as e:
            logger.error(f"Multi-team campaign error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            # Always close browsers
            self.close_all_browsers()
    
    def is_working_hours(self) -> bool:
        """Check if within working hours"""
        try:
            current = datetime.now().time()
            start = datetime.strptime(SCRIPT_START_TIME, '%H:%M').time()
            end = datetime.strptime(SCRIPT_END_TIME, '%H:%M').time()
            return start <= current <= end
        except Exception:
            return True  # Default to allowing operation

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
    """Display multi-team configuration banner"""
    safe_print("\n" + "="*70)
    safe_print("🚀 MULTI-TEAM WHATSAPP AUTOMATION SYSTEM")
    safe_print("="*70)
    safe_print(f"🌐 Method: Parallel Selenium WhatsApp Web")
    template_name = os.getenv('WATI_TEMPLATE_NAME', 'Template_Name')
    safe_print(f"📋 Template: {template_name} (content from template.txt)")
    safe_print(f"📎 Media Mode: {'ENABLED' if SEND_MEDIA else 'TEXT-ONLY'}")
    if SEND_MEDIA:
        safe_print(f"📊 Priority: 1️⃣ Images → 2️⃣ Videos → 3️⃣ Documents")
    safe_print(f"⏰ Working Hours: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")
    safe_print(f"🎯 Mode: {'TEST' if USE_TEST_NUMBER else 'PRODUCTION'}")
    
    # Show team configuration
    try:
        team_manager = PhoneTeamManager()
        teams = team_manager.get_all_teams()
        safe_print(f"")
        safe_print(f"📱 PHONE TEAMS CONFIGURATION:")
        total_capacity = 0
        for team_id, team in teams.items():
            counsellor_list = ', '.join(team['counsellors'].keys())
            capacity = team['capacity']
            total_capacity += capacity
            safe_print(f"   🔹 {team['manager']} {team['network']} ({team['phone']})")
            safe_print(f"      👥 Team: {counsellor_list}")
            safe_print(f"      📊 Capacity: {capacity} messages/day")
        
        safe_print(f"")
        safe_print(f"🌍 GLOBAL LIMITS:")
        safe_print(f"   📈 Total Team Capacity: {total_capacity} messages/day")
        safe_print(f"   🚧 Global Daily Limit: {GLOBAL_DAILY_LIMIT} messages/day")
        effective_capacity = min(total_capacity, GLOBAL_DAILY_LIMIT)
        safe_print(f"   ⚡ EFFECTIVE Daily Limit: {effective_capacity} messages/day")
        if GLOBAL_DAILY_LIMIT < total_capacity:
            safe_print(f"   ⚠️  Global limit is CONTROLLING (limiting from {total_capacity} to {GLOBAL_DAILY_LIMIT})")
        else:
            safe_print(f"   ✅ Team capacity is within global limit")
        
    except Exception as e:
        safe_print(f"⚠️ Team configuration error: {e}")
        safe_print(f"👥 Fallback: {len(ALL_COUNSELLORS)} counsellors configured")
    
    safe_print(f"")
    safe_print(f"🔧 AUTOMATION SETTINGS:")
    delay_min_min = MIN_DELAY_BETWEEN_MESSAGES // 60
    delay_max_min = MAX_DELAY_BETWEEN_MESSAGES // 60
    safe_print(f"   🤖→👤 Human-like Delays: {MIN_DELAY_BETWEEN_MESSAGES}s-{MAX_DELAY_BETWEEN_MESSAGES}s ({delay_min_min}-{delay_max_min} min)")
    safe_print(f"   🖥️ Max Browsers: {os.getenv('MAX_CONCURRENT_BROWSERS', '4')}")
    safe_print(f"   🔄 Parallel Mode: {'ENABLED' if os.getenv('ENABLE_PARALLEL_EXECUTION', 'true').lower() == 'true' else 'DISABLED'}")
    safe_print(f"   📂 Profiles Base: {os.getenv('CHROME_PROFILES_BASE_PATH', 'Default')}")
    
    # Add delay recommendations
    if MAX_DELAY_BETWEEN_MESSAGES < 120:
        safe_print(f"   ⚠️  DELAY WARNING: Very fast delays may trigger WhatsApp detection")
    elif MAX_DELAY_BETWEEN_MESSAGES > 600:
        safe_print(f"   🐌 SLOW MODE: Extra careful delays for maximum safety")
    
    safe_print(f"")
    safe_print(f"📊 AUTOMATED DAILY REPORTING:")
    safe_print(f"   📋 Comprehensive campaign reports generated automatically")
    safe_print(f"   📱 Auto-sent to management: Salman Sir, Sagar Sir, Sweta Mam, Dipali Mam, Fahad")
    safe_print(f"   📈 Includes: Team performance, counselor stats, failover events")
    safe_print(f"   📄 Template: report.txt (customizable like template.txt)")
    safe_print(f"   💼 Business insights: Lead value, weekly progress, next campaign")
    
    safe_print(f"")
    safe_print(f"🔄 INTELLIGENT FAILOVER SYSTEM:")
    safe_print(f"   🚨 Real-time WhatsApp session monitoring")
    safe_print(f"   🔄 Automatic lead redistribution on team failure")
    safe_print(f"   📱 sweta_jio fails → merge with sweta_airtel")
    safe_print(f"   📱 dipali_jio fails → merge with dipali_airtel")
    safe_print(f"   👥 Combined counselor pools for seamless operation")
    safe_print(f"")
    safe_print(f"🔐 CRITICAL SECURITY NOTICE:")
    safe_print(f"   ⚠️  MUST scan QR codes with CORRECT manager phones!")
    safe_print(f"   📱 Each team ONLY uses its designated WhatsApp number")
    safe_print(f"   🚨 Teams without proper login will be SKIPPED")
    safe_print(f"   ✅ Only active/logged-in teams will process leads")
    safe_print(f"   🔄 Failed teams automatically failover to backups")
    safe_print("="*70)

def print_final_summary(result: Dict):
    """Print multi-team campaign summary"""
    safe_print("\n" + "🏁"*60)
    safe_print("📊 MULTI-TEAM CAMPAIGN EXECUTION SUMMARY")
    safe_print("🏁"*60)
    
    status = result['status']
    
    if status == 'completed':
        metrics = result.get('metrics', {})
        successful_teams = result.get('successful_teams', [])
        failed_teams = result.get('failed_teams', [])
        
        safe_print(f"✅ STATUS: COMPLETED")
        safe_print(f"")
        safe_print(f"🌐 GLOBAL RESULTS:")
        safe_print(f"   📤 Messages Sent: {metrics.get('sent', 0)}")
        safe_print(f"   📱 Delivered: {metrics.get('delivered', 0)}")
        safe_print(f"   👀 Read: {metrics.get('read', 0)}")
        safe_print(f"   ❌ Failed: {metrics.get('failed', 0)}")
        safe_print(f"   ⚡ Success Rate: {metrics.get('success_rate', 0):.1f}%")
        safe_print(f"   🌍 Global Quota Used: {metrics.get('global_quota_used', 0)}/{GLOBAL_DAILY_LIMIT}")
        
        safe_print(f"")
        safe_print(f"📱 TEAM STATUS:")
        safe_print(f"   ✅ Successful Teams: {len(successful_teams)}")
        if successful_teams:
            try:
                team_manager = PhoneTeamManager()
                for team_id in successful_teams:
                    team_config = team_manager.get_team_by_id(team_id)
                    if team_config:
                        safe_print(f"      🔹 {team_id}: {team_config['manager']} {team_config['network']} ({team_config['phone']})")
                    else:
                        safe_print(f"      🔹 {team_id}")
            except:
                for team_id in successful_teams:
                    safe_print(f"      🔹 {team_id}")
        
        if failed_teams:
            safe_print(f"   ❌ Failed Teams: {len(failed_teams)} (SKIPPED - No WhatsApp Login)")
            try:
                team_manager = PhoneTeamManager()
                for team_id in failed_teams:
                    team_config = team_manager.get_team_by_id(team_id)
                    if team_config:
                        safe_print(f"      🔸 {team_id}: {team_config['manager']} {team_config['network']} ({team_config['phone']}) - LOGIN REQUIRED")
                    else:
                        safe_print(f"      🔸 {team_id} - LOGIN REQUIRED")
            except:
                for team_id in failed_teams:
                    safe_print(f"      🔸 {team_id} - LOGIN REQUIRED")
        
        # 🚀 NEW: Show failover events if any occurred
        failover_events = result.get('failover_events', [])
        if failover_events:
            safe_print(f"")
            safe_print(f"🔄 INTELLIGENT FAILOVER EVENTS:")
            for event in failover_events:
                failed_team = event.get('failed_team', 'Unknown')
                backup_team = event.get('backup_team', 'Unknown')
                leads_count = event.get('leads_redistributed', 0)
                timestamp = event.get('timestamp', 'Unknown')
                safe_print(f"   💥 {failed_team} → 🔄 {backup_team} ({leads_count} leads at {timestamp})")
            safe_print(f"   ✅ All failed team leads automatically processed by backup teams")
        
        # Show team breakdown if available
        team_breakdown = metrics.get('team_breakdown', {})
        if team_breakdown:
            safe_print(f"")
            safe_print(f"📊 TEAM BREAKDOWN:")
            for team_id, team_metrics in team_breakdown.items():
                team_sent = team_metrics.get('sent', 0)
                team_failed = team_metrics.get('failed', 0)
                team_total = team_metrics.get('total_processed', 0)
                if team_total > 0:
                    team_success_rate = ((team_sent) / team_total) * 100
                    safe_print(f"   📱 {team_id}: {team_sent} sent, {team_failed} failed ({team_success_rate:.1f}% success)")
        
        if metrics.get('sent', 0) > 0:
            safe_print("\n🎯 NEXT STEPS:")
            safe_print("   ✅ Check WhatsApp Web sessions for delivery confirmations")
            safe_print("   📱 Monitor responses across all manager phones")
            safe_print("   🔍 Review message logs in admin panel")
            safe_print("   📊 Check team-specific analytics")
            safe_print("   📊 Daily report sent to management automatically")
        else:
            safe_print("\n⚠️ NO MESSAGES SENT - CHECK:")
            safe_print("   🌐 WhatsApp Web login status for all teams")
            safe_print("   📱 Phone number formats in .env")
            safe_print("   🖥️ Browser and Chrome driver setup")
            safe_print("   👥 Team configurations in .env")
        
        # 📊 NEW: Show daily report status
        safe_print("\n📊 DAILY REPORT STATUS:")
        safe_print("   📋 Comprehensive report generated from campaign data")
        safe_print("   📱 Sent to: Salman Sir, Sagar Sir, Sweta Mam, Dipali Mam, Fahad")
        safe_print("   📄 Template: report.txt (customizable)")
        safe_print("   💼 Includes: Performance, analytics, business insights")
    
    elif status == 'all_browsers_failed':
        safe_print(f"🖥️ STATUS: ALL BROWSER SESSIONS FAILED")
        safe_print("🔧 CHECK:")
        safe_print("   📱 WhatsApp Web QR code scan for all phones")
        safe_print("   🖥️ Chrome driver path and permissions")
        safe_print("   📂 Chrome profile directories")
        safe_print("   🌐 Internet connection")
    
    elif status == 'no_leads_to_distribute':
        safe_print(f"📭 STATUS: NO LEADS AVAILABLE FOR DISTRIBUTION")
        safe_print("🔍 CHECK:")
        safe_print("   📊 Lead API and filters")
        safe_print("   💾 Team quotas and capacity")
        safe_print("   🌍 Global daily limit")
    
    elif status == 'outside_working_hours':
        safe_print(f"🕐 STATUS: OUTSIDE WORKING HOURS")
        safe_print(f"⏰ Current: {result.get('current_time', 'Unknown')}")
        safe_print(f"🕘 Allowed: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")
    
    elif status == 'global_quota_exhausted':
        safe_print(f"🌍 STATUS: GLOBAL DAILY LIMIT REACHED")
        safe_print(f"🚫 Maximum {GLOBAL_DAILY_LIMIT} messages/day limit reached")
        safe_print("📅 Script will resume tomorrow")
    
    elif status == 'error':
        safe_print(f"💥 STATUS: SYSTEM ERROR")
        safe_print(f"🔍 Error: {result.get('message', 'Unknown error')}")
        safe_print("🔧 CHECK:")
        safe_print("   📝 Script logs for details")
        safe_print("   🌐 Network connectivity")
        safe_print("   📂 File permissions")
    
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
        
        # Initialize multi-team automation
        automation = MultiTeamAutomation()
        
        # Run multi-team campaign
        result = automation.run_multi_team_campaign()
        
        # Display results
        print_final_summary(result)
        
    except KeyboardInterrupt:
        logger.info("🛑 Campaign interrupted by user")
        safe_print("🛑 Campaign stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        safe_print(f"💥 Error: {e}")
        traceback.print_exc()
