// scripts/sync.js
const { sequelize } = require('../models');

async function syncDatabase() {
  try {
    await sequelize.authenticate();
    console.log('[+] Connected to MySQL database successfully.');

    // Automatically sync models to MySQL tables
    await sequelize.sync({ alter: true });
    console.log('[+] All 4 tables created/updated successfully using Sequelize!');

    process.exit(0);
  } catch (error) {
    console.error('[-] Database sync error:', error);
    process.exit(1);
  }
}

syncDatabase();