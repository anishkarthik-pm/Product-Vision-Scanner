# Quick Start Guide

Get up and running in 30 minutes with pre-trained models.

## For Complete Beginners

### What You Need

- Computer with Python 3.8+
- Android phone (Android 7.0+)
- 30 minutes of time

### Step-by-Step

#### 1. Download Pre-trained Model (Option 1)

**If you don't want to train from scratch:**

```bash
# Download pre-trained model (when available)
wget https://example.com/fruit_model.tflite -O model.tflite
wget https://example.com/labels.txt -O labels.txt
```

**Skip to step 3 (Android App)**

#### 2. Train Your Own Model (Option 2)

**If you want to train from scratch:**

```bash
# Install Python dependencies
cd model
pip install -r requirements.txt

# Download dataset
python download_dataset.py

# Train model (2-3 hours on GPU)
python train_model.py

# Convert to mobile format
python convert_to_tflite.py
```

**Result:** `output/tflite_models/model.tflite` and `output/labels.txt`

#### 3. Build Android App

```bash
# Go to project root
cd offline_fruit_identifier

# Copy model to Android assets
cp model/output/tflite_models/model.tflite \
   android_app/FruitIdentifier/app/src/main/assets/

cp model/output/labels.txt \
   android_app/FruitIdentifier/app/src/main/assets/

# Build APK
cd android_app/FruitIdentifier
./gradlew assembleRelease
```

**Result:** APK at `app/build/outputs/apk/release/app-release-unsigned.apk`

#### 4. Install on Phone

```bash
# Connect phone via USB (enable USB debugging)
adb install app/build/outputs/apk/release/app-release-unsigned.apk

# Or copy APK to phone and install manually
```

#### 5. Test the App!

1. Open "Fruit Identifier" app
2. Allow camera permission
3. Point at a fruit (apple, banana, orange)
4. See instant predictions!

---

## Using Pre-built APK

**If available, you can download pre-built APK:**

```bash
# Download APK
wget https://example.com/fruit-identifier.apk

# Install on phone
adb install fruit-identifier.apk
```

---

## Supported Fruits & Vegetables

The default model recognizes 131 classes including:

**Fruits:**
- Apples (multiple varieties)
- Bananas
- Oranges
- Grapes
- Strawberries
- Peaches
- Pears
- Plums
- And 50+ more...

**Vegetables:**
- Tomatoes
- Bell Peppers
- Cucumbers
- Carrots
- Onions
- And 20+ more...

---

## Expected Performance

| Device Type | Inference Time | Accuracy |
|-------------|---------------|----------|
| High-end (Pixel 6, S21) | ~50ms | 94-95% |
| Mid-range (Pixel 4a) | ~100ms | 94-95% |
| Budget (SD665) | ~150ms | 94-95% |

---

## Common Issues

**App crashes on startup:**
- Check that model.tflite is in assets folder
- Verify model file size (should be 3-4 MB)
- Check camera permission is granted

**Predictions are wrong:**
- Ensure good lighting
- Hold camera steady
- Point at center of fruit
- Try from different angles

**App is slow:**
- Close other apps
- Check GPU delegate is enabled
- Try INT8 quantized model

---

## What's Happening Under the Hood

```
┌─────────────────┐
│  Camera Feed    │  Your phone camera
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocess     │  Resize to 224x224, normalize
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MobileNetV2    │  CNN runs on your phone
│  (TFLite)       │  No internet needed!
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Top-5 Results  │  Apple Red (95%), Apple Granny (3%), ...
└─────────────────┘
```

**Privacy:** Everything runs on your device. No data is sent anywhere.

---

## Next Steps

### Customize the Model

**Add your own classes:**

1. Collect 100+ images per class
2. Organize in folders: `dataset/train/ClassName/`
3. Retrain: `python train_model.py --data-dir dataset/`

**Improve accuracy:**

- Add more training data
- Use data augmentation
- Fine-tune hyperparameters
- Try different architectures (EfficientNet, ResNet)

### Enhance the App

**Add features:**
- Multiple object detection (detect many fruits at once)
- Nutritional information database
- Voice announcements
- Save history of scans
- Export to CSV

**See example code in:**
- `docs/ENHANCEMENTS.md`
- `examples/multi_object_detection.py`
- `examples/nutrition_database.kt`

---

## Folder Structure

```
offline_fruit_identifier/
│
├── model/                       # Python training code
│   ├── train_model.py          # Train MobileNetV2
│   ├── convert_to_tflite.py   # Convert to mobile
│   ├── download_dataset.py     # Get Fruits-360
│   └── output/                 # Generated models
│       ├── model.tflite        # Mobile model
│       └── labels.txt          # Class names
│
├── android_app/                # Android application
│   └── FruitIdentifier/
│       ├── app/src/main/
│       │   ├── java/.../
│       │   │   ├── MainActivity.kt          # Camera + UI
│       │   │   ├── TFLiteClassifier.kt      # ML inference
│       │   │   └── ImageProcessor.kt        # Preprocessing
│       │   └── assets/
│       │       ├── model.tflite            # Copy here!
│       │       └── labels.txt              # Copy here!
│       └── app/build/outputs/apk/
│           └── release/
│               └── app-release-unsigned.apk  # Your APK!
│
├── scripts/                    # Utility scripts
│   ├── test_model.py          # Test accuracy
│   └── build_apk.sh           # Build automation
│
├── docs/                       # Documentation
│   ├── SETUP_GUIDE.md         # Complete setup
│   └── ANDROID_GUIDE.md       # Android details
│
└── README.md                   # Main documentation
```

---

## Troubleshooting

### Python Environment

```bash
# Check Python version
python --version  # Should be 3.8+

# Check TensorFlow
python -c "import tensorflow as tf; print(tf.__version__)"

# Reinstall if needed
pip install --upgrade tensorflow
```

### Android Build

```bash
# Clean build
cd android_app/FruitIdentifier
./gradlew clean
./gradlew assembleRelease

# Check model file
ls -lh app/src/main/assets/model.tflite  # Should be ~4MB
```

### Device Connection

```bash
# Check device connected
adb devices

# If empty, enable USB debugging:
# Settings → About Phone → Tap Build Number 7 times
# Settings → Developer Options → USB Debugging → ON
```

---

## Resources

**Documentation:**
- [Complete Setup Guide](docs/SETUP_GUIDE.md)
- [Training Guide](docs/TRAINING_GUIDE.md)
- [Android Guide](docs/ANDROID_GUIDE.md)

**External:**
- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [Android CameraX](https://developer.android.com/training/camerax)
- [MobileNet Architecture](https://arxiv.org/abs/1801.04381)

---

**Time to build:** ~30 minutes (excluding training)

**Cost:** $0 (all open source)

**Privacy:** 100% offline, no data collection

**Accuracy:** ~95% on common fruits/vegetables

---

Enjoy your offline fruit identifier! 🍎🍌🍊
