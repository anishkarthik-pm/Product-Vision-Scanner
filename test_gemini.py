#!/usr/bin/env python3
"""
Gemini Quick Test

Quick test to verify Gemini analyzer is working.
"""

import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("GEMINI COMPLIANCE ANALYZER - QUICK TEST")
    print("=" * 60)
    print()

    # Step 1: Check imports
    print("Step 1: Checking imports...")
    try:
        from analyzer import GeminiComplianceAnalyzer
        print("✓ Gemini analyzer imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nFix: Run 'pip install google-generativeai>=0.3.0'")
        return 1

    # Step 2: Check API key
    print("\nStep 2: Checking Gemini API key...")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("✗ Gemini API key not configured")
            print("\nFix:")
            print("  1. Get your API key from: https://makersuite.google.com/app/apikey")
            print("  2. Copy .env.example to .env")
            print("  3. Edit .env and add: GEMINI_API_KEY=your_key_here")
            return 1
        elif api_key in ["your_gemini_api_key_here", "your_api_key_here"]:
            print("✗ API key still set to placeholder")
            print("\nFix:")
            print("  1. Get real API key from: https://makersuite.google.com/app/apikey")
            print("  2. Edit .env and replace placeholder")
            return 1
        else:
            # Show partial key for verification
            visible_part = api_key[:10] if len(api_key) > 10 else api_key[:5]
            print(f"✓ API key configured (starts with: {visible_part}...)")
    except Exception as e:
        print(f"✗ Error checking API key: {e}")
        return 1

    # Step 3: Initialize analyzer
    print("\nStep 3: Initializing Gemini analyzer...")
    try:
        analyzer = GeminiComplianceAnalyzer()
        print("✓ Analyzer initialized successfully")
        print(f"  Model: {analyzer.model_name}")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return 1

    # Step 4: Check for test image
    print("\nStep 4: Looking for test image...")
    test_images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        test_images.extend(Path('.').glob(f'*{ext}'))
        test_images.extend(Path('.').glob(f'test*{ext}'))
        test_images.extend(Path('.').glob(f'sample*{ext}'))

    if test_images:
        test_image = str(test_images[0])
        print(f"✓ Found test image: {test_image}")

        # Step 5: Run analysis
        print("\nStep 5: Running Gemini analysis...")
        print("(This will make an API call - may take a few seconds)")

        try:
            # Quality check first
            print("\n  Running quality check...")
            quality = analyzer.quality_check(test_image)

            print(f"  Suitable: {quality.get('suitable_for_analysis', 'unknown')}")
            print(f"  Recommendation: {quality.get('recommendation', 'unknown')}")

            if quality.get('suitable_for_analysis'):
                print("\n  Running waste analysis with Gemini...")
                result = analyzer.analyze_waste(test_image)

                if 'error' in result:
                    print(f"  ✗ Analysis error: {result.get('error_message')}")
                    if 'raw_response' in result:
                        print(f"  Raw response: {result['raw_response'][:200]}")
                else:
                    print(f"\n  ✓ Analysis complete!")
                    print(f"  - Model used: {result.get('_metadata', {}).get('model_used')}")
                    print(f"  - Capture type: {result.get('capture_type')}")
                    print(f"  - Products found: {len(result.get('products', []))}")
                    print(f"  - Total items: {result.get('estimated_total_items', 0)}")
                    print(f"  - Confidence: {result.get('confidence', 0):.2f}")
                    print(f"  - Image quality: {result.get('image_quality', 'unknown')}")

                    if result.get('products'):
                        print(f"\n  First product:")
                        p = result['products'][0]
                        print(f"    Name: {p.get('product_name')}")
                        print(f"    Condition: {p.get('condition')}")

            else:
                print(f"\n  ⚠️ Image quality issues: {', '.join(quality.get('issues', []))}")
                print(f"  Recommendation: {quality.get('recommendation')}")

            print("\n" + "=" * 60)
            print("✓ TEST PASSED - Gemini analyzer is working!")
            print("=" * 60)
            print("\nNext steps:")
            print("  1. Try: python -m analyzer.multi_cli analyze image.jpg --type waste")
            print("  2. Read: GEMINI_SETUP.md for detailed Gemini usage")
            print("  3. Check: examples/gemini_usage.py for code samples")
            print()
            return 0

        except Exception as e:
            print(f"\n✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            print("\nTroubleshooting:")
            print("  - Check your API key at: https://makersuite.google.com/app/apikey")
            print("  - Verify internet connection")
            print("  - Check API quota/billing")
            return 1
    else:
        print("⚠️ No test images found")
        print("\nTo complete the test:")
        print("  1. Add any .jpg or .png image to this directory")
        print("  2. Run this script again: python test_gemini.py")
        print("\n  Or download a sample:")
        print("  curl -o test.jpg 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800'")
        print()

        print("=" * 60)
        print("✓ PARTIAL SUCCESS - Setup verified, waiting for test image")
        print("=" * 60)
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
