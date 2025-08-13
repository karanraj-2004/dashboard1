import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Title
st.title("📊 Sales Dashboard with Excel Upload")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.write("### Data Preview")
        st.dataframe(df)

        # Optional: Display basic stats
        st.write("### Dataset Info")
        st.write(f"Number of rows: {df.shape[0]}")
        st.write(f"Number of columns: {df.shape[1]}")

        # Example dashboard chart (edit as per your actual data columns)
        if "Sales" in df.columns and "Date" in df.columns:
            fig = px.line(df, x="Date", y="Sales", title="Sales Over Time")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")

else:
    st.info("Please upload an Excel file to view the dashboard.")



