const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const FactorEvaluation = sequelize.define('FactorEvaluation', {
  factor_eval_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  evaluation_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: { model: 'evaluations', key: 'evaluation_id' }
  },
  factor_key: { type: DataTypes.STRING(100), allowNull: false },
  raw_value: { type: DataTypes.DECIMAL(12, 4) },
  evaluation: { type: DataTypes.ENUM('Low', 'Medium', 'High'), allowNull: false }
}, {
  tableName: 'factor_evaluations',
  timestamps: false
});

module.exports = FactorEvaluation;