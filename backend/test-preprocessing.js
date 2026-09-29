const {
    preprocessEntity
} = require('./preprocessing/preprocessEntity');


const sample = {
    entity_id: 'TEST001',
    entity_name: 'ABC Corporation',

    sector: 'Technology',
    country: 'India',

    revenue_usd_m: '250',
    ebitda_margin_pct: '15.2',
    ebit_margin_pct: '10.5',

    cash_usd_m: '50',
    total_assets_usd_m: '500',
    equity_usd_m: '200',
    net_debt_usd_m: '160',

    debt_to_equity: '0.8',
    interest_expense_usd_m: '10',
    interest_coverage: '3.2',

    operating_cf_usd_m: '40',
    capex_usd_m: '20',
    fcf_usd_m: '20',

    dscr: '1.5',
    current_ratio: '2.1',
    quick_ratio: '1.8',

    dso_days: '45',
    dpo_days: '40',
    dio_days: '50',

    revenue_cagr_3y_pct: '12.1',

    years_in_operation: '15',
    ownership_type: 'Public',
    auditor_tier: 'Big4',

    governance_score_0_100: '85',
    esg_controversies_3y: '2',
    country_risk_0_100: '40',

    industry_cyclicality: 'Medium',
    fx_revenue_pct: '30',

    hedging_policy: null,

    collateral_coverage_pct: '120',
    covenant_quality: 'Standard',

    payment_incidents_12m: '0',
    legal_disputes_open: '1',

    sanctions_exposure: null,

    financials_audited: 'Yes'
};


const result = preprocessEntity(sample);

console.log(
    JSON.stringify(result, null, 2)
);