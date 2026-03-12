import streamlit as st
import pandas as pd

st.title("Student Document Analysis System")

st.write("Upload document for analysis")

uploaded_file = st.file_uploader("Upload file")

if uploaded_file:
    st.success("File uploaded successfully")

    st.subheader("Analysis Result")

    data = {
        "Document": ["Charter", "Event Plan", "Financial Report"],
        "Issue": [
            "Missing signature",
            "No event dates",
            "Incomplete financial data"
        ],
        "Recommendation": [
            "Add signature of organization leader",
            "Specify event dates",
            "Provide full financial information"
        ]
    }

    df = pd.DataFrame(data)
    st.table(df)
