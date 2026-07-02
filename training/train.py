import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import EfficientNetB0
from config import (
    TRAIN_DIR, VAL_DIR, MODEL_SAVE_DIR, BEST_MODEL_PATH, LABELS_PATH,
    IMAGE_SIZE, BATCH_SIZE, EPOCHS, LEARNING_RATE, RANDOM_SEED
)

def create_augmentation_layer():
    """Defines image augmentation operations as Keras layers."""
    return tf.keras.Sequential([
        layers.RandomRotation(0.15, seed=RANDOM_SEED),
        # Note authenticity changes are avoided; we do horizontal shift and zoom slightly
        layers.RandomTranslation(height_factor=0.0, width_factor=0.1, seed=RANDOM_SEED),
        layers.RandomZoom(0.1, seed=RANDOM_SEED),
        layers.RandomBrightness(0.15, value_range=(0.0, 255.0), seed=RANDOM_SEED),
    ], name="data_augmentation")

def build_transfer_model(num_classes: int = 2) -> models.Model:
    """Builds an EfficientNetB0 transfer learning model with custom classification head."""
    # 1. Base model with frozen weights
    # EfficientNet has built-in normalization layers expecting input in [0, 255] range
    base_model = EfficientNetB0(weights="imagenet", include_top=False, input_shape=(*IMAGE_SIZE, 3))
    base_model.trainable = False
    
    # 2. Add classification layers on top of base
    model = models.Sequential([
        # Augmentation layer (skipped automatically during evaluation/inference)
        create_augmentation_layer(),
        
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax")
    ])
    
    return model

def main():
    print("🧠 Starting Model Training Pipeline using TensorFlow/Keras")
    
    # Ensure save directory exists
    MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load train and validate datasets
    print("📂 Loading training dataset splits...")
    train_dataset = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",  # returns integer labels [0, 1]
        shuffle=True,
        seed=RANDOM_SEED
    )
    
    val_dataset = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=False
    )
    
    # Get class names and save to labels.json
    class_names = train_dataset.class_names
    print(f"✓ Detected classes: {class_names}")
    
    # Map index to name and save to models/counterfeit/labels.json
    # Keras infers alphabetically: counterfeit -> index 0, real -> index 1
    # We map 0 -> "Counterfeit" and 1 -> "Genuine"
    labels_dict = {
        "0": "Counterfeit" if class_names[0] == "counterfeit" else "Genuine",
        "1": "Genuine" if class_names[1] == "real" else "Counterfeit"
    }
    
    with open(LABELS_PATH, "w") as f:
        json.dump(labels_dict, f, indent=4)
    print(f"✓ Saved class labels map to: {LABELS_PATH}")

    # Optimize datasets for loading performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
    val_dataset = val_dataset.prefetch(buffer_size=AUTOTUNE)
    
    # 2. Build model
    print("🏗️ Creating EfficientNetB0 transfer learning model architecture...")
    model = build_transfer_model(num_classes=len(class_names))
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    # 3. Callbacks
    # Save the model to best_model.keras
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(BEST_MODEL_PATH),
        monitor="val_accuracy",
        save_best_only=True,
        mode="max",
        verbose=1
    )
    
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1
    )
    
    # 4. Train the model
    print(f"🚀 Training model for {EPOCHS} epochs...")
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=EPOCHS,
        callbacks=[checkpoint, early_stopping]
    )
    
    print(f"✓ Training finished! Best model checkpoint saved to: {BEST_MODEL_PATH}")

if __name__ == "__main__":
    main()
