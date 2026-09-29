const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Evaluation = sequelize.define('Evaluation', {
  evaluation_id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
  entity_id: {
    type: DataTypes.STRING(50),
    allowNull: false,
    references: { model: 'entities', key: 'entity_id' }
  },
  evaluation_date: { type: DataTypes.DATE, defaultValue: DataTypes.NOW },
  low_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  medium_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  high_count: { type: DataTypes.INTEGER, defaultValue: 0 },
  is_red_flag_triggered: { type: DataTypes.BOOLEAN, defaultValue: false },
  red_flag_reasons: { type: DataTypes.JSON },
  summary: { type: DataTypes.TEXT },
  final_evaluation: { type: DataTypes.ENUM('Low', 'Medium', 'High'), allowNull: false }
}, {
  tableName: 'evaluations',
  timestamps: false
});

module.exports = Evaluation;