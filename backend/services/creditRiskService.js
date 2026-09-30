const { evaluateEntity } = require("./ruleEngine");
const { predictCreditRisk } = require("./mlService");

async function evaluateCreditRisk(applicationData) {
  if (!applicationData) {
    throw new Error("Application data is required");
  }

  // ---------------------------------------------
  // 1. Rule-based factor evaluation
  // ---------------------------------------------
  const ruleResult = await evaluateEntity(applicationData);

  // ---------------------------------------------
  // 2. ML prediction
  // ---------------------------------------------
  const mlResult = await predictCreditRisk(applicationData);

  const mlPrediction = mlResult.predicted_risk;

  const ruleSummary = ruleResult.summary;

  // ---------------------------------------------
  // 3. Check for significant rule concerns
  // ---------------------------------------------
  const hasHighRiskFactors = ruleSummary.high > 0;

  const hasMediumRiskFactors = ruleSummary.medium > 0;

  // ---------------------------------------------
  // 4. Determine review status
  // ---------------------------------------------
  let decisionStatus = "Normal";

  if (mlPrediction === "High" || hasHighRiskFactors) {
    decisionStatus = "Review Required";
  } else if (hasMediumRiskFactors) {
    decisionStatus = "Review Recommended";
  }

  // ---------------------------------------------
  // 5. Check whether ML and rule signals agree
  // ---------------------------------------------
  let ruleSignal = "Low";

  if (ruleSummary.high > 0) {
    ruleSignal = "High";
  } else if (ruleSummary.medium > 0) {
    ruleSignal = "Medium";
  }

  const signalsAgree = mlPrediction === ruleSignal;

  // ---------------------------------------------
  // 6. Extract concerning factors
  // ---------------------------------------------
  const riskFactors = [];

  for (const [factor, evaluation] of Object.entries(
    ruleResult.factor_evaluations,
  )) {
    if (evaluation === "High" || evaluation === "Medium") {
      riskFactors.push({
        factor,
        evaluation,
      });
    }
  }

  // ---------------------------------------------
  // 7. Final response
  // ---------------------------------------------
  return {
    entity_id: applicationData.entity_id || null,

    final_evaluation: mlPrediction,

    ml_prediction: mlPrediction,

    rule_assessment: {
      low: ruleSummary.low,
      medium: ruleSummary.medium,
      high: ruleSummary.high,
    },

    signals_agree: signalsAgree,

    decision_status: decisionStatus,

    risk_factors: riskFactors,

    factor_evaluations: ruleResult.factor_evaluations,
  };
}

module.exports = {
  evaluateCreditRisk,
};
