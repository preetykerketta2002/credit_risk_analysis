const sequelize = require('../config/database');
const Entity = require('./Entity');
const FactorThreshold = require('./FactorThreshold');
const Evaluation = require('./Evaluation');
const FactorEvaluation = require('./FactorEvaluation');
const CreditOutcome = require('./CreditOutcome');

// Relational Associations
Entity.hasMany(Evaluation, { foreignKey: 'entity_id', onDelete: 'CASCADE' });
Evaluation.belongsTo(Entity, { foreignKey: 'entity_id' });

Evaluation.hasMany(FactorEvaluation, { foreignKey: 'evaluation_id', onDelete: 'CASCADE' });
FactorEvaluation.belongsTo(Evaluation, { foreignKey: 'evaluation_id' });

Entity.hasOne(CreditOutcome, {
    foreignKey: 'entity_id',
    onDelete: 'CASCADE'
});

CreditOutcome.belongsTo(Entity, {
    foreignKey: 'entity_id'
});

module.exports = {
    sequelize,
    Entity,
    CreditOutcome,
    FactorThreshold,
    Evaluation,
    FactorEvaluation
};

