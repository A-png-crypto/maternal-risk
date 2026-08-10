async function predictRisk() {

    const loading =
        document.getElementById("loading");

    const resultCard =
        document.getElementById("result-card");


    // ==========================================
    // GET INPUTS
    // ==========================================

    const patient = {

        Age:
            document.getElementById("Age").value,

        Systolic_BP:
            document.getElementById("Systolic_BP").value,

        Diastolic_BP:
            document.getElementById("Diastolic_BP").value,

        Blood_Glucose:
            document.getElementById("Blood_Glucose").value,

        BMI:
            document.getElementById("BMI").value,

        Heart_Rate:
            document.getElementById("Heart_Rate").value,

        Parity:
            document.getElementById("Parity").value,

        Hemoglobin:
            document.getElementById("Hemoglobin").value

    };


    // ==========================================
    // CHECK INPUTS
    // ==========================================

    for (
        const key in patient
    ) {

        if (
            patient[key] === ""
        ) {

            alert(
                "Please complete all eight fields."
            );

            return;
        }

    }


    // ==========================================
    // SHOW LOADING
    // ==========================================

    loading.classList.remove(
        "hidden"
    );


    // ==========================================
    // SEND DATA TO PYTHON
    // ==========================================

    try {

        const response =
            await fetch(
                "/predict",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            patient
                        )

                }
            );


        const data =
            await response.json();


        // ======================================
        // HIDE LOADING
        // ======================================

        loading.classList.add(
            "hidden"
        );


        // ======================================
        // ERROR
        // ======================================

        if (!data.success) {

            resultCard.innerHTML = `

                <div class="result-placeholder">

                    <div class="large-icon">
                        ⚠️
                    </div>

                    <h3>
                        Prediction Error
                    </h3>

                    <p>
                        ${data.error}
                    </p>

                </div>

            `;

            return;

        }


        // ======================================
        // RISK LEVEL
        // ======================================

        const risk =
            data.risk_level;


        let riskClass =
            "";

        let riskIcon =
            "🩺";


        if (
            risk.toLowerCase()
                .includes("low")
        ) {

            riskClass =
                "low-risk";

            riskIcon =
                "🟢";

        }


        else if (
            risk.toLowerCase()
                .includes("medium")
        ) {

            riskClass =
                "medium-risk";

            riskIcon =
                "🟡";

        }


        else if (
            risk.toLowerCase()
                .includes("high")
        ) {

            riskClass =
                "high-risk";

            riskIcon =
                "🔴";

        }


        // ======================================
        // PROBABILITIES
        // ======================================

        let probabilityHTML =
            "";


        for (
            const [level, probability]
            of Object.entries(
                data.probabilities
            )
        ) {

            probabilityHTML += `

                <div class="probability-row">

                    <div class="probability-label">

                        <span>
                            ${level}
                        </span>

                        <strong>
                            ${probability}%
                        </strong>

                    </div>

                    <div class="progress">

                        <div
                            class="progress-bar"
                            style="width:${probability}%">
                        </div>

                    </div>

                </div>

            `;

        }


        // ======================================
        // DISPLAY RESULT
        // ======================================

        resultCard.innerHTML = `

            <div class="risk-result">

                <div class="risk-icon">
                    ${riskIcon}
                </div>

                <h2 class="${riskClass}">
                    ${risk} Risk
                </h2>

                <p>
                    ANN prediction completed
                    successfully.
                </p>

                <div class="probability">

                    <h3>
                        Prediction Probability
                    </h3>

                    ${probabilityHTML}

                </div>

            </div>

        `;


    }

    catch (error) {

        loading.classList.add(
            "hidden"
        );


        resultCard.innerHTML = `

            <div class="result-placeholder">

                <div class="large-icon">
                    ❌
                </div>

                <h3>
                    Connection Error
                </h3>

                <p>
                    Make sure the Flask
                    Python server is running.
                </p>

            </div>

        `;

        console.error(
            error
        );

    }

}
