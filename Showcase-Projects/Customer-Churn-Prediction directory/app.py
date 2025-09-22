import streamlit as st
import pandas as pd
import numpy as np
import pickle

# --------------------------
# Load Model and Scaler
# --------------------------
model = pickle.load(open("churn_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# Column names used in training
feature_columns = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 'PhoneService',
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'Contract', 'PaperlessBilling', 'PaymentMethod', 'MonthlyCharges', 'TotalCharges'
]

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Customer Churn Prediction", layout="wide")
st.title("Customer Churn Prediction App")
st.write("Predict if a customer is likely to churn based on their details.")

# --------------------------
# Sidebar Input
# --------------------------
st.sidebar.header("Enter Customer Details")

input_data = {}
# Default numeric values for example
default_values = {
    'gender': 0, 'SeniorCitizen': 0, 'Partner': 0, 'Dependents': 0, 'tenure': 0,
    'PhoneService': 1, 'MultipleLines': 0, 'InternetService': 0, 'OnlineSecurity': 0,
    'OnlineBackup': 0, 'DeviceProtection': 0, 'TechSupport': 0, 'StreamingTV': 0,
    'StreamingMovies': 0, 'Contract': 0, 'PaperlessBilling': 1, 'PaymentMethod': 0,
    'MonthlyCharges': 0.0, 'TotalCharges': 0.0
}

# Create inputs
for col in feature_columns:
    if col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
        input_data[col] = st.sidebar.number_input(col, value=float(default_values[col]))
    else:
        input_data[col] = st.sidebar.number_input(col, value=int(default_values[col]))

# Convert to DataFrame
features = pd.DataFrame([input_data])

# --------------------------
# Scale numeric features
# --------------------------
numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
features[numeric_cols] = scaler.transform(features[numeric_cols])

# --------------------------
# Prediction
# --------------------------
if st.button("Predict Churn"):
    pred = model.predict(features)
    pred_proba = model.predict_proba(features)[0][1]
    
    if pred[0] == 1:
        st.error(f"Customer is likely to CHURN! Probability: {pred_proba:.2f}")
    else:
        st.success(f"Customer is NOT likely to churn. Probability of churn: {pred_proba:.2f}")

# --------------------------
# Notes
# --------------------------
st.markdown("---")
st.markdown("""
**About this App:**
- Enter customer details in the sidebar.
- Categorical features are encoded numerically as done during training.
- Numeric features are scaled using the saved StandardScaler.
- Random Forest model predicts churn probability.
""")
