# Multi-Type Compliance Analyzer Guide

Comprehensive guide for using the enhanced multi-type compliance analyzer supporting waste, shelf, promo, and FIFO analysis.

## Overview

The Multi-Type Compliance Analyzer extends the basic analyzer with support for multiple retail compliance scenarios:

- **Waste Analysis**: Shrinkage and disposal tracking
- **Shelf Analysis**: On-Shelf Availability (OSA) and compliance
- **Promo Analysis**: Promotional display execution
- **FIFO Analysis**: First In, First Out rotation compliance
- **Quality Check**: Pre-analysis image quality assessment

## Quick Start

### Using Python API

```python
from analyzer import MultiTypeComplianceAnalyzer

# Initialize
analyzer = MultiTypeComplianceAnalyzer()

# Waste analysis
waste_result = analyzer.analyze_waste("waste_bin.jpg")

# Shelf compliance
shelf_result = analyzer.analyze_shelf("shelf.jpg")

# Promo compliance
promo_result = analyzer.analyze_promo("endcap.jpg")

# FIFO check
fifo_result = analyzer.analyze_fifo("cooler.jpg")

# Quality check
quality = analyzer.quality_check("image.jpg")
```

### Using CLI

```bash
# Waste analysis
python -m analyzer.multi_cli analyze waste_bin.jpg --type waste

# Shelf analysis
python -m analyzer.multi_cli analyze shelf.jpg --type shelf

# Promo analysis
python -m analyzer.multi_cli analyze endcap.jpg --type promo

# FIFO analysis
python -m analyzer.multi_cli analyze cooler.jpg --type fifo

# Quality check
python -m analyzer.multi_cli analyze image.jpg --type quality_check

# Save to JSON
python -m analyzer.multi_cli analyze image.jpg --type waste --output report.json
```

## Capture Types

### 1. Waste Analysis (`waste`)

**Purpose**: Track disposed/wasted products for shrinkage reporting

**Output Structure**:
```json
{
  "capture_type": "waste",
  "products": [
    {
      "product_name": "Organic Milk 1L",
      "brand": "Happy Farms",
      "sku": "12345",
      "quantity": 3,
      "unit": "bottles",
      "expiry_date": "2025-11-15",
      "condition": "expired",
      "damage_details": "Products expired 5 days ago"
    }
  ],
  "waste_reason": "Expiration - products past sell-by date",
  "estimated_total_items": 15,
  "image_quality": "clear",
  "confidence": 0.92
}
```

**Key Fields**:
- `products`: List of wasted items with details
- `condition`: `expired | damaged | spoiled | packaging_torn | contaminated | recall`
- `waste_reason`: Primary cause of waste
- `estimated_total_items`: Total count

**Use Cases**:
- Daily waste tracking
- Shrinkage analysis
- Expiration monitoring
- Loss prevention reporting

---

### 2. Shelf Analysis (`shelf`)

**Purpose**: Monitor On-Shelf Availability and shelf compliance

**Output Structure**:
```json
{
  "capture_type": "shelf",
  "shelf_overview": {
    "total_facings": 24,
    "stocked_facings": 20,
    "empty_facings": 4,
    "osa_percentage": 83.3,
    "shelf_level": "eye_level"
  },
  "products": [
    {
      "product_name": "Cereal Brand A",
      "facings": 6,
      "stock_level": "full",
      "price_visible": true
    }
  ],
  "issues": [
    {
      "issue_type": "out_of_stock",
      "product_name": "Cereal Brand B",
      "severity": "high",
      "description": "4 facings empty, popular product OOS"
    }
  ],
  "compliance_status": "issues_found",
  "confidence": 0.88
}
```

**Key Fields**:
- `shelf_overview`: OSA metrics
- `osa_percentage`: On-Shelf Availability percentage
- `issues`: Compliance problems (OOS, low stock, misplaced items)
- `stock_level`: `full | adequate | low | out_of_stock`

**Use Cases**:
- OSA monitoring
- Planogram compliance
- Stock level tracking
- Merchandising audits

---

### 3. Promo Analysis (`promo`)

**Purpose**: Verify promotional display execution and compliance

**Output Structure**:
```json
{
  "capture_type": "promo",
  "promo_details": {
    "promo_type": "endcap",
    "promo_title": "Black Friday Sale",
    "products_on_promo": 5,
    "display_quality": "good",
    "signage_visible": true,
    "price_visible": true,
    "validity_dates": {
      "start_date": "2025-11-24",
      "end_date": "2025-11-27",
      "dates_visible": true
    }
  },
  "products": [
    {
      "product_name": "Product A",
      "promo_price": 9.99,
      "regular_price": 14.99,
      "stock_level": "adequate"
    }
  ],
  "issues": [],
  "compliance_status": "compliant",
  "confidence": 0.91
}
```

**Key Fields**:
- `promo_type`: `endcap | display_stand | shelf_signage | bundle | price_reduction`
- `display_quality`: `excellent | good | poor | damaged`
- `validity_dates`: Promo start/end dates
- `issues`: Execution problems

**Use Cases**:
- Promotional compliance audits
- Display quality monitoring
- Price verification
- Campaign execution tracking

---

### 4. FIFO Analysis (`fifo`)

**Purpose**: Verify First In, First Out rotation compliance

**Output Structure**:
```json
{
  "capture_type": "fifo",
  "fifo_compliance": {
    "compliant": false,
    "total_products_checked": 3,
    "violations_found": 1,
    "overall_status": "minor_violations"
  },
  "products": [
    {
      "product_name": "Yogurt 500g",
      "front_expiry_date": "2025-12-01",
      "back_expiry_date": "2025-11-25",
      "fifo_status": "violation",
      "violation_details": "Newer product (12/01) in front of older product (11/25)",
      "days_until_expiry_front": 11,
      "recommendation": "Rotate stock - move 11/25 products to front"
    }
  ],
  "issues": [
    {
      "product_name": "Yogurt 500g",
      "issue_type": "newer_in_front",
      "severity": "high",
      "description": "FIFO violation detected - newer products blocking older inventory"
    }
  ],
  "confidence": 0.85
}
```

**Key Fields**:
- `fifo_compliance`: Overall compliance metrics
- `fifo_status`: `correct | violation | unclear | unable_to_verify`
- `front_expiry_date` vs `back_expiry_date`: Date comparison
- `recommendation`: Corrective actions

**Use Cases**:
- FIFO rotation verification
- Expiration risk prevention
- Inventory rotation audits
- Cooler/freezer compliance

---

### 5. Quality Check (`quality_check`)

**Purpose**: Pre-assess image quality before full analysis

**Output Structure**:
```json
{
  "suitable_for_analysis": true,
  "blur_level": "clear",
  "lighting": "good",
  "angle": "straight",
  "content_visible": true,
  "issues": [],
  "recommendation": "proceed"
}
```

**Key Fields**:
- `suitable_for_analysis`: true/false
- `blur_level`: `clear | slight | severe`
- `lighting`: `good | dim | overexposed`
- `recommendation`: `proceed | retake_blur | retake_lighting | retake_angle | retake_framing`

**Use Cases**:
- Pre-flight image validation
- Mobile app image quality checks
- Automated rejection of poor images
- User feedback on image capture

---

## Best Practices

### 1. Workflow Pattern

```python
analyzer = MultiTypeComplianceAnalyzer()

# Step 1: Quality check
quality = analyzer.quality_check(image_path)

if not quality['suitable_for_analysis']:
    print(f"Please retake: {quality['recommendation']}")
    return

# Step 2: Perform analysis
result = analyzer.analyze_image(image_path, capture_type="waste")

# Step 3: Save results
analyzer.analyze_and_save(image_path, "waste", "report.json")
```

### 2. Batch Processing

```python
images = [
    ("waste1.jpg", "waste"),
    ("shelf1.jpg", "shelf"),
    ("promo1.jpg", "promo")
]

for image, type in images:
    result = analyzer.analyze_image(image, capture_type=type)
    # Process result...
```

### 3. Confidence Thresholds

```python
result = analyzer.analyze_waste(image_path)

if result['confidence'] < 0.7:
    print("⚠️ Low confidence - manual review recommended")
elif result['confidence'] < 0.9:
    print("✓ Good confidence")
else:
    print("✓✓ High confidence")
```

### 4. Error Handling

```python
try:
    result = analyzer.analyze_image(image_path, capture_type="waste")

    if "error" in result:
        print(f"Analysis error: {result['error_message']}")
    else:
        # Process successful result
        pass

except FileNotFoundError:
    print("Image file not found")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Schema Validation

All outputs are validated against JSON schemas defined in `analyzer/schemas.py`.

To validate a report:

```python
from jsonschema import validate
from analyzer.schemas import SCHEMAS
import json

with open("report.json") as f:
    report = json.load(f)

# Validate
validate(instance=report, schema=SCHEMAS["waste"])
print("✓ Report is valid")
```

Or use the validation script:

```bash
python validate_schema.py report.json
```

## Integration Examples

### Dashboard Integration

```python
import requests

analyzer = MultiTypeComplianceAnalyzer()
result = analyzer.analyze_shelf("shelf.jpg")

# Post to API
requests.post("https://dashboard.example.com/api/reports", json=result)
```

### Database Storage

```python
import sqlite3

result = analyzer.analyze_waste("waste.jpg")

conn = sqlite3.connect("compliance.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO waste_reports (timestamp, total_items, confidence, data)
    VALUES (?, ?, ?, ?)
""", (
    result['_metadata']['analysis_timestamp'],
    result['estimated_total_items'],
    result['confidence'],
    json.dumps(result)
))

conn.commit()
```

### Alert System

```python
result = analyzer.analyze_fifo("cooler.jpg")

if result['fifo_compliance']['violations_found'] > 0:
    # Send alert
    for issue in result['issues']:
        if issue['severity'] in ['critical', 'high']:
            send_alert(f"FIFO violation: {issue['description']}")
```

## Tips for Best Results

1. **Image Quality**
   - Use high resolution (1024px+ recommended)
   - Ensure good lighting
   - Keep camera stable (avoid blur)
   - Capture straight-on when possible

2. **Content Framing**
   - Include all relevant products in frame
   - Ensure labels/dates are visible
   - Avoid obstructions
   - Get close enough to read text

3. **Analysis Type Selection**
   - `waste`: Use for disposal bins, damaged goods
   - `shelf`: Use for shelf/gondola views
   - `promo`: Use for endcaps, displays, promotional areas
   - `fifo`: Use when you can see front AND back products

4. **Confidence Interpretation**
   - < 0.6: Low confidence, recommend retake or manual review
   - 0.6-0.8: Moderate confidence, acceptable for most uses
   - 0.8-0.9: Good confidence
   - > 0.9: High confidence

## Troubleshooting

**Low Confidence Scores**
- Check image quality (blur, lighting)
- Ensure text/labels are visible
- Try capturing from different angle
- Improve lighting conditions

**Missing Product Details**
- Products listed with null fields indicate unreadable labels
- Get closer to products
- Ensure labels face camera
- Improve lighting on label areas

**Schema Validation Errors**
- Check that all required fields are present
- Verify data types match schema
- Ensure enum values are valid
- Review `analyzer/schemas.py` for requirements

## Support

- **Examples**: See `examples/multi_type_usage.py`
- **Schemas**: See `analyzer/schemas.py`
- **Prompts**: See `analyzer/prompts.py`
- **Main README**: See `README.md`
