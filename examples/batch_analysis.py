"""
Batch analysis example

Analyze multiple images and generate a consolidated report.
"""

import json
from pathlib import Path
from analyzer import RetailComplianceAnalyzer

def analyze_batch(image_dir: str, output_dir: str):
    """
    Analyze all images in a directory and save individual reports.

    Args:
        image_dir: Directory containing images
        output_dir: Directory to save reports
    """
    analyzer = RetailComplianceAnalyzer()

    image_path = Path(image_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Supported image formats
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Find all images
    images = [
        f for f in image_path.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    if not images:
        print(f"No images found in {image_dir}")
        return

    print(f"Found {len(images)} images to analyze\n")

    # Analyze each image
    results = []
    for i, image_file in enumerate(images, 1):
        print(f"[{i}/{len(images)}] Analyzing {image_file.name}...")

        try:
            result = analyzer.analyze_image(str(image_file))

            # Save individual report
            report_file = output_path / f"{image_file.stem}_report.json"
            with open(report_file, "w") as f:
                json.dump(result, f, indent=2)

            results.append({
                "image": image_file.name,
                "status": result["analysis_status"],
                "products": result["overall_compliance"]["total_products"],
                "violations": result["overall_compliance"]["violation_count"]
            })

            print(f"  ✓ Complete - {result['overall_compliance']['total_products']} products, "
                  f"{result['overall_compliance']['violation_count']} violations")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({
                "image": image_file.name,
                "status": "error",
                "error": str(e)
            })

    # Save summary report
    summary_file = output_path / "batch_summary.json"
    with open(summary_file, "w") as f:
        json.dump({
            "total_images": len(images),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }, f, indent=2)

    print(f"\nBatch analysis complete!")
    print(f"Reports saved to: {output_dir}")
    print(f"Summary: {summary_file}")

def main():
    # Example usage
    image_directory = "store_images"  # Directory with your images
    output_directory = "reports"      # Where to save reports

    analyze_batch(image_directory, output_directory)

if __name__ == "__main__":
    main()
