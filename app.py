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
    return pd.read_csv("Coffee_sales.csv")

coffee = load_data()

st.write("Dataset preview")
st.dataframe(coffee.head())
