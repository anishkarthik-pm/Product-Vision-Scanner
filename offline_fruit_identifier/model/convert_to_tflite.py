"""
Convert trained Keras model to TensorFlow Lite format for mobile deployment.

This script:
1. Loads the trained .h5 model
2. Converts to TFLite format
3. Applies quantization (INT8, FP16)
4. Compares model sizes and accuracy
5. Saves optimized models

Usage:
    python convert_to_tflite.py
    python convert_to_tflite.py --model output/fruit_vegetable_classifier.h5
"""

import os
import sys
import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Conversion configuration"""

    INPUT_MODEL = "output/fruit_vegetable_classifier.h5"
    OUTPUT_DIR = "output/tflite_models"
    TEST_DIR = "fruits-360/Test"
    IMAGE_SIZE = 224
    NUM_CALIBRATION_IMAGES = 100


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model(model_path):
    """Load trained Keras model."""

    print("\n" + "=" * 60)
    print("LOADING MODEL")
    print("=" * 60)

    if not os.path.exists(model_path):
        print(f"✗ Model not found: {model_path}")
        print("\nPlease train the model first:")
        print("  python train_model.py")
        sys.exit(1)

    model = keras.models.load_model(model_path)

    print(f"✓ Model loaded: {model_path}")
    print(f"  Input shape: {model.input_shape}")
    print(f"  Output shape: {model.output_shape}")
    print(f"  Parameters: {model.count_params():,}")

    return model


# ============================================================================
# REPRESENTATIVE DATASET (for INT8 quantization)
# ============================================================================

def representative_dataset_gen():
    """
    Generator function for calibration dataset.

    INT8 quantization requires representative data to determine
    optimal quantization parameters (scale/zero-point).

    We use a subset of test images for calibration.
    """

    test_images_dir = Path(Config.TEST_DIR)

    if not test_images_dir.exists():
        print(f"⚠ Test directory not found: {Config.TEST_DIR}")
        print("  Skipping INT8 quantization")
        return

    # Collect image paths
    image_paths = list(test_images_dir.rglob("*.jpg"))[:Config.NUM_CALIBRATION_IMAGES]

    print(f"\n✓ Using {len(image_paths)} calibration images")

    for i, img_path in enumerate(image_paths):
        # Load and preprocess image
        img = keras.preprocessing.image.load_img(
            img_path,
            target_size=(Config.IMAGE_SIZE, Config.IMAGE_SIZE)
        )
        img_array = keras.preprocessing.image.img_to_array(img)

        # Normalize to [-1, 1] (same as training)
        img_array = (img_array / 127.5) - 1.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

        yield [img_array]


# ============================================================================
# CONVERSION FUNCTIONS
# ============================================================================

def convert_to_tflite_float32(model, output_path):
    """
    Convert to TFLite with FLOAT32 precision (baseline).

    This is the standard conversion with no optimization.
    Largest size, highest accuracy.
    """

    print("\n" + "=" * 60)
    print("CONVERTING TO TFLITE (FLOAT32)")
    print("=" * 60)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # No optimization
    tflite_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    size_mb = len(tflite_model) / (1024 * 1024)
    print(f"✓ Model saved: {output_path}")
    print(f"  Size: {size_mb:.2f} MB")

    return tflite_model, size_mb


def convert_to_tflite_float16(model, output_path):
    """
    Convert to TFLite with FLOAT16 precision.

    Benefits:
    - 50% size reduction
    - Minimal accuracy loss (<0.1%)
    - Hardware acceleration on modern GPUs
    """

    print("\n" + "=" * 60)
    print("CONVERTING TO TFLITE (FLOAT16)")
    print("=" * 60)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Enable FP16 quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]

    tflite_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    size_mb = len(tflite_model) / (1024 * 1024)
    print(f"✓ Model saved: {output_path}")
    print(f"  Size: {size_mb:.2f} MB")

    return tflite_model, size_mb


def convert_to_tflite_int8(model, output_path):
    """
    Convert to TFLite with INT8 quantization.

    Benefits:
    - 75% size reduction
    - 2-3x inference speedup
    - Runs on integer-only hardware (Edge TPU)
    - Small accuracy loss (~1-2%)

    Requires representative dataset for calibration.
    """

    print("\n" + "=" * 60)
    print("CONVERTING TO TFLITE (INT8)")
    print("=" * 60)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Enable INT8 quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Provide representative dataset
    converter.representative_dataset = representative_dataset_gen

    # Enforce full integer quantization
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    try:
        tflite_model = converter.convert()

        # Save
        with open(output_path, 'wb') as f:
            f.write(tflite_model)

        size_mb = len(tflite_model) / (1024 * 1024)
        print(f"✓ Model saved: {output_path}")
        print(f"  Size: {size_mb:.2f} MB")

        return tflite_model, size_mb

    except Exception as e:
        print(f"⚠ INT8 conversion failed: {e}")
        print("  This may happen if test images are not available")
        return None, 0


def convert_to_tflite_dynamic_range(model, output_path):
    """
    Convert to TFLite with dynamic range quantization.

    This is a simpler quantization that doesn't require
    calibration data. Good balance between size and accuracy.
    """

    print("\n" + "=" * 60)
    print("CONVERTING TO TFLITE (DYNAMIC RANGE QUANTIZATION)")
    print("=" * 60)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Enable dynamic range quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    size_mb = len(tflite_model) / (1024 * 1024)
    print(f"✓ Model saved: {output_path}")
    print(f"  Size: {size_mb:.2f} MB")

    return tflite_model, size_mb


# ============================================================================
# MODEL TESTING
# ============================================================================

def test_tflite_model(model_path, num_test_images=100):
    """
    Test TFLite model accuracy on test set.

    Loads model, runs inference on test images,
    and computes top-1 and top-5 accuracy.
    """

    print(f"\n  Testing accuracy...")

    # Load interpreter
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Check if model uses INT8
    is_int8 = input_details[0]['dtype'] == np.int8

    # Load test images
    test_images_dir = Path(Config.TEST_DIR)
    if not test_images_dir.exists():
        print("  ⚠ Test directory not found, skipping accuracy test")
        return None, None

    # Get class folders
    class_folders = sorted([d for d in test_images_dir.iterdir() if d.is_dir()])
    class_to_idx = {folder.name: idx for idx, folder in enumerate(class_folders)}

    # Collect test images
    test_data = []
    for class_folder in class_folders:
        images = list(class_folder.glob("*.jpg"))[:num_test_images // len(class_folders)]
        for img_path in images:
            test_data.append((img_path, class_to_idx[class_folder.name]))

    if len(test_data) == 0:
        print("  ⚠ No test images found")
        return None, None

    # Run inference
    correct_top1 = 0
    correct_top5 = 0

    for img_path, true_label in test_data:
        # Load and preprocess
        img = keras.preprocessing.image.load_img(
            img_path,
            target_size=(Config.IMAGE_SIZE, Config.IMAGE_SIZE)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = (img_array / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

        # Quantize input if INT8 model
        if is_int8:
            input_scale, input_zero_point = input_details[0]['quantization']
            img_array = img_array / input_scale + input_zero_point
            img_array = img_array.astype(np.int8)

        # Run inference
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])[0]

        # Dequantize output if INT8 model
        if is_int8:
            output_scale, output_zero_point = output_details[0]['quantization']
            output = (output.astype(np.float32) - output_zero_point) * output_scale

        # Get predictions
        top5_indices = np.argsort(output)[-5:][::-1]

        if top5_indices[0] == true_label:
            correct_top1 += 1
        if true_label in top5_indices:
            correct_top5 += 1

    top1_accuracy = correct_top1 / len(test_data)
    top5_accuracy = correct_top5 / len(test_data)

    print(f"  ✓ Top-1 Accuracy: {top1_accuracy:.4f} ({top1_accuracy*100:.2f}%)")
    print(f"  ✓ Top-5 Accuracy: {top5_accuracy:.4f} ({top5_accuracy*100:.2f}%)")

    return top1_accuracy, top5_accuracy


# ============================================================================
# COMPARISON TABLE
# ============================================================================

def print_comparison_table(results):
    """Print comparison table of all converted models."""

    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    print(f"\n{'Model Type':<25} {'Size (MB)':<12} {'Top-1 Acc':<12} {'Top-5 Acc':<12}")
    print("-" * 60)

    for model_type, data in results.items():
        size = f"{data['size_mb']:.2f}" if data['size_mb'] else "N/A"
        top1 = f"{data['top1_accuracy']*100:.2f}%" if data['top1_accuracy'] else "N/A"
        top5 = f"{data['top5_accuracy']*100:.2f}%" if data['top5_accuracy'] else "N/A"

        print(f"{model_type:<25} {size:<12} {top1:<12} {top5:<12}")

    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    print("\n📱 For Android App:")
    print("  → Use INT8 or Dynamic Range quantization")
    print("  → Best balance of size, speed, and accuracy")
    print("  → Recommended: Dynamic Range (easiest to implement)")

    print("\n⚡ For Maximum Speed:")
    print("  → Use INT8 quantization")
    print("  → Requires GPU delegate or Edge TPU")
    print("  → 2-3x faster inference")

    print("\n🎯 For Maximum Accuracy:")
    print("  → Use FLOAT32 or FLOAT16")
    print("  → Minimal accuracy loss")
    print("  → Larger model size")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main conversion pipeline."""

    parser = argparse.ArgumentParser(description='Convert model to TFLite')
    parser.add_argument('--model', type=str, default=Config.INPUT_MODEL, help='Input model path')
    parser.add_argument('--output-dir', type=str, default=Config.OUTPUT_DIR, help='Output directory')
    parser.add_argument('--skip-tests', action='store_true', help='Skip accuracy testing')
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("TENSORFLOW LITE CONVERSION")
    print("=" * 60)
    print(f"  TensorFlow version: {tf.__version__}")
    print(f"  Input model: {args.model}")
    print(f"  Output directory: {args.output_dir}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Load model
    model = load_model(args.model)

    # Convert to different formats
    results = {}

    # 1. FLOAT32
    float32_path = os.path.join(args.output_dir, "model_float32.tflite")
    float32_model, float32_size = convert_to_tflite_float32(model, float32_path)

    if not args.skip_tests:
        top1, top5 = test_tflite_model(float32_path)
    else:
        top1, top5 = None, None

    results['FLOAT32 (baseline)'] = {
        'size_mb': float32_size,
        'top1_accuracy': top1,
        'top5_accuracy': top5,
        'path': float32_path
    }

    # 2. FLOAT16
    float16_path = os.path.join(args.output_dir, "model_float16.tflite")
    float16_model, float16_size = convert_to_tflite_float16(model, float16_path)

    if not args.skip_tests:
        top1, top5 = test_tflite_model(float16_path)
    else:
        top1, top5 = None, None

    results['FLOAT16'] = {
        'size_mb': float16_size,
        'top1_accuracy': top1,
        'top5_accuracy': top5,
        'path': float16_path
    }

    # 3. Dynamic Range Quantization
    dynamic_path = os.path.join(args.output_dir, "model_dynamic.tflite")
    dynamic_model, dynamic_size = convert_to_tflite_dynamic_range(model, dynamic_path)

    if not args.skip_tests:
        top1, top5 = test_tflite_model(dynamic_path)
    else:
        top1, top5 = None, None

    results['Dynamic Range INT8'] = {
        'size_mb': dynamic_size,
        'top1_accuracy': top1,
        'top5_accuracy': top5,
        'path': dynamic_path
    }

    # 4. Full INT8
    int8_path = os.path.join(args.output_dir, "model_int8.tflite")
    int8_model, int8_size = convert_to_tflite_int8(model, int8_path)

    if int8_model and not args.skip_tests:
        top1, top5 = test_tflite_model(int8_path)
    else:
        top1, top5 = None, None

    results['Full INT8'] = {
        'size_mb': int8_size,
        'top1_accuracy': top1,
        'top5_accuracy': top5,
        'path': int8_path
    }

    # Print comparison
    print_comparison_table(results)

    # Save results
    results_path = os.path.join(args.output_dir, "conversion_results.json")
    with open(results_path, 'w') as f:
        # Convert to serializable format
        serializable_results = {}
        for k, v in results.items():
            serializable_results[k] = {
                'size_mb': float(v['size_mb']) if v['size_mb'] else None,
                'top1_accuracy': float(v['top1_accuracy']) if v['top1_accuracy'] else None,
                'top5_accuracy': float(v['top5_accuracy']) if v['top5_accuracy'] else None,
                'path': v['path']
            }
        json.dump(serializable_results, f, indent=2)

    print(f"\n✓ Results saved: {results_path}")

    # Copy recommended model
    recommended_model = dynamic_path
    final_path = os.path.join(args.output_dir, "model.tflite")
    import shutil
    shutil.copy(recommended_model, final_path)

    print(f"\n✓ Recommended model copied to: {final_path}")
    print("\n" + "=" * 60)
    print("✓ CONVERSION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Copy {final_path} to Android app assets/")
    print("  2. Copy labels.txt to Android app assets/")
    print("  3. Build Android app")
    print("=" * 60)


if __name__ == "__main__":
    main()
