@echo off
echo ============================================================
echo 🖥️  WHATSAPP AUTOMATION - NEW PC SETUP
echo ============================================================
echo.

echo 📋 This script will help you set up WhatsApp automation on a new PC
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Note: Some features may require administrator privileges
    echo    Right-click and "Run as administrator" if you encounter issues
    echo.
)

echo 🔍 STEP 1: Checking system requirements...
echo.

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo ✅ Windows Version: %VERSION%

REM Check if Chrome is installed
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Google Chrome: INSTALLED
) else (
    echo ❌ Google Chrome: NOT FOUND
    echo    Please download and install Chrome from: https://www.google.com/chrome/
    echo    This is REQUIRED for the automation to work.
    pause
    exit /b 1
)

REM Check internet connection
ping google.com -n 1 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Internet Connection: ACTIVE
) else (
    echo ❌ Internet Connection: NO CONNECTION
    echo    Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo 📁 STEP 2: Setting up application folder...
echo.

REM Create application folder
set APP_DIR=C:\WhatsApp_Automation
if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%"
    echo ✅ Created folder: %APP_DIR%
) else (
    echo ✅ Folder already exists: %APP_DIR%
)

REM Check if main executable exists
if exist "%APP_DIR%\WhatsApp_Multi_Team_Automation.exe" (
    echo ✅ Main application: FOUND
) else (
    echo ❌ Main application: NOT FOUND
    echo.
    echo 📋 MANUAL SETUP REQUIRED:
    echo    1. Copy WhatsApp_Multi_Team_Automation.exe to: %APP_DIR%
    echo    2. Copy .env file to: %APP_DIR%
    echo    3. Copy template.txt to: %APP_DIR%
    echo    4. Copy media folder to: %APP_DIR%
    echo.
    echo 💡 TIP: You can drag and drop files to copy them
    pause
    exit /b 1
)

REM Check required files
echo.
echo 📋 STEP 3: Checking required files...
echo.

if exist "%APP_DIR%\.env" (
    echo ✅ Configuration file (.env): FOUND
) else (
    echo ❌ Configuration file (.env): NOT FOUND
    echo    This file contains your phone numbers and settings
)

if exist "%APP_DIR%\template.txt" (
    echo ✅ Message template: FOUND
) else (
    echo ❌ Message template: NOT FOUND
    echo    This file contains your WhatsApp message template
)

if exist "%APP_DIR%\media" (
    echo ✅ Media folder: FOUND
) else (
    echo ❌ Media folder: NOT FOUND
    echo    This folder should contain your images and videos
)

echo.
echo 🔧 STEP 4: Configuration check...
echo.

if exist "%APP_DIR%\.env" (
    echo 📝 Your .env file contains your phone numbers and API settings
    echo    You may need to edit this file with your specific details
    echo.
    echo 💡 To edit: Right-click .env → Open with → Notepad
) else (
    echo ⚠️  You need to create a .env file with your configuration
)

echo.
echo 🚀 STEP 5: Ready to run?
echo.

if exist "%APP_DIR%\WhatsApp_Multi_Team_Automation.exe" (
    if exist "%APP_DIR%\.env" (
        if exist "%APP_DIR%\template.txt" (
            echo ✅ ALL REQUIREMENTS MET!
            echo.
            echo 🎯 Next steps:
            echo    1. Edit .env file with your phone numbers and settings
            echo    2. Update template.txt with your message (if needed)
            echo    3. Run the application: %APP_DIR%\WhatsApp_Multi_Team_Automation.exe
            echo    4. Scan QR codes with correct manager phones
            echo.
            choice /C YN /M "Do you want to run the application now"
            if !errorlevel!==1 (
                echo.
                echo 🚀 Starting WhatsApp Automation...
                cd "%APP_DIR%"
                start "" "WhatsApp_Multi_Team_Automation.exe"
                echo.
                echo 📱 Remember to scan QR codes with the CORRECT manager phones!
                echo 🔐 Each team must use its designated WhatsApp number!
                pause
            ) else (
                echo.
                echo 📋 Setup complete! Run when ready: %APP_DIR%\WhatsApp_Multi_Team_Automation.exe
            )
        )
    )
) else (
    echo ❌ SETUP INCOMPLETE
    echo    Please copy all required files to: %APP_DIR%
)

echo.
echo 📚 HELP RESOURCES:
echo    📖 NEW_PC_SETUP_GUIDE.md - Complete setup instructions
echo    📋 QUICK_START_CHECKLIST.txt - Quick reference
echo    🛠️  TROUBLESHOOT_BUILD_ERRORS.md - Problem solving
echo.

echo 🏁 Setup script complete!
pause
