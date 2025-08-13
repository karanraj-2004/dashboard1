import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📈 Sales Dashboard", layout="wide")

# --- File Upload ---
st.sidebar.header("📂 Upload Excel File")
uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load Excel data
    df = pd.read_excel(uploaded_file)

    # Ensure Date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # --- Sidebar Filters ---
    st.sidebar.header("📊 Filter Data")

    # Date filter
    if 'Date' in df.columns:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [df['Date'].min(), df['Date'].max()]
        )
        filtered_df = df[
            (df['Date'] >= pd.to_datetime(date_range[0])) &
            (df['Date'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        filtered_df = df.copy()

    # City filter
    if 'City' in df.columns:
        city_filter = st.sidebar.multiselect("Select City", options=df['City'].dropna().unique())
        if city_filter:
            filtered_df = filtered_df[filtered_df['City'].isin(city_filter)]

    # State filter
    if 'State' in df.columns:
        state_filter = st.sidebar.multiselect("Select State", options=df['State'].dropna().unique())
        if state_filter:
            filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]

    # --- KPI Metrics ---
    st.title("📈 Sales Dashboard")

    if 'Qty' in filtered_df.columns:
        total_qty = filtered_df['Qty'].sum()
    else:
        total_qty = 0

    if 'Product Description' in filtered_df.columns:
        num_products = filtered_df['Product Description'].nunique()
        if not filtered_df.empty:
            top_product = filtered_df.groupby('Product Description')['Qty'].sum().idxmax()
        else:
            top_product = "N/A"
    else:
        num_products = 0
        top_product = "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Qty", f"{total_qty}")
    col2.metric("Number of Products", f"{num_products}")
    col3.metric("Top Product", top_product)

    # --- Charts ---
    if not filtered_df.empty:
        # Bar Chart
        if 'Product Description' in filtered_df.columns and 'Qty' in filtered_df.columns:
            bar_data = filtered_df.groupby('Product Description', as_index=False)['Qty'].sum()
            fig_bar = px.bar(bar_data, x='Product Description', y='Qty',
                             title="Product vs Qty", text='Qty')
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart
            fig_pie = px.pie(bar_data, names='Product Description', values='Qty',
                             title="Product Share by Qty")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Line Chart
        if 'Date' in filtered_df.columns and 'Qty' in filtered_df.columns:
            time_data = filtered_df.groupby('Date', as_index=False)['Qty'].sum()
            fig_line = px.line(time_data, x='Date', y='Qty',
                               title="Qty Over Time", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    # --- Download Filtered Data ---
    st.download_button(
        label="📥 Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="filtered_sales.csv",
        mime="text/csv"
    )

else:
    st.info("📤 Please upload an Excel file to start.")
