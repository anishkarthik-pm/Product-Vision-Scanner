"""
Test trained model accuracy on sample images.

This script:
1. Loads the TFLite model
2. Tests on sample images
3. Displays predictions
4. Measures inference time

Usage:
    python test_model.py --model output/tflite_models/model.tflite --image test_images/apple.jpg
    python test_model.py --test-dir test_images/ --benchmark
"""

import os
import sys
import argparse
import time
from pathlib import Path

import numpy as np
from PIL import Image
import tensorflow as tf


def load_labels(labels_path):
    """Load class labels from file."""
    with open(labels_path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def preprocess_image(image_path, input_size=224):
    """
    Preprocess image for model inference.

    Steps:
    1. Load image
    2. Resize to input_size x input_size
    3. Convert to RGB
    4. Normalize to [-1, 1]
    5. Add batch dimension
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize((input_size, input_size))
    img_array = np.array(img, dtype=np.float32)

    # Normalize to [-1, 1]
    img_array = (img_array / 127.5) - 1.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def run_inference(interpreter, image_array):
    """
    Run TFLite inference.

    Returns:
        predictions: Array of class probabilities
        inference_time: Time taken in milliseconds
    """
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], image_array)

    # Run inference
    start_time = time.time()
    interpreter.invoke()
    inference_time = (time.time() - start_time) * 1000

    # Get output
    output = interpreter.get_tensor(output_details[0]['index'])[0]

    return output, inference_time


def get_top_k_predictions(predictions, labels, k=5):
    """Get top-K predictions with labels."""
    top_k_indices = np.argsort(predictions)[-k:][::-1]

    results = []
    for idx in top_k_indices:
        results.append({
            'label': labels[idx] if idx < len(labels) else f'Class {idx}',
            'confidence': float(predictions[idx]),
            'index': int(idx)
        })

    return results


def test_single_image(model_path, labels_path, image_path):
    """Test model on a single image."""

    print("\n" + "=" * 60)
    print("TESTING SINGLE IMAGE")
    print("=" * 60)

    # Load model
    print(f"\nLoading model: {model_path}")
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Load labels
    labels = load_labels(labels_path)
    print(f"Loaded {len(labels)} labels")

    # Preprocess image
    print(f"\nPreprocessing image: {image_path}")
    image_array = preprocess_image(image_path)

    # Run inference
    print("Running inference...")
    predictions, inference_time = run_inference(interpreter, image_array)

    # Get top predictions
    results = get_top_k_predictions(predictions, labels)

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nInference time: {inference_time:.2f}ms\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['label']:<40} {result['confidence']*100:>6.2f}%")

    print("\n" + "=" * 60)


def test_directory(model_path, labels_path, test_dir):
    """Test model on all images in a directory."""

    print("\n" + "=" * 60)
    print("TESTING DIRECTORY")
    print("=" * 60)

    # Load model
    print(f"\nLoading model: {model_path}")
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Load labels
    labels = load_labels(labels_path)
    print(f"Loaded {len(labels)} labels")

    # Find all images
    test_dir = Path(test_dir)
    image_extensions = ['.jpg', '.jpeg', '.png']
    images = []

    for ext in image_extensions:
        images.extend(list(test_dir.rglob(f'*{ext}')))

    print(f"\nFound {len(images)} images")

    if len(images) == 0:
        print("No images found!")
        return

    # Test each image
    inference_times = []
    correct = 0
    total = 0

    for img_path in images:
        # Get true label from parent directory name
        true_label = img_path.parent.name

        # Preprocess and run inference
        image_array = preprocess_image(str(img_path))
        predictions, inference_time = run_inference(interpreter, image_array)
        inference_times.append(inference_time)

        # Get top prediction
        top_result = get_top_k_predictions(predictions, labels, k=1)[0]
        predicted_label = top_result['label']
        confidence = top_result['confidence']

        # Check if correct
        if predicted_label.lower() == true_label.lower():
            correct += 1
            status = "✓"
        else:
            status = "✗"

        total += 1

        print(f"{status} {img_path.name:<30} True: {true_label:<20} Pred: {predicted_label:<20} ({confidence*100:.1f}%)")

    # Summary
    accuracy = (correct / total) * 100 if total > 0 else 0
    avg_inference_time = np.mean(inference_times)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total images: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average inference time: {avg_inference_time:.2f}ms")
    print("=" * 60)


def benchmark_model(model_path, iterations=100):
    """Benchmark model performance."""

    print("\n" + "=" * 60)
    print("BENCHMARKING MODEL")
    print("=" * 60)

    # Load model
    print(f"\nLoading model: {model_path}")
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input details
    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']

    print(f"Input shape: {input_shape}")
    print(f"Iterations: {iterations}")

    # Create dummy input
    dummy_input = np.random.rand(*input_shape).astype(np.float32)

    # Warmup
    print("\nWarming up...")
    for _ in range(10):
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()

    # Benchmark
    print("Benchmarking...")
    times = []

    for i in range(iterations):
        start = time.time()
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()
        end = time.time()
        times.append((end - start) * 1000)

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{iterations}")

    # Results
    times = np.array(times)
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Average: {np.mean(times):.2f}ms")
    print(f"Median: {np.median(times):.2f}ms")
    print(f"Min: {np.min(times):.2f}ms")
    print(f"Max: {np.max(times):.2f}ms")
    print(f"Std Dev: {np.std(times):.2f}ms")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Test TFLite model')
    parser.add_argument('--model', type=str, default='output/tflite_models/model.tflite',
                        help='Path to TFLite model')
    parser.add_argument('--labels', type=str, default='output/labels.txt',
                        help='Path to labels file')
    parser.add_argument('--image', type=str, help='Path to single test image')
    parser.add_argument('--test-dir', type=str, help='Path to test images directory')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark')
    parser.add_argument('--iterations', type=int, default=100, help='Benchmark iterations')

    args = parser.parse_args()

    # Check model exists
    if not os.path.exists(args.model):
        print(f"Error: Model not found: {args.model}")
        print("\nPlease train and convert the model first:")
        print("  python train_model.py")
        print("  python convert_to_tflite.py")
        sys.exit(1)

    # Check labels exist
    if not os.path.exists(args.labels):
        print(f"Error: Labels not found: {args.labels}")
        sys.exit(1)

    # Run requested test
    if args.benchmark:
        benchmark_model(args.model, args.iterations)
    elif args.image:
        test_single_image(args.model, args.labels, args.image)
    elif args.test_dir:
        test_directory(args.model, args.labels, args.test_dir)
    else:
        print("Please specify --image, --test-dir, or --benchmark")
        parser.print_help()


if __name__ == "__main__":
    main()
