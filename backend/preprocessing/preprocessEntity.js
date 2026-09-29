// preprocessing/preprocessEntity.js

const { cleanEntity } = require('./clean');
const { validateEntity } = require('./validator');
const { validateDomainRules } = require('./domainValidator');


function preprocessEntity(rawData) {

    // --------------------------------
    // Step 1: Clean raw input
    // --------------------------------

    const cleanedData = cleanEntity(rawData);


    // --------------------------------
    // Step 2: Structural validation
    // --------------------------------

    const validationResult = validateEntity(cleanedData);

    if (!validationResult.valid) {

        return {
            success: false,
            errors: validationResult.errors,
            data: cleanedData
        };
    }


    // --------------------------------
    // Step 3: Domain validation
    // --------------------------------

    const domainErrors = validateDomainRules(cleanedData);

    if (domainErrors.length > 0) {

        return {
            success: false,
            errors: domainErrors,
            data: cleanedData
        };
    }


    // --------------------------------
    // Step 4: Return clean data
    // --------------------------------

    return {
        success: true,
        errors: [],
        data: cleanedData
    };
}


module.exports = {
    preprocessEntity
};