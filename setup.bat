@echo off
REM Setup script for Retail Compliance Analyzer (Windows)

echo ============================================================
echo RETAIL COMPLIANCE ANALYZER - AUTOMATED SETUP
echo ============================================================
echo.

REM Check Python
echo Step 1: Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo √ Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Step 2: Creating virtual environment...
if exist venv (
    echo Warning: Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo √ Virtual environment created
)

REM Activate virtual environment
echo.
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo √ Virtual environment activated

REM Install dependencies
echo.
echo Step 4: Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
echo √ Dependencies installed

REM Set up .env file
echo.
echo Step 5: Setting up environment configuration...
if exist .env (
    echo Warning: .env file already exists. Skipping...
) else (
    copy .env.example .env >nul
    echo √ .env file created from template
    echo.
    echo Warning: IMPORTANT: Edit .env and add your Anthropic API key!
    echo.
    echo Get your API key from: https://console.anthropic.com/
    echo.
    echo Then edit .env:
    echo   notepad .env
    echo.
)

REM Run verification
echo.
echo Step 6: Running setup verification...
python test_setup.py

echo.
echo ============================================================
echo SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. If not done already, configure your API key:
echo    notepad .env
echo.
echo 2. Activate the virtual environment (in new terminal sessions):
echo    venv\Scripts\activate
echo.
echo 3. Run a quick test:
echo    python quick_test.py
echo.
echo 4. Try analyzing an image:
echo    python -m analyzer.multi_cli analyze image.jpg --type waste
echo.
echo 5. Read the documentation:
echo    - QUICKSTART.md - Quick start guide
echo    - MULTI_TYPE_GUIDE.md - Comprehensive guide
echo    - examples\ - Code examples
echo.

pause
