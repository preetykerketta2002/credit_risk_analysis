// preprocessing/domainValidator.js


function validateNonNegative(data, fields) {

    const errors = [];

    for (const field of fields) {

        const value = data[field];

        if (value === null || value === undefined) {
            continue;
        }

        if (value < 0) {
            errors.push(
                `${field} cannot be negative`
            );
        }
    }

    return errors;
}


function validatePercentageRange(data, fields) {

    const errors = [];

    for (const field of fields) {

        const value = data[field];

        if (value === null || value === undefined) {
            continue;
        }

        if (value < 0 || value > 100) {
            errors.push(
                `${field} must be between 0 and 100`
            );
        }
    }

    return errors;
}


function validateDomainRules(data) {

    const errors = [];

    // Values that represent counts/durations.
    errors.push(
        ...validateNonNegative(data, [
            'years_in_operation',
            'dso_days',
            'dpo_days',
            'dio_days',
            'esg_controversies_3y',
            'payment_incidents_12m',
            'legal_disputes_open'
        ])
    );


    // Scores and percentages explicitly bounded by 0–100.
    errors.push(
        ...validatePercentageRange(data, [
            'governance_score_0_100',
            'country_risk_0_100',
            'fx_revenue_pct'
        ])
    );


    return errors;
}


module.exports = {
    validateDomainRules
};