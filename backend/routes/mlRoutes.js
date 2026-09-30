const express = require("express");

const {
    predictCreditRisk
} = require("../services/mlService");


const router = express.Router();


router.post("/predict", async (req, res) => {

    try {

        const applicationData = req.body;


        const result = await predictCreditRisk(
            applicationData
        );


        return res.status(200).json(result);

    } catch (error) {

        console.error(
            "ML prediction error:",
            error
        );


        return res.status(
            error.status || 500
        ).json({

            message: "Credit risk prediction failed",

            error: error.details || error.message

        });
    }
});


module.exports = router;