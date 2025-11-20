# Retail Compliance Analyzer

AI-powered retail store compliance auditing system that analyzes store images and extracts structured data for compliance reporting.

## Features

- **Vision-Based Analysis**: Uses Claude's vision capabilities to analyze retail store images
- **Structured JSON Output**: Produces standardized compliance reports in JSON format
- **Confidence Scoring**: Provides confidence scores (0.0-1.0) for each detected item
- **Compliance Violations**: Automatically identifies expired products, damaged items, and other violations
- **Fact-Based Reporting**: Only reports what is visible in images, never assumes or infers

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Product-Vision-Scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Command Line Interface

Analyze a single image:
```bash
python -m analyzer.cli analyze path/to/store_image.jpg
```

Analyze with output to file:
```bash
python -m analyzer.cli analyze path/to/image.jpg --output report.json
```

### Python API

```python
from analyzer.compliance_analyzer import RetailComplianceAnalyzer

# Initialize analyzer
analyzer = RetailComplianceAnalyzer()

# Analyze an image
result = analyzer.analyze_image("path/to/image.jpg")

# Access the structured data
print(f"Total products: {result['overall_compliance']['total_products']}")
print(f"Violations: {result['overall_compliance']['violation_count']}")

# Save report
import json
with open("report.json", "w") as f:
    json.dump(result, indent=2, fp=f)
```

## Output Schema

The analyzer produces JSON output following this structure:

```json
{
  "report_id": "unique-id",
  "timestamp": "2025-11-20T10:00:00Z",
  "analysis_status": "success",
  "products": [
    {
      "product_id": "prod_001",
      "name": "Product Name",
      "brand": "Brand Name",
      "category": "dairy",
      "dates": {
        "expiration_date": "2025-12-31",
        "date_visibility": "clear"
      },
      "condition": {
        "status": "good",
        "damage_type": null
      },
      "compliance": {
        "is_compliant": true,
        "violations": []
      },
      "confidence": 0.95
    }
  ],
  "overall_compliance": {
    "status": "pass",
    "total_products": 10,
    "compliant_count": 9,
    "violation_count": 1
  }
}
```

See `schema.json` for the complete JSON schema definition.

## Critical Rules

The analyzer follows these strict guidelines:

- ✅ **Only reports what is visible** in the image
- ✅ **Never assumes or infers** information
- ✅ **Marks unclear items** as "unclear" rather than guessing
- ✅ **Provides confidence scores** (0.0-1.0) for all detections
- ✅ **Returns valid JSON** only
- ✅ **Uses null** for fields that cannot be determined

## Use Cases

- **Compliance Auditing**: Track expired products and violations
- **Waste Management**: Identify products approaching expiration
- **Quality Control**: Detect damaged or improperly stored items
- **Operations Dashboard**: Feed structured data into reporting systems
- **Inventory Monitoring**: Track product conditions over time

## Requirements

- Python 3.8+
- Anthropic API key (Claude access)
- Image files in common formats (JPG, PNG, etc.)

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
