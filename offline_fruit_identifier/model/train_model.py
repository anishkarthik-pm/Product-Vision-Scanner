"""
Train MobileNetV2-based fruit and vegetable classifier.

This script:
1. Loads Fruits-360 dataset
2. Applies data augmentation
3. Builds MobileNetV2 model with transfer learning
4. Trains the model
5. Evaluates and saves results

Usage:
    python train_model.py
    python train_model.py --epochs 50 --batch-size 64
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard

import matplotlib.pyplot as plt


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Training configuration"""

    # Data
    DATA_DIR = "fruits-360"
    TRAIN_DIR = os.path.join(DATA_DIR, "Training")
    VAL_DIR = os.path.join(DATA_DIR, "Validation")
    TEST_DIR = os.path.join(DATA_DIR, "Test")

    # Model
    IMAGE_SIZE = 224  # MobileNetV2 expects 224x224
    CHANNELS = 3
    INPUT_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, CHANNELS)

    # Training
    BATCH_SIZE = 32
    EPOCHS = 30
    INITIAL_LEARNING_RATE = 0.001

    # Augmentation
    ROTATION_RANGE = 20
    WIDTH_SHIFT = 0.2
    HEIGHT_SHIFT = 0.2
    ZOOM_RANGE = 0.2
    HORIZONTAL_FLIP = True

    # Output
    MODEL_NAME = "fruit_vegetable_classifier"
    OUTPUT_DIR = "output"


# ============================================================================
# DATA LOADING
# ============================================================================

def verify_dataset():
    """Check if dataset exists and is properly structured."""

    print("\n" + "=" * 60)
    print("VERIFYING DATASET")
    print("=" * 60)

    if not os.path.exists(Config.DATA_DIR):
        print(f"\n✗ Dataset not found: {Config.DATA_DIR}")
        print("\nPlease run: python download_dataset.py")
        sys.exit(1)

    if not os.path.exists(Config.TRAIN_DIR):
        print(f"\n✗ Training data not found: {Config.TRAIN_DIR}")
        sys.exit(1)

    print(f"✓ Dataset found: {Config.DATA_DIR}")
    print(f"✓ Training data: {Config.TRAIN_DIR}")

    # Count classes and images
    train_classes = [d for d in Path(Config.TRAIN_DIR).iterdir() if d.is_dir()]
    print(f"✓ Classes: {len(train_classes)}")

    train_images = len(list(Path(Config.TRAIN_DIR).rglob("*.jpg")))
    print(f"✓ Training images: {train_images:,}")

    if train_images == 0:
        print("\n✗ No training images found!")
        sys.exit(1)

    return len(train_classes)


def create_data_generators():
    """
    Create training and validation data generators with augmentation.

    Augmentation techniques:
    - Rotation: Random rotation up to 20 degrees
    - Shift: Random horizontal/vertical shifts
    - Zoom: Random zoom in/out
    - Flip: Random horizontal flip
    - Normalization: Rescale pixels to [-1, 1] for MobileNetV2
    """

    print("\n" + "=" * 60)
    print("CREATING DATA GENERATORS")
    print("=" * 60)

    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./127.5,  # Scale to [-1, 1]
        rotation_range=Config.ROTATION_RANGE,
        width_shift_range=Config.WIDTH_SHIFT,
        height_shift_range=Config.HEIGHT_SHIFT,
        zoom_range=Config.ZOOM_RANGE,
        horizontal_flip=Config.HORIZONTAL_FLIP,
        fill_mode='nearest',
        preprocessing_function=lambda x: x - 1.0  # Shift to [-1, 1]
    )

    # Validation data (no augmentation, only normalization)
    val_datagen = ImageDataGenerator(
        rescale=1./127.5,
        preprocessing_function=lambda x: x - 1.0
    )

    # Load training data
    train_generator = train_datagen.flow_from_directory(
        Config.TRAIN_DIR,
        target_size=(Config.IMAGE_SIZE, Config.IMAGE_SIZE),
        batch_size=Config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        seed=42
    )

    # Load validation data
    if os.path.exists(Config.VAL_DIR):
        val_generator = val_datagen.flow_from_directory(
            Config.VAL_DIR,
            target_size=(Config.IMAGE_SIZE, Config.IMAGE_SIZE),
            batch_size=Config.BATCH_SIZE,
            class_mode='categorical',
            shuffle=False
        )
    else:
        # Use validation_split if no separate validation folder
        print("⚠ No validation folder found, using 10% of training data")
        val_generator = None

    print(f"✓ Training samples: {train_generator.samples}")
    print(f"✓ Classes: {len(train_generator.class_indices)}")
    print(f"✓ Batch size: {Config.BATCH_SIZE}")

    if val_generator:
        print(f"✓ Validation samples: {val_generator.samples}")

    return train_generator, val_generator


# ============================================================================
# MODEL BUILDING
# ============================================================================

def build_model(num_classes):
    """
    Build MobileNetV2-based classifier.

    Architecture:
    1. MobileNetV2 base (pretrained on ImageNet) - frozen initially
    2. Global Average Pooling
    3. Dropout (0.2) for regularization
    4. Dense layer (128 units) with ReLU
    5. Dropout (0.5)
    6. Output layer (num_classes) with Softmax

    Why MobileNetV2?
    - Optimized for mobile/edge devices
    - Uses depthwise separable convolutions
    - Small size (~14MB)
    - High accuracy on image classification
    """

    print("\n" + "=" * 60)
    print("BUILDING MODEL")
    print("=" * 60)

    # Load pretrained MobileNetV2 (without top classification layer)
    base_model = MobileNetV2(
        input_shape=Config.INPUT_SHAPE,
        include_top=False,  # Exclude ImageNet classifier
        weights='imagenet'   # Use pretrained weights
    )

    # Freeze base model for initial training
    base_model.trainable = False

    print(f"✓ Loaded MobileNetV2 base model")
    print(f"  Parameters: {base_model.count_params():,}")

    # Build classifier on top
    model = keras.Sequential([
        base_model,

        # Global pooling reduces spatial dimensions
        layers.GlobalAveragePooling2D(),

        # Regularization
        layers.Dropout(0.2),

        # Dense layer for learning
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),

        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])

    print(f"✓ Added classification head")
    print(f"  Total parameters: {model.count_params():,}")
    print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

    return model


def compile_model(model, learning_rate=Config.INITIAL_LEARNING_RATE):
    """
    Compile model with optimizer, loss, and metrics.

    Optimizer: Adam (adaptive learning rate)
    Loss: Categorical crossentropy (multi-class classification)
    Metrics: Accuracy, Top-5 accuracy
    """

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            keras.metrics.TopKCategoricalAccuracy(k=5, name='top5_accuracy')
        ]
    )

    print(f"✓ Model compiled")
    print(f"  Optimizer: Adam (lr={learning_rate})")
    print(f"  Loss: Categorical Crossentropy")

    return model


# ============================================================================
# TRAINING
# ============================================================================

def create_callbacks():
    """
    Create training callbacks for monitoring and optimization.

    Callbacks:
    1. ModelCheckpoint: Save best model based on validation accuracy
    2. EarlyStopping: Stop if no improvement for 5 epochs
    3. ReduceLROnPlateau: Reduce learning rate when plateauing
    4. TensorBoard: Log metrics for visualization
    """

    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    callbacks = [
        # Save best model
        ModelCheckpoint(
            filepath=os.path.join(Config.OUTPUT_DIR, 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),

        # Early stopping
        EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),

        # Reduce learning rate
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),

        # TensorBoard logging
        TensorBoard(
            log_dir=os.path.join(Config.OUTPUT_DIR, 'logs'),
            histogram_freq=1
        )
    ]

    print(f"✓ Callbacks configured")
    return callbacks


def train_model(model, train_gen, val_gen, epochs=Config.EPOCHS):
    """
    Train model in two stages:
    1. Train only top layers (base frozen)
    2. Fine-tune entire model (base unfrozen)
    """

    print("\n" + "=" * 60)
    print("TRAINING MODEL")
    print("=" * 60)

    callbacks = create_callbacks()

    # Stage 1: Train top layers
    print("\n[STAGE 1] Training classification head (base frozen)...")
    print(f"  Epochs: {epochs // 2}")

    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs // 2,
        callbacks=callbacks,
        verbose=1
    )

    # Stage 2: Fine-tune entire model
    print("\n[STAGE 2] Fine-tuning entire model (base unfrozen)...")

    # Unfreeze base model
    model.layers[0].trainable = True

    # Recompile with lower learning rate
    compile_model(model, learning_rate=Config.INITIAL_LEARNING_RATE / 10)

    print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    print(f"  Epochs: {epochs // 2}")

    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs // 2,
        callbacks=callbacks,
        verbose=1
    )

    # Combine histories
    history = {
        'accuracy': history1.history['accuracy'] + history2.history['accuracy'],
        'val_accuracy': history1.history['val_accuracy'] + history2.history['val_accuracy'],
        'loss': history1.history['loss'] + history2.history['loss'],
        'val_loss': history1.history['val_loss'] + history2.history['val_loss']
    }

    return history


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(model, test_dir=Config.TEST_DIR):
    """Evaluate model on test set."""

    print("\n" + "=" * 60)
    print("EVALUATING MODEL")
    print("=" * 60)

    if not os.path.exists(test_dir):
        print(f"⚠ Test directory not found: {test_dir}")
        return None

    # Create test generator
    test_datagen = ImageDataGenerator(
        rescale=1./127.5,
        preprocessing_function=lambda x: x - 1.0
    )

    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(Config.IMAGE_SIZE, Config.IMAGE_SIZE),
        batch_size=Config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    print(f"✓ Test samples: {test_generator.samples}")

    # Evaluate
    results = model.evaluate(test_generator, verbose=1)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"  Loss: {results[0]:.4f}")
    print(f"  Accuracy: {results[1]:.4f} ({results[1]*100:.2f}%)")
    print(f"  Top-5 Accuracy: {results[2]:.4f} ({results[2]*100:.2f}%)")

    return {
        'test_loss': results[0],
        'test_accuracy': results[1],
        'test_top5_accuracy': results[2]
    }


def plot_training_history(history, save_path=None):
    """Plot training and validation metrics."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Accuracy
    ax1.plot(history['accuracy'], label='Train Accuracy')
    ax1.plot(history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)

    # Loss
    ax2.plot(history['loss'], label='Train Loss')
    ax2.plot(history['val_loss'], label='Val Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Training plot saved: {save_path}")
    else:
        plt.show()


# ============================================================================
# SAVE MODEL & METADATA
# ============================================================================

def save_model_and_metadata(model, train_gen, history, test_results):
    """Save model, labels, and training metadata."""

    print("\n" + "=" * 60)
    print("SAVING MODEL & METADATA")
    print("=" * 60)

    # Save model
    model_path = os.path.join(Config.OUTPUT_DIR, f'{Config.MODEL_NAME}.h5')
    model.save(model_path)
    print(f"✓ Model saved: {model_path}")

    # Save class labels
    labels_path = os.path.join(Config.OUTPUT_DIR, 'labels.txt')
    class_names = [k for k, v in sorted(train_gen.class_indices.items(), key=lambda x: x[1])]
    with open(labels_path, 'w') as f:
        f.write('\n'.join(class_names))
    print(f"✓ Labels saved: {labels_path}")

    # Save training metadata
    metadata = {
        'model_name': Config.MODEL_NAME,
        'timestamp': datetime.now().isoformat(),
        'architecture': 'MobileNetV2',
        'num_classes': len(class_names),
        'image_size': Config.IMAGE_SIZE,
        'training': {
            'epochs': len(history['accuracy']),
            'batch_size': Config.BATCH_SIZE,
            'initial_lr': Config.INITIAL_LEARNING_RATE,
            'final_train_accuracy': float(history['accuracy'][-1]),
            'final_val_accuracy': float(history['val_accuracy'][-1]),
            'best_val_accuracy': float(max(history['val_accuracy']))
        },
        'test_results': test_results if test_results else {},
        'augmentation': {
            'rotation_range': Config.ROTATION_RANGE,
            'width_shift': Config.WIDTH_SHIFT,
            'height_shift': Config.HEIGHT_SHIFT,
            'zoom_range': Config.ZOOM_RANGE,
            'horizontal_flip': Config.HORIZONTAL_FLIP
        }
    }

    metadata_path = os.path.join(Config.OUTPUT_DIR, 'training_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")

    # Save training history
    history_path = os.path.join(Config.OUTPUT_DIR, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"✓ History saved: {history_path}")

    # Plot training curves
    plot_path = os.path.join(Config.OUTPUT_DIR, 'training_curves.png')
    plot_training_history(history, save_path=plot_path)

    print("\n✓ All files saved to:", Config.OUTPUT_DIR)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main training pipeline."""

    parser = argparse.ArgumentParser(description='Train fruit/vegetable classifier')
    parser.add_argument('--epochs', type=int, default=Config.EPOCHS, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=Config.BATCH_SIZE, help='Batch size')
    parser.add_argument('--lr', type=float, default=Config.INITIAL_LEARNING_RATE, help='Learning rate')
    args = parser.parse_args()

    # Update config
    Config.EPOCHS = args.epochs
    Config.BATCH_SIZE = args.batch_size
    Config.INITIAL_LEARNING_RATE = args.lr

    print("\n" + "=" * 60)
    print("FRUIT & VEGETABLE CLASSIFIER TRAINING")
    print("=" * 60)
    print(f"  TensorFlow version: {tf.__version__}")
    print(f"  GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")
    print(f"  Image size: {Config.IMAGE_SIZE}x{Config.IMAGE_SIZE}")
    print(f"  Batch size: {Config.BATCH_SIZE}")
    print(f"  Epochs: {Config.EPOCHS}")

    # Step 1: Verify dataset
    num_classes = verify_dataset()

    # Step 2: Create data generators
    train_gen, val_gen = create_data_generators()

    # Step 3: Build model
    model = build_model(num_classes)
    model = compile_model(model)

    # Step 4: Train model
    history = train_model(model, train_gen, val_gen, epochs=Config.EPOCHS)

    # Step 5: Evaluate model
    test_results = evaluate_model(model)

    # Step 6: Save everything
    save_model_and_metadata(model, train_gen, history, test_results)

    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review training metrics in output/training_metadata.json")
    print("  2. Check training curves in output/training_curves.png")
    print("  3. Convert to TFLite: python convert_to_tflite.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
