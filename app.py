from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# DATASET
# =========================================================

DATASET_NAME = "POLY CLINIC,PENINSULA RD(2019).csv"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    DATASET_NAME
)


# =========================================================
# LOAD DATASET
# =========================================================

if not os.path.exists(DATASET_PATH):

    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )


df = pd.read_csv(DATASET_PATH)


# =========================================================
# EIGHT MATERNAL HEALTH FEATURES
# =========================================================

features = [
    "Age",
    "Systolic_BP",
    "Diastolic_BP",
    "Blood_Glucose",
    "BMI",
    "Heart_Rate",
    "Parity",
    "Hemoglobin"
]

target = "Risk_Level"


# =========================================================
# CHECK COLUMNS
# =========================================================

missing_columns = [
    column
    for column in features + [target]
    if column not in df.columns
]


if missing_columns:

    raise ValueError(
        "The following columns are missing from "
        f"your dataset: {missing_columns}\n\n"
        f"Columns found: {list(df.columns)}"
    )


# =========================================================
# PREPARE DATA
# =========================================================

data = df[
    features + [target]
].copy()


# Convert numerical columns

for column in features:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# Remove missing values

data = data.dropna()


# Remove duplicate records

data = data.drop_duplicates()


# =========================================================
# INPUT AND TARGET
# =========================================================

X = data[features]

y = data[target].astype(str)


# =========================================================
# ENCODE TARGET
# =========================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)


# =========================================================
# STANDARDIZATION
# =========================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)


# =========================================================
# ARTIFICIAL NEURAL NETWORK
# =========================================================

model = MLPClassifier(
    hidden_layer_sizes=(128, 64, 32),
    activation="relu",
    solver="adam",
    learning_rate_init=0.001,
    max_iter=2000,
    random_state=42
)


# =========================================================
# TRAIN MODEL
# =========================================================

model.fit(
    X_train_scaled,
    y_train
)


# =========================================================
# MODEL EVALUATION
# =========================================================

y_pred = model.predict(
    X_test_scaled
)


accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        accuracy=round(accuracy * 100, 2),
        precision=round(precision * 100, 2),
        recall=round(recall * 100, 2),
        f1=round(f1 * 100, 2),
        records=len(data)
    )


# =========================================================
# PREDICTION API
# =========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        values = request.get_json()


        # -----------------------------------------------
        # GET PATIENT VALUES
        # -----------------------------------------------

        patient = [

            float(values["Age"]),

            float(values["Systolic_BP"]),

            float(values["Diastolic_BP"]),

            float(values["Blood_Glucose"]),

            float(values["BMI"]),

            float(values["Heart_Rate"]),

            float(values["Parity"]),

            float(values["Hemoglobin"])

        ]


        # -----------------------------------------------
        # CREATE DATAFRAME
        # -----------------------------------------------

        patient_df = pd.DataFrame(
            [patient],
            columns=features
        )


        # -----------------------------------------------
        # SCALE
        # -----------------------------------------------

        patient_scaled = scaler.transform(
            patient_df
        )


        # -----------------------------------------------
        # PREDICT
        # -----------------------------------------------

        prediction = model.predict(
            patient_scaled
        )


        # -----------------------------------------------
        # RISK LEVEL
        # -----------------------------------------------

        risk_level = (
            label_encoder
            .inverse_transform(prediction)[0]
        )


        # -----------------------------------------------
        # PROBABILITY
        # -----------------------------------------------

        probabilities = model.predict_proba(
            patient_scaled
        )[0]


        probability_result = {}

        for class_name, probability in zip(
            label_encoder.classes_,
            probabilities
        ):

            probability_result[
                class_name
            ] = round(
                float(probability * 100),
                2
            )


        # -----------------------------------------------
        # RESPONSE
        # -----------------------------------------------

        return jsonify({

            "success": True,

            "risk_level": risk_level,

            "probabilities":
                probability_result

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 400


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )