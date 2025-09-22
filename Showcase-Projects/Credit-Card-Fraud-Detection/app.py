import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ---------------------------
# Load Model and Dataset
# ---------------------------
model = pickle.load(open("model.pkl", "rb"))
data = pd.read_csv("data/creditcard.csv")

st.set_page_config(page_title="Credit Card Fraud Detection", layout="wide")
st.title("💳 Credit Card Fraud Detection")
st.write("This app predicts whether a credit card transaction is fraudulent or not.")

# ---------------------------
# Sidebar for User Input
# ---------------------------
st.sidebar.header("Choose Input Method")
input_method = st.sidebar.radio("Select input type:", ["Sample Transaction", "Manual Input", "Index Lookup"])

# ---------------------------
# Option 1: Sample Transaction
# ---------------------------
if input_method == "Sample Transaction":
    st.subheader("Select a Sample Transaction")
    
    # Select 1 random fraud
    fraud_sample = data[data['Class']==1].sample(1)
    
    # Select 4 random non-fraud
    nonfraud_sample = data[data['Class']==0].sample(4)
    
    # Combine and shuffle
    sample_rows = pd.concat([fraud_sample, nonfraud_sample]).sample(frac=1)
    
    # Create friendly labels (show Fraud / Not Fraud)
    row_labels = [f"Index {i} - {'Fraud' if row['Class']==1 else 'Not Fraud'}" for i, row in sample_rows.iterrows()]
    
    selected_label = st.selectbox("Choose a sample row:", row_labels)
    selected_index = int(selected_label.split()[1])
    selected_row = data.loc[selected_index]
    features = selected_row.drop("Class").values.reshape(1, -1)

# ---------------------------
# Option 2: Manual Input
# ---------------------------
elif input_method == "Manual Input":
    st.subheader("Enter Transaction Details Manually")
    input_dict = {}
    input_dict["Time"] = st.number_input("Time", value=float(data["Time"].mean()))
    for col in [f"V{i}" for i in range(1,29)]:
        input_dict[col] = st.number_input(col, value=float(data[col].mean()))
    input_dict["Amount"] = st.number_input("Amount", value=float(data["Amount"].mean()))
    features = np.array([list(input_dict.values())])

# ---------------------------
# Option 3: Index Lookup
# ---------------------------
else:
    st.subheader("Check any transaction by Index")
    idx = st.number_input("Enter Index (0 to {})".format(len(data)-1), min_value=0, max_value=len(data)-1, step=1)
    selected_row = data.loc[int(idx)]
    features = selected_row.drop("Class").values.reshape(1, -1)
    st.write(f"Actual Class: {'Fraud' if selected_row['Class']==1 else 'Not Fraud'}")

# ---------------------------
# Prediction
# ---------------------------
if st.button("Predict"):
    prediction = model.predict(features)
    prediction_proba = model.predict_proba(features)[0][1]

    st.write("## Prediction Result:")
    if prediction[0] == 1:
        st.error(f"⚠️ Fraudulent Transaction detected! Probability: {prediction_proba:.2f}")
    else:
        st.success(f"✅ Not Fraudulent. Probability of fraud: {prediction_proba:.2f}")

# ---------------------------
# Detailed Explanation at Bottom
# ---------------------------
st.markdown("---")
st.markdown("""
**About this App:**  

1️⃣ **Index**  
- This is the row number in  dataset (`data.csv`).  
- Example: `Index 43428` means this transaction is at row 43428.  
- Helps  identify the transaction being tested.

2️⃣ **Class**  
- Class is the actual label in the dataset:  
  - 0 → Not Fraudulent  
  - 1 → Fraudulent  
- Example: `Class 1.0` means the transaction is actually a fraud.

3️⃣ **Why show Index and Class?**  
- The dropdown shows 5 sample transactions from the dataset.  
- Displaying `Index ... - Class ...` makes it clear which transaction is fraud or non-fraud before clicking Predict.  
- Helps you test if the model prediction matches the actual label.  

✅ **In short:**  
`Index 43428 - Class 1.0` → Transaction at row 43428 is actually fraud in the dataset.

- You can either select **sample transactions**, enter **all 30 features manually**, or **lookup any transaction by Index**.  
- Designed for portfolio showcase: interactive, professional, and easy to test.
""")