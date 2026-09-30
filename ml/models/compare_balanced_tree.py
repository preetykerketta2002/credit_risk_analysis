import os
import pandas as pd

from sqlalchemy import create_engine

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "credit_risk_evaluator")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# ============================================================
# FEATURES
# ============================================================

NUMERICAL_FEATURES = [
    "interest_coverage",
    "debt_to_equity",
    "dscr",
    "ebitda_margin_pct",
    "current_ratio",
    "cash_usd_m",
    "operating_cf_usd_m",
    "net_debt_usd_m",
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

FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

TARGET = "risk_bucket"


# ============================================================
# LOAD DATA
# ============================================================

query = """
SELECT
    e.entity_id,
    e.entity_name,

    e.interest_coverage,
    e.debt_to_equity,
    e.dscr,
    e.ebitda_margin_pct,
    e.current_ratio,
    e.cash_usd_m,
    e.operating_cf_usd_m,
    e.net_debt_usd_m,
    e.years_in_operation,
    e.dso_days,
    e.fx_revenue_pct,
    e.collateral_coverage_pct,

    e.sector,
    e.country,
    e.ownership_type,
    e.auditor_tier,
    e.industry_cyclicality,
    e.hedging_policy,
    e.covenant_quality,
    e.sanctions_exposure,
    e.financials_audited,

    c.risk_bucket

FROM entities e

INNER JOIN credit_outcomes c
    ON e.entity_id = c.entity_id

ORDER BY e.entity_id
"""

df = pd.read_sql(query, engine)

X = df[FEATURES]
y = df[TARGET]


# ============================================================
# PREPROCESSING
# ============================================================

numerical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    ))
])

preprocessor = ColumnTransformer([
    ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
    ("categorical", categorical_pipeline, CATEGORICAL_FEATURES)
])


# ============================================================
# MODELS
# ============================================================

normal_tree = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", DecisionTreeClassifier(
        random_state=42
    ))
])

balanced_tree = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    ))
])


# ============================================================
# CROSS VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(model, model_name):

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    predictions = cross_val_predict(
        model,
        X,
        y,
        cv=cv,
        method="predict"
    )

    accuracy = accuracy_score(y, predictions)

    precision = precision_score(
        y,
        predictions,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y,
        predictions,
        average="macro",
        zero_division=0
    )

    f1 = f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0
    )

    print(f"Accuracy          : {accuracy:.4f}")
    print(f"Macro Precision   : {precision:.4f}")
    print(f"Macro Recall      : {recall:.4f}")
    print(f"Macro F1-score    : {f1:.4f}")

    print("\nConfusion Matrix")
    print("----------------")

    labels = ["Low", "Medium", "High"]

    cm = confusion_matrix(
        y,
        predictions,
        labels=labels
    )

    print("             Low  Medium  High")

    for i, label in enumerate(labels):
        print(
            f"Actual {label:<7}"
            f"{cm[i][0]:>5}"
            f"{cm[i][1]:>8}"
            f"{cm[i][2]:>6}"
        )

    print("\nClassification Report")
    print("---------------------")

    print(
        classification_report(
            y,
            predictions,
            labels=labels,
            zero_division=0
        )
    )

    return {
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predictions": predictions
    }


# ============================================================
# RUN BOTH MODELS
# ============================================================

print("=" * 70)
print("DECISION TREE CLASS-WEIGHT EXPERIMENT")
print("=" * 70)

print("\nDataset:")
print(f"Total records: {len(df)}")

print("\nClass distribution:")
print(y.value_counts())


normal_results = evaluate_model(
    normal_tree,
    "A. NORMAL DECISION TREE"
)

balanced_results = evaluate_model(
    balanced_tree,
    "B. BALANCED DECISION TREE"
)


# ============================================================
# DIRECT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("FINAL COMPARISON")
print("=" * 70)

print(
    f"{'Metric':<20}"
    f"{'Normal Tree':>18}"
    f"{'Balanced Tree':>20}"
)

print("-" * 58)

print(
    f"{'Accuracy':<20}"
    f"{normal_results['accuracy']:>18.4f}"
    f"{balanced_results['accuracy']:>20.4f}"
)

print(
    f"{'Macro Precision':<20}"
    f"{normal_results['precision']:>18.4f}"
    f"{balanced_results['precision']:>20.4f}"
)

print(
    f"{'Macro Recall':<20}"
    f"{normal_results['recall']:>18.4f}"
    f"{balanced_results['recall']:>20.4f}"
)

print(
    f"{'Macro F1':<20}"
    f"{normal_results['f1']:>18.4f}"
    f"{balanced_results['f1']:>20.4f}"
)


# ============================================================
# HIGH-RISK RECALL
# ============================================================

normal_report = classification_report(
    y,
    normal_results["predictions"],
    labels=["Low", "Medium", "High"],
    output_dict=True,
    zero_division=0
)

balanced_report = classification_report(
    y,
    balanced_results["predictions"],
    labels=["Low", "Medium", "High"],
    output_dict=True,
    zero_division=0
)

print("\nHigh-risk class comparison:")
print(
    f"Normal Tree High Recall   : "
    f"{normal_report['High']['recall']:.4f}"
)

print(
    f"Balanced Tree High Recall : "
    f"{balanced_report['High']['recall']:.4f}"
)

print("\n" + "=" * 70)
print("EXPERIMENT COMPLETED")
print("=" * 70)