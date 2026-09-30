const { Entity, CreditOutcome } = require("../models");
const { evaluateEntity } = require("../services/ruleEngine");
const { predictCreditRisk } = require("../services/mlService");


// ============================================================
// COMPARE RULE ENGINE VS ML MODEL
// ============================================================

async function compareRiskSignals() {

    console.log("=".repeat(70));
    console.log("RULE ENGINE vs ML MODEL COMPARISON");
    console.log("=".repeat(70));


    // --------------------------------------------------------
    // Load all historical entities
    // --------------------------------------------------------

    const entities = await Entity.findAll({
        order: [["entity_id", "ASC"]]
    });


    console.log(`Total entities: ${entities.length}`);


    const results = [];


    // --------------------------------------------------------
    // Evaluate each entity
    // --------------------------------------------------------

    for (const entityModel of entities) {

        const entity =
            entityModel.toJSON();


        try {

            // ------------------------------------------------
            // 1. Historical actual risk
            // ------------------------------------------------

            const outcome =
                await CreditOutcome.findOne({
                    where: {
                        entity_id:
                            entity.entity_id
                    }
                });


            const actualRisk =
                outcome
                    ? outcome.risk_bucket
                    : null;


            // ------------------------------------------------
            // 2. Rule-based evaluation
            // ------------------------------------------------

            const ruleResult =
                await evaluateEntity(entity);


            // ------------------------------------------------
            // 3. ML prediction
            // ------------------------------------------------

            const mlResult =
                await predictCreditRisk(entity);


            const mlPrediction =
                mlResult.predicted_risk;


            // ------------------------------------------------
            // 4. Determine rule signal
            // ------------------------------------------------

            let ruleSignal = "Low";


            if (ruleResult.summary.high > 0) {

                ruleSignal = "High";

            } else if (
                ruleResult.summary.medium > 0
            ) {

                ruleSignal = "Medium";
            }


            // ------------------------------------------------
            // 5. Check agreement
            // ------------------------------------------------

            const signalsAgree =
                ruleSignal === mlPrediction;


            // ------------------------------------------------
            // 6. Store result
            // ------------------------------------------------

            results.push({

                entity_id:
                    entity.entity_id,

                entity_name:
                    entity.entity_name,

                actual_risk:
                    actualRisk,

                ml_prediction:
                    mlPrediction,

                rule_signal:
                    ruleSignal,

                rule_low:
                    ruleResult.summary.low,

                rule_medium:
                    ruleResult.summary.medium,

                rule_high:
                    ruleResult.summary.high,

                signals_agree:
                    signalsAgree

            });


            console.log(
                `${entity.entity_id} | ` +
                `Actual=${actualRisk} | ` +
                `ML=${mlPrediction} | ` +
                `Rule=${ruleSignal} | ` +
                `Agree=${signalsAgree}`
            );


        } catch (error) {

            console.error(
                `Failed for ${entity.entity_id}:`,
                error.message
            );

        }
    }


    // ========================================================
    // SUMMARY
    // ========================================================

    console.log("\n");
    console.log("=".repeat(70));
    console.log("SUMMARY");
    console.log("=".repeat(70));


    const agreementCount =
        results.filter(
            result =>
                result.signals_agree
        ).length;


    const disagreementCount =
        results.length -
        agreementCount;


    console.log(
        `Entities evaluated : ${results.length}`
    );

    console.log(
        `Agreement          : ${agreementCount}`
    );

    console.log(
        `Disagreement       : ${disagreementCount}`
    );


    // --------------------------------------------------------
    // ML accuracy against historical outcome
    // --------------------------------------------------------

    const mlCorrect =
        results.filter(
            result =>
                result.actual_risk ===
                result.ml_prediction
        ).length;


    const mlAccuracy =
        results.length > 0
            ? (
                mlCorrect /
                results.length *
                100
            ).toFixed(2)
            : "0.00";


    console.log(
        `ML accuracy        : ${mlAccuracy}%`
    );


    // --------------------------------------------------------
    // Rule accuracy against historical outcome
    // --------------------------------------------------------

    const ruleCorrect =
        results.filter(
            result =>
                result.actual_risk ===
                result.rule_signal
        ).length;


    const ruleAccuracy =
        results.length > 0
            ? (
                ruleCorrect /
                results.length *
                100
            ).toFixed(2)
            : "0.00";


    console.log(
        `Rule accuracy      : ${ruleAccuracy}%`
    );


    console.log("=".repeat(70));


    // --------------------------------------------------------
    // Print detailed disagreement cases
    // --------------------------------------------------------

    console.log("\n");
    console.log("DISAGREEMENT CASES");
    console.log("=".repeat(70));


    const disagreements =
        results.filter(
            result =>
                !result.signals_agree
        );


    if (disagreements.length === 0) {

        console.log(
            "No disagreements found."
        );

    } else {

        for (const result of disagreements) {

            console.log(
                `${result.entity_id} | ` +
                `Actual=${result.actual_risk} | ` +
                `ML=${result.ml_prediction} | ` +
                `Rule=${result.rule_signal} | ` +
                `Low=${result.rule_low} ` +
                `Medium=${result.rule_medium} ` +
                `High=${result.rule_high}`
            );

        }
    }


    console.log("=".repeat(70));
}


// ============================================================
// RUN
// ============================================================

compareRiskSignals()
    .then(() => {

        console.log(
            "\nComparison completed."
        );

        process.exit(0);

    })
    .catch(error => {

        console.error(
            "\nComparison failed:",
            error
        );

        process.exit(1);

    });