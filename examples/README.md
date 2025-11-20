# Examples

This directory contains example scripts demonstrating various use cases for the Retail Compliance Analyzer.

## Available Examples

### 1. basic_usage.py
Simple example showing basic analyzer usage.

```bash
python examples/basic_usage.py
```

**What it does:**
- Initializes the analyzer
- Analyzes a single image
- Prints product information and compliance status

### 2. batch_analysis.py
Process multiple images in batch mode.

```bash
python examples/batch_analysis.py
```

**What it does:**
- Scans a directory for images
- Analyzes each image
- Generates individual reports
- Creates a summary report

**Use case:** Process daily store photos for compliance monitoring

### 3. filter_violations.py
Filter and display specific types of violations.

```bash
python examples/filter_violations.py
```

**What it does:**
- Analyzes an image
- Filters products by violation type
- Displays critical, expired, and damaged items separately

**Use case:** Generate targeted reports for specific compliance issues

### 4. sample_report.json
Example output showing the complete report structure.

This is a sample report demonstrating:
- Multiple products with different conditions
- Various violation types (expired, damaged, unclear)
- Confidence scores for each detection
- Complete compliance assessment

## Modifying Examples

All examples use placeholder image paths. Update these lines in each script:

```python
image_path = "store_image.jpg"  # Change to your image path
```

For batch processing:
```python
image_directory = "store_images"  # Your image directory
output_directory = "reports"      # Where to save reports
```

## Creating Your Own Scripts

Basic template:

```python
from analyzer import RetailComplianceAnalyzer

# Initialize
analyzer = RetailComplianceAnalyzer()

# Analyze
result = analyzer.analyze_image("your_image.jpg")

# Process results
for product in result['products']:
    # Your logic here
    pass
```

## Tips

1. **Image Paths**: Use absolute paths or ensure you're running from the correct directory
2. **API Key**: Make sure your `.env` file is configured with your Anthropic API key
3. **Error Handling**: Add try/except blocks for production use
4. **Output**: Customize the output format based on your needs

## Integration Examples

### Dashboard Integration
```python
import requests
from analyzer import RetailComplianceAnalyzer

analyzer = RetailComplianceAnalyzer()
result = analyzer.analyze_image("store.jpg")

# Post to your dashboard API
requests.post("https://your-dashboard.com/api/reports", json=result)
```

### Email Alerts for Critical Violations
```python
import smtplib
from email.mime.text import MIMEText
from analyzer import RetailComplianceAnalyzer

analyzer = RetailComplianceAnalyzer()
result = analyzer.analyze_image("store.jpg")

if result['overall_compliance']['violation_count'] > 0:
    critical = result['overall_compliance']['critical_violations']
    if critical:
        # Send email alert
        msg = MIMEText(f"Critical violations found: {critical}")
        # ... configure and send email
```

### Database Storage
```python
import sqlite3
from analyzer import RetailComplianceAnalyzer

analyzer = RetailComplianceAnalyzer()
result = analyzer.analyze_image("store.jpg")

# Store in database
conn = sqlite3.connect("compliance.db")
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO reports (report_id, timestamp, status, violations)
    VALUES (?, ?, ?, ?)
""", (
    result['report_id'],
    result['timestamp'],
    result['overall_compliance']['status'],
    result['overall_compliance']['violation_count']
))
conn.commit()
```

## Need Help?

- Check the main [README.md](../README.md)
- Review the [QUICKSTART.md](../QUICKSTART.md) guide
- Examine the [schema.json](../schema.json) for output structure
