import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
file_path = r"C:\Users\karan\Downloads\Mock_up_data .xlsx"
df = pd.read_excel(file_path)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Sidebar Filters
st.sidebar.header("📊 Filter Data")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)

city_filter = st.sidebar.multiselect("Select City", options=df['City'].unique())
state_filter = st.sidebar.multiselect("Select State", options=df['State'].unique())

# Apply Filters
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
]

if city_filter:
    filtered_df = filtered_df[filtered_df['City'].isin(city_filter)]
if state_filter:
    filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]

# KPI Metrics
total_qty = filtered_df['Qty'].sum()
num_products = filtered_df['Product Description'].nunique()
top_product = filtered_df.groupby('Product Description')['Qty'].sum().idxmax()

st.title("📈 Sales Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Qty", f"{total_qty}")
col2.metric("Number of Products", f"{num_products}")
col3.metric("Top Product", top_product)

# --- Product vs Qty Bar Chart ---
bar_data = filtered_df.groupby('Product Description', as_index=False)['Qty'].sum()
fig_bar = px.bar(bar_data, x='Product Description', y='Qty',
                 title="Product vs Qty", text='Qty')
fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)

# --- Product Share Pie Chart ---
fig_pie = px.pie(bar_data, names='Product Description', values='Qty',
                 title="Product Share by Qty")
st.plotly_chart(fig_pie, use_container_width=True)

# --- Qty Over Time Line Chart ---
time_data = filtered_df.groupby('Date', as_index=False)['Qty'].sum()
fig_line = px.line(time_data, x='Date', y='Qty',
                   title="Qty Over Time", markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# Download Filtered Data
st.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name="filtered_sales.csv",
    mime="text/csv"
)


