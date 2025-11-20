# Output Reports Folder

All CSV reports are saved here after batch processing.

## Report Types

### Detailed Reports
One row per product/item found in images.

**Filename format**: `{capture_type}_analysis_{timestamp}.csv`

Examples:
- `waste_analysis_20250120_143022.csv` - Detailed waste report
- `shelf_analysis_20250120_150000.csv` - Detailed shelf report

### Summary Reports
One row per image (summary statistics).

**Filename format**: `{capture_type}_summary_{timestamp}.csv`

Examples:
- `waste_summary_20250120_143022.csv` - Summary per image
- `shelf_summary_20250120_150000.csv` - Summary per image

## CSV Fields

### Waste Analysis CSV

| Field | Description |
|-------|-------------|
| image_name | Original image filename |
| timestamp | Analysis timestamp |
| product_name | Product name |
| brand | Brand name |
| sku | Product SKU (if visible) |
| quantity | Quantity count |
| unit | Unit (pieces, kg, etc.) |
| expiry_date | Expiry date (YYYY-MM-DD) |
| batch_code | Batch code (if visible) |
| mrp | MRP/price (if visible) |
| condition | expired/damaged/spoiled/etc |
| damage_details | Specific damage description |
| waste_reason | Overall waste reason |
| confidence | Analysis confidence (0.0-1.0) |
| image_quality | clear/partial/poor |

### Shelf Analysis CSV

| Field | Description |
|-------|-------------|
| image_name | Original image filename |
| timestamp | Analysis timestamp |
| total_facings | Total shelf facings |
| stocked_facings | Facings with product |
| empty_facings | Empty facings |
| osa_percentage | On-Shelf Availability % |
| compliance_status | compliant/issues_found/etc |
| confidence | Analysis confidence |
| issues_count | Number of issues found |

### Promo Analysis CSV

| Field | Description |
|-------|-------------|
| image_name | Original image filename |
| timestamp | Analysis timestamp |
| promo_type | endcap/display_stand/etc |
| promo_title | Promotion title |
| products_on_promo | Number of products |
| display_quality | excellent/good/poor |
| signage_visible | true/false |
| price_visible | true/false |
| compliance_status | Compliance status |
| confidence | Analysis confidence |
| issues_count | Number of issues |

### FIFO Analysis CSV

| Field | Description |
|-------|-------------|
| image_name | Original image filename |
| timestamp | Analysis timestamp |
| product_name | Product name |
| brand | Brand name |
| front_expiry_date | Front product expiry |
| back_expiry_date | Back product expiry |
| fifo_status | correct/violation/unclear |
| violation_details | Violation description |
| days_until_expiry | Days to expiry |
| recommendation | Recommended action |
| confidence | Analysis confidence |

## Opening CSV Files

### Excel
Double-click the CSV file or:
1. Open Excel
2. File → Open
3. Select CSV file

### Google Sheets
1. Go to sheets.google.com
2. File → Import
3. Upload CSV file

### Python/Pandas
```python
import pandas as pd

df = pd.read_csv('output_reports/waste_analysis_20250120.csv')
print(df.head())
```

## Notes

- All timestamps are in UTC
- Confidence scores range from 0.0 (low) to 1.0 (high)
- Empty/null fields indicate data not visible in image
- Files are UTF-8 encoded for international character support
