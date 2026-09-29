// preprocessing/validator.js

const {
    NUMERICAL_FIELDS,
    REQUIRED_FIELDS,
    ALLOWED_VALUES
} = require('./constants');


function validateRequiredFields(data) {
    const errors = [];

    for (const field of REQUIRED_FIELDS) {
        const value = data[field];

        if (
            value === null ||
            value === undefined ||
            String(value).trim() === ''
        ) {
            errors.push(`${field} is required`);
        }
    }

    return errors;
}


function validateNumericalFields(data) {
    const errors = [];

    for (const field of NUMERICAL_FIELDS) {
        const value = data[field];

        // Missing values are allowed.
        // They will be handled later by the ML pipeline.
        if (value === null || value === undefined) {
            continue;
        }

        if (typeof value !== 'number' || !Number.isFinite(value)) {
            errors.push(
                `${field} must be a valid number`
            );
        }
    }

    return errors;
}


function validateCategoricalFields(data) {
    const errors = [];

    for (const [field, allowedValues] of Object.entries(ALLOWED_VALUES)) {

        const value = data[field];

        // Missing categorical values are allowed.
        if (value === null || value === undefined) {
            continue;
        }

        if (!allowedValues.includes(value)) {
            errors.push(
                `${field} must be one of: ${allowedValues.join(', ')}`
            );
        }
    }

    return errors;
}


function validateEntity(data) {

    const errors = [
        ...validateRequiredFields(data),
        ...validateNumericalFields(data),
        ...validateCategoricalFields(data)
    ];

    return {
        valid: errors.length === 0,
        errors
    };
}


module.exports = {
    validateEntity
};