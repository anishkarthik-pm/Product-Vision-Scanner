# Gemini Setup Guide

Quick guide to set up the Retail Compliance Analyzer with **Google Gemini API**.

## Why Gemini?

- **Faster**: Gemini 1.5 Flash is optimized for speed
- **Cost-effective**: Generally lower cost per API call
- **Structured outputs**: Native JSON mode with schema validation
- **Multimodal**: Excellent vision capabilities

## Quick Setup

### Step 1: Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key (starts with `AIza...`)

### Step 2: Install Dependencies

```bash
# Clone the repository
git clone https://github.com/anishkarthik-pm/Product-Vision-Scanner.git
cd Product-Vision-Scanner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies (includes google-generativeai)
pip install -r requirements.txt
```

### Step 3: Configure API Key

```bash
# Copy the template
cp .env.example .env

# Edit .env
nano .env
```

**Update these lines:**
```bash
# Google Gemini API Key
GEMINI_API_KEY=AIza_your_actual_api_key_here
```

Save and close.

### Step 4: Test It

Create a test file `test_gemini.py`:

```python
from analyzer import GeminiComplianceAnalyzer

# Initialize
analyzer = GeminiComplianceAnalyzer()

# Test with your image
result = analyzer.analyze_waste("your_image.jpg")

print(f"Total items: {result['estimated_total_items']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Products found: {len(result['products'])}")
```

Run it:
```bash
python test_gemini.py
```

## Usage Examples

### Basic Waste Analysis

```python
from analyzer import GeminiComplianceAnalyzer

analyzer = GeminiComplianceAnalyzer()
result = analyzer.analyze_waste("waste_image.jpg")

print(f"Waste reason: {result['waste_reason']}")
print(f"Total items: {result['estimated_total_items']}")

for product in result['products']:
    print(f"- {product['product_name']}: {product['condition']}")
```

### Shelf Compliance

```python
analyzer = GeminiComplianceAnalyzer()
result = analyzer.analyze_shelf("shelf_image.jpg")

print(f"OSA: {result['shelf_overview']['osa_percentage']}%")
print(f"Compliance: {result['compliance_status']}")
```

### With Quality Check

```python
analyzer = GeminiComplianceAnalyzer()

# Check quality first
quality = analyzer.quality_check("image.jpg")

if quality['suitable_for_analysis']:
    result = analyzer.analyze_waste("image.jpg")
    print(f"Analysis complete: {result['confidence']:.2f}")
else:
    print(f"Please retake: {quality['recommendation']}")
```

### All Capture Types

```python
analyzer = GeminiComplianceAnalyzer()

# Waste analysis
waste = analyzer.analyze_waste("waste.jpg")

# Shelf analysis
shelf = analyzer.analyze_shelf("shelf.jpg")

# Promotional compliance
promo = analyzer.analyze_promo("promo.jpg")

# FIFO compliance
fifo = analyzer.analyze_fifo("cooler.jpg")
```

### Choose Model

```python
# Fast and cheap (default)
flash = GeminiComplianceAnalyzer(model="gemini-1.5-flash")

# More powerful
pro = GeminiComplianceAnalyzer(model="gemini-1.5-pro")

# Custom temperature
analyzer = GeminiComplianceAnalyzer(temperature=0.0)  # Most deterministic
```

### Save Results

```python
analyzer = GeminiComplianceAnalyzer()

result = analyzer.analyze_and_save(
    image_path="waste.jpg",
    capture_type="waste",
    output_path="report.json"
)
```

## API Key Security

⚠️ **Important**: Never commit your API key to git!

The `.env` file is already in `.gitignore`, but double-check:

```bash
cat .gitignore | grep .env
# Should show: .env
```

## Model Comparison

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **gemini-1.5-flash** | ⚡ Very Fast | 💰 Low | Most use cases, batch processing |
| **gemini-1.5-pro** | 🐌 Slower | 💰💰 Higher | Complex images, critical analysis |

**Recommendation**: Start with `gemini-1.5-flash` for most scenarios.

## Gemini vs Claude

Both work great! Choose based on your needs:

| Feature | Gemini | Claude |
|---------|--------|--------|
| **Speed** | ⚡⚡⚡ Faster (Flash) | ⚡⚡ Fast |
| **Cost** | 💰 Lower | 💰💰 Higher |
| **Vision Quality** | ✓ Excellent | ✓ Excellent |
| **Structured Output** | ✓ Native JSON mode | ✓ Supported |
| **Ease of Setup** | ✓ Simple | ✓ Simple |

**Use Gemini if**: Cost and speed are priorities
**Use Claude if**: You prefer Anthropic's ecosystem

## Troubleshooting

### "GEMINI_API_KEY must be set"

```bash
# Check .env exists
ls -la .env

# Verify key is set (don't show full key)
grep "GEMINI_API_KEY" .env | head -c 30

# If missing, edit .env
nano .env
```

### "No module named 'google.generativeai'"

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install google-generativeai
pip install google-generativeai>=0.3.0
```

### API Key Invalid

- Make sure you copied the full key
- Check for extra spaces or newlines
- Regenerate key at https://makersuite.google.com/app/apikey

### Rate Limits

If you hit rate limits:

```python
import time

for image in images:
    result = analyzer.analyze_waste(image)
    time.sleep(1)  # Wait 1 second between calls
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete Gemini example: quality check -> analyze -> save
"""

from analyzer import GeminiComplianceAnalyzer

def main():
    # Initialize analyzer
    analyzer = GeminiComplianceAnalyzer(model="gemini-1.5-flash")

    image_path = "waste_bin.jpg"

    # Step 1: Quality check
    print("Checking image quality...")
    quality = analyzer.quality_check(image_path)

    if not quality['suitable_for_analysis']:
        print(f"❌ Image quality issue: {quality['recommendation']}")
        return

    print("✓ Image quality OK")

    # Step 2: Analyze
    print("Analyzing waste...")
    result = analyzer.analyze_waste(image_path)

    if 'error' in result:
        print(f"❌ Analysis error: {result['error_message']}")
        return

    # Step 3: Display results
    print(f"\n✓ Analysis complete!")
    print(f"  Waste reason: {result['waste_reason']}")
    print(f"  Total items: {result['estimated_total_items']}")
    print(f"  Products: {len(result['products'])}")
    print(f"  Confidence: {result['confidence']:.2%}")

    # Step 4: Save
    analyzer.analyze_and_save(
        image_path,
        "waste",
        "waste_report.json"
    )
    print(f"\n✓ Report saved to waste_report.json")

if __name__ == "__main__":
    main()
```

## Pricing (as of 2024)

Gemini 1.5 Flash is very cost-effective:
- Input: ~$0.00001875 per image
- Output: ~$0.000075 per 1K tokens

For 1000 images: ~$0.02 + output costs

*Check current pricing at: https://ai.google.dev/pricing*

## Next Steps

1. ✅ Get your Gemini API key
2. ✅ Set up `.env` with your key
3. ✅ Install dependencies
4. ✅ Run a test analysis
5. 📚 Read `MULTI_TYPE_GUIDE.md` for advanced usage
6. 💻 Check `examples/gemini_usage.py` for more examples

## Support

- **Gemini Docs**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Project Docs**: See `MULTI_TYPE_GUIDE.md`
- **Examples**: See `examples/gemini_usage.py`

---

**You're all set!** 🚀 Start analyzing retail images with Gemini.
