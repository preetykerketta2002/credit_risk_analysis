import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_USER = "root"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "credit_risk_evaluator"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ============================================================
# LOAD DATA
# ============================================================

engine = create_engine(DATABASE_URL)

query = """
SELECT
    e.*,
    c.risk_bucket
FROM entities e
INNER JOIN credit_outcomes c
    ON e.entity_id = c.entity_id
"""

df = pd.read_sql(query, engine)

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\n====================================")
print("DATASET INFORMATION")
print("====================================")

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")


# ============================================================
# TARGET
# ============================================================

TARGET = "risk_bucket"

print("\n====================================")
print("TARGET DISTRIBUTION")
print("====================================")

print(df[TARGET].value_counts())


# ============================================================
# REMOVE NON-ML / LEAKAGE FEATURES
# ============================================================

DROP_COLUMNS = [
    "entity_id",
    "entity_name",
]

# These are not in entities, but kept here in case
# the data source is later joined with credit_outcomes.
LEAKAGE_COLUMNS = [
    "PD_1y_pct",
    "LGD_pct",
    "EAD_usd_m",
    "implied_rating",
]

columns_to_drop = [
    col for col in DROP_COLUMNS + LEAKAGE_COLUMNS
    if col in df.columns
]

X = df.drop(
    columns=columns_to_drop + [TARGET],
    errors="ignore"
)

y = df[TARGET]


# ============================================================
# MISSING VALUES
# ============================================================

print("\n====================================")
print("MISSING VALUES")
print("====================================")

missing = X.isnull().sum()

missing = missing[missing > 0].sort_values(
    ascending=False
)

if len(missing) == 0:
    print("No missing values.")
else:
    print(missing)


# ============================================================
# IDENTIFY FEATURE TYPES
# ============================================================

NUMERICAL_FEATURES = X.select_dtypes(
    include=np.number
).columns.tolist()

CATEGORICAL_FEATURES = X.select_dtypes(
    exclude=np.number
).columns.tolist()

print("\n====================================")
print("FEATURE TYPES")
print("====================================")

print(f"Numerical features   : {len(NUMERICAL_FEATURES)}")
print(f"Categorical features : {len(CATEGORICAL_FEATURES)}")


# ============================================================
# NUMERICAL CORRELATION
# ============================================================

print("\n====================================")
print("NUMERICAL CORRELATION WITH TARGET")
print("====================================")

# Encode target only for correlation analysis.
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)

correlation_data = X[NUMERICAL_FEATURES].copy()

correlation_data["risk_bucket"] = y_encoded

correlations = (
    correlation_data
    .corr(numeric_only=True)["risk_bucket"]
    .drop("risk_bucket")
    .abs()
    .sort_values(ascending=False)
)

print(correlations.to_string())


# ============================================================
# PREPARE DATA FOR MUTUAL INFORMATION
# ============================================================

X_mi = X.copy()

# Fill numerical missing values
for column in NUMERICAL_FEATURES:
    X_mi[column] = X_mi[column].fillna(
        X_mi[column].median()
    )

# Encode categorical features
for column in CATEGORICAL_FEATURES:
    X_mi[column] = X_mi[column].fillna("Missing")

    encoder = LabelEncoder()

    X_mi[column] = encoder.fit_transform(
        X_mi[column].astype(str)
    )


# ============================================================
# MUTUAL INFORMATION
# ============================================================

print("\n====================================")
print("MUTUAL INFORMATION")
print("====================================")

mi_scores = mutual_info_classif(
    X_mi,
    y_encoded,
    random_state=42
)

mi_results = pd.Series(
    mi_scores,
    index=X_mi.columns
).sort_values(ascending=False)

print(mi_results.to_string())


# ============================================================
# RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

print("\n====================================")
print("RANDOM FOREST FEATURE IMPORTANCE")
print("====================================")

rf = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    max_depth=4
)

rf.fit(X_mi, y_encoded)

importance = pd.Series(
    rf.feature_importances_,
    index=X_mi.columns
).sort_values(ascending=False)

print(importance.to_string())


# ============================================================
# FINAL FEATURE SUMMARY
# ============================================================

feature_summary = pd.DataFrame({
    "correlation": correlations,
    "mutual_information": mi_results,
    "random_forest_importance": importance
})

feature_summary = feature_summary.fillna(0)

feature_summary["combined_score"] = (
    feature_summary["correlation"]
    + feature_summary["mutual_information"]
    + feature_summary["random_forest_importance"]
)

feature_summary = feature_summary.sort_values(
    "combined_score",
    ascending=False
)

print("\n====================================")
print("FEATURE SELECTION SUMMARY")
print("====================================")

print(feature_summary.to_string())


# ============================================================
# SAVE RESULTS
# ============================================================

feature_summary.to_csv(
    "ml/feature_selection/feature_selection_results.csv"
)

print("\n====================================")
print("RESULT")
print("====================================")

print(
    "Feature selection results saved to "
    "ml/feature_selection/feature_selection_results.csv"
)