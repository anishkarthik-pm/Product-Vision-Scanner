# Test Images

Place your test images here for model validation.

## Structure

```
test_images/
├── Apple/
│   ├── apple1.jpg
│   ├── apple2.jpg
│   └── ...
├── Banana/
│   ├── banana1.jpg
│   └── ...
└── Orange/
    ├── orange1.jpg
    └── ...
```

## Usage

```bash
# Test model on this directory
python scripts/test_model.py --test-dir test_images/
```

## Guidelines

- Use clear, well-lit photos
- Center the fruit in frame
- Use JPEG or PNG format
- Minimum resolution: 224x224
- Organize by class name (folder = class label)
