const sequelize = require("../config/database");
const { CreditOutcome } = require("../models");

async function cleanupCreditOutcomes() {
  try {
    await sequelize.authenticate();

    console.log("[+] Connected to MySQL");

    // Find all entity IDs having duplicate outcomes
    const [duplicates] = await sequelize.query(`
      SELECT entity_id, COUNT(*) AS count
      FROM credit_outcomes
      GROUP BY entity_id
      HAVING COUNT(*) > 1
    `);

    console.log(
      `[+] Duplicate entities found: ${duplicates.length}`
    );

    if (duplicates.length === 0) {
      console.log("[+] No duplicate credit outcomes found.");
      return;
    }

    // Keep the oldest record for every entity
    // and delete the remaining duplicates.
    for (const duplicate of duplicates) {
      const entityId = duplicate.entity_id;

      const rows = await CreditOutcome.findAll({
        where: {
          entity_id: entityId,
        },
        order: [["id", "ASC"]],
      });

      const rowsToDelete = rows.slice(1);

      for (const row of rowsToDelete) {
        await row.destroy();
      }

      console.log(
        `[+] ${entityId}: kept 1, deleted ${rowsToDelete.length}`
      );
    }

    console.log("\n====================================");
    console.log("CLEANUP COMPLETED");
    console.log("====================================");

    const [result] = await sequelize.query(`
      SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT entity_id) AS unique_entities
      FROM credit_outcomes
    `);

    console.log(
      `Total credit outcomes : ${result[0].total_rows}`
    );

    console.log(
      `Unique entities       : ${result[0].unique_entities}`
    );

  } catch (error) {
    console.error("[X] Cleanup failed:");
    console.error(error);
  } finally {
    await sequelize.close();
  }
}

cleanupCreditOutcomes();