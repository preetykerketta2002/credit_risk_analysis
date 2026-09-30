import os
import joblib
import pandas as pd

from sqlalchemy import create_engine


# ============================================================
# 1. PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "saved_models",
    "decision_tree.pkl"
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

FEATURES = (
    NUMERICAL_FEATURES +
    CATEGORICAL_FEATURES
)


# ============================================================
# 4. LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)

print("=" * 60)
print("DECISION TREE MODEL LOADED")
print("=" * 60)

print(f"Model: {MODEL_PATH}")


# ============================================================
# 5. PREDICTION FUNCTION
# ============================================================

def predict_risk(application_data):

    """
    Predict credit risk for a new application.

    application_data:
        Dictionary containing the required model features.

    Returns:
        Predicted risk bucket.
    """

    # Convert dictionary to DataFrame
    input_data = pd.DataFrame(
        [application_data]
    )

    # Make sure columns are in exactly
    # the same order used during training
    input_data = input_data[FEATURES]

    # Predict
    prediction = model.predict(
        input_data
    )[0]

    return prediction


# ============================================================
# 6. TEST WITH DATABASE ENTITY
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
WHERE e.entity_id = 'ENT001'
"""

entity = pd.read_sql(
    query,
    engine
)


if entity.empty:

    print("\nENT001 not found.")

else:

    row = entity.iloc[0]

    application_data = {
        feature: row[feature]
        for feature in FEATURES
    }

    prediction = predict_risk(
        application_data
    )

    actual = row["risk_bucket"]

    print("\n" + "=" * 60)
    print("PREDICTION TEST")
    print("=" * 60)

    print(f"Entity ID       : {row['entity_id']}")
    print(f"Entity Name     : {row['entity_name']}")
    print(f"Actual Risk     : {actual}")
    print(f"Predicted Risk  : {prediction}")

    print("=" * 60)