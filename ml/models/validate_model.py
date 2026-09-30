import os
import joblib
import pandas as pd

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
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

print("=" * 70)
print("INDEPENDENT MODEL VALIDATION")
print("=" * 70)

print(f"Total records: {len(df)}")

print("\nOriginal class distribution:")
print(df[TARGET].value_counts())

# ============================================================
# FEATURES + TARGET
# ============================================================

X = df[FEATURES]
y = df[TARGET]

# ============================================================
# STRATIFIED TRAIN / VALIDATION SPLIT
# ============================================================

X_train, X_validation, y_train, y_validation = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining set:")
print(f"Records: {len(X_train)}")
print(y_train.value_counts())

print("\nValidation set:")
print(f"Records: {len(X_validation)}")
print(y_validation.value_counts())

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
# DECISION TREE
# ============================================================

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", DecisionTreeClassifier(
        random_state=42
    ))
])

# ============================================================
# TRAIN ONLY ON TRAINING DATA
# ============================================================

print("\nTraining Decision Tree...")

model.fit(X_train, y_train)

print("Training completed.")

# ============================================================
# VALIDATION PREDICTION
# ============================================================

y_pred = model.predict(X_validation)

# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(y_validation, y_pred)

precision = precision_score(
    y_validation,
    y_pred,
    average="macro",
    zero_division=0
)

recall = recall_score(
    y_validation,
    y_pred,
    average="macro",
    zero_division=0
)

f1 = f1_score(
    y_validation,
    y_pred,
    average="macro",
    zero_division=0
)

print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print(f"Accuracy          : {accuracy:.4f}")
print(f"Macro Precision   : {precision:.4f}")
print(f"Macro Recall      : {recall:.4f}")
print(f"Macro F1-score    : {f1:.4f}")

# ============================================================
# CONFUSION MATRIX
# ============================================================

labels = ["Low", "Medium", "High"]

cm = confusion_matrix(
    y_validation,
    y_pred,
    labels=labels
)

print("\nConfusion Matrix")
print("----------------")

print("             Predicted")
print("             Low  Medium  High")

for i, label in enumerate(labels):
    print(
        f"Actual {label:<7}"
        f"{cm[i][0]:>5}"
        f"{cm[i][1]:>8}"
        f"{cm[i][2]:>6}"
    )

# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report")
print("---------------------")

print(
    classification_report(
        y_validation,
        y_pred,
        labels=labels,
        zero_division=0
    )
)

# ============================================================
# RECORD-LEVEL PREDICTIONS
# ============================================================

results = df.loc[X_validation.index, [
    "entity_id",
    "entity_name"
]].copy()

results["actual_risk"] = y_validation
results["predicted_risk"] = y_pred

print("\nValidation Predictions")
print("----------------------")

print(results.to_string(index=False))

# ============================================================
# SAVE VALIDATION MODEL
# ============================================================

output_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "saved_models"
)

os.makedirs(output_dir, exist_ok=True)

validation_model_path = os.path.join(
    output_dir,
    "decision_tree_validation.pkl"
)

joblib.dump(model, validation_model_path)

print("\nValidation model saved:")
print(validation_model_path)

print("\n" + "=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)