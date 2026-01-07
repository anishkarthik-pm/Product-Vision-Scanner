"""
Download and prepare Fruits-360 dataset for training.

This script downloads the dataset from Kaggle and organizes it
into train/validation/test splits.
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
import json

def download_fruits360():
    """
    Download Fruits-360 dataset from Kaggle.

    Prerequisites:
    1. Install kaggle: pip install kaggle
    2. Create Kaggle account and get API token
    3. Place kaggle.json in ~/.kaggle/

    Alternative: Manual download from
    https://www.kaggle.com/datasets/moltean/fruits
    """

    print("=" * 60)
    print("FRUITS-360 DATASET DOWNLOADER")
    print("=" * 60)

    # Check if dataset already exists
    if os.path.exists("fruits-360"):
        print("\n✓ Dataset folder already exists!")
        response = input("  Re-download? (y/n): ")
        if response.lower() != 'y':
            print("  Using existing dataset.")
            return
        else:
            print("  Removing old dataset...")
            shutil.rmtree("fruits-360")

    print("\n[1/4] Checking Kaggle credentials...")
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        print("\n⚠ Kaggle credentials not found!")
        print("\nTo download automatically:")
        print("1. Create a Kaggle account: https://www.kaggle.com")
        print("2. Go to Account Settings → API → Create New Token")
        print("3. Place kaggle.json in ~/.kaggle/")
        print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        print("\nAlternatively, download manually:")
        print("https://www.kaggle.com/datasets/moltean/fruits")
        print("Extract to: ./fruits-360/")
        sys.exit(1)

    print("✓ Kaggle credentials found")

    print("\n[2/4] Downloading dataset (this may take 10-15 minutes)...")
    try:
        os.system("kaggle datasets download -d moltean/fruits")
        print("✓ Download complete")
    except Exception as e:
        print(f"✗ Download failed: {e}")
        print("Try manual download from: https://www.kaggle.com/datasets/moltean/fruits")
        sys.exit(1)

    print("\n[3/4] Extracting dataset...")
    try:
        with zipfile.ZipFile("fruits.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove("fruits.zip")
        print("✓ Extraction complete")
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        sys.exit(1)

    print("\n[4/4] Organizing dataset structure...")
    organize_dataset()

    print("\n" + "=" * 60)
    print("✓ DATASET READY!")
    print("=" * 60)
    print_dataset_stats()


def organize_dataset():
    """Organize dataset into train/val/test splits."""

    # Expected structure after download
    train_dir = Path("fruits-360/Training")
    test_dir = Path("fruits-360/Test")

    if not train_dir.exists():
        print("✗ Training directory not found!")
        print(f"  Expected: {train_dir}")
        sys.exit(1)

    # Count classes and images
    train_classes = [d for d in train_dir.iterdir() if d.is_dir()]
    test_classes = [d for d in test_dir.iterdir() if d.is_dir()]

    print(f"  Found {len(train_classes)} classes in training")
    print(f"  Found {len(test_classes)} classes in testing")

    # Create validation split (10% of training data)
    val_dir = Path("fruits-360/Validation")
    if not val_dir.exists():
        print("  Creating validation split...")
        val_dir.mkdir(parents=True)

        import random
        random.seed(42)

        for class_dir in train_classes:
            class_name = class_dir.name
            images = list(class_dir.glob("*.jpg"))

            # Take 10% for validation
            n_val = max(1, len(images) // 10)
            val_images = random.sample(images, n_val)

            # Create validation class directory
            val_class_dir = val_dir / class_name
            val_class_dir.mkdir(parents=True, exist_ok=True)

            # Move images
            for img in val_images:
                shutil.copy(img, val_class_dir / img.name)

        print("  ✓ Validation split created")

    print("✓ Dataset organized")


def print_dataset_stats():
    """Print dataset statistics."""

    train_dir = Path("fruits-360/Training")
    val_dir = Path("fruits-360/Validation")
    test_dir = Path("fruits-360/Test")

    def count_images(directory):
        return len(list(directory.rglob("*.jpg")))

    def count_classes(directory):
        return len([d for d in directory.iterdir() if d.is_dir()])

    print("\nDataset Statistics:")
    print(f"  Training:   {count_images(train_dir):,} images, {count_classes(train_dir)} classes")

    if val_dir.exists():
        print(f"  Validation: {count_images(val_dir):,} images, {count_classes(val_dir)} classes")

    print(f"  Testing:    {count_images(test_dir):,} images, {count_classes(test_dir)} classes")

    # Save class names
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    with open("class_labels.txt", "w") as f:
        f.write("\n".join(classes))

    print(f"\n✓ Class labels saved to: class_labels.txt")
    print(f"  Total classes: {len(classes)}")

    # Save metadata
    metadata = {
        "dataset": "Fruits-360",
        "num_classes": len(classes),
        "train_images": count_images(train_dir),
        "val_images": count_images(val_dir) if val_dir.exists() else 0,
        "test_images": count_images(test_dir),
        "image_size": "100x100",
        "classes": classes[:10] + ["..."] if len(classes) > 10 else classes
    }

    with open("dataset_info.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("✓ Dataset info saved to: dataset_info.json")


def verify_dataset():
    """Verify dataset structure and integrity."""

    print("\n" + "=" * 60)
    print("VERIFYING DATASET")
    print("=" * 60)

    required_dirs = [
        "fruits-360/Training",
        "fruits-360/Test"
    ]

    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} NOT FOUND")
            all_good = False

    if all_good:
        print("\n✓ Dataset verification passed!")
        return True
    else:
        print("\n✗ Dataset verification failed!")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FRUITS-360 DATASET SETUP")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Download Fruits-360 dataset from Kaggle (~500MB)")
    print("  2. Extract and organize files")
    print("  3. Create train/validation/test splits")
    print("  4. Generate class labels file")
    print("\nEstimated time: 10-15 minutes")
    print("=" * 60)

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    download_fruits360()

    if verify_dataset():
        print("\n✓ Setup complete! Ready for training.")
        print("\nNext step:")
        print("  python train_model.py")
    else:
        print("\n✗ Setup incomplete. Please check errors above.")
        sys.exit(1)
