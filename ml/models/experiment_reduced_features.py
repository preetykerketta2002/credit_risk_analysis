import os
import json

import pandas as pd

from sqlalchemy import create_engine

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. DATABASE
# ============================================================

DATABASE_URL = (
    "mysql+pymysql://root:root"
    "@localhost:3306/credit_risk_evaluator"
)

engine = create_engine(DATABASE_URL)


# ============================================================
# 2. LOAD DATA
# ============================================================

query = """
SELECT
    e.*,
    c.risk_bucket
FROM entities e
INNER JOIN credit_outcomes c
    ON e.entity_id = c.entity_id
"""

df = pd.read_sql(query, engine)

print("=" * 70)
print("REDUCED FEATURE EXPERIMENT")
print("=" * 70)

print(f"Rows: {len(df)}")

print("\nTarget distribution:")
print(df["risk_bucket"].value_counts())


# ============================================================
# 3. REDUCED FEATURE SET
# ============================================================

NUMERICAL_FEATURES = [
    "debt_to_equity",
    "interest_coverage",
    "dscr",
    "ebitda_margin_pct",
    "current_ratio",
    "years_in_operation",
    "dso_days",
    "fx_revenue_pct",
    "collateral_coverage_pct"
]

CATEGORICAL_FEATURES = [
    "sector",
    "country",
    "ownership_type",
    "auditor_tier",
    "industry_cyclicality",
    "hedging_policy",
    "covenant_quality",
    "sanctions_exposure",
    "financials_audited"
]

FEATURES = (
    NUMERICAL_FEATURES +
    CATEGORICAL_FEATURES
)

X = df[FEATURES]
y = df["risk_bucket"]


print("\nNumerical features:")
for feature in NUMERICAL_FEATURES:
    print(f"  - {feature}")

print("\nCategorical features:")
for feature in CATEGORICAL_FEATURES:
    print(f"  - {feature}")


# ============================================================
# 4. PREPROCESSING
# ============================================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            numerical_pipeline,
            NUMERICAL_FEATURES
        ),
        (
            "categorical",
            categorical_pipeline,
            CATEGORICAL_FEATURES
        )
    ]
)


# ============================================================
# 5. MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        class_weight="balanced",
        random_state=42,
        max_depth=5
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        max_depth=6,
        n_jobs=-1
    )
}


# ============================================================
# 6. SAME CROSS-VALIDATION SPLITS
# ============================================================

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)


# ============================================================
# 7. RUN EXPERIMENT
# ============================================================

experiment_results = {}


for model_name, model in models.items():

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    fold_results = []

    all_y_true = []
    all_y_pred = []

    for fold, (train_index, test_index) in enumerate(
        cv.split(X, y),
        start=1
    ):

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        pipeline.fit(
            X_train,
            y_train
        )

        y_pred = pipeline.predict(
            X_test
        )

        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        precision = precision_score(
            y_test,
            y_pred,
            labels=[
                "Low",
                "Medium",
                "High"
            ],
            average="macro",
            zero_division=0
        )

        recall = recall_score(
            y_test,
            y_pred,
            labels=[
                "Low",
                "Medium",
                "High"
            ],
            average="macro",
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            y_pred,
            labels=[
                "Low",
                "Medium",
                "High"
            ],
            average="macro",
            zero_division=0
        )

        high_recall = recall_score(
            y_test,
            y_pred,
            labels=["High"],
            average="macro",
            zero_division=0
        )

        fold_result = {
            "fold": fold,
            "accuracy": round(float(accuracy), 4),
            "precision_macro": round(float(precision), 4),
            "recall_macro": round(float(recall), 4),
            "f1_macro": round(float(f1), 4),
            "high_risk_recall": round(
                float(high_recall),
                4
            )
        }

        fold_results.append(
            fold_result
        )

        all_y_true.extend(
            y_test.tolist()
        )

        all_y_pred.extend(
            y_pred.tolist()
        )

        print(f"\nFold {fold}")
        print("-" * 40)

        print(
            f"Accuracy          : {accuracy:.4f}"
        )

        print(
            f"Precision (Macro) : {precision:.4f}"
        )

        print(
            f"Recall (Macro)    : {recall:.4f}"
        )

        print(
            f"F1-score (Macro)  : {f1:.4f}"
        )

        print(
            f"High-risk Recall  : {high_recall:.4f}"
        )

    # ========================================================
    # OVERALL OUT-OF-FOLD PERFORMANCE
    # ========================================================

    overall_accuracy = accuracy_score(
        all_y_true,
        all_y_pred
    )

    overall_precision = precision_score(
        all_y_true,
        all_y_pred,
        labels=[
            "Low",
            "Medium",
            "High"
        ],
        average="macro",
        zero_division=0
    )

    overall_recall = recall_score(
        all_y_true,
        all_y_pred,
        labels=[
            "Low",
            "Medium",
            "High"
        ],
        average="macro",
        zero_division=0
    )

    overall_f1 = f1_score(
        all_y_true,
        all_y_pred,
        labels=[
            "Low",
            "Medium",
            "High"
        ],
        average="macro",
        zero_division=0
    )

    experiment_results[model_name] = {
        "folds": fold_results,
        "overall": {
            "accuracy": round(
                float(overall_accuracy),
                4
            ),
            "precision_macro": round(
                float(overall_precision),
                4
            ),
            "recall_macro": round(
                float(overall_recall),
                4
            ),
            "f1_macro": round(
                float(overall_f1),
                4
            )
        }
    }


# ============================================================
# 8. SAVE RESULTS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "models",
    "results"
)

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "reduced_feature_results.json"
)

with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        experiment_results,
        file,
        indent=4
    )


# ============================================================
# 9. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("REDUCED FEATURE EXPERIMENT SUMMARY")
print("=" * 70)

for model_name, data in experiment_results.items():

    overall = data["overall"]

    print(f"\n{model_name}")

    print(
        f"Accuracy          : "
        f"{overall['accuracy']:.4f}"
    )

    print(
        f"Precision (Macro) : "
        f"{overall['precision_macro']:.4f}"
    )

    print(
        f"Recall (Macro)    : "
        f"{overall['recall_macro']:.4f}"
    )

    print(
        f"F1-score (Macro)  : "
        f"{overall['f1_macro']:.4f}"
    )

print("\nResults saved to:")
print(OUTPUT_FILE)