import os
import json

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RESULTS_FILE = os.path.join(
    BASE_DIR,
    "models",
    "results",
    "model_results.json"
)


# ============================================================
# 2. LOAD RESULTS
# ============================================================

with open(RESULTS_FILE, "r") as file:
    results = json.load(file)


LABELS = [
    "Low",
    "Medium",
    "High"
]


# ============================================================
# 3. ANALYZE EACH MODEL / FOLD
# ============================================================

for model_name, model_data in results.items():

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    folds = model_data["folds"]

    for fold_data in folds:

        fold = fold_data["fold"]

        y_true = fold_data["y_true"]
        y_pred = fold_data["y_pred"]

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

        # High-risk recall
        high_recall = recall_score(
            y_true,
            y_pred,
            labels=["High"],
            average="macro",
            zero_division=0
        )

        print(f"\nFold {fold}")
        print("-" * 40)

        print(f"Accuracy          : {accuracy:.4f}")
        print(f"Precision (Macro) : {precision:.4f}")
        print(f"Recall (Macro)    : {recall:.4f}")
        print(f"F1-score (Macro)  : {f1:.4f}")
        print(f"High-risk Recall  : {high_recall:.4f}")

        print("\nActual → Predicted")

        for actual, predicted in zip(
            y_true,
            y_pred
        ):
            print(
                f"  {actual:8} → {predicted}"
            )