"""
Batch Image Processor with CSV Output

Processes all images from input_images/ folder and saves results as CSV in output_reports/
"""

import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from analyzer import GeminiComplianceAnalyzer


class BatchProcessor:
    """Process multiple images and generate CSV reports."""

    def __init__(
        self,
        input_folder: str = "input_images",
        output_folder: str = "output_reports",
        capture_type: str = "waste"
    ):
        """
        Initialize batch processor.

        Args:
            input_folder: Folder containing images to process
            output_folder: Folder to save CSV reports
            capture_type: Type of analysis (waste, shelf, promo, fifo)
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.capture_type = capture_type
        self.analyzer = GeminiComplianceAnalyzer()

        # Create folders if they don't exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)

    def find_images(self) -> List[Path]:
        """Find all image files in input folder."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = []

        for ext in image_extensions:
            images.extend(self.input_folder.glob(f'*{ext}'))
            images.extend(self.input_folder.glob(f'*{ext.upper()}'))

        return sorted(images)

    def convert_waste_to_csv(self, result: Dict[str, Any], image_name: str) -> List[Dict]:
        """
        Convert waste analysis result to CSV rows.

        Args:
            result: Analysis result dictionary
            image_name: Name of the analyzed image

        Returns:
            List of dictionaries (one per product)
        """
        rows = []

        for product in result.get('products', []):
            row = {
                'image_name': image_name,
                'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
                'product_name': product.get('product_name', ''),
                'brand': product.get('brand', ''),
                'sku': product.get('sku', ''),
                'quantity': product.get('quantity', ''),
                'unit': product.get('unit', ''),
                'expiry_date': product.get('expiry_date', ''),
                'batch_code': product.get('batch_code', ''),
                'mrp': product.get('mrp', ''),
                'condition': product.get('condition', ''),
                'damage_details': product.get('damage_details', ''),
                'waste_reason': result.get('waste_reason', ''),
                'confidence': result.get('confidence', ''),
                'image_quality': result.get('image_quality', '')
            }
            rows.append(row)

        return rows

    def convert_shelf_to_csv(self, result: Dict[str, Any], image_name: str) -> List[Dict]:
        """Convert shelf analysis result to CSV rows."""
        overview = result.get('shelf_overview', {})

        # Create summary row
        summary_row = {
            'image_name': image_name,
            'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
            'total_facings': overview.get('total_facings', ''),
            'stocked_facings': overview.get('stocked_facings', ''),
            'empty_facings': overview.get('empty_facings', ''),
            'osa_percentage': overview.get('osa_percentage', ''),
            'compliance_status': result.get('compliance_status', ''),
            'confidence': result.get('confidence', ''),
            'issues_count': len(result.get('issues', []))
        }

        return [summary_row]

    def convert_promo_to_csv(self, result: Dict[str, Any], image_name: str) -> List[Dict]:
        """Convert promo analysis result to CSV rows."""
        promo = result.get('promo_details', {})

        row = {
            'image_name': image_name,
            'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
            'promo_type': promo.get('promo_type', ''),
            'promo_title': promo.get('promo_title', ''),
            'products_on_promo': promo.get('products_on_promo', ''),
            'display_quality': promo.get('display_quality', ''),
            'signage_visible': promo.get('signage_visible', ''),
            'price_visible': promo.get('price_visible', ''),
            'compliance_status': result.get('compliance_status', ''),
            'confidence': result.get('confidence', ''),
            'issues_count': len(result.get('issues', []))
        }

        return [row]

    def convert_fifo_to_csv(self, result: Dict[str, Any], image_name: str) -> List[Dict]:
        """Convert FIFO analysis result to CSV rows."""
        rows = []

        for product in result.get('products', []):
            row = {
                'image_name': image_name,
                'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
                'product_name': product.get('product_name', ''),
                'brand': product.get('brand', ''),
                'front_expiry_date': product.get('front_expiry_date', ''),
                'back_expiry_date': product.get('back_expiry_date', ''),
                'fifo_status': product.get('fifo_status', ''),
                'violation_details': product.get('violation_details', ''),
                'days_until_expiry': product.get('days_until_expiry_front', ''),
                'recommendation': product.get('recommendation', ''),
                'confidence': result.get('confidence', '')
            }
            rows.append(row)

        return rows

    def convert_to_csv_rows(self, result: Dict[str, Any], image_name: str) -> List[Dict]:
        """
        Convert analysis result to CSV rows based on capture type.

        Args:
            result: Analysis result
            image_name: Image filename

        Returns:
            List of row dictionaries
        """
        if 'error' in result:
            # Return error row
            return [{
                'image_name': image_name,
                'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
                'error': result.get('error_message', 'Unknown error')
            }]

        converters = {
            'waste': self.convert_waste_to_csv,
            'shelf': self.convert_shelf_to_csv,
            'promo': self.convert_promo_to_csv,
            'fifo': self.convert_fifo_to_csv
        }

        converter = converters.get(self.capture_type)
        if converter:
            return converter(result, image_name)
        else:
            # Generic conversion
            return [{
                'image_name': image_name,
                'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
                'capture_type': self.capture_type,
                'confidence': result.get('confidence', ''),
                'raw_json': json.dumps(result)
            }]

    def process_images(self) -> str:
        """
        Process all images and generate CSV report.

        Returns:
            Path to generated CSV file
        """
        images = self.find_images()

        if not images:
            print(f"No images found in {self.input_folder}/")
            print(f"Please add images to the folder and try again.")
            return None

        print(f"Found {len(images)} images to process")
        print(f"Capture type: {self.capture_type}")
        print()

        all_rows = []
        successful = 0
        failed = 0

        for i, image_path in enumerate(images, 1):
            print(f"[{i}/{len(images)}] Processing {image_path.name}...", end=" ")

            try:
                # Analyze image
                result = self.analyzer.analyze_image(
                    str(image_path),
                    capture_type=self.capture_type
                )

                if 'error' in result:
                    print(f"✗ Error: {result.get('error_message', 'Unknown')}")
                    failed += 1
                else:
                    print(f"✓ Done (confidence: {result.get('confidence', 0):.2f})")
                    successful += 1

                # Convert to CSV rows
                rows = self.convert_to_csv_rows(result, image_path.name)
                all_rows.extend(rows)

            except Exception as e:
                print(f"✗ Exception: {str(e)}")
                failed += 1
                all_rows.append({
                    'image_name': image_path.name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': str(e)
                })

        # Generate CSV filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{self.capture_type}_analysis_{timestamp}.csv"
        csv_path = self.output_folder / csv_filename

        # Write CSV
        if all_rows:
            # Get all unique keys from all rows
            fieldnames = set()
            for row in all_rows:
                fieldnames.update(row.keys())
            fieldnames = sorted(fieldnames)

            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_rows)

            print()
            print("=" * 60)
            print("PROCESSING COMPLETE")
            print("=" * 60)
            print(f"Total images: {len(images)}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            print()
            print(f"CSV Report saved to: {csv_path}")
            print()

            return str(csv_path)
        else:
            print("\nNo data to write to CSV")
            return None

    def generate_summary_csv(self) -> str:
        """
        Generate a summary CSV with one row per image.

        Returns:
            Path to summary CSV file
        """
        images = self.find_images()

        if not images:
            return None

        print(f"Generating summary CSV for {len(images)} images...")

        summary_rows = []

        for image_path in images:
            try:
                result = self.analyzer.analyze_image(
                    str(image_path),
                    capture_type=self.capture_type
                )

                summary_row = {
                    'image_name': image_path.name,
                    'timestamp': result.get('_metadata', {}).get('analysis_timestamp', ''),
                    'capture_type': self.capture_type,
                    'status': 'error' if 'error' in result else 'success',
                    'confidence': result.get('confidence', ''),
                }

                # Add type-specific summary
                if self.capture_type == 'waste':
                    summary_row['total_items'] = result.get('estimated_total_items', '')
                    summary_row['products_count'] = len(result.get('products', []))
                    summary_row['waste_reason'] = result.get('waste_reason', '')
                elif self.capture_type == 'shelf':
                    overview = result.get('shelf_overview', {})
                    summary_row['osa_percentage'] = overview.get('osa_percentage', '')
                    summary_row['empty_facings'] = overview.get('empty_facings', '')
                    summary_row['compliance_status'] = result.get('compliance_status', '')
                elif self.capture_type == 'fifo':
                    fifo = result.get('fifo_compliance', {})
                    summary_row['compliant'] = fifo.get('compliant', '')
                    summary_row['violations_found'] = fifo.get('violations_found', '')

                summary_rows.append(summary_row)

            except Exception as e:
                summary_rows.append({
                    'image_name': image_path.name,
                    'status': 'error',
                    'error': str(e)
                })

        # Save summary CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{self.capture_type}_summary_{timestamp}.csv"
        csv_path = self.output_folder / csv_filename

        if summary_rows:
            fieldnames = set()
            for row in summary_rows:
                fieldnames.update(row.keys())
            fieldnames = sorted(fieldnames)

            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_rows)

            print(f"Summary CSV saved to: {csv_path}")
            return str(csv_path)

        return None


def main():
    """Main entry point for batch processing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process images from input_images/ and save CSV reports to output_reports/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process waste images (default)
  python batch_processor.py

  # Process shelf images
  python batch_processor.py --type shelf

  # Process promotional images
  python batch_processor.py --type promo

  # Process FIFO compliance
  python batch_processor.py --type fifo

  # Custom folders
  python batch_processor.py --input my_images --output my_reports

  # Generate summary only
  python batch_processor.py --summary-only

Workflow:
  1. Drop your images in input_images/ folder
  2. Run: python batch_processor.py --type waste
  3. Find CSV report in output_reports/ folder
        """
    )

    parser.add_argument(
        '--type',
        choices=['waste', 'shelf', 'promo', 'fifo'],
        default='waste',
        help='Type of analysis to perform (default: waste)'
    )
    parser.add_argument(
        '--input',
        default='input_images',
        help='Input folder containing images (default: input_images)'
    )
    parser.add_argument(
        '--output',
        default='output_reports',
        help='Output folder for CSV reports (default: output_reports)'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Generate summary CSV only (one row per image)'
    )

    args = parser.parse_args()

    # Initialize processor
    processor = BatchProcessor(
        input_folder=args.input,
        output_folder=args.output,
        capture_type=args.type
    )

    # Process images
    if args.summary_only:
        csv_path = processor.generate_summary_csv()
    else:
        csv_path = processor.process_images()

    if csv_path:
        print(f"✓ Processing complete! Check: {csv_path}")
        return 0
    else:
        print("✗ No images processed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
