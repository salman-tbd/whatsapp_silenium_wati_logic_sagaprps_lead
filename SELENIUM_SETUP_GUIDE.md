# Selenium WhatsApp Web Automation - Setup Guide

## 🎯 Overview

This is the **Selenium-powered version** of the WhatsApp Lead Automation System. Instead of using WATI API, it directly controls WhatsApp Web through browser automation to send messages.

## 🔄 Key Differences from WATI Version

| Feature | WATI Version | Selenium Version |
|---------|--------------|------------------|
| **Message Method** | WATI API calls | Browser automation (WhatsApp Web) |
| **Templates** | Pre-approved templates required | Dynamic message creation |
| **Setup Complexity** | API credentials only | Browser + Chrome setup |
| **Scalability** | High (API-based) | Medium (browser-based) |
| **Cost** | WATI subscription required | Free (but slower) |
| **Reliability** | High (API) | Medium (browser dependent) |
| **Rate Limits** | WATI/WhatsApp limits | Manual delays between messages |

---

## 🛠️ Prerequisites & Installation

### 1. System Requirements
```
- Python 3.7+
- Google Chrome browser
- ChromeDriver executable
- Internet connection
- WhatsApp account with phone verification
```

### 2. Python Dependencies
```bash
pip install selenium python-dotenv requests pyperclip
```

### 3. ChromeDriver Setup (Two Options)

#### Option A: Automatic Setup (Recommended)
```bash
# Modern Selenium will auto-detect ChromeDriver
# Just ensure Chrome browser is installed
# Leave CHROME_DRIVER_PATH empty in config.env
```

#### Option B: Manual Setup
1. **Download ChromeDriver**: https://chromedriver.chromium.org/
2. **Match Chrome version**: Check your Chrome version in `chrome://version/`
3. **Place executable**: Put `chromedriver.exe` in your project folder
4. **Set path** in config.env: `CHROME_DRIVER_PATH=D:\Projects\chromedriver.exe`

---

## ⚙️ Configuration Setup

### 1. Environment Variables (`config.env`)
```env
# Lead API Configuration (same as WATI version)
LEAD_API_URL=https://evolgroups.com/lead/get-leads-basic-info/
LEAD_API_TOKEN=Token your_api_token_here
LEAD_OWNER_ID=227
LEAD_LOG_API_URL=https://evolgroups.com/lead/post-selenium-msg-logs/

# Testing Configuration
USE_TEST_NUMBER=false
TEST_MOBILE_NUMBER=+917567905829

# Selenium Configuration
CHROME_DRIVER_PATH=                    # Leave empty for auto-detection (recommended)
# CHROME_DRIVER_PATH=D:\Projects\chromedriver.exe  # OR set specific path
CHROME_PROFILE_PATH=C:\Users\admin\AppData\Local\Google\Chrome\User Data\WhatsAppBot
WHATSAPP_SCAN_TIMEOUT=60
MESSAGE_SEND_DELAY=2.0
```

### 2. Chrome Profile Setup
```bash
# Create dedicated Chrome profile directory
mkdir "C:\Users\admin\AppData\Local\Google\Chrome\User Data\WhatsAppBot"
```

---

## 🚀 First-Time Setup Process

### Step 1: Initial WhatsApp Web Login
```bash
# Run the script for first time
python lead_automation_selenium_whatsapp.py
```

1. **Chrome Opens**: Script opens Chrome with WhatsApp Web
2. **QR Code Appears**: Scan QR code with your phone's WhatsApp
3. **Login Saves**: Profile saves login for future runs
4. **Ready to Send**: Script proceeds with lead processing

### Step 2: Verify Configuration
- ✅ ChromeDriver path is correct
- ✅ Chrome profile directory exists
- ✅ WhatsApp QR code successfully scanned
- ✅ Lead API credentials working
- ✅ Test number configured (if testing)

---

## 📱 WhatsApp Web Session Management

### Login Process
```
1. Script opens Chrome with dedicated profile
2. Navigates to https://web.whatsapp.com/
3. Checks for existing login or QR code
4. Waits for QR scan (60 seconds timeout)
5. Verifies chat interface access
6. Ready for messaging
```

### Session Persistence
- **Profile Saves Login**: Chrome profile maintains WhatsApp login
- **Auto-Reconnect**: Subsequent runs automatically log in
- **Session Timeout**: May need re-scan if session expires
- **Multiple Devices**: WhatsApp allows 4 linked devices

---

## 📤 Message Sending Process

### How Messages Are Created
```python
# Template parameters converted to personalized message
lead_name = "John Doe"
counsellor_name = "Anandi"  
counsellor_phone = "+919512270915"

# Creates message like:
"""
Hello John Doe,

I hope this message finds you well! 

I'm Anandi from EvolGroups, and I'm reaching out regarding 
your Australia PR settlement inquiry...

Please contact me at +919512270915 for assistance.

Best regards,
Anandi
EvolGroups Team
"""
```

### Sending Workflow
```
1. Navigate to: https://web.whatsapp.com/send?phone={number}
2. Wait for chat interface to load
3. Find message input box (multiple selectors)
4. Copy message to clipboard
5. Paste message using Ctrl+V
6. Send with Enter key
7. Verify message sent (check for timestamps)
8. Add delay before next message
```

---

## 🔧 Configuration Options

### Timing Settings
```python
SCRIPT_START_TIME = '09:00'        # Campaign start time
SCRIPT_END_TIME = '21:00'          # Campaign end time
MESSAGE_SEND_DELAY = 2.0           # Delay between messages (seconds)
WHATSAPP_SCAN_TIMEOUT = 60         # QR scan timeout (seconds)
```

### Counsellor Limits
```python
COUNSELLORS = {
    'Anandi': {'daily_limit': 50, 'number': '+919512270915'},
    'Preeti': {'daily_limit': 50, 'number': '+918799334198'},
    # ... reduced limits for browser-based sending
}
```

### Browser Options
```python
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage") 
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
```

---

## 🚨 Error Handling & Troubleshooting

### Common Issues

#### 1. Selenium 4.x Compatibility Error
```
Error: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
Solution: Update to fixed version (already fixed in latest script)
```

#### 2. ChromeDriver Not Found
```
Error: 'chromedriver' executable needs to be in PATH
Solutions:
- Leave CHROME_DRIVER_PATH empty for auto-detection (recommended)
- Install ChromeDriver via pip: pip install chromedriver-autoinstaller
- Download manually from https://chromedriver.chromium.org/
```

#### 3. ChromeDriver Version Mismatch
```
Error: SessionNotCreatedException: chrome not reachable
Solution: Download matching ChromeDriver version or use auto-detection
```

#### 4. Chrome Profile Permission Issues
```
Error: cannot create default profile directory
Solutions:
- ✅ FIXED: Script now auto-detects and uses fallback profiles
- The system will automatically try:
  1. Configured profile path
  2. Temporary directory fallback
  3. Chrome default profile
- No manual action required!
```

#### 5. WhatsApp Web Not Loading
```
Error: WhatsApp Web initialization failed
Solutions:
- Check internet connection
- Clear browser cache
- Verify Chrome profile permissions
- Try different user profile path
```

#### 6. QR Code Scan Timeout
```
Error: QR Code scan timeout
Solutions:
- Increase WHATSAPP_SCAN_TIMEOUT
- Ensure phone has WhatsApp installed
- Check phone's camera permissions
- Try refreshing WhatsApp Web
```

#### 7. Message Input Not Found
```
Error: Could not find message input box
Solutions:
- WhatsApp Web interface changed
- Contact number invalid
- Chat restrictions applied
- Browser window minimized/hidden
```

#### 8. Message Send Failures
```
Error: Send error: timeout
Solutions:
- Increase MESSAGE_SEND_DELAY
- Check network stability
- Verify phone number format
- Ensure WhatsApp session active
```

### Debug Mode
```python
# Enable detailed Selenium logging
logging.getLogger('selenium').setLevel(logging.DEBUG)
```

---

## 📊 Performance Characteristics

### Throughput Comparison
| Metric | WATI API | Selenium Web |
|--------|----------|--------------|
| **Messages/Hour** | 500+ | 100-200 |
| **Reliability** | 95%+ | 85-90% |
| **Setup Time** | 5 minutes | 30 minutes |
| **Monitoring** | API dashboard | Browser observation |

### Resource Usage
- **Memory**: ~200-500MB (Chrome browser)
- **CPU**: ~5-15% (automation scripts)
- **Network**: ~1-5MB per session
- **Disk**: ~100MB (Chrome profile)

---

## 🔐 Security Considerations

### WhatsApp Account Safety
- ✅ Use dedicated business WhatsApp number
- ✅ Don't exceed reasonable daily limits (50-100 messages)
- ✅ Maintain human-like delays between messages
- ✅ Monitor for WhatsApp warnings/restrictions
- ❌ Never use personal WhatsApp account
- ❌ Don't send spam or inappropriate content

### Browser Security
- ✅ Use isolated Chrome profile
- ✅ Keep ChromeDriver updated
- ✅ Restrict profile access permissions
- ✅ Regular profile cleanup
- ❌ Don't share profile directory
- ❌ Don't run on shared computers

---

## 🎯 Best Practices

### Operational Guidelines
1. **Start Small**: Test with 10-20 messages initially
2. **Monitor Actively**: Watch browser during first runs
3. **Maintain Delays**: Don't rush message sending
4. **Check Responses**: Monitor WhatsApp for customer replies
5. **Backup Profiles**: Save working Chrome profiles

### Message Quality
1. **Personalization**: Use lead names and relevant counsellor info
2. **Professional Tone**: Maintain business communication standards
3. **Clear CTAs**: Include specific contact information
4. **Compliance**: Follow WhatsApp Business Policy
5. **Opt-out Options**: Respect unsubscribe requests

### Scaling Tips
1. **Batch Processing**: Process leads in smaller batches (50-100)
2. **Time Distribution**: Spread messages throughout the day
3. **Multiple Profiles**: Use different Chrome profiles for different campaigns
4. **Error Recovery**: Implement retry logic for failed messages
5. **Monitoring Setup**: Log all activities for troubleshooting

---

## 🚀 Quick Start Checklist

- [ ] Install Python dependencies (`pip install selenium python-dotenv requests pyperclip`)
- [ ] Download and configure ChromeDriver
- [ ] Set up dedicated Chrome profile directory
- [ ] Update `config.env` with correct paths and credentials
- [ ] Test with `USE_TEST_NUMBER=true` first
- [ ] Scan WhatsApp Web QR code on first run
- [ ] Verify message sending with test lead
- [ ] Monitor logs for any errors
- [ ] Switch to production mode (`USE_TEST_NUMBER=false`)
- [ ] Set appropriate daily limits for counsellors

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Weekly**: Check Chrome/ChromeDriver updates
- **Monthly**: Clean up old Chrome profile data
- **Quarterly**: Review and update message templates
- **As Needed**: Re-scan QR code if session expires

### Monitoring Points
- ✅ Message delivery success rates
- ✅ Browser memory usage
- ✅ WhatsApp session status
- ✅ Error log patterns
- ✅ Daily quota consumption

---

*This guide covers the complete setup and operation of the Selenium WhatsApp Web automation system. For technical support, refer to the detailed logs and error messages.*
