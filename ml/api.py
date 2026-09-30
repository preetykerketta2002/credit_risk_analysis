import os
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


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
    "ml",
    "models",
    "saved_models",
    "decision_tree.pkl"
)


# ============================================================
# 2. LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


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
# 4. REQUEST VALIDATION MODEL
# ============================================================

class CreditApplication(BaseModel):

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    interest_coverage: float
    debt_to_equity: float
    dscr: float
    ebitda_margin_pct: float
    current_ratio: float
    cash_usd_m: float
    operating_cf_usd_m: float
    net_debt_usd_m: float
    years_in_operation: float
    dso_days: float
    fx_revenue_pct: float
    collateral_coverage_pct: float

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    sector: str
    country: str
    ownership_type: str
    auditor_tier: str
    industry_cyclicality: str
    hedging_policy: str
    covenant_quality: str
    sanctions_exposure: str
    financials_audited: str


# ============================================================
# 5. FASTAPI APP
# ============================================================

app = FastAPI(
    title="Credit Risk ML API",
    description="Decision Tree based credit risk prediction API",
    version="1.0.0"
)


# ============================================================
# 6. HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Credit Risk ML API is running",
        "model": "Decision Tree"
    }


# ============================================================
# 7. PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict_risk(application_data: CreditApplication):

    try:

        # ----------------------------------------------------
        # Convert validated request to dictionary
        # ----------------------------------------------------

        application_dict = application_data.model_dump()


        # ----------------------------------------------------
        # Convert dictionary to DataFrame
        # ----------------------------------------------------

        input_data = pd.DataFrame(
            [application_dict]
        )


        # ----------------------------------------------------
        # Keep exactly the same feature order
        # used during model training
        # ----------------------------------------------------

        input_data = input_data[FEATURES]


        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        prediction = model.predict(
            input_data
        )[0]


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "predicted_risk": prediction
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )