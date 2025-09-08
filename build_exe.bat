@echo off
echo ============================================================
echo 🚀 WHATSAPP AUTOMATION .EXE BUILDER
echo ============================================================
echo.

echo 📋 Checking requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller is ready

echo.
echo 🔨 Building WhatsApp Automation .exe file...
echo ⏳ This may take 2-5 minutes...
echo.

REM Check if script file exists
if not exist "lead_automation_selenium_whatsapp.py" (
    echo ❌ ERROR: lead_automation_selenium_whatsapp.py not found!
    echo 📁 Current directory: %CD%
    echo 📋 Files in current directory:
    dir *.py
    echo.
    echo 🔧 SOLUTIONS:
    echo    1. Copy lead_automation_selenium_whatsapp.py to this folder
    echo    2. Run this script from the folder containing your Python file
    echo    3. Update this script with correct filename
    pause
    exit /b 1
)

echo ✅ Found script file: lead_automation_selenium_whatsapp.py

REM Build the executable
pyinstaller --onefile --console --name "WhatsApp_Multi_Team_Automation" lead_automation_selenium_whatsapp.py

if %errorlevel% neq 0 (
    echo ❌ Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo.
echo 📁 Your .exe file is located at:
echo    dist\WhatsApp_Multi_Team_Automation.exe
echo.
echo 📋 Next steps:
echo    1. Copy the .exe file to your desired location
echo    2. Copy .env, template.txt, and media folder to same location
echo    3. Double-click the .exe to run!
echo.
echo 🎯 For advanced build with all files included, use:
echo    pyinstaller build_whatsapp_automation.spec
echo.

pause
