// models/index.js
const sequelize = require('../config/database');
const Entity = require('./Entity');
const FactorThreshold = require('./FactorThreshold');
const Evaluation = require('./Evaluation');
const FactorEvaluation = require('./FactorEvaluation');

// Relational Associations
Entity.hasMany(Evaluation, { foreignKey: 'entity_id', onDelete: 'CASCADE' });
Evaluation.belongsTo(Entity, { foreignKey: 'entity_id' });

Evaluation.hasMany(FactorEvaluation, { foreignKey: 'evaluation_id', onDelete: 'CASCADE' });
FactorEvaluation.belongsTo(Evaluation, { foreignKey: 'evaluation_id' });

module.exports = {
  sequelize,
  Entity,
  FactorThreshold,
  Evaluation,
  FactorEvaluation
};