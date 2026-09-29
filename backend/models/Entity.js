const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Entity = sequelize.define('Entity', {
  entity_id: { type: DataTypes.STRING(50), primaryKey: true, allowNull: false },
  entity_name: { type: DataTypes.STRING(255), allowNull: false },
  sector: { type: DataTypes.STRING(100) },
  country: { type: DataTypes.STRING(100) },
  
  // Financial Variables
  revenue_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  ebitda_margin_pct: { type: DataTypes.DECIMAL(5, 2) },
  ebit_margin_pct: { type: DataTypes.DECIMAL(5, 2) },
  cash_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  total_assets_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  equity_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  net_debt_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  debt_to_equity: { type: DataTypes.DECIMAL(8, 4) },
  interest_expense_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  interest_coverage: { type: DataTypes.DECIMAL(8, 4) },
  operating_cf_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  capex_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  fcf_usd_m: { type: DataTypes.DECIMAL(12, 2) },
  dscr: { type: DataTypes.DECIMAL(8, 4) },
  current_ratio: { type: DataTypes.DECIMAL(8, 4) },
  quick_ratio: { type: DataTypes.DECIMAL(8, 4) },
  
  // Working Capital Cycle Days
  dso_days: { type: DataTypes.INTEGER, allowNull: true },
  dpo_days: { type: DataTypes.INTEGER, allowNull: true },
  dio_days: { type: DataTypes.INTEGER, allowNull: true },
  
  revenue_cagr_3y_pct: { type: DataTypes.DECIMAL(5, 2) },
  
  // Operational & Risk Factors
  years_in_operation: { type: DataTypes.INTEGER },
  ownership_type: { type: DataTypes.STRING(50) },
  auditor_tier: { type: DataTypes.STRING(50) },
  governance_score_0_100: { type: DataTypes.INTEGER },
  esg_controversies_3y: { type: DataTypes.INTEGER },
  country_risk_0_100: { type: DataTypes.INTEGER },
  industry_cyclicality: { type: DataTypes.STRING(50) },
  fx_revenue_pct: { type: DataTypes.DECIMAL(5, 2) },
  hedging_policy: { type: DataTypes.STRING(50) },
  collateral_coverage_pct: { type: DataTypes.DECIMAL(5, 2) },
  covenant_quality: { type: DataTypes.STRING(50) },
  payment_incidents_12m: { type: DataTypes.INTEGER },
  legal_disputes_open: { type: DataTypes.INTEGER },
  sanctions_exposure: { type: DataTypes.STRING(50) },
  financials_audited: { type: DataTypes.STRING(10) }
}, {
  tableName: 'entities',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

module.exports = Entity;