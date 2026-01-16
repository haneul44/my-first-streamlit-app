import streamlit as st
import pandas as pd

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="☕ Coffee Sales Dashboard",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Coffee Sales Dashboard")
st.caption("Exploratory analysis of coffee sales data")

@st.cache_data
def load_data():
    return pd.read_csv("Coffe_sales.csv")

coffee = load_data()

st.write("Dataset preview")
st.dataframe(coffee.head())

import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

coffee['coffee_name'] = coffee['coffee_name'].str.strip().str.title()
coffee['cash_type'] = coffee['cash_type'].str.strip().str.title()
coffee['Date'] = pd.to_datetime(coffee['Date'], format='%Y-%m-%d')

#Set color paltte
coffee_color_map = {
    'Americano': '#6F4E37',            # Espresso brown
    'Americano With Milk': '#8B5A2B',  # Mocha
    'Latte': '#C2A878',                # Latte beige
    'Cappuccino': '#A47148',           # Caramel
    'Espresso': '#4B2E1E',             # Dark roast
    'Cortado': '#D2B48C',              # Tan
    'Hot Chocolate': '#3B2416',        # Cocoa dark
    'Cocoa': '#9C6B4F'                 # Cocoa light
}

# 1) 월별 매출 집계 (전체 기간)
monthly_rev_line = (
    coffee
    .set_index('Date')
    .resample('MS')['money']   # MS = Month Start 기준으로 월별
    .sum()
    .reset_index()
)

# 2) 라인 그래프
fig = px.line(
    monthly_rev_line,
    x='Date',
    y='money',
    title='Monthly Revenue Trend (Line)',
    template='plotly_white'
)

fig.update_traces(mode='lines+markers')
fig.update_layout(
    xaxis_title='Month',
    yaxis_title='Revenue',
    xaxis=dict(
        tickmode='array',
        tickvals=monthly_rev_line['Date'],
        ticktext=[d.strftime('%Y-%m') for d in monthly_rev_line['Date']]
    )
)

fig.show()
