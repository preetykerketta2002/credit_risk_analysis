const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const CreditOutcome = sequelize.define('CreditOutcome', {

    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },

    entity_id: {
    type: DataTypes.STRING(50),
    allowNull: false,
    unique: true,
    references: {
        model: 'entities',
        key: 'entity_id'
    }
},

    pd_1y_pct: {
        type: DataTypes.DECIMAL(8, 4)
    },

    lgd_pct: {
        type: DataTypes.DECIMAL(8, 4)
    },

    ead_usd_m: {
        type: DataTypes.DECIMAL(12, 2)
    },

    risk_bucket: {
        type: DataTypes.ENUM(
            'Low',
            'Medium',
            'High'
        ),
        allowNull: false
    },

    implied_rating: {
        type: DataTypes.STRING(20)
    }

}, {
    tableName: 'credit_outcomes',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at'
});

module.exports = CreditOutcome;