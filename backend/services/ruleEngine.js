const { FactorThreshold } = require("../models");

// ==================================================
// CATEGORICAL VALUE MAPPINGS
// ==================================================
//
// Entity table stores human-readable values.
// Threshold table stores numeric codes.
//
// ==================================================

const FACTOR_MAPPINGS = {
  auditor_tier: {
    Other: 0,
    Big4: 1,
  },

  financials_audited: {
    No: 0,
    Yes: 1,
  },

  industry_cyclicality: {
    Low: 0,
    Medium: 1,
    High: 2,
  },

  hedging_policy: {
    None: 0,
    Partial: 1,
    Comprehensive: 2,
  },

  covenant_quality: {
    Weak: 0,
    Standard: 1,
    Strong: 2,
  },

  sanctions_exposure: {
    None: 0,
    Indirect: 1,
    Direct: 2,
  },
};

// ==================================================
// ENTITY FIELD → THRESHOLD TABLE FACTOR KEY
// ==================================================
//
// The entity table uses clean field names.
//
// The threshold CSV uses encoded factor names for
// categorical fields.
//
// ==================================================

const THRESHOLD_FACTOR_KEYS = {
  auditor_tier:
    "auditor_tier_code (Other=0, Big4=1)",

  financials_audited:
    "financials_audited_code (No=0, Yes=1)",

  industry_cyclicality:
    "industry_cyclicality_code (Low=0, Medium=1, High=2)",

  hedging_policy:
    "hedging_policy_code (None=0, Partial=1, Comprehensive=2)",

  covenant_quality:
    "covenant_quality_code (Weak=0, Standard=1, Strong=2)",

  sanctions_exposure:
    "sanctions_exposure_code (None=0, Indirect=1, Direct=2)",
};

// ==================================================
// EVALUATE SINGLE FACTOR
// ==================================================

async function evaluateFactor(factorKey, value) {
  // --------------------------------------
  // 1. Validate factor key
  // --------------------------------------

  if (!factorKey) {
    throw new Error("factorKey is required");
  }

  // --------------------------------------
  // 2. Handle missing value
  // --------------------------------------

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  // --------------------------------------
  // 3. Convert categorical value to code
  // --------------------------------------

  let evaluationValue = value;

  if (FACTOR_MAPPINGS[factorKey]) {
    const mapping = FACTOR_MAPPINGS[factorKey];

    if (!(value in mapping)) {
      throw new Error(
        `Invalid value '${value}' for factor '${factorKey}'`
      );
    }

    evaluationValue = mapping[value];
  }

  // --------------------------------------
  // 4. Find corresponding threshold factor
  // --------------------------------------

  const thresholdFactorKey =
    THRESHOLD_FACTOR_KEYS[factorKey] || factorKey;

  // --------------------------------------
  // 5. Fetch rules from database
  // --------------------------------------

  const rules = await FactorThreshold.findAll({
    where: {
      factor_key: thresholdFactorKey,
    },
    order: [["threshold_id", "ASC"]],
  });

  if (rules.length === 0) {
    throw new Error(
      `No rules found for factor: ${factorKey}`
    );
  }

  // --------------------------------------
  // 6. Compare value against rules
  // --------------------------------------

  for (const rule of rules) {
    const start = rule.start_range;
    const end = rule.end_range;

    // Some categorical rules in the source sheet
    // have blank ranges. We do not invent a meaning
    // for those rows.
    if (start === null || end === null) {
      continue;
    }

    const numericValue = Number(evaluationValue);
    const numericStart = Number(start);
    const numericEnd = Number(end);

    if (
      numericValue >= numericStart &&
      numericValue <= numericEnd
    ) {
      return rule.evaluation;
    }
  }

  // --------------------------------------
  // 7. No matching range
  // --------------------------------------

  return null;
}

// ==================================================
// FACTORS TO EVALUATE
// ==================================================
//
// These are the factors that actually have rules
// in the threshold sheet.
//
// ownership_type is intentionally excluded because
// there is no ownership_type rule in the threshold CSV.
//
// ==================================================

const EVALUATION_FACTORS = [
  "revenue_usd_m",
  "ebitda_margin_pct",
  "ebit_margin_pct",
  "debt_to_equity",
  "interest_coverage",
  "dscr",
  "current_ratio",
  "quick_ratio",
  "revenue_cagr_3y_pct",
  "years_in_operation",
  "auditor_tier",
  "governance_score_0_100",
  "esg_controversies_3y",
  "country_risk_0_100",
  "industry_cyclicality",
  "fx_revenue_pct",
  "hedging_policy",
  "collateral_coverage_pct",
  "covenant_quality",
  "payment_incidents_12m",
  "legal_disputes_open",
  "sanctions_exposure",
  "financials_audited"
];

// ==================================================
// EVALUATE COMPLETE ENTITY
// ==================================================

async function evaluateEntity(entity) {
  if (!entity) {
    throw new Error("Entity data is required");
  }

  const factorEvaluations = {};

  let lowCount = 0;
  let mediumCount = 0;
  let highCount = 0;

  // --------------------------------------
  // Evaluate every factor
  // --------------------------------------

  for (const factor of EVALUATION_FACTORS) {
    const value = entity[factor];

    // Missing input
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      factorEvaluations[factor] = null;
      continue;
    }

    try {
      const evaluation = await evaluateFactor(
        factor,
        value
      );

      factorEvaluations[factor] = evaluation;

      // Count evaluation levels
      if (evaluation === "Low") {
        lowCount++;
      } else if (evaluation === "Medium") {
        mediumCount++;
      } else if (evaluation === "High") {
        highCount++;
      }

    } catch (error) {
      factorEvaluations[factor] = {
        error: error.message,
      };
    }
  }

  // --------------------------------------
  // Return complete result
  // --------------------------------------

  return {
    entity_id: entity.entity_id,

    factor_evaluations: factorEvaluations,

    summary: {
      low: lowCount,
      medium: mediumCount,
      high: highCount,
    },
  };
}

// ==================================================
// EXPORT
// ==================================================

module.exports = {
  evaluateFactor,
  evaluateEntity,
};