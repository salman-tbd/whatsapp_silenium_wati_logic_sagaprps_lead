# 📝 Static Template System Guide

## 🎯 Overview
The WhatsApp automation now uses a **simple static template system** for easy management and reliable operation.

---

## 📋 Template Management

### Message Template
- **File**: `template.txt`
- **Location**: Project root directory
- **Format**: Plain text with `{{1}}`, `{{2}}`, `{{3}}` placeholders

### Current Template Content:
```
🇦🇺 From dream to destination — Australia awaits!

Hi {{1}},
I'm {{2}} from Migrate Zone.

We're now processing top Australian visas like the 482 Work Permit and the 186 PR.

✅ 2,200+ happy clients & families settled. You could be the next! 🇦🇺

📞 Call or WhatsApp: {{3}}

🏢 Visit our office for a FREE consultation and check eligibility

📸 Client Wins: https://www.instagram.com/reel/DMrhR9aINFs/
🔔 Get visa updates first – follow us on Instagram!: https://www.instagram.com/migrate_zone/

✈️ Call to start your Australia journey today!
```

### Parameter Substitution:
- `{{1}}` → Lead Name (e.g., "Ketan Patel")
- `{{2}}` → Counsellor Name (e.g., "Karan") 
- `{{3}}` → Counsellor Phone (e.g., "+919773432629")

---

## 📱 Media Management

### Media Directory
- **Location**: `media/` folder
- **Supported Formats**: JPG, PNG, GIF, MP4, AVI, MOV, PDF, DOC, DOCX
- **Usage**: Place any image/video/document in the `media/` folder

### How It Works:
1. **Smart Priority System** - Messages sent in this order:
   - 📝 **Text-only** (if `SEND_MEDIA=false`)
   - 📸 **Images first** (.jpg, .jpeg, .png, .gif) 
   - 🎥 **Videos second** (.mp4, .avi, .mov)
   - 📄 **Documents last** (.pdf, .doc, .docx)
2. **Media + Caption** - Sends media with template text as caption via WhatsApp Web
3. **Text Fallback** - If no media found or sending fails, sends text-only message

### Current Media Files:
Your `media/` folder contains:
- `image (11).png` (1.4 MB) ✅
- `🎉 From Mehsana to Australia...mp4` (1.8 MB) ✅

### Enhanced Upload Features:
- ✅ **Absolute Path Handling** - Handles full Windows paths correctly
- ✅ **Special Character Support** - Handles spaces, emojis, parentheses in filenames
- ✅ **File Verification** - Checks file exists and logs size before upload
- ✅ **Temp File Fallback** - Creates simplified filename if special chars cause issues
- ✅ **Upload Verification** - Confirms file actually uploaded to WhatsApp
- ✅ **Send Confirmation** - Verifies message was sent successfully

**Next run will send the image with your Australia PR template as caption using enhanced upload!**

---

## ✏️ Easy Editing

### To Update Message Template:
1. **Open**: `template.txt` in any text editor
2. **Edit**: Modify text while keeping `{{1}}`, `{{2}}`, `{{3}}` placeholders
3. **Save**: File will be used immediately on next automation run

### To Add/Change Media:
1. **Add Files**: Copy images/videos to `media/` folder
2. **Remove Old**: Delete unwanted media files
3. **Smart Priority**: Images → Videos → Documents (see priority control below)

### To Control Message Priority:

#### **📝 Text-Only Messages:**
- Add `SEND_MEDIA=false` to your `.env` file
- **Result**: Sends only template text, no media

#### **📸 Image Messages:**  
- Add `SEND_MEDIA=true` to your `.env` file (default)
- Keep only images in `media/` folder
- **Result**: Sends images with template text as caption

#### **🎥 Video Messages:**
- Add `SEND_MEDIA=true` to your `.env` file (default)  
- Remove images, keep only videos in `media/` folder
- **Result**: Sends videos with template text as caption

---

## 🚀 Benefits

✅ **Simple Management** - Edit template.txt anytime  
✅ **No API Dependencies** - Works offline, no WATI API needed  
✅ **Easy Media** - Just drop files in media folder  
✅ **Reliable Operation** - No network calls for templates  
✅ **Version Control** - Template changes can be tracked  
✅ **Quick Updates** - Edit and run immediately  

---

## 📂 Project Structure

```
D:\Projects\WhatsAppNewProject\
├── lead_automation_selenium_whatsapp.py ✅ Main script
├── template.txt ✅ Message template  
├── media/ ✅ Media files directory
│   ├── image1.jpg (optional)
│   └── video1.mp4 (optional)
├── .env ✅ Configuration
└── other files...
```

---

## 🔧 Example Usage

### Text + Image Message:
1. **Template**: `template.txt` with your message
2. **Media**: `media/australia-pr.jpg` 
3. **Result**: Image sent with message as caption

### Text-Only Message:
1. **Template**: `template.txt` with your message
2. **Media**: Empty `media/` folder
3. **Result**: Text message only

---

## 💡 Quick Tips

- **Keep Placeholders**: Always maintain `{{1}}`, `{{2}}`, `{{3}}` in template
- **Unicode Support**: Emojis and special characters work perfectly
- **Media Size**: Keep images under 16MB for WhatsApp compatibility
- **Backup Template**: Keep a copy of `template.txt` for safety

**Your template system is now simple, reliable, and easy to manage!** 📝✨
