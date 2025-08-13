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

    # Clean column names
    df.columns = df.columns.str.strip().str.replace("\n", " ")

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

    # --- Metric Selection ---
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        selected_metric = st.sidebar.selectbox("Select Metric", numeric_cols, index=0)
    else:
        selected_metric = None

    # --- KPI Metrics ---
    st.title("📈 Sales Dashboard")

    if selected_metric:
        total_value = filtered_df[selected_metric].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Total {selected_metric}", f"{total_value:,.2f}")

    if 'Product Description' in filtered_df.columns and selected_metric:
        num_products = filtered_df['Product Description'].nunique()
        if not filtered_df.empty:
            top_product = filtered_df.groupby('Product Description')[selected_metric].sum().idxmax()
        else:
            top_product = "N/A"
    else:
        num_products = 0
        top_product = "N/A"

    if selected_metric:
        col2.metric("Number of Products", f"{num_products}")
        col3.metric("Top Product", top_product)

    # --- Charts ---
    if not filtered_df.empty and selected_metric:
        # Bar Chart
        if 'Product Description' in filtered_df.columns:
            bar_data = filtered_df.groupby('Product Description', as_index=False)[selected_metric].sum()
            fig_bar = px.bar(bar_data, x='Product Description', y=selected_metric,
                             title=f"Product vs {selected_metric}", text=selected_metric)
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart
            fig_pie = px.pie(bar_data, names='Product Description', values=selected_metric,
                             title=f"Product Share by {selected_metric}")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Line Chart
        if 'Date' in filtered_df.columns:
            time_data = filtered_df.groupby('Date', as_index=False)[selected_metric].sum()
            fig_line = px.line(time_data, x='Date', y=selected_metric,
                               title=f"{selected_metric} Over Time", markers=True)
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
