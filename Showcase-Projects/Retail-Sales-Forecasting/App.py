import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import load_model
import joblib
import matplotlib.pyplot as plt

# ----------------------------
# Page config and dark theme
# ----------------------------
st.set_page_config(page_title="Retail Sales Forecasting", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    body {background-color: #0e1117; color: #ffffff;}
    .stButton>button {background-color: #1f77b4; color: white;}
    .stNumberInput>div>input {background-color: #1e1e1e; color: white;}
    .stSelectbox>div>div {background-color: #1e1e1e; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Retail Sales Forecasting Dashboard")

# ----------------------------
# Load models and scalers
# ----------------------------
hgb = joblib.load("hgb_model.pkl")
scaler = joblib.load("feature_scaler.pkl")
target_scaler = joblib.load("target_scaler.pkl")
lstm_model = load_model("lstm_model.h5", compile=False)

# ----------------------------
# User Inputs (3 Columns × 5 Rows)
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    store = st.number_input("Store Number", min_value=1)
    temperature = st.number_input("Temperature")
    markdown1 = st.number_input("MarkDown1")
    markdown4 = st.number_input("MarkDown4")
    cpi = st.number_input("CPI")

with col2:
    dept = st.number_input("Department Number", min_value=1)
    fuel_price = st.number_input("Fuel Price")
    markdown2 = st.number_input("MarkDown2")
    markdown5 = st.number_input("MarkDown5")
    unemployment = st.number_input("Unemployment")

with col3:
    markdown3 = st.number_input("MarkDown3")
    store_type = st.selectbox("Store Type", ["A","B","C"])
    size = st.number_input("Store Size")
    is_holiday = st.checkbox("Is Holiday")
    lag1 = st.number_input("Lag 1 Sales")
    lag2 = st.number_input("Lag 2 Sales")  # 6th field in col3, okay for last row

# ----------------------------
# Predict button
# ----------------------------
if st.button("Predict Sales"):
    
    # Encode store type
    le = LabelEncoder()
    le.fit(["A","B","C"])
    store_type_encoded = le.transform([store_type])[0]
    
    # Prepare input DataFrame
    input_df = pd.DataFrame([[temperature, fuel_price, markdown1, markdown2, markdown3, markdown4,
                              markdown5, cpi, unemployment, store_type_encoded, size, is_holiday,
                              lag1, lag2]],
                            columns=['Temperature','Fuel_Price','MarkDown1','MarkDown2','MarkDown3',
                                     'MarkDown4','MarkDown5','CPI','Unemployment','Type','Size',
                                     'IsHoliday','Lag_1','Lag_2'])
    
    # Scale features
    input_scaled = scaler.transform(input_df)
    
    # ML Prediction (Current)
    ml_scaled_pred = hgb.predict(input_scaled)
    ml_pred = target_scaler.inverse_transform(ml_scaled_pred.reshape(-1,1))[0][0]
    
    # LSTM Prediction (Future)
    input_seq = input_scaled.reshape((1, input_scaled.shape[1], 1))
    lstm_scaled_pred = lstm_model.predict(input_seq)[0][0]
    lstm_pred = target_scaler.inverse_transform([[lstm_scaled_pred]])[0][0]
    
    # Display results
    st.subheader("Predicted Weekly Sales")
    st.write(f"ML (Current) Prediction: **{ml_pred:.2f} units**")
    st.write(f"LSTM (Future) Prediction: **{lstm_pred:.2f} units**")
    
    # Non-tech explanation
    average_pred = (ml_pred + lstm_pred)/2
    st.markdown(
        f"""
        <div style="background-color:#1e1e1e;padding:15px;border-radius:10px;color:white">
        <h4 style="color:#ffdd57">What this means:</h4>
        Based on past sales, store characteristics, and other factors, we <b>expect weekly sales to be around {average_pred:.0f} units</b> for this store and department.<br>
        The ML model predicts <b>current week sales</b> based on individual factors.<br>
        The LSTM model predicts <b>future sales</b> by looking at trends over time.<br>
        Together, they give a more reliable estimate.
        </div>
        """, unsafe_allow_html=True
    )
    
    # Chart for comparison
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(["ML (Current)", "LSTM (Future)"], [ml_pred, lstm_pred], color=["#1f77b4", "#ff7f0e"])
    ax.set_ylabel("Units Sold")
    ax.set_title("Comparison of Predicted Sales")
    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor("#0e1117")
    ax.tick_params(colors='white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    st.pyplot(fig)
