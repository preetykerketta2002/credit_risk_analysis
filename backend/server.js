const express = require("express");
require("dotenv").config();

const mlRoutes = require("./routes/mlRoutes");
const creditRiskRoutes = require("./routes/creditRiskRoutes");


const app = express();


// ============================================================
// Middleware
// ============================================================

app.use(express.json());


// ============================================================
// Routes
// ============================================================

// ML-only prediction
app.use("/api/ml", mlRoutes);


// Complete credit risk evaluation
app.use(
    "/api/credit-risk",
    creditRiskRoutes
);


// ============================================================
// Health Check
// ============================================================

app.get("/", (req, res) => {

    res.json({
        message: "Credit Risk Backend API is running"
    });

});


// ============================================================
// Start Server
// ============================================================

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {

    console.log(
        `Backend server running on http://localhost:${PORT}`
    );

});