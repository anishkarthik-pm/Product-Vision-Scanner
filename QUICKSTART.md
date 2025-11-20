# Quick Start Guide

Get started with the Retail Compliance Analyzer in 5 minutes.

## Step 1: Installation

```bash
# Clone the repository
git clone <repository-url>
cd Product-Vision-Scanner

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your API key from: https://console.anthropic.com/
```

Your `.env` file should look like:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

## Step 3: Analyze Your First Image

### Using the CLI

```bash
python -m analyzer.cli analyze path/to/store_image.jpg
```

This will display a detailed compliance report in your terminal.

### Using Python

Create a file `test_analyzer.py`:

```python
from analyzer import RetailComplianceAnalyzer

analyzer = RetailComplianceAnalyzer()
result = analyzer.analyze_image("store_image.jpg")

print(f"Products found: {result['overall_compliance']['total_products']}")
print(f"Violations: {result['overall_compliance']['violation_count']}")
```

Run it:
```bash
python test_analyzer.py
```

## Step 4: Save Results

Save analysis to a JSON file:

```bash
python -m analyzer.cli analyze store_image.jpg --output report.json
```

## Common Use Cases

### 1. Check for Expired Products

```bash
python -m analyzer.cli analyze shelf.jpg | grep -i "expired"
```

### 2. Batch Process Multiple Images

```bash
python examples/batch_analysis.py
```

### 3. Generate Compliance Report

```python
from analyzer import RetailComplianceAnalyzer
import json

analyzer = RetailComplianceAnalyzer()
result = analyzer.analyze_image("store.jpg")

# Extract compliance summary
compliance = result['overall_compliance']
print(f"Status: {compliance['status']}")
print(f"Critical Violations: {len(compliance['critical_violations'])}")

# Save full report
with open("compliance_report.json", "w") as f:
    json.dump(result, f, indent=2)
```

## Understanding the Output

The analyzer returns structured JSON with:

- **products**: List of all products detected
  - Product details (name, brand, category)
  - Expiration dates
  - Condition assessment
  - Compliance violations
  - Confidence scores

- **overall_compliance**: Summary statistics
  - Total products analyzed
  - Compliance counts
  - Critical violations list

- **image_metadata**: Image information
  - Resolution
  - Quality score

## Tips for Best Results

1. **Image Quality**: Use high-resolution images (1024px+ recommended)
2. **Lighting**: Ensure good lighting on products and labels
3. **Focus**: Make sure expiration dates and labels are in focus
4. **Angle**: Photograph products straight-on for better text recognition
5. **Coverage**: Include multiple angles if needed for complete coverage

## Troubleshooting

### "ANTHROPIC_API_KEY must be set"
- Check that your `.env` file exists and contains your API key
- Ensure you're running from the project root directory

### "Image not found"
- Verify the image path is correct
- Use absolute paths or paths relative to current directory

### Low confidence scores
- Improve image quality (resolution, lighting, focus)
- Ensure text is clearly visible and not blurred
- Try a closer photo of the specific area

## Next Steps

- Check out the [examples/](examples/) directory for more advanced usage
- Read the full [README.md](README.md) for detailed documentation
- Review the [schema.json](schema.json) for complete output format
- Integrate with your compliance dashboard or reporting system

## Support

For issues or questions:
- Check the documentation in the repository
- Review example scripts in `examples/`
- Open an issue on GitHub
