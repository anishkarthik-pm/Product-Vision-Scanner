# Batch Processing Guide

Process multiple images at once and get CSV reports automatically!

## 🚀 Quick Start

### 1. Drop Images in Folder
```bash
# Copy your images to input_images/
cp /path/to/your/images/*.jpg input_images/
```

### 2. Run Batch Processor
```bash
# Process all images (waste analysis)
python batch_processor.py

# Or specify analysis type
python batch_processor.py --type shelf
```

### 3. Get CSV Report
```bash
# Check output folder
ls output_reports/

# Open the CSV
open output_reports/waste_analysis_20250120_143022.csv
```

That's it! 🎉

---

## 📁 Folder Structure

```
Product-Vision-Scanner/
├── input_images/          ← Drop your images here
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
│
└── output_reports/        ← CSV reports appear here
    ├── waste_analysis_20250120_143022.csv
    └── waste_summary_20250120_143022.csv
```

---

## 🎯 Analysis Types

### Waste Analysis (Default)
```bash
python batch_processor.py --type waste
```

**Use for**: Waste bins, damaged products, expired items

**CSV Output**: One row per product found
- Product name, brand, quantity
- Condition (expired/damaged/spoiled)
- Expiry dates, damage details
- Waste reason, confidence scores

### Shelf Compliance
```bash
python batch_processor.py --type shelf
```

**Use for**: Store shelves, stock levels

**CSV Output**: One row per shelf image
- Total facings, empty facings
- OSA percentage
- Compliance status, issues found

### Promotional Compliance
```bash
python batch_processor.py --type promo
```

**Use for**: Promotional displays, endcaps

**CSV Output**: One row per promo display
- Promo type, display quality
- Signage/price visibility
- Compliance status

### FIFO Compliance
```bash
python batch_processor.py --type fifo
```

**Use for**: Coolers showing front and back products

**CSV Output**: One row per product checked
- Front/back expiry dates
- FIFO status (correct/violation)
- Recommendations for rotation

---

## 📊 Output Formats

### Detailed CSV
Contains all products/items found across all images.

**Example: waste_analysis_20250120.csv**
```csv
image_name,product_name,brand,quantity,unit,condition,damage_details,confidence
waste1.jpg,Milk 1L,Happy Farms,3,bottles,expired,Expired 5 days ago,0.92
waste1.jpg,Bread,Baker's,2,loaves,damaged,Packaging torn,0.88
waste2.jpg,Oranges,Fresh,12,pieces,spoiled,Brown spots visible,0.85
```

### Summary CSV
One row per image with summary statistics.

**Example: waste_summary_20250120.csv**
```csv
image_name,total_items,products_count,waste_reason,confidence
waste1.jpg,5,2,Expiration,0.90
waste2.jpg,12,1,Spoilage,0.85
```

---

## 💡 Usage Examples

### Example 1: Daily Waste Tracking
```bash
# 1. Store manager takes photos of waste bin
# 2. Upload photos to input_images/
# 3. Run processor
python batch_processor.py --type waste

# 4. Get CSV with all wasted items
# 5. Import to Excel/Google Sheets for reporting
```

### Example 2: Weekly Shelf Audits
```bash
# 1. Take photos of all store shelves
# 2. Upload to input_images/
# 3. Run shelf analysis
python batch_processor.py --type shelf

# 4. Get OSA metrics for all shelves
# 5. Identify out-of-stock issues
```

### Example 3: Promotional Campaign Verification
```bash
# 1. Photograph all promotional displays
# 2. Upload images
# 3. Run promo analysis
python batch_processor.py --type promo

# 4. Verify all displays are compliant
# 5. Generate report for management
```

### Example 4: Cooler FIFO Compliance
```bash
# 1. Take photos showing front and back of products
# 2. Upload images
# 3. Run FIFO check
python batch_processor.py --type fifo

# 4. Identify rotation violations
# 5. Take corrective action
```

---

## ⚙️ Advanced Options

### Custom Folders
```bash
# Use different folders
python batch_processor.py --input my_images --output my_reports
```

### Summary Only
```bash
# Generate summary CSV only (faster)
python batch_processor.py --summary-only
```

### View Help
```bash
python batch_processor.py --help
```

---

## 📈 Working with CSV in Excel/Sheets

### Excel
1. Open the CSV file in Excel
2. Data will auto-populate
3. Use filters, pivot tables, charts
4. Save as .xlsx for advanced features

### Google Sheets
1. Go to sheets.google.com
2. File → Import → Upload CSV
3. Create charts and analysis
4. Share with team

### Python/Pandas
```python
import pandas as pd

# Load CSV
df = pd.read_csv('output_reports/waste_analysis_20250120.csv')

# Filter by condition
expired = df[df['condition'] == 'expired']
print(f"Expired items: {len(expired)}")

# Group by product
summary = df.groupby('product_name')['quantity'].sum()
print(summary)

# Export to Excel with formatting
df.to_excel('waste_report.xlsx', index=False)
```

---

## 🔄 Workflow Automation

### Daily Automated Processing

Create a script `daily_process.sh`:
```bash
#!/bin/bash
# Daily waste processing script

# Process images
python batch_processor.py --type waste

# Move processed images to archive
mkdir -p archive/$(date +%Y%m%d)
mv input_images/*.jpg archive/$(date +%Y%m%d)/

# Send email with CSV (optional)
# mail -s "Daily Waste Report" team@company.com < output_reports/waste_*.csv
```

Run daily with cron:
```bash
# Edit crontab
crontab -e

# Add daily run at 6 PM
0 18 * * * /path/to/daily_process.sh
```

---

## 📋 CSV Field Reference

### All Analysis Types Include:
- `image_name` - Original image filename
- `timestamp` - Analysis timestamp (UTC)
- `confidence` - Confidence score (0.0-1.0)

### Waste-Specific Fields:
- `product_name`, `brand`, `sku`
- `quantity`, `unit`
- `expiry_date`, `batch_code`, `mrp`
- `condition` - expired/damaged/spoiled/packaging_torn/contaminated/recall
- `damage_details` - Specific observations
- `waste_reason` - Overall waste cause

### Shelf-Specific Fields:
- `total_facings`, `stocked_facings`, `empty_facings`
- `osa_percentage` - On-Shelf Availability %
- `compliance_status` - compliant/issues_found/critical_issues
- `issues_count` - Number of issues detected

### Promo-Specific Fields:
- `promo_type` - endcap/display_stand/shelf_signage/bundle/price_reduction
- `promo_title` - Promotional text
- `products_on_promo` - Number of products
- `display_quality` - excellent/good/poor/damaged
- `signage_visible`, `price_visible` - Boolean

### FIFO-Specific Fields:
- `product_name`, `brand`
- `front_expiry_date`, `back_expiry_date`
- `fifo_status` - correct/violation/unclear/unable_to_verify
- `violation_details` - Description of violation
- `days_until_expiry` - Days remaining
- `recommendation` - Suggested action

---

## ⚠️ Troubleshooting

### No images found
```
Problem: "No images found in input_images/"
Solution: Add .jpg/.png images to input_images/ folder
```

### API errors
```
Problem: Analysis fails with API error
Solution: Check GEMINI_API_KEY in .env file
        Verify internet connection
        Check API quota/billing
```

### Low confidence scores
```
Problem: Confidence scores < 0.6
Solution: Ensure images are:
         - High resolution (1024px+)
         - Well-lit
         - In focus
         - Labels clearly visible
```

### CSV encoding issues
```
Problem: Special characters display incorrectly
Solution: Open CSV with UTF-8 encoding
         In Excel: Data → Get External Data → From Text → UTF-8
```

---

## 🎯 Best Practices

1. **Image Quality**
   - Use 1080p or higher resolution
   - Ensure good lighting
   - Keep camera stable (avoid blur)
   - Capture labels/dates clearly

2. **Organization**
   - Name images descriptively
   - Include date/location in filename
   - Process daily for best tracking
   - Archive processed images

3. **CSV Management**
   - Keep CSVs in output_reports/
   - Import to database for long-term storage
   - Create backups regularly
   - Use version control for reports

4. **Performance**
   - Process 10-50 images at a time
   - Use `--summary-only` for quick overviews
   - Monitor API usage/costs
   - Consider batch processing during off-hours

---

## 📚 Next Steps

- Read `GEMINI_SETUP.md` for API configuration
- Check `examples/` for Python automation scripts
- Review `MULTI_TYPE_GUIDE.md` for detailed analysis info
- Set up automated workflows for your store

---

## 🆘 Support

- **Batch Processing Issues**: Check this guide
- **API Setup**: See `GEMINI_SETUP.md`
- **Analysis Details**: See `MULTI_TYPE_GUIDE.md`
- **General Help**: See `README.md`
