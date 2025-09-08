@echo off
echo ============================================================
echo 🔍 WHATSAPP AUTOMATION FILE FINDER
echo ============================================================
echo.

echo 📁 Current directory: %CD%
echo.

echo 📋 Looking for Python files:
dir *.py /b 2>nul
if %errorlevel% neq 0 (
    echo    ❌ No Python files found in current directory
) else (
    echo    ✅ Python files found above
)
echo.

echo 📋 Looking for required files:
echo.

if exist "lead_automation_selenium_whatsapp.py" (
    echo ✅ lead_automation_selenium_whatsapp.py - FOUND
) else (
    echo ❌ lead_automation_selenium_whatsapp.py - NOT FOUND
)

if exist ".env" (
    echo ✅ .env - FOUND
) else (
    echo ❌ .env - NOT FOUND
)

if exist "template.txt" (
    echo ✅ template.txt - FOUND
) else (
    echo ❌ template.txt - NOT FOUND
)

if exist "media" (
    echo ✅ media folder - FOUND
) else (
    echo ❌ media folder - NOT FOUND
)

echo.
echo 🔧 RECOMMENDATIONS:
echo.

if not exist "lead_automation_selenium_whatsapp.py" (
    echo 📂 NAVIGATE TO CORRECT FOLDER:
    echo    1. Open File Explorer
    echo    2. Find your Python script file
    echo    3. Copy this find_my_files.bat to that folder
    echo    4. Run it again
    echo.
    echo 🔍 SEARCH FOR YOUR FILE:
    echo    Windows Key + R → type: cmd
    echo    In command prompt type:
    echo    dir C:\ /s /b lead_automation_selenium_whatsapp.py
    echo.
) else (
    echo ✅ Ready to build! Run build_exe.bat
)

echo.
echo 📁 Directory contents:
dir /b
echo.

pause
