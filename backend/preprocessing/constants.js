// preprocessing/constants.js

const NUMERICAL_FIELDS = [
    'revenue_usd_m',
    'ebitda_margin_pct',
    'ebit_margin_pct',
    'cash_usd_m',
    'total_assets_usd_m',
    'equity_usd_m',
    'net_debt_usd_m',
    'debt_to_equity',
    'interest_expense_usd_m',
    'interest_coverage',
    'operating_cf_usd_m',
    'capex_usd_m',
    'fcf_usd_m',
    'dscr',
    'current_ratio',
    'quick_ratio',
    'dso_days',
    'dpo_days',
    'dio_days',
    'revenue_cagr_3y_pct',
    'years_in_operation',
    'governance_score_0_100',
    'esg_controversies_3y',
    'country_risk_0_100',
    'fx_revenue_pct',
    'collateral_coverage_pct',
    'payment_incidents_12m',
    'legal_disputes_open'
];

const CATEGORICAL_FIELDS = [
    'sector',
    'country',
    'ownership_type',
    'auditor_tier',
    'industry_cyclicality',
    'hedging_policy',
    'covenant_quality',
    'sanctions_exposure',
    'financials_audited'
];

const REQUIRED_FIELDS = [
    'entity_id',
    'entity_name'
];

const ALLOWED_VALUES = {
    industry_cyclicality: [
        'Low',
        'Medium',
        'High'
    ],

    hedging_policy: [
        'None',
        'Partial',
        'Comprehensive'
    ],

    covenant_quality: [
        'Weak',
        'Standard',
        'Strong'
    ],

    sanctions_exposure: [
        'None',
        'Indirect',
        'Direct'
    ],

    financials_audited: [
        'Yes',
        'No'
    ]
};

module.exports = {
    NUMERICAL_FIELDS,
    CATEGORICAL_FIELDS,
    REQUIRED_FIELDS,
    ALLOWED_VALUES
};