const express = require("express");

const {
    evaluateCreditRisk
} = require("../services/creditRiskService");


const router = express.Router();


// ============================================================
// COMPLETE CREDIT RISK EVALUATION
// ============================================================

router.post("/evaluate", async (req, res) => {

    try {

        const applicationData = req.body;

        const result =
            await evaluateCreditRisk(
                applicationData
            );

        return res
            .status(200)
            .json(result);

    } catch (error) {

        console.error(
            "Credit risk evaluation error:",
            error
        );

        return res
            .status(error.status || 500)
            .json({

                message:
                    "Credit risk evaluation failed",

                error:
                    error.message,

                details:
                    error.details || null

            });
    }

});


module.exports = router;