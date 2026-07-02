import json
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from config import TEST_DIR, BEST_MODEL_PATH, METRICS_PATH, IMAGE_SIZE, BATCH_SIZE

def main():
    print("📊 Evaluating model performance on test set split...")
    
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {BEST_MODEL_PATH}. Run training first.")
        
    # 1. Load best model checkpoint
    model = tf.keras.models.load_model(str(BEST_MODEL_PATH))
    print(f"✓ Successfully loaded model from: {BEST_MODEL_PATH}")
    
    # 2. Load test set directory
    test_dataset = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=False
    )
    
    y_true = []
    y_pred = []
    
    print("📡 Executing model predictions over test splits...")
    for images, labels in test_dataset:
        preds = model.predict(images)
        pred_labels = np.argmax(preds, axis=1)
        y_true.extend(labels.numpy())
        y_pred.extend(pred_labels)
        
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # 3. Calculate classification metrics
    # Note: Keras alphabetically labels 'counterfeit' as index 0, 'real' as index 1
    # We define Genuine ('real') as the positive class (1) for binary scores.
    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, average="binary", zero_division=0))
    recall = float(recall_score(y_true, y_pred, average="binary", zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average="binary", zero_division=0))
    
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1])
        }
    }
    
    # Save to metrics.json
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print("\n==========================================")
    print("📈 Evaluation Report on Test Set:")
    print("==========================================")
    print(f"• Accuracy:  {accuracy * 100:.2f}%")
    print(f"• Precision: {precision * 100:.2f}%")
    print(f"• Recall:    {recall * 100:.2f}%")
    print(f"• F1 Score:  {f1 * 100:.2f}%")
    print("• Confusion Matrix:")
    print(f"  - True Negatives (TN/Counterfeit Correct):  {metrics['confusion_matrix']['tn']}")
    print(f"  - False Positives (FP/Counterfeit Wrong):  {metrics['confusion_matrix']['fp']}")
    print(f"  - False Negatives (FN/Genuine Wrong):      {metrics['confusion_matrix']['fn']}")
    print(f"  - True Positives (TP/Genuine Correct):      {metrics['confusion_matrix']['tp']}")
    print("==========================================\n")
    print(f"✓ Saved validation stats metrics to: {METRICS_PATH}")

if __name__ == "__main__":
    main()
