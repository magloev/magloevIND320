import streamlit as st
from src.mongo_loader import load_mongo_data

st.title("Electricity Exchange")

df = load_mongo_data()

st.dataframe(df.head())