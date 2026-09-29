const mysql = require('mysql2/promise');
require('dotenv').config();

async function syncDatabase() {
  try {
    // -----------------------------------------
    // 1. Create database if it doesn't exist
    // -----------------------------------------
    const connection = await mysql.createConnection({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASS
    });

    const dbName = process.env.DB_NAME || 'credit_risk_evaluator';

    await connection.query(
      `CREATE DATABASE IF NOT EXISTS \`${dbName}\`;`
    );

    console.log(
      `[+] Database '${dbName}' ensured/created successfully.`
    );

    await connection.end();

    // -----------------------------------------
    // 2. Load Sequelize
    // -----------------------------------------
    const { sequelize } = require('../models');

    await sequelize.authenticate();

    console.log('[+] Connected to MySQL database via Sequelize.');

    // -----------------------------------------
    // 3. Remove old UNIQUE indexes
    // -----------------------------------------
    const queryInterface = sequelize.getQueryInterface();

    const oldIndexes = [
      'factor_key',
      'factor_key_2',
      'factor_key_3',
      'factor_thresholds_factor_key'
    ];

    for (const indexName of oldIndexes) {
      try {
        await queryInterface.removeIndex(
          'factor_thresholds',
          indexName
        );

        console.log(
          `[+] Removed old index: ${indexName}`
        );
      } catch (error) {
        // Index may not exist on a fresh database
        console.log(
          `[-] Index ${indexName} not found or already removed`
        );
      }
    }

    // -----------------------------------------
    // 4. Sync all Sequelize models
    // -----------------------------------------
    await sequelize.sync({ alter: true });

    console.log(
      '[+] All tables created/updated successfully using Sequelize!'
    );

    // -----------------------------------------
    // 5. Make sure factor_key has a NORMAL index
    // -----------------------------------------
    const indexes = await queryInterface.showIndex(
      'factor_thresholds'
    );

    const indexExists = indexes.some(
      index =>
        index.name === 'idx_factor_thresholds_factor_key'
    );

    if (!indexExists) {
      await queryInterface.addIndex(
        'factor_thresholds',
        ['factor_key'],
        {
          name: 'idx_factor_thresholds_factor_key',
          unique: false
        }
      );

      console.log(
        '[+] Created non-unique factor_key index.'
      );
    }

    console.log('[+] Database synchronization completed.');

    process.exit(0);

  } catch (error) {
    console.error('[-] Database sync error:', error);
    process.exit(1);
  }
}

syncDatabase();