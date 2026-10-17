import streamlit as st
import pandas as pd
from pymongo import MongoClient

@st.cache_resource
def get_mongo_client():
    return MongoClient(st.secrets["mongo_uri"])

@st.cache_data(ttl=600)
def load_mongo_data():
    client = get_mongo_client()

    db = client["ind320"]
    collection = db["transfers"]

    data = list(collection.find({}, {"_id": 0}))

    return pd.DataFrame(data)