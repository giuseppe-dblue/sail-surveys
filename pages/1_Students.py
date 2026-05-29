import pandas as pd
import streamlit as st

from analysis.constants import GRADE_ORDER, PRIMARY_COUNTRIES
from analysis.correlation_ui import render_correlation_tab
from analysis.data import load_data
from analysis.questions import QUESTIONS
from analysis.ui import render_question


def _apply_filters(
    df: pd.DataFrame,
    countries: list[str],
    genders: list[str],
    grades: list[str],
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if countries:
        mask &= df["1. Country"].isin(countries)
    if genders:
        mask &= df["2. Gender"].isin(genders)
    if grades:
        mask &= df["3. Grade/Year of Study"].isin(grades)
    return df[mask]


def _sidebar(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    with st.sidebar:
        st.header("Filters")
        extra = sorted(c for c in df["1. Country"].dropna().unique() if c not in PRIMARY_COUNTRIES)
        countries = st.multiselect("Country", options=PRIMARY_COUNTRIES + extra, default=PRIMARY_COUNTRIES)
        genders = st.multiselect("Gender", options=df["2. Gender"].dropna().unique().tolist(),
                                 default=df["2. Gender"].dropna().unique().tolist())
        available_grades = [g for g in GRADE_ORDER if g in df["3. Grade/Year of Study"].values]
        grades = st.multiselect("Grade / Year", options=available_grades, default=available_grades)
        st.divider()
        st.caption(f"All respondents: **{len(df)}**")
    return countries, genders, grades


def _sidebar_filtered_caption(total: int, filtered: int) -> None:
    with st.sidebar:
        st.caption(f"Active selection: **{filtered}** of {total}")


def _descriptive_tab(filtered: pd.DataFrame, total: int, countries: list[str]) -> None:
    country_str = ", ".join(countries) if countries else "All"
    st.caption(f"Showing **{len(filtered)}** of {total} responses — Countries: {country_str}")
    st.divider()

    sections: dict[str, list[dict]] = {}
    for q in QUESTIONS:
        sections.setdefault(q["section"], []).append(q)

    for section_name, questions in sections.items():
        st.header(section_name)
        for q in questions:
            with st.expander(q["label"], expanded=True):
                render_question(q, filtered)
        st.divider()


st.title("SAIL Survey — Student AI Usage Analysis")

df = load_data()
countries, genders, grades = _sidebar(df)
filtered = _apply_filters(df, countries, genders, grades)
_sidebar_filtered_caption(len(df), len(filtered))

tab_desc, tab_corr = st.tabs(["📋 Descriptive Analysis", "🔗 Correlation Analysis"])

with tab_desc:
    _descriptive_tab(filtered, len(df), countries)

with tab_corr:
    render_correlation_tab(filtered)
