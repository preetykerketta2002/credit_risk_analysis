import os
import json
import joblib
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


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAVED_MODELS_DIR = os.path.join(BASE_DIR, "models", "saved_models")
RESULTS_DIR = os.path.join(BASE_DIR, "models", "results")

os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# 2. DATABASE CONFIGURATION
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

engine = create_engine(DATABASE_URL)


# ============================================================
# 3. LOAD DATA
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

print("=" * 60)
print("DATASET")
print("=" * 60)

print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")

print("\nTarget distribution:")
print(df["risk_bucket"].value_counts())


# ============================================================
# 4. REMOVE DATA LEAKAGE / METADATA
# ============================================================

DROP_COLUMNS = [
    "entity_id",
    "entity_name",
    "created_at",
    "updated_at",
    "risk_bucket"
]

X = df.drop(columns=DROP_COLUMNS)
y = df["risk_bucket"]


# ============================================================
# 5. SELECT FEATURES
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


# Keep only selected features
X = X[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]


print("\nSelected numerical features:")
for feature in NUMERICAL_FEATURES:
    print(f"  - {feature}")

print("\nSelected categorical features:")
for feature in CATEGORICAL_FEATURES:
    print(f"  - {feature}")


# ============================================================
# 6. PREPROCESSING
# ============================================================

numerical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
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
        ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES)
    ]
)


# ============================================================
# 7. DEFINE MODELS
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
# 8. STRATIFIED CROSS VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)


# ============================================================
# 9. TRAIN MODELS
# ============================================================

results = {}


for model_name, model in models.items():

    print("\n" + "=" * 60)
    print(f"TRAINING: {model_name}")
    print("=" * 60)

    # Complete pipeline:
    # preprocessing → model
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    all_y_true = []
    all_y_pred = []

    fold_results = []

    # --------------------------------------------
    # Cross-validation
    # --------------------------------------------

    for fold, (train_index, test_index) in enumerate(
        cv.split(X, y), start=1
    ):

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        print(f"\nFold {fold}")
        print(f"Training samples : {len(X_train)}")
        print(f"Testing samples  : {len(X_test)}")

        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Store predictions
        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())

        fold_results.append(
            {
                "fold": fold,
                "y_true": y_test.tolist(),
                "y_pred": y_pred.tolist()
            }
        )

    # ========================================================
    # SAVE CROSS-VALIDATION RESULTS
    # ========================================================

    results[model_name] = {
        "y_true": all_y_true,
        "y_pred": all_y_pred,
        "folds": fold_results
    }

    # ========================================================
    # TRAIN FINAL MODEL ON ALL DATA
    # ========================================================

    print("\nTraining final model on complete dataset...")

    pipeline.fit(X, y)

    # Save complete pipeline
    filename = (
        model_name
        .lower()
        .replace(" ", "_")
        + ".pkl"
    )

    model_path = os.path.join(
        SAVED_MODELS_DIR,
        filename
    )

    joblib.dump(
        pipeline,
        model_path
    )

    print(f"Saved model: {model_path}")


# ============================================================
# 10. SAVE RESULTS
# ============================================================

results_path = os.path.join(
    RESULTS_DIR,
    "model_results.json"
)

with open(results_path, "w") as file:
    json.dump(
        results,
        file,
        indent=4
    )


# ============================================================
# 11. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("TRAINING COMPLETED")
print("=" * 60)

print(f"\nModels saved in:")
print(SAVED_MODELS_DIR)

print(f"\nResults saved in:")
print(results_path)