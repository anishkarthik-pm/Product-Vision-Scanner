# Complete Setup Guide

This guide walks you through setting up the entire offline fruit identification system from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Model Training](#model-training)
4. [Android App Setup](#android-app-setup)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

**For Training:**
- 8GB+ RAM (16GB recommended)
- 50GB+ free disk space
- GPU optional but recommended (speeds up training 10x)

**For Android:**
- Android device with API 24+ (Android 7.0+)
- Camera
- 2GB+ RAM

### Software Requirements

**For Training:**
- Python 3.8+
- pip
- virtualenv (recommended)
- Git

**For Android:**
- Android Studio Arctic Fox or later
- JDK 17
- Android SDK (API 24-34)
- Gradle 8.0+

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd offline_fruit_identifier
```

### 2. Python Environment

Create and activate virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

Install dependencies:

```bash
cd model
pip install -r requirements.txt
```

Verify installation:

```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

Should output: `2.14.0` or similar

### 3. Kaggle API Setup (for dataset)

Create Kaggle account:
1. Go to https://www.kaggle.com
2. Create account
3. Go to Account Settings → API
4. Click "Create New Token"
5. Download `kaggle.json`

Install credentials:

```bash
# Linux/Mac
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Windows
mkdir %USERPROFILE%\.kaggle
copy Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

---

## Model Training

### Step 1: Download Dataset

```bash
cd model
python download_dataset.py
```

This downloads Fruits-360 dataset (~500MB).

**Expected output:**
```
[1/4] Checking Kaggle credentials...
✓ Kaggle credentials found

[2/4] Downloading dataset...
✓ Download complete

[3/4] Extracting dataset...
✓ Extraction complete

[4/4] Organizing dataset...
✓ Dataset organized

Dataset Statistics:
  Training:   50,000+ images, 131 classes
  Validation: 5,000+ images, 131 classes
  Testing:    15,000+ images, 131 classes
```

### Step 2: Train Model

```bash
python train_model.py
```

**Training time:**
- GPU: 2-3 hours
- CPU: 8-10 hours

**What happens:**
1. Loads dataset
2. Creates data augmentation pipeline
3. Builds MobileNetV2 model
4. Trains in two stages (frozen base, then fine-tuning)
5. Evaluates on test set
6. Saves model and metrics

**Output files:**
- `output/fruit_vegetable_classifier.h5` - Full model
- `output/best_model.h5` - Best checkpoint
- `output/labels.txt` - Class labels
- `output/training_metadata.json` - Training stats
- `output/training_curves.png` - Accuracy/loss plots

### Step 3: Convert to TFLite

```bash
python convert_to_tflite.py
```

**Conversion time:** 5-10 minutes

**What happens:**
1. Loads trained model
2. Converts to TFLite FLOAT32
3. Converts to TFLite FLOAT16
4. Converts to TFLite INT8 (with quantization)
5. Tests each model's accuracy
6. Generates comparison report

**Output files:**
- `output/tflite_models/model.tflite` - Recommended model
- `output/tflite_models/model_float32.tflite` - Baseline
- `output/tflite_models/model_float16.tflite` - Half precision
- `output/tflite_models/model_int8.tflite` - Quantized
- `output/tflite_models/conversion_results.json` - Comparison

**Expected results:**
```
MODEL COMPARISON
Model Type               Size (MB)    Top-1 Acc    Top-5 Acc
------------------------------------------------------------
FLOAT32 (baseline)       14.23        95.2%        99.1%
FLOAT16                  7.12         95.0%        99.0%
Dynamic Range INT8       3.95         94.8%        98.9%
Full INT8                3.87         93.8%        98.7%

Recommended: Dynamic Range (best balance)
```

---

## Android App Setup

### Step 1: Install Android Studio

Download from: https://developer.android.com/studio

Install with default options.

### Step 2: Configure SDK

1. Open Android Studio
2. Go to Tools → SDK Manager
3. Install:
   - Android 7.0 (API 24)
   - Android 14 (API 34)
   - Android SDK Build-Tools 34
   - Android SDK Platform-Tools

### Step 3: Import Project

1. Open Android Studio
2. File → Open
3. Navigate to `offline_fruit_identifier/android_app/FruitIdentifier`
4. Click OK

Android Studio will:
- Download Gradle dependencies
- Sync project
- Index files

This takes 5-10 minutes on first run.

### Step 4: Copy Model Files

```bash
cd offline_fruit_identifier

# Copy model
cp model/output/tflite_models/model.tflite \
   android_app/FruitIdentifier/app/src/main/assets/

# Copy labels
cp model/output/labels.txt \
   android_app/FruitIdentifier/app/src/main/assets/
```

Verify in Android Studio:
- Project view → app → src → main → assets
- Should see: `model.tflite` and `labels.txt`

### Step 5: Build APK

**Option A: Android Studio GUI**

1. Build → Build Bundle(s) / APK(s) → Build APK(s)
2. Wait for build (5-10 minutes first time)
3. Click "locate" in notification
4. Find APK at: `app/build/outputs/apk/release/app-release-unsigned.apk`

**Option B: Command Line**

```bash
cd android_app/FruitIdentifier
./gradlew assembleRelease
```

APK location: `app/build/outputs/apk/release/app-release-unsigned.apk`

### Step 6: Install on Device

**Via USB:**

```bash
# Enable USB debugging on phone (Settings → Developer Options)
adb install app/build/outputs/apk/release/app-release-unsigned.apk
```

**Manual Installation:**

1. Copy APK to phone
2. Open file manager
3. Tap APK
4. Allow installation from unknown sources
5. Install

---

## Testing

### Test Model on Desktop

```bash
cd model

# Test single image
python ../scripts/test_model.py --image test_images/apple.jpg

# Test entire directory
python ../scripts/test_model.py --test-dir ../test_images/

# Benchmark performance
python ../scripts/test_model.py --benchmark --iterations 100
```

### Test Android App

1. Open app on phone
2. Allow camera permission
3. Point camera at fruit/vegetable
4. Check predictions appear within 500ms
5. Try different angles and lighting

**Good test subjects:**
- Apples (red, green)
- Bananas
- Oranges
- Tomatoes
- Bell peppers

---

## Troubleshooting

### Python Issues

**Issue: TensorFlow won't install**
```bash
# Try specific version
pip install tensorflow==2.14.0

# Or use conda
conda install tensorflow
```

**Issue: Out of memory during training**
```python
# Reduce batch size in train_model.py
Config.BATCH_SIZE = 16  # Instead of 32
```

**Issue: Kaggle API error**
```bash
# Verify credentials
cat ~/.kaggle/kaggle.json

# Reinstall kaggle
pip install --upgrade kaggle
```

### Android Issues

**Issue: Gradle sync failed**
- File → Invalidate Caches → Invalidate and Restart
- Delete `.gradle` folder and re-sync

**Issue: Model not found**
- Verify `model.tflite` is in `app/src/main/assets/`
- Clean project: Build → Clean Project
- Rebuild: Build → Rebuild Project

**Issue: App crashes on launch**
- Check Logcat for errors
- Verify camera permission in manifest
- Check model file size (should be 3-4 MB)

**Issue: Slow inference (>500ms)**
- GPU delegate may not be working
- Check device compatibility
- Try disabling GPU: `useGpu = false` in MainActivity

**Issue: Poor accuracy**
- Check lighting (need bright, even light)
- Hold camera steady
- Ensure fruit is in focus
- Try fruits from training set

---

## Next Steps

✅ **System is running!**

Now you can:

1. **Customize the model:**
   - Add your own fruit/vegetable classes
   - Retrain with custom dataset
   - Fine-tune for specific use case

2. **Enhance the app:**
   - Add multiple object detection
   - Show nutritional information
   - Add voice feedback
   - Save identification history

3. **Optimize performance:**
   - Enable GPU delegate
   - Use INT8 quantization
   - Reduce model size further

4. **Deploy to production:**
   - Sign APK properly
   - Publish to Play Store
   - Add analytics
   - Implement updates

---

## Resources

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [CameraX Documentation](https://developer.android.com/training/camerax)
- [Fruits-360 Dataset](https://www.kaggle.com/moltean/fruits)
- [MobileNet Paper](https://arxiv.org/abs/1801.04381)

---

**Need help? Check the issue tracker or documentation.**
