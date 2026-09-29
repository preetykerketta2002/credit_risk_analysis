const fs = require("fs");
const path = require("path");

const { parse } = require("csv-parse/sync");

const {
  sequelize,
  Entity,
  CreditOutcome,
  FactorThreshold,
} = require("../models");

const { preprocessEntity } = require("../preprocessing/preprocessEntity");

// ==================================================
// FILE PATHS
// ==================================================

const DATASET_PATH = path.join(
  __dirname,
  "../../data/credit_risk_dataset_50_entities.csv"
);

const THRESHOLD_PATH = path.join(
  __dirname,
  "../../data/factor_thresholds_evaluator_global-truth.csv"
);

// ==================================================
// CSV READER
// ==================================================

function readCsv(filePath) {
  const fileContent = fs.readFileSync(filePath, "utf-8");

  return parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  });
}

// ==================================================
// SAFE NUMBER CONVERSION
// ==================================================

function toNumber(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number) ? number : null;
}

// ==================================================
// IMPORT ENTITIES + OUTCOMES
// ==================================================

async function importEntities() {
  console.log("\n====================================");
  console.log("IMPORTING CREDIT RISK DATASET");
  console.log("====================================\n");

  const rows = readCsv(DATASET_PATH);

  console.log(`[+] Rows found: ${rows.length}`);

  let successful = 0;
  let failed = 0;

  for (const [index, row] of rows.entries()) {
    const rowNumber = index + 2;

    console.log(`Processing row ${rowNumber}: ${row.entity_id}`);

    try {
      // --------------------------------------
      // Preprocess entity data
      // --------------------------------------

      const result = preprocessEntity(row);

      if (!result.success) {
        failed++;

        console.error(`[-] Row ${rowNumber} rejected`);
        console.error(result.errors);

        continue;
      }

      // --------------------------------------
      // Save entity
      // --------------------------------------

      await Entity.upsert(result.data);

      // --------------------------------------
      // Save historical outcome
      // --------------------------------------

      const outcomeData = {
        entity_id: row.entity_id,

        pd_1y_pct: toNumber(row.PD_1y_pct),

        lgd_pct: toNumber(row.LGD_pct),

        ead_usd_m: toNumber(row.EAD_usd_m),

        risk_bucket: row.risk_bucket,

        implied_rating: row.implied_rating || null,
      };

      await CreditOutcome.upsert(outcomeData);

      successful++;

      console.log(`[+] ${row.entity_id} imported`);

    } catch (error) {
      failed++;

      console.error(
        `[-] Failed row ${rowNumber}:`,
        error.message
      );
    }
  }

  console.log("\n====================================");
  console.log("ENTITY IMPORT SUMMARY");
  console.log("====================================");

  console.log(`Total rows : ${rows.length}`);
  console.log(`Successful : ${successful}`);
  console.log(`Failed     : ${failed}`);
}

// ==================================================
// IMPORT THRESHOLD RULES
// ==================================================

async function importThresholds() {
  console.log("\n====================================");
  console.log("IMPORTING THRESHOLD RULES");
  console.log("====================================\n");

  const rows = readCsv(THRESHOLD_PATH);

  console.log(`[+] Threshold rows found: ${rows.length}`);

  // --------------------------------------
  // Clear old threshold rules
  // --------------------------------------

  console.log("[+] Clearing existing threshold rules...");

  await FactorThreshold.destroy({
    where: {},
    truncate: true,
  });

  console.log("[+] Existing threshold rules cleared.");

  let successful = 0;
  let failed = 0;

  for (const [index, row] of rows.entries()) {
    const rowNumber = index + 2;

    try {
      const factor = row.factor?.trim();

      const startRange = toNumber(row.start_range);

      const endRange = toNumber(row.end_range);

      const evaluation = row.evaluation?.trim();

      // --------------------------------------
      // Validate threshold row
      // --------------------------------------

      if (!factor) {
        throw new Error("factor is missing");
      }

      // Either BOTH ranges must exist
      // OR BOTH ranges can be empty.
      if (
        (startRange === null && endRange !== null) ||
        (startRange !== null && endRange === null)
      ) {
        throw new Error(
          "start_range and end_range must both be provided or both be empty"
        );
      }

      if (!["Low", "Medium", "High"].includes(evaluation)) {
        throw new Error(`Invalid evaluation: ${evaluation}`);
      }

      // --------------------------------------
      // Insert threshold
      // --------------------------------------

      await FactorThreshold.create({
        factor_key: factor,
        start_range: startRange,
        end_range: endRange,
        evaluation: evaluation,
      });

      successful++;

    } catch (error) {
      failed++;

      console.error(
        `[-] Threshold row ${rowNumber} failed:`,
        error.message
      );
    }
  }

  console.log("\n====================================");
  console.log("THRESHOLD IMPORT SUMMARY");
  console.log("====================================");

  console.log(`Total rows : ${rows.length}`);
  console.log(`Successful : ${successful}`);
  console.log(`Failed     : ${failed}`);
}

// ==================================================
// MAIN
// ==================================================

async function main() {
  try {
    await sequelize.authenticate();

    console.log("[+] Connected to MySQL");

    await importEntities();

    await importThresholds();

    console.log("\n====================================");
    console.log("IMPORT COMPLETED");
    console.log("====================================\n");

  } catch (error) {
    console.error("[-] Import failed:", error);

  } finally {
    await sequelize.close();
  }
}

main();