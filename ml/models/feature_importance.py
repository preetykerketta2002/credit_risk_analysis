import os
import joblib
import pandas as pd

from sqlalchemy import create_engine


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SAVED_MODELS_DIR = os.path.join(
    BASE_DIR,
    "models",
    "saved_models"
)


# ============================================================
# 2. DATABASE
# ============================================================

DATABASE_URL = (
    "mysql+pymysql://root:root"
    "@localhost:3306/credit_risk_evaluator"
)

engine = create_engine(DATABASE_URL)


# ============================================================
# 3. FEATURES
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


# ============================================================
# 4. MODEL FILES
# ============================================================

MODEL_FILES = {
    "Logistic Regression": "logistic_regression.pkl",
    "Decision Tree": "decision_tree.pkl",
    "Random Forest": "random_forest.pkl"
}


# ============================================================
# 5. ANALYZE MODELS
# ============================================================

for model_name, filename in MODEL_FILES.items():

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    model_path = os.path.join(
        SAVED_MODELS_DIR,
        filename
    )

    pipeline = joblib.load(model_path)

    # Get preprocessing component
    preprocessor = pipeline.named_steps["preprocessor"]

    # Get trained model
    model = pipeline.named_steps["model"]

    # Get transformed feature names
    transformed_features = (
        preprocessor
        .get_feature_names_out()
    )

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    if model_name == "Logistic Regression":

        # For multiclass logistic regression,
        # take the mean absolute coefficient
        # across all classes.

        importance = abs(model.coef_).mean(axis=0)

    # --------------------------------------------------------
    # Decision Tree / Random Forest
    # --------------------------------------------------------

    else:

        importance = model.feature_importances_

    # --------------------------------------------------------
    # Create dataframe
    # --------------------------------------------------------

    importance_df = pd.DataFrame(
        {
            "feature": transformed_features,
            "importance": importance
        }
    )

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    # --------------------------------------------------------
    # Display top 15
    # --------------------------------------------------------

    print("\nTop 15 features:\n")

    print(
        importance_df
        .head(15)
        .to_string(index=False)
    )