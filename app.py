import streamlit as st

from analysis.auth import check_password

st.set_page_config(page_title="SAIL Survey Analysis", layout="wide", page_icon="📊")

if not check_password():
    st.stop()

pg = st.navigation([
    st.Page("pages/1_Students.py", title="Students"),
    st.Page("pages/2_Teachers.py", title="Teachers"),
])
pg.run()
