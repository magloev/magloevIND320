import streamlit as st

st.set_page_config(
    page_title="IND320 Dashboard",
    layout="wide"
)

st.title("IND320 Dashboard")


def home():
    st.write("Dashboard IND320 WIP")


pages = [
    st.Page(home, title="Home"),
    st.Page("pages/reservoirdata.py", title="Reservoir Data"),
    st.Page("pages/plots.py", title="Plots"),
    st.Page("pages/dummy.py", title="Dummy Page")
]

pg = st.navigation(pages)
pg.run()