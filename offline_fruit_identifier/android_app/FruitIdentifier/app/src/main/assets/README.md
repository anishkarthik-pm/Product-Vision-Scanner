# Assets Folder

Place your model files here before building the APK.

## Required Files

1. **model.tflite** - TensorFlow Lite model (~4MB)
   - Source: `model/output/tflite_models/model.tflite`
   - Copy command: `cp ../../model/output/tflite_models/model.tflite .`

2. **labels.txt** - Class labels file
   - Source: `model/output/labels.txt`
   - Copy command: `cp ../../model/output/labels.txt .`

## Verification

Before building APK, verify files exist:

```bash
ls -lh model.tflite  # Should show ~4MB
ls -lh labels.txt    # Should show 131 lines
```

## Build Process

The build script will automatically copy these files:

```bash
cd ../../..
./scripts/build_apk.sh
```

## Notes

- Files are excluded from git (too large)
- Must be copied after training/conversion
- App will crash if files are missing
