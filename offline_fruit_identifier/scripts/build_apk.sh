#!/bin/bash

#
# Build Android APK for Fruit Identifier app
#
# This script:
# 1. Checks prerequisites
# 2. Copies model files to assets
# 3. Builds APK using Gradle
# 4. Outputs APK location
#

set -e  # Exit on error

echo "========================================"
echo "BUILDING FRUIT IDENTIFIER APK"
echo "========================================"

# Configuration
PROJECT_DIR="android_app/FruitIdentifier"
MODEL_FILE="model/output/tflite_models/model.tflite"
LABELS_FILE="model/output/labels.txt"
ASSETS_DIR="$PROJECT_DIR/app/src/main/assets"

# Check if running from correct directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Must run from offline_fruit_identifier/ directory"
    exit 1
fi

# Step 1: Check prerequisites
echo ""
echo "[1/5] Checking prerequisites..."

if [ ! -f "$MODEL_FILE" ]; then
    echo "✗ Model not found: $MODEL_FILE"
    echo ""
    echo "Please train and convert the model first:"
    echo "  cd model/"
    echo "  python train_model.py"
    echo "  python convert_to_tflite.py"
    exit 1
fi

if [ ! -f "$LABELS_FILE" ]; then
    echo "✗ Labels not found: $LABELS_FILE"
    exit 1
fi

echo "✓ Model found"
echo "✓ Labels found"

# Step 2: Create assets directory
echo ""
echo "[2/5] Setting up assets..."

mkdir -p "$ASSETS_DIR"

# Step 3: Copy model files
echo ""
echo "[3/5] Copying model files to assets..."

cp "$MODEL_FILE" "$ASSETS_DIR/model.tflite"
cp "$LABELS_FILE" "$ASSETS_DIR/labels.txt"

echo "✓ Copied model.tflite ($(du -h "$ASSETS_DIR/model.tflite" | cut -f1))"
echo "✓ Copied labels.txt"

# Step 4: Build APK
echo ""
echo "[4/5] Building APK with Gradle..."
echo "(This may take a few minutes...)"

cd "$PROJECT_DIR"

# Make gradlew executable
chmod +x ./gradlew

# Build release APK
./gradlew assembleRelease

cd ../..

# Step 5: Find and display APK location
echo ""
echo "[5/5] Finding APK..."

APK_PATH="$PROJECT_DIR/app/build/outputs/apk/release/app-release-unsigned.apk"

if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo ""
    echo "========================================"
    echo "✓ BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "APK Location:"
    echo "  $APK_PATH"
    echo ""
    echo "APK Size: $APK_SIZE"
    echo ""
    echo "Next steps:"
    echo "  1. Sign the APK (required for installation):"
    echo "     scripts/sign_apk.sh"
    echo ""
    echo "  2. Install on device:"
    echo "     adb install $APK_PATH"
    echo ""
    echo "  3. Or copy to device and install manually"
    echo "========================================"
else
    echo ""
    echo "✗ Build failed - APK not found"
    echo "Check the build output above for errors"
    exit 1
fi
