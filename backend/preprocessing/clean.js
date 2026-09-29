// preprocessing/clean.js

const {
    NUMERICAL_FIELDS,
    CATEGORICAL_FIELDS
} = require('./constants');


function cleanString(value) {
    if (value === null || value === undefined) {
        return null;
    }

    const cleaned = String(value).trim();

    if (cleaned === '') {
        return null;
    }

    return cleaned;
}


function cleanNumber(value) {
    if (value === null || value === undefined) {
        return null;
    }

    if (typeof value === 'string' && value.trim() === '') {
        return null;
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return null;
    }

    return number;
}


function cleanEntity(data) {
    const cleaned = {};

    // -----------------------------
    // Clean numerical fields
    // -----------------------------

    for (const field of NUMERICAL_FIELDS) {
        cleaned[field] = cleanNumber(data[field]);
    }


    // -----------------------------
    // Clean categorical fields
    // -----------------------------

    for (const field of CATEGORICAL_FIELDS) {
        cleaned[field] = cleanString(data[field]);
    }


    // -----------------------------
    // Clean identifiers
    // -----------------------------

    cleaned.entity_id = cleanString(data.entity_id);
    cleaned.entity_name = cleanString(data.entity_name);


    return cleaned;
}


module.exports = {
    cleanEntity
};