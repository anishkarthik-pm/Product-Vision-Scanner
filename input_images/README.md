# Input Images Folder

Drop your retail store images here for batch processing.

## Supported Formats

- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.webp`

## Usage

1. **Add your images to this folder**
   ```bash
   # Copy images here
   cp /path/to/your/images/*.jpg input_images/
   ```

2. **Run batch processor**
   ```bash
   # Process all images
   python batch_processor.py --type waste
   ```

3. **Check results**
   ```bash
   # CSV reports will be in output_reports/
   ls output_reports/
   ```

## Naming Convention

No specific naming required - all images in this folder will be processed.

Good practices:
- `waste_store1_20250120.jpg` - Descriptive names
- `shelf_aisle3_morning.jpg` - Include context
- `promo_endcap_blackfriday.jpg` - Include date/location

## Examples

### Waste Analysis
Drop images of:
- Waste bins
- Damaged products
- Expired items
- Disposal areas

### Shelf Analysis
Drop images of:
- Store shelves
- Product displays
- Stock levels

### Promo Analysis
Drop images of:
- Promotional displays
- Endcaps
- Special offers

### FIFO Analysis
Drop images of:
- Coolers (showing front and back products)
- Product rows with visible expiry dates

## Tips

- ✓ Use high-resolution images (1024px+ recommended)
- ✓ Ensure good lighting
- ✓ Keep labels/dates visible
- ✓ Capture straight-on when possible
- ✗ Avoid blurry images
- ✗ Avoid heavily shadowed images
