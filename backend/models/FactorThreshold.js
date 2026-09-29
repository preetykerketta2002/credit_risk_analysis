const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const FactorThreshold = sequelize.define(
  'FactorThreshold',
  {
    threshold_id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },

    factor_key: {
      type: DataTypes.STRING(150),
      allowNull: false
    },

    start_range: {
      type: DataTypes.DECIMAL(20, 4),
      allowNull: true
    },

    end_range: {
      type: DataTypes.DECIMAL(20, 4),
      allowNull: true
    },

    evaluation: {
      type: DataTypes.ENUM('Low', 'Medium', 'High'),
      allowNull: false
    }
  },
  {
    tableName: 'factor_thresholds',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at',

    indexes: [
      {
        name: 'idx_factor_thresholds_factor_key',
        fields: ['factor_key']
      }
    ]
  }
);

module.exports = FactorThreshold;