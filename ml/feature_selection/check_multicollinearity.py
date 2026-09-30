import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from statsmodels.stats.outliers_influence import variance_inflation_factor


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
# CANDIDATE NUMERICAL FEATURES
# ============================================================

CANDIDATE_FEATURES = [
    "interest_coverage",
    "debt_to_equity",
    "dscr",
    "ebitda_margin_pct",
    "ebit_margin_pct",
    "current_ratio",
    "quick_ratio",
    "cash_usd_m",
    "operating_cf_usd_m",
    "fcf_usd_m",
    "revenue_usd_m",
    "years_in_operation",
    "interest_expense_usd_m",
    "net_debt_usd_m",
    "equity_usd_m",
    "dso_days",
    "fx_revenue_pct",
    "collateral_coverage_pct",
]


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


print("\n====================================")
print("MULTICOLLINEARITY ANALYSIS")
print("====================================")

print(f"Rows: {len(df)}")


# ============================================================
# PREPARE FEATURES
# ============================================================

X = df[CANDIDATE_FEATURES].copy()

# Convert everything to numeric
for column in X.columns:
    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )

# Handle missing values
X = X.fillna(X.median())


# ============================================================
# CORRELATION MATRIX
# ============================================================

print("\n====================================")
print("CORRELATION MATRIX")
print("====================================")

correlation_matrix = X.corr()

print(
    correlation_matrix.round(2).to_string()
)


# ============================================================
# HIGH CORRELATION PAIRS
# ============================================================

print("\n====================================")
print("HIGH CORRELATION PAIRS")
print("====================================")

threshold = 0.80

found_pair = False

for i in range(len(correlation_matrix.columns)):
    for j in range(i + 1, len(correlation_matrix.columns)):

        feature_1 = correlation_matrix.columns[i]
        feature_2 = correlation_matrix.columns[j]

        correlation = correlation_matrix.iloc[i, j]

        if abs(correlation) >= threshold:

            print(
                f"{feature_1} <-> {feature_2}: "
                f"{correlation:.3f}"
            )

            found_pair = True


if not found_pair:
    print(
        f"No feature pairs with "
        f"|correlation| >= {threshold}"
    )


# ============================================================
# VIF
# ============================================================

print("\n====================================")
print("VARIANCE INFLATION FACTOR (VIF)")
print("====================================")

vif_data = pd.DataFrame()

vif_data["feature"] = X.columns

vif_data["VIF"] = [
    variance_inflation_factor(
        X.values,
        i
    )
    for i in range(X.shape[1])
]

vif_data = vif_data.sort_values(
    "VIF",
    ascending=False
)

print(
    vif_data.round(3).to_string(index=False)
)


# ============================================================
# INTERPRETATION
# ============================================================

print("\n====================================")
print("VIF INTERPRETATION")
print("====================================")

print("VIF < 5     → generally acceptable")
print("VIF 5 - 10  → possible multicollinearity")
print("VIF > 10    → strong multicollinearity")


# ============================================================
# SAVE RESULTS
# ============================================================

correlation_matrix.to_csv(
    "ml/feature_selection/correlation_matrix.csv"
)

vif_data.to_csv(
    "ml/feature_selection/vif_results.csv",
    index=False
)

print("\n====================================")
print("RESULTS SAVED")
print("====================================")

print(
    "correlation_matrix.csv"
)

print(
    "vif_results.csv"
)