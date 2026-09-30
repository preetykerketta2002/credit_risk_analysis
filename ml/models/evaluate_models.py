import os
import json

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 1. PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS_DIR = os.path.join(BASE_DIR, "models", "results")

RESULTS_FILE = os.path.join(
    RESULTS_DIR,
    "model_results.json"
)


# ============================================================
# 2. LOAD SAVED PREDICTIONS
# ============================================================

with open(RESULTS_FILE, "r") as file:
    results = json.load(file)


# ============================================================
# 3. CLASS LABELS
# ============================================================

LABELS = [
    "Low",
    "Medium",
    "High"
]


# ============================================================
# 4. EVALUATE EACH MODEL
# ============================================================

evaluation_results = {}


for model_name, model_data in results.items():

    y_true = model_data["y_true"]
    y_pred = model_data["y_pred"]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS
    )

    # --------------------------------------------------------
    # Classification Report
    # --------------------------------------------------------

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0
    )

    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    evaluation_results[model_name] = {
        "accuracy": round(float(accuracy), 4),
        "precision_macro": round(float(precision), 4),
        "recall_macro": round(float(recall), 4),
        "f1_macro": round(float(f1), 4),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report
    }


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)


for model_name, metrics in evaluation_results.items():

    print("\n" + "-" * 70)
    print(model_name)
    print("-" * 70)

    print(
        f"Accuracy          : {metrics['accuracy']:.4f}"
    )

    print(
        f"Precision (Macro) : {metrics['precision_macro']:.4f}"
    )

    print(
        f"Recall (Macro)    : {metrics['recall_macro']:.4f}"
    )

    print(
        f"F1-score (Macro)  : {metrics['f1_macro']:.4f}"
    )

    print("\nConfusion Matrix")
    print("Rows = Actual")
    print("Columns = Predicted")
    print("Labels:", LABELS)

    for row in metrics["confusion_matrix"]:
        print(row)

    print("\nClassification Report")
    print(metrics["classification_report"])


# ============================================================
# 6. SAVE EVALUATION RESULTS
# ============================================================

evaluation_file = os.path.join(
    RESULTS_DIR,
    "evaluation_results.json"
)


# Classification report is already a string,
# so everything is JSON serializable.

with open(evaluation_file, "w") as file:

    json.dump(
        evaluation_results,
        file,
        indent=4
    )


print("\n" + "=" * 70)
print("EVALUATION COMPLETED")
print("=" * 70)

print("\nEvaluation results saved at:")
print(evaluation_file)