# Local Setup Instructions

Step-by-step guide to set up the Retail Compliance Analyzer on your local machine.

## Prerequisites

- Python 3.8 or higher
- Git
- Anthropic API key (get from https://console.anthropic.com/)

---

## Step 1: Clone the Repository

```bash
# If you haven't cloned yet
git clone https://github.com/anishkarthik-pm/Product-Vision-Scanner.git
cd Product-Vision-Scanner

# OR if already cloned, pull latest changes
cd Product-Vision-Scanner
git pull origin claude/retail-compliance-analyzer-01C68UCBLnc57njb6sLcHPV2
```

---

## Step 2: Check Python Version

```bash
python --version
# or
python3 --version

# Should show Python 3.8 or higher
```

If Python is not installed or version is < 3.8:
- **macOS**: `brew install python@3.11`
- **Ubuntu/Debian**: `sudo apt update && sudo apt install python3.11`
- **Windows**: Download from https://www.python.org/downloads/

---

## Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your prompt
```

---

## Step 4: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep anthropic
pip list | grep Pillow
```

You should see:
```
anthropic    0.39.0 (or higher)
Pillow       10.x.x
jsonschema   4.x.x
python-dotenv 1.x.x
```

---

## Step 5: Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to "API Keys" section
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-...`)

⚠️ **Important**: Keep this key secret! Never commit it to git.

---

## Step 6: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your API key
# On macOS/Linux:
nano .env
# or
vim .env
# or use any text editor

# On Windows:
notepad .env
```

Update the `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here

# Optional settings
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
```

Save and close the file.

---

## Step 7: Verify Setup

Run the setup verification script:

```bash
python test_setup.py
```

Expected output:
```
============================================================
Retail Compliance Analyzer - Setup Verification
============================================================

✓ Python Version
  Python 3.x.x

✓ Required Packages
  All required packages installed

✓ Environment Configuration
  API key configured

✓ Analyzer Module
  Analyzer module loads successfully

✓ JSON Schema
  schema.json is valid

============================================================
✓ All checks passed! Your setup is ready.

Next steps:
  1. Place a store image in the project directory
  2. Run: python -m analyzer.cli analyze your_image.jpg
  3. Check out examples/ for more usage patterns
============================================================
```

If you see ✗ (errors), fix them before proceeding.

---

## Step 8: Test with a Sample Image

### Option A: Use a test image from the web

```bash
# Download a sample grocery store image
curl -o test_image.jpg "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800"
```

### Option B: Use your own image

Place any retail/grocery store image in the project directory.

---

## Step 9: Run Your First Analysis

### Test 1: Quality Check

```bash
python -m analyzer.multi_cli analyze test_image.jpg --type quality_check
```

This checks if the image is suitable for analysis.

### Test 2: Waste Analysis

```bash
python -m analyzer.multi_cli analyze test_image.jpg --type waste
```

### Test 3: Save to JSON

```bash
python -m analyzer.multi_cli analyze test_image.jpg --type waste --output report.json

# View the report
cat report.json
# or on Windows:
type report.json
```

### Test 4: Using Python

Create a test script `test_analyzer.py`:

```python
from analyzer import MultiTypeComplianceAnalyzer

# Initialize
analyzer = MultiTypeComplianceAnalyzer()

# Run quality check
print("Running quality check...")
quality = analyzer.quality_check("test_image.jpg")
print(f"Suitable: {quality['suitable_for_analysis']}")
print(f"Recommendation: {quality['recommendation']}")

# If suitable, analyze
if quality['suitable_for_analysis']:
    print("\nRunning waste analysis...")
    result = analyzer.analyze_waste("test_image.jpg")
    print(f"Total items: {result.get('estimated_total_items', 0)}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print("✓ Analysis complete!")
else:
    print("⚠️ Image quality issues detected")
```

Run it:
```bash
python test_analyzer.py
```

---

## Step 10: Explore Examples

```bash
# View available examples
ls examples/

# Try different capture types
python -m analyzer.multi_cli analyze shelf_image.jpg --type shelf
python -m analyzer.multi_cli analyze promo_image.jpg --type promo
python -m analyzer.multi_cli analyze cooler_image.jpg --type fifo
```

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY must be set"

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# Check contents (without showing the key)
grep "ANTHROPIC_API_KEY" .env

# If not set, edit .env and add your key
nano .env
```

### Error: "No module named 'anthropic'"

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "Image file not found"

**Solution**:
```bash
# Check current directory
pwd

# List files
ls *.jpg

# Use absolute path
python -m analyzer.multi_cli analyze /full/path/to/image.jpg --type waste
```

### Low Confidence Scores

**Causes**:
- Image is blurry
- Poor lighting
- Text/labels not visible
- Image resolution too low

**Solution**:
- Run quality check first
- Retake image with better conditions
- Ensure text is clearly visible

### API Rate Limits

If you hit rate limits:
```python
# Add delays between requests
import time

for image in images:
    result = analyzer.analyze_waste(image)
    time.sleep(2)  # Wait 2 seconds between calls
```

---

## Quick Command Reference

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Deactivate when done
deactivate

# Install/update dependencies
pip install -r requirements.txt

# Run verification
python test_setup.py

# Analyze image (waste)
python -m analyzer.multi_cli analyze image.jpg --type waste

# Analyze image (shelf)
python -m analyzer.multi_cli analyze image.jpg --type shelf

# Quality check
python -m analyzer.multi_cli analyze image.jpg --type quality_check

# Save to file
python -m analyzer.multi_cli analyze image.jpg --type waste -o report.json

# Validate report
python validate_schema.py report.json
```

---

## Next Steps

1. **Read the guides**:
   - `README.md` - Full documentation
   - `QUICKSTART.md` - Quick start guide
   - `MULTI_TYPE_GUIDE.md` - Multi-type analyzer guide

2. **Explore examples**:
   - `examples/basic_usage.py`
   - `examples/batch_analysis.py`
   - `examples/multi_type_usage.py`

3. **Integrate into your workflow**:
   - Connect to your database
   - Set up automated processing
   - Build dashboards

---

## Support

- **Documentation**: Check `MULTI_TYPE_GUIDE.md`
- **Examples**: Review files in `examples/` directory
- **Schemas**: See `analyzer/schemas.py` for output structures
- **Issues**: Report bugs on GitHub

---

## Security Notes

⚠️ **Never commit your `.env` file to git!**

The `.gitignore` file already excludes it, but double-check:
```bash
cat .gitignore | grep .env
# Should show: .env
```

✓ `.env` is gitignored
✓ `.env.example` is safe to commit (no real keys)
✓ Keep your API key secret
