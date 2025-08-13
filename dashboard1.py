import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="📊 Sales Dashboard", layout="wide")

# Upload Excel file
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip().str.replace("\n", " ")

    # Rename Sales column if needed
    if "Unnamed: 6" in df.columns:
        df.rename(columns={"Unnamed: 6": "Sales"}, inplace=True)

    # Strip spaces & normalize text columns
    for col in ["City", "State"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Convert Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    default_y = "Sales" if "Sales" in numeric_cols else "Qty" if "Qty" in numeric_cols else numeric_cols[0]

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    start_date, end_date = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])
    cities = st.sidebar.multiselect("Select City", sorted(df["City"].dropna().unique()))
    states = st.sidebar.multiselect("Select State", sorted(df["State"].dropna().unique()))

    # Apply filters
    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]
    if cities:
        filtered_df = filtered_df[filtered_df["City"].isin(cities)]
    if states:
        filtered_df = filtered_df[filtered_df["State"].isin(states)]

    # KPIs
    st.title("📈 Sales Dashboard")
    total_qty = filtered_df["Qty"].sum() if "Qty" in filtered_df else 0
    num_products = filtered_df["Product Description"].nunique() if "Product Description" in filtered_df else 0
    top_product = filtered_df.groupby("Product Description")["Qty"].sum().idxmax() if "Product Description" in filtered_df else "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Qty", f"{total_qty}")
    col2.metric("Number of Products", f"{num_products}")
    col3.metric("Top Product", top_product)

    # Metric selector
    y_axis = st.selectbox("Select Metric", numeric_cols, index=numeric_cols.index(default_y))

    # Line chart
    time_data = filtered_df.groupby("Date", as_index=False)[y_axis].sum()
    fig_line = px.line(time_data, x="Date", y=y_axis, title=f"{y_axis} Over Time", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Bar chart
    bar_data = filtered_df.groupby("Product Description", as_index=False)[y_axis].sum()
    fig_bar = px.bar(bar_data, x="Product Description", y=y_axis, title=f"Product vs {y_axis}", text=y_axis)
    fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Pie chart
    pie_data = filtered_df.groupby("City", as_index=False)[y_axis].sum()
    fig_pie = px.pie(pie_data, names="City", values=y_axis, title=f"{y_axis} Distribution by City")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Data table
    st.subheader("📋 Filtered Data")
    st.dataframe(filtered_df)

    # Download filtered data
    st.download_button(
        label="💾 Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="filtered_sales.csv",
        mime="text/csv"
    )
else:
    st.info("👆 Upload an Excel file to start the dashboard.")
