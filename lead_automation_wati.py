"""
Lead Automation with WATI WhatsApp Integration
==============================================

This script automates the process of:
1. Fetching leads from the /get-leads/ API with optional owner_id & limit params
2. Sending WhatsApp messages using WATI API (template: temp1)
3. Applying per-counsellor daily quota limits and working time constraints
4. Replacing parameters: {{counsellor_name}}, {{counsellor_number}}, {{lead_id}}

Author: Assistant
Version: 1.0
Requirements: python-dotenv, requests
"""

import requests
import os
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from urllib.parse import urlparse, quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# Load environment variables
load_dotenv('../config.env')  # config.env is one level up

# Configure logging with UTF-8 encoding for file and safe console output
import sys

# File handler with UTF-8 encoding
file_handler = logging.FileHandler('lead_automation.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler with safe encoding
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# ⏰ TIME WINDOW SETTINGS
SCRIPT_START_TIME = '09:00'  # Local time
SCRIPT_END_TIME = '18:00'    # Local time

# 🧑‍💼 COUNSELLOR CONFIGURATION & QUOTAS
COUNSELLORS = {
    'Anandi': {
        'daily_limit': 30,
        'number': '+919512270915',
    },
    'Preeti': {
        'daily_limit': 5,
        'number': '+918799334198',
    },
    'Khushali': {
        'daily_limit': 5,
        'number': '+917069629625',
    },
    'Karan': {
        'daily_limit': 5,
        'number': '+919773432629',
    },
    'Sangita': {
        'daily_limit': 5,
        'number': '+918128758628',
    },
    'Maitri': {
        'daily_limit': 5,
        'number': '+918866817620',
    },
    'Chitra': {
        'daily_limit': 5,
        'number': '+918128817870',
    },
    'Pragatee': {
        'daily_limit': 5,
        'number': '+919687046717',
    },
    'Vaidehi': {
        'daily_limit': 5,
        'number': '+917874202685',
    }
}

# Static configuration for all counsellors
STATIC_OWNER_ID = int(os.getenv('LEAD_OWNER_ID', '227'))

# 🎯 DEPLOYMENT MODE
USE_TEST_NUMBER = os.getenv('USE_TEST_NUMBER', 'true').lower() == 'true'
TEST_MOBILE_NUMBER = os.getenv('TEST_MOBILE_NUMBER', '+918128557443')

# 🔐 API CONFIGURATION

LEAD_API_URL = os.getenv('LEAD_API_URL', 'https://your-domain.com/lead/get-leads-basic-info/')
API_TOKEN = os.getenv('LEAD_API_TOKEN', 'Token your_token_here')
WATI_TEMPLATE_NAME = os.getenv('WATI_TEMPLATE_NAME', 'wati_campaign_sagarps_leads')
WATI_LOG_API_URL = os.getenv('WATI_LOG_API_URL', 'https://your-domain.com/lead/post-wati-msg-logs/')

# Headers for Lead API
LEAD_API_HEADERS = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}

class WATIWhatsAppAPI:
    """WATI WhatsApp API Client Class"""

    def __init__(self, api_key: str = None, base_url: str = None, instance_id: str = None):
        self.api_key = api_key or os.getenv('WATI_API_KEY')
        self.base_url = base_url or os.getenv('WATI_BASE_URL')
        self.instance_id = instance_id or os.getenv('WATI_INSTANCE_ID')

        if not self.api_key:
            raise ValueError("WATI API key not found. Please set WATI_API_KEY in config.env")
        if not self.base_url:
            raise ValueError("WATI base URL not found. Please set WATI_BASE_URL in config.env")
        if not self.instance_id:
            raise ValueError("WATI instance ID not found. Please set WATI_INSTANCE_ID in config.env")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

        logger.info("WATI API client initialized successfully")

    def _validate_phone_number(self, number: str) -> str:
        number = number.strip()
        return number.lstrip('+')

    def _make_request(self, endpoint: str, payload: Dict = None) -> Dict:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"Making request to: {url}")
            if payload:
                logger.debug(f"Payload: {payload}")

            response = self.session.post(url, json=payload if payload else None, headers=self.headers, timeout=30)
            logger.debug(f"Response status: {response.status_code}")

            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text

            if response.status_code == 200:
                logger.debug("Request successful")
                return {'success': True, 'data': response_data, 'status_code': 200}
            else:
                error_msg = f"API Error {response.status_code}: {response_data}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg, 'status_code': response.status_code}
        except Exception as e:
            return {'success': False, 'error': f"Unexpected error: {str(e)}"}

    def send_template_message(self, phone_number: str, template_name: str, parameters: List[Dict[str, str]] = None, headerValues: Optional[List[Dict]] = None, broadcast_name: str = "lead_automation") -> Dict:
        try:
            formatted_phone = self._validate_phone_number(phone_number)

            payload = {
                "template_name": template_name,
                "broadcast_name": broadcast_name
            }
            if parameters:
                payload["parameters"] = parameters
            if headerValues:
                payload["headerValues"] = headerValues

            endpoint = f"sendTemplateMessage?whatsappNumber={formatted_phone}"
            result = self._make_request(endpoint, payload)
            if result['success']:
                logger.info(f"Template message '{template_name}' sent to {formatted_phone}")
            return result
        except Exception as e:
            return {'success': False, 'error': f"Template message error: {str(e)}"}

class LeadAutomationManager:
    """Manages lead fetching and WhatsApp automation"""

    def __init__(self):
        self.wati_client = WATIWhatsAppAPI()
        self.quota_file = 'quota_usage.json'
        self.sent_messages_file = 'sent_messages.json'
        self.daily_quota = self._load_daily_quota()
        self.sent_messages_today = self._load_sent_messages_today()

    def _load_daily_quota(self) -> Dict:
        """Load daily quota usage from file"""
        try:
            if os.path.exists(self.quota_file):
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    return data.get(today, {})
            return {}
        except Exception as e:
            logger.error(f"Error loading quota file: {e}")
            return {}

    def _save_daily_quota(self):
        """Save daily quota usage to file"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            # Load existing data
            all_data = {}
            if os.path.exists(self.quota_file):
                with open(self.quota_file, 'r') as f:
                    all_data = json.load(f)

            # Update today's data
            all_data[today] = self.daily_quota

            # Keep only last 7 days of data
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            all_data = {k: v for k, v in all_data.items() if k >= cutoff_date}

            # Save back to file
            with open(self.quota_file, 'w') as f:
                json.dump(all_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving quota file: {e}")

    def _load_sent_messages_today(self) -> set:
        """Load sent messages for today to prevent duplicates"""
        try:
            if os.path.exists(self.sent_messages_file):
                with open(self.sent_messages_file, 'r') as f:
                    data = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    return set(data.get(today, []))
            return set()
        except Exception as e:
            logger.error(f"Error loading sent messages file: {e}")
            return set()

    def _save_sent_message(self, lead_id: str):
        """Save sent message to prevent duplicates"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            # Load existing data
            all_data = {}
            if os.path.exists(self.sent_messages_file):
                with open(self.sent_messages_file, 'r') as f:
                    all_data = json.load(f)

            # Update today's data
            if today not in all_data:
                all_data[today] = []
            all_data[today].append(lead_id)

            # Keep only last 7 days of data
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            all_data = {k: v for k, v in all_data.items() if k >= cutoff_date}

            # Save back to file
            with open(self.sent_messages_file, 'w') as f:
                json.dump(all_data, f, indent=2)

            self.sent_messages_today.add(lead_id)

        except Exception as e:
            logger.error(f"Error saving sent message: {e}")

    def is_within_working_hours(self) -> bool:
        """Check if current time is within working hours"""
        try:
            current_time = datetime.now().time()
            start_time = datetime.strptime(SCRIPT_START_TIME, '%H:%M').time()
            end_time = datetime.strptime(SCRIPT_END_TIME, '%H:%M').time()

            return start_time <= current_time <= end_time
        except Exception as e:
            logger.error(f"Error checking working hours: {e}")
            return False

    def fetch_leads(self, owner_id: int, limit: int) -> List[Dict]:
        """Fetch leads from the API"""
        try:
            params = {
                'owner_id': owner_id,
                'limit': limit,
                'template_name': WATI_TEMPLATE_NAME
            }

            logger.info(f"Fetching leads for owner_id: {owner_id}, limit: {limit}, template: {WATI_TEMPLATE_NAME}")
            response = requests.get(LEAD_API_URL, params=params, headers=LEAD_API_HEADERS, timeout=30)

            if response.status_code == 200:
                data = response.json()
                leads = data.get('data', [])
                logger.info(f"Successfully fetched {len(leads)} leads")
                return leads
            else:
                logger.error(f"Error fetching leads: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Exception while fetching leads: {e}")
            return []

    def save_message_log(self, lead: Dict, message_content: str, msg_status: str,
                     to_phone: str, from_phone: str = None) -> bool:
        """Save message log to database via API"""
        try:
            payload = {
                "lead_id": lead.get('lead_id'),
                "message_content": message_content,
                "msg_type": "template",
                "msg_status": msg_status,
                "to_phone_number": to_phone,
                "from_phone_number": from_phone,
                "template_name": WATI_TEMPLATE_NAME
            }

            # Add sent_at timestamp for successful sends
            if msg_status == "sent":
                payload["sent_at"] = datetime.now().isoformat()

            logger.debug(f"Saving message log to {WATI_LOG_API_URL} with payload: {payload}")
            response = requests.post(WATI_LOG_API_URL, json=payload, headers=LEAD_API_HEADERS, timeout=30)

            if response.status_code == 201:
                logger.info(f"✅ Message log saved successfully for lead {lead.get('lead_id')}")
                return True
            else:
                logger.error(f"❌ Failed to save message log - Status: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Exception saving message log: {e}")
            return False

    def send_whatsapp_message(self, lead: Dict, counsellor_name: str, counsellor_number: str) -> Tuple[bool, str, bool]:
        """Send WhatsApp message to a lead with detailed API response logging

        Returns:
            Tuple[bool, str, bool]: (success, message, should_continue_processing)
            - success: Whether the message was actually delivered
            - message: Success/error message
            - should_continue_processing: False if systematic failure (stop all processing)
        """
        try:
            lead_id = str(lead.get('lead_id', ''))
            lead_name = lead.get('full_name', 'Customer')

            # Use test number or actual lead number based on configuration
            if USE_TEST_NUMBER:
                mobile_number = TEST_MOBILE_NUMBER
                actual_mobile = lead.get('mobile_number_formatted', 'N/A')
                logger.info(f"🧪 TEST MODE: Sending to test number {mobile_number} (Lead's actual: {actual_mobile})")
            else:
                raw_mobile = lead.get('mobile_number_formatted', '')
                if not raw_mobile:
                    logger.error(f"❌ No mobile number found for lead {lead_id}")
                    return False, "No mobile number available", True  # Continue with other leads

                # Format phone number with +91 country code if not present
                if raw_mobile.startswith('+'):
                    mobile_number = raw_mobile
                elif raw_mobile.startswith('91') and len(raw_mobile) == 12:
                    mobile_number = f"+{raw_mobile}"
                elif len(raw_mobile) == 10:
                    mobile_number = f"+91{raw_mobile}"
                else:
                    mobile_number = f"+91{raw_mobile.lstrip('0')}"

                logger.info(f"🚀 PRODUCTION MODE: Sending to lead's number: {mobile_number} - Lead: {lead_name} (ID: {lead_id})")
                logger.info(f"   📱 Original: {raw_mobile} → Formatted: {mobile_number}")

            # Prepare template parameters
            parameters = [
                {"name": "1", "value": lead_name},           # {{1}} - Lead name
                {"name": "2", "value": counsellor_name},     # {{2}} - Counsellor name
                {"name": "3", "value": counsellor_number}    # {{3}} - Counsellor number
            ]

            # Log message details
            logger.info(f"📋 Message Details:")
            logger.info(f"   Template: {WATI_TEMPLATE_NAME}")
            logger.info(f"   To: {mobile_number} ({lead_name})")
            logger.info(f"   From: {counsellor_name} ({counsellor_number})")
            logger.info(f"   Parameters: {parameters}")

            # Send message with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"📡 Attempt {attempt + 1}/{max_retries}: Sending WhatsApp message...")

                    result = self.wati_client.send_template_message(
                        phone_number=mobile_number,
                        template_name=WATI_TEMPLATE_NAME,
                        parameters=parameters,
                        broadcast_name=f"lead_automation_{counsellor_name}"
                    )

                    # Detailed response logging with proper success detection
                    if result.get('success'):
                        api_response = result.get('data', {})

                        # Check if WATI actually delivered the message (not just HTTP 200)
                        wati_result = api_response.get('result', False)
                        wati_info = api_response.get('info', '')

                        if wati_result == True:
                            # TRUE SUCCESS - Message actually sent
                            logger.info(f"✅ WATI MESSAGE DELIVERED for Lead {lead_id}")
                            logger.info(f"   📊 API Response: {api_response}")
                            logger.info(f"   📱 Delivered to: {mobile_number}")
                            logger.info(f"   👤 Lead: {lead_name}")
                            logger.info(f"   🎯 Template: {WATI_TEMPLATE_NAME}")
                            logger.info(f"   👨‍💼 Counsellor: {counsellor_name}")

                            # Save successful delivery log
                            log_saved = self.save_message_log(
                            lead=lead,
                                message_content=f"Template: {WATI_TEMPLATE_NAME}, Parameters: {parameters}",
                            msg_status="sent",
                            to_phone=mobile_number,
                            from_phone=counsellor_number
                        )

                            if log_saved:
                                logger.info(f"   💾 Message log saved successfully")
                            else:
                                logger.warning(f"   ⚠️ Failed to save message log")

                            return True, f"Message Delivered - {api_response}", True  # Continue processing

                        else:
                            # FALSE SUCCESS - HTTP 200 but message not delivered
                            logger.error(f"❌ WATI MESSAGE NOT DELIVERED for Lead {lead_id}")
                            logger.error(f"   🔴 WATI Result: {wati_result}")
                            logger.error(f"   📋 WATI Info: {wati_info}")
                            logger.error(f"   📊 Full Response: {api_response}")
                            logger.error(f"   📱 Target: {mobile_number}")
                            logger.error(f"   🎯 Template: {WATI_TEMPLATE_NAME}")

                            # Save failed delivery log
                            self.save_message_log(
                                lead=lead,
                                message_content=f"Template: {WATI_TEMPLATE_NAME}, Parameters: {parameters}",
                                msg_status="failed",
                                to_phone=mobile_number,
                                from_phone=counsellor_number
                            )

                            # Specific error handling with stop/continue decision
                            if "not enough credits" in wati_info.lower():
                                logger.error(f"   💳 CRITICAL ERROR: WATI account out of credits!")
                                logger.error(f"   🛑 STOPPING AUTOMATION - All future messages will fail!")
                                return False, f"No Credits: {wati_info}", False  # STOP processing
                            elif "template" in wati_info.lower() and ("not approved" in wati_info.lower() or "rejected" in wati_info.lower()):
                                logger.error(f"   🚫 CRITICAL ERROR: Template not approved!")
                                logger.error(f"   🛑 STOPPING AUTOMATION - All future messages will fail!")
                                return False, f"Template Issue: {wati_info}", False  # STOP processing
                            elif "account" in wati_info.lower() and ("suspended" in wati_info.lower() or "disabled" in wati_info.lower()):
                                logger.error(f"   🔐 CRITICAL ERROR: Account issue!")
                                logger.error(f"   🛑 STOPPING AUTOMATION - All future messages will fail!")
                                return False, f"Account Issue: {wati_info}", False  # STOP processing
                            elif "validWhatsAppNumber" in api_response and not api_response.get('validWhatsAppNumber'):
                                logger.error(f"   📱 ERROR: Invalid WhatsApp number format for this lead!")
                                return False, f"Invalid Number: {wati_info}", True  # Continue with other leads
                            else:
                                logger.warning(f"   ⚠️ Unknown WATI failure - continuing with other leads")
                                return False, f"WATI Delivery Failed: {wati_info}", True  # Continue processing

                    else:
                        error_msg = result.get('error', 'Unknown error')
                        status_code = result.get('status_code', 'Unknown')

                        logger.error(f"❌ WATI API FAILED for Lead {lead_id}")
                        logger.error(f"   🔴 Status Code: {status_code}")
                        logger.error(f"   📋 Error: {error_msg}")
                        logger.error(f"   📱 Target: {mobile_number}")
                        logger.error(f"   🎯 Template: {WATI_TEMPLATE_NAME}")

                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt
                            logger.warning(f"   🔄 Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            # Save failed message log
                            self.save_message_log(
                                lead=lead,
                                message_content=f"Template: {WATI_TEMPLATE_NAME}, Parameters: {parameters}",
                                msg_status="failed",
                                to_phone=mobile_number,
                                from_phone=counsellor_number
                            )
                            return False, f"API Error {status_code}: {error_msg}", True  # Continue with other leads

                except Exception as e:
                    logger.error(f"❌ EXCEPTION on attempt {attempt + 1} for Lead {lead_id}")
                    logger.error(f"   🔴 Exception: {str(e)}")
                    logger.error(f"   📱 Target: {mobile_number}")

                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"   🔄 Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        # Save failed message log
                        self.save_message_log(
                            lead=lead,
                            message_content=f"Template: {WATI_TEMPLATE_NAME}, Parameters: {parameters}",
                            msg_status="failed",
                            to_phone=mobile_number,
                            from_phone=counsellor_number
                        )
                        return False, f"Exception: {str(e)}", True  # Continue with other leads

            return False, "Max retries exceeded", True  # Continue with other leads

        except Exception as e:
            logger.error(f"❌ CRITICAL EXCEPTION in send_whatsapp_message for Lead {lead.get('lead_id', 'unknown')}")
            logger.error(f"   🔴 Exception: {str(e)}")
            return False, f"Critical Error: {str(e)}", True  # Continue with other leads

    def get_available_counsellor(self) -> Optional[Tuple[str, Dict]]:
        """Get a randomly selected available counsellor based on quota limits"""
        available_counsellors = []

        # Find all available counsellors
        for counsellor_name, counsellor_config in COUNSELLORS.items():
            current_quota = self.daily_quota.get(counsellor_name, 0)
            daily_limit = counsellor_config['daily_limit']

            if current_quota < daily_limit:
                available_counsellors.append((counsellor_name, counsellor_config))

        if not available_counsellors:
            logger.warning("All counsellors have reached their daily quota limits")
            return None

        # Randomly select from available counsellors
        selected = random.choice(available_counsellors)
        logger.debug(f"Selected counsellor: {selected[0]} from {len(available_counsellors)} available")
        return selected

    def process_counsellor_leads(self, counsellor_name: str, counsellor_config: Dict) -> Dict:
        """Process leads for a specific counsellor"""
        logger.info(f"Processing leads for counsellor: {counsellor_name}")

        # Check quota
        current_quota = self.daily_quota.get(counsellor_name, 0)
        daily_limit = counsellor_config['daily_limit']

        if current_quota >= daily_limit:
            logger.info(f"Daily quota exhausted for {counsellor_name} ({current_quota}/{daily_limit})")
            return {
                'counsellor': counsellor_name,
                'status': 'quota_exhausted',
                'sent': 0,
                'failed': 0,
                'quota_used': current_quota,
                'quota_limit': daily_limit
            }

        remaining_quota = daily_limit - current_quota
        logger.info(f"📊 Quota status: {current_quota}/{daily_limit} used, {remaining_quota} remaining")

        # Fetch leads using static owner_id
        leads = self.fetch_leads(STATIC_OWNER_ID, remaining_quota)

        if not leads:
            logger.info(f"❌ No leads found for {counsellor_name}")
            return {
                'counsellor': counsellor_name,
                'status': 'no_leads',
                'sent': 0,
                'failed': 0,
                'quota_used': current_quota,
                'quota_limit': daily_limit
            }

        # Process leads
        sent_count = 0
        failed_count = 0
        counsellor_number = counsellor_config['number']

        for lead in leads:
            if current_quota + sent_count >= daily_limit:
                logger.info(f"🛑 Quota limit reached for {counsellor_name}")
                break

            success, message, should_continue = self.send_whatsapp_message(lead, counsellor_name, counsellor_number)

            if success:
                sent_count += 1
                # Update quota
                self.daily_quota[counsellor_name] = current_quota + sent_count
                self._save_daily_quota()
            else:
                failed_count += 1
                logger.error(f"❌ Failed to send to lead {lead.get('lead_id')}: {message}")

                # Check if we should stop processing due to systematic failure
                if not should_continue:
                    logger.error(f"🛑 STOPPING processing for {counsellor_name} due to systematic failure!")
                    break  # Exit the lead processing loop for this counsellor

            # Small delay between messages
            time.sleep(1)

        result = {
            'counsellor': counsellor_name,
            'status': 'completed',
            'sent': sent_count,
            'failed': failed_count,
            'quota_used': current_quota + sent_count,
            'quota_limit': daily_limit,
            'leads_processed': len(leads)
        }

        logger.info(f"Completed {counsellor_name}: {sent_count} sent, {failed_count} failed")
        return result

    def run_automation(self) -> Dict:
        """Main automation execution with random counsellor selection"""
        logger.info("Starting Lead Automation with WATI Integration (Random Counsellor Selection)")
        logger.info(f"Working hours: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")

        # Check working hours
        if not self.is_within_working_hours():
            current_time = datetime.now().strftime('%H:%M')
            logger.warning(f"Current time ({current_time}) is outside working hours ({SCRIPT_START_TIME} - {SCRIPT_END_TIME})")
            return {
                'status': 'outside_working_hours',
                'message': f'Script only runs between {SCRIPT_START_TIME} and {SCRIPT_END_TIME}',
                'current_time': current_time
            }

        # Calculate total remaining quota across all counsellors
        total_remaining_quota = 0
        counsellor_stats = {}

        for counsellor_name, counsellor_config in COUNSELLORS.items():
            current_quota = self.daily_quota.get(counsellor_name, 0)
            daily_limit = counsellor_config['daily_limit']
            remaining = max(0, daily_limit - current_quota)
            total_remaining_quota += remaining

            counsellor_stats[counsellor_name] = {
                'counsellor': counsellor_name,
                'sent': 0,
                'failed': 0,
                'quota_used': current_quota,
                'quota_limit': daily_limit,
                'remaining': remaining
            }

            logger.info(f"📊 {counsellor_name}: {current_quota}/{daily_limit} used, {remaining} remaining")

        if total_remaining_quota == 0:
            logger.warning("All counsellors have reached their daily quota limits")
            return {
                'status': 'all_quotas_exhausted',
                'message': 'All counsellors have reached their daily quota limits',
                'counsellor_results': list(counsellor_stats.values())
            }

        logger.info(f"📊 Total remaining quota across all counsellors: {total_remaining_quota}")

        # Fetch leads (limit to total remaining quota to avoid waste)
        leads = self.fetch_leads(STATIC_OWNER_ID, min(total_remaining_quota, 700))

        if not leads:
            logger.info("❌ No leads found to process")
            return {
                'status': 'no_leads',
                'message': 'No leads found to process',
                'counsellor_results': list(counsellor_stats.values())
            }

        logger.info(f"📨 Processing {len(leads)} leads with random counsellor assignment")

        total_sent = 0
        total_failed = 0

        # Process each lead with random counsellor selection
        for i, lead in enumerate(leads, 1):
            try:
                lead_id = str(lead.get('lead_id', ''))
                lead_name = lead.get('full_name', 'Customer')

                # Check if message already sent today
                if lead_id in self.sent_messages_today:
                    logger.info(f"Lead {lead_id}: Message already sent today, skipping")
                    continue

                # Get available counsellor randomly
                counsellor_selection = self.get_available_counsellor()
                if not counsellor_selection:
                    logger.warning(f"No available counsellors for lead {lead_id}, stopping processing")
                    break

                counsellor_name, counsellor_config = counsellor_selection
                counsellor_number = counsellor_config['number']

                logger.info(f"📞 [{i}/{len(leads)}] Processing lead {lead_id} ({lead_name}) → Assigned to {counsellor_name}")

                # Send WhatsApp message
                success, message, should_continue = self.send_whatsapp_message(lead, counsellor_name, counsellor_number)
                
                if success:
                    total_sent += 1
                    counsellor_stats[counsellor_name]['sent'] += 1
                    
                    # Update quota
                    self.daily_quota[counsellor_name] = self.daily_quota.get(counsellor_name, 0) + 1
                    counsellor_stats[counsellor_name]['quota_used'] += 1
                    counsellor_stats[counsellor_name]['remaining'] -= 1
                    
                    # Save quota and sent message tracking
                    self._save_daily_quota()
                    self._save_sent_message(lead_id)
                    
                    logger.info(f"✅ Message sent to {lead_name} via {counsellor_name} (Quota: {counsellor_stats[counsellor_name]['quota_used']}/{counsellor_stats[counsellor_name]['quota_limit']})")
                    
                else:
                    total_failed += 1
                    counsellor_stats[counsellor_name]['failed'] += 1
                    logger.error(f"❌ Failed to send to lead {lead_id}: {message}")
                    
                    # Check if we should stop processing due to systematic failure
                    if not should_continue:
                        logger.error("🛑 STOPPING AUTOMATION due to systematic failure!")
                        logger.error("🔍 Fix the issue and restart the script")
                        break  # Exit the lead processing loop
                
                # Small delay between messages
                time.sleep(1)
                
            except Exception as e:
                total_failed += 1
                logger.error(f"❌ Error processing lead {lead.get('lead_id', 'unknown')}: {e}")
        
        # Convert counsellor_stats to the expected format
        results = []
        for counsellor_name, stats in counsellor_stats.items():
                results.append({
                    'counsellor': counsellor_name,
                'status': 'completed',
                'sent': stats['sent'],
                'failed': stats['failed'],
                'quota_used': stats['quota_used'],
                'quota_limit': stats['quota_limit']
                })
        
        # Summary
        summary = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'total_sent': total_sent,
            'total_failed': total_failed,
            'leads_processed': len(leads),
            'counsellor_results': results,
            'selection_method': 'random'
        }
        
        # Enhanced completion logging
        logger.info("=" * 80)
        logger.info("🎯 LEAD AUTOMATION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"📊 OVERALL STATISTICS:")
        logger.info(f"   📨 Total Messages Sent: {total_sent}")
        logger.info(f"   ❌ Total Failed: {total_failed}")
        logger.info(f"   📋 Total Leads Processed: {len(leads)}")
        logger.info(f"   ⚡ Success Rate: {(total_sent / len(leads) * 100):.1f}%" if len(leads) > 0 else "   ⚡ Success Rate: 0%")
        logger.info(f"   🎲 Selection Method: RANDOM")
        
        logger.info(f"\n👥 COUNSELLOR PERFORMANCE:")
        logger.info("-" * 60)
        for counsellor_name, stats in counsellor_stats.items():
            success_rate = (stats['sent'] / (stats['sent'] + stats['failed']) * 100) if (stats['sent'] + stats['failed']) > 0 else 0
            status_emoji = "✅" if stats['sent'] > 0 else "⭕"
            logger.info(f"{status_emoji} {counsellor_name}:")
            logger.info(f"   📤 Sent: {stats['sent']}")
            logger.info(f"   ❌ Failed: {stats['failed']}")
            logger.info(f"   📊 Success Rate: {success_rate:.1f}%")
            logger.info(f"   🎯 Quota: {stats['quota_used']}/{stats['quota_limit']} ({stats['remaining']} remaining)")
            logger.info("")
        
        # Check if any messages went through
        if total_sent > 0:
            logger.info("🎉 SUCCESS: Messages were sent successfully!")
            logger.info("📱 Check WATI dashboard for delivery reports")
            logger.info("🔍 Monitor delivery status in WhatsApp Business Manager")
        else:
            if total_failed > 0:
                logger.info("⚠️  WARNING: No messages were sent successfully")
                logger.info("🔧 Most likely cause: WATI credits exhausted or template issues")
                logger.info("💳 Check WATI account credits and template approval status")
            else:
                logger.info("⚠️  WARNING: No messages were sent successfully")
                logger.info("🔧 Check WATI template approval status")
                logger.info("📞 Verify phone number formats")
                logger.info("🔑 Confirm API credentials are valid")
        
        logger.info("=" * 80)
        
        return summary

def safe_print(text):
    """Safe print function that handles encoding issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emoji and special characters for Windows console
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def load_config_info():
    """Display configuration information"""
    safe_print("=" * 50)
    safe_print("LEAD AUTOMATION CONFIGURATION")
    safe_print("=" * 50)
    safe_print(f"Lead API URL: {LEAD_API_URL}")
    safe_print(f"API Token: {'*' * 8 + API_TOKEN[-4:] if len(API_TOKEN) > 8 else 'Not set'}")
    safe_print(f"WATI Template: {WATI_TEMPLATE_NAME}")
    safe_print(f"WATI Log API URL: {WATI_LOG_API_URL}")
    safe_print(f"Working Hours: {SCRIPT_START_TIME} - {SCRIPT_END_TIME}")
    safe_print(f"WATI API Key: {'*' * 8 + os.getenv('WATI_API_KEY', 'Not set')[-4:] if os.getenv('WATI_API_KEY') else 'Not set'}")
    safe_print(f"WATI Base URL: {os.getenv('WATI_BASE_URL', 'Not set')}")
    safe_print(f"Static Owner ID: {STATIC_OWNER_ID}")
    safe_print(f"Deployment Mode: {'TEST' if USE_TEST_NUMBER else 'PRODUCTION'}")
    safe_print(f"Test Mobile Number: {TEST_MOBILE_NUMBER}")
    safe_print(f"Selection Method: RANDOM (counsellors are randomly assigned to each lead)")
    safe_print("\nCOUNSELLOR CONFIGURATION:")
    for name, config in COUNSELLORS.items():
        safe_print(f"  {name}: Limit={config['daily_limit']}, Phone={config['number']}")
    safe_print("=" * 50)

if __name__ == "__main__":
    try:
        # Display configuration
        load_config_info()
        
        # Startup banner
        safe_print("\n" + "🚀" * 30)
        safe_print("🤖 STARTING LEAD AUTOMATION WITH WATI INTEGRATION")
        safe_print("🚀" * 30)
        safe_print("📋 This script will:")
        safe_print("   1️⃣  Fetch leads from the API")
        safe_print("   2️⃣  Randomly assign counsellors to leads") 
        safe_print("   3️⃣  Send WhatsApp messages via WATI")
        safe_print("   4️⃣  Log all activities for tracking")
        safe_print("   5️⃣  Provide detailed success/failure reports")
        safe_print("")
        safe_print("⏰ Working Hours: 09:00 - 21:00")
        safe_print("🎲 Selection: Random counsellor assignment")
        safe_print("📊 Live Logging: All API responses will be shown")
        safe_print("")
        safe_print("🚨 IMPORTANT REMINDERS:")
        safe_print("   💳 Ensure WATI account has sufficient credits")
        safe_print("   📱 Verify phone numbers have +91 country code")
        safe_print("   ✅ Check template approval status in WATI dashboard")
        safe_print("🚀" * 30)
        
        # Initialize automation manager
        automation = LeadAutomationManager()
        
        # Run automation
        result = automation.run_automation()
        
        # Enhanced final summary
        safe_print("\n" + "=" * 80)
        safe_print("📋 EXECUTION SUMMARY & ANALYSIS")
        safe_print("=" * 80)
        
        status = result['status']
        total_sent = result.get('total_sent', 0)
        total_failed = result.get('total_failed', 0)
        total_processed = result.get('leads_processed', 0)
        
        # Overall status
        if status == 'completed':
            if total_sent > 0:
                safe_print(f"✅ STATUS: SUCCESS - {total_sent} messages sent")
            else:
                safe_print(f"⚠️  STATUS: COMPLETED BUT NO MESSAGES SENT")
        elif status == 'outside_working_hours':
            safe_print(f"🕐 STATUS: OUTSIDE WORKING HOURS")
        elif status == 'all_quotas_exhausted':
            safe_print(f"🚫 STATUS: ALL QUOTAS EXHAUSTED")
        elif status == 'no_leads':
            safe_print(f"📭 STATUS: NO LEADS FOUND")
        else:
            safe_print(f"❓ STATUS: {status.upper()}")
        
        safe_print(f"\n📊 DELIVERY STATISTICS:")
        safe_print(f"   📨 Messages Sent: {total_sent}")
        safe_print(f"   ❌ Messages Failed: {total_failed}")
        safe_print(f"   📋 Leads Processed: {total_processed}")
        
        if total_processed > 0:
            success_rate = (total_sent / total_processed) * 100
            safe_print(f"   ⚡ Success Rate: {success_rate:.1f}%")
        
        if 'counsellor_results' in result and result['counsellor_results']:
            safe_print(f"\n👥 COUNSELLOR BREAKDOWN:")
            safe_print("-" * 50)
            for counsellor_result in result['counsellor_results']:
                name = counsellor_result['counsellor']
                sent = counsellor_result['sent']
                failed = counsellor_result['failed']
                quota_used = counsellor_result.get('quota_used', 0)
                quota_limit = counsellor_result.get('quota_limit', 0)
                
                # Calculate individual success rate
                individual_total = sent + failed
                individual_rate = (sent / individual_total * 100) if individual_total > 0 else 0
                status_emoji = "✅" if sent > 0 else "⭕" if failed > 0 else "➖"
                
                safe_print(f"{status_emoji} {name}:")
                safe_print(f"   📤 Sent: {sent}")
                safe_print(f"   ❌ Failed: {failed}")
                safe_print(f"   📊 Rate: {individual_rate:.1f}%")
                safe_print(f"   🎯 Quota: {quota_used}/{quota_limit}")
        
        # Action items based on results
        safe_print(f"\n🎯 NEXT STEPS:")
        if total_sent > 0:
            safe_print("   ✅ Check WATI dashboard for delivery confirmations")
            safe_print("   📱 Monitor WhatsApp Business Manager for delivery status")
            safe_print("   🔍 Check admin panel logs at: https://evolgroups.com/admin_techno/App_Leads/watimsglog/")
        else:
            # Check if automation was stopped early vs completed with no success
            if total_processed < len(result.get('leads_processed', 0)) if 'leads_processed' in result else False:
                safe_print("   🛑 AUTOMATION STOPPED EARLY due to systematic failure!")
                safe_print("   🔧 The issue affects all messages - fix it before continuing")
                safe_print("")
            
            safe_print("   🚨 URGENT: No messages were actually delivered!")
            safe_print("")
            safe_print("   🔴 Most Likely Issues:")
            safe_print("   💳 1. WATI Credits Exhausted - Recharge your account")
            safe_print("   📱 2. Invalid Phone Numbers - Check +91 formatting")
            safe_print("   🚫 3. Template Not Approved - Verify in WATI dashboard")
            safe_print("   🔐 4. Account Suspended - Check WATI account status")
            safe_print("")
            safe_print("   🔧 Troubleshooting Steps:")
            safe_print("   1️⃣  Login to WATI dashboard → Check credits balance")
            safe_print("   2️⃣  Verify template approval status")
            safe_print("   3️⃣  Check phone number formats (+91xxxxxxxxxx)")
            safe_print("   4️⃣  Review API credentials and permissions")
            safe_print("   5️⃣  Ensure account is active and not suspended")
        
        safe_print("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        safe_print(f"Error: {e}")