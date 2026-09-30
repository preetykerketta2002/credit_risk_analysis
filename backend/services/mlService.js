const ML_API_URL =
    process.env.ML_API_URL ||
    "http://127.0.0.1:8000/predict";


async function predictCreditRisk(applicationData) {

    const response = await fetch(
        ML_API_URL,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(applicationData)
        }
    );


    const data = await response.json();


    if (!response.ok) {

        const error = new Error(
            `ML prediction failed with status ${response.status}`
        );

        error.status = response.status;
        error.details = data;

        throw error;
    }


    return data;
}


module.exports = {
    predictCreditRisk
};