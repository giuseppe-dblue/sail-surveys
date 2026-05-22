import pandas as pd
import streamlit as st
from analysis.constants import DATA_PATH

# Students responded with origin country; remap to the school country.
COUNTRY_REMAP = {
    "Afghanistan":      "Turkey",
    "Germany":          "Turkey",
    "Ghana":            "Spain",
    "Spain (Catalonia)": "Spain",
    "Portugal":         "Slovenia",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    df["1. Country"] = df["1. Country"].replace(COUNTRY_REMAP)
    return df
