import pandas as pd
import streamlit as st

from analysis.constants import AGE_ORDER, EXPERIENCE_ORDER, PRIMARY_COUNTRIES
from analysis.correlation_ui_teachers import render_correlation_tab_teachers
from analysis.data_teachers import load_teachers
from analysis.questions_teachers import QUESTIONS_TEACHERS
from analysis.ui_teachers import render_question_teacher


def _apply_filters(
    df: pd.DataFrame,
    countries: list[str],
    genders: list[str],
    age_groups: list[str],
    experiences: list[str],
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if countries:
        mask &= df["1. Country"].isin(countries)
    if genders:
        mask &= df["2. Gender"].isin(genders)
    if age_groups:
        mask &= df["3. Age Group"].isin(age_groups)
    if experiences:
        mask &= df["4. Years of Teaching Experience"].isin(experiences)
    return df[mask]


def _sidebar(df: pd.DataFrame) -> tuple[list[str], list[str], list[str], list[str]]:
    with st.sidebar:
        st.header("Filters")
        extra = sorted(
            c for c in df["1. Country"].dropna().unique() if c not in PRIMARY_COUNTRIES
        )
        countries = st.multiselect(
            "Country", options=PRIMARY_COUNTRIES + extra, default=PRIMARY_COUNTRIES
        )
        genders = st.multiselect(
            "Gender",
            options=df["2. Gender"].dropna().unique().tolist(),
            default=df["2. Gender"].dropna().unique().tolist(),
        )
        available_ages = [a for a in AGE_ORDER if a in df["3. Age Group"].values]
        age_groups = st.multiselect(
            "Age Group", options=available_ages, default=available_ages
        )
        available_exp = [
            e for e in EXPERIENCE_ORDER
            if e in df["4. Years of Teaching Experience"].values
        ]
        experiences = st.multiselect(
            "Teaching Experience", options=available_exp, default=available_exp
        )
        st.divider()
        st.caption(f"All respondents: **{len(df)}**")
    return countries, genders, age_groups, experiences


def _sidebar_filtered_caption(total: int, filtered: int) -> None:
    with st.sidebar:
        st.caption(f"Active selection: **{filtered}** of {total}")


def _descriptive_tab(filtered: pd.DataFrame, total: int, countries: list[str]) -> None:
    country_str = ", ".join(countries) if countries else "All"
    st.caption(
        f"Showing **{len(filtered)}** of {total} responses — Countries: {country_str}"
    )
    st.divider()

    sections: dict[str, list[dict]] = {}
    for q in QUESTIONS_TEACHERS:
        sections.setdefault(q["section"], []).append(q)

    for section_name, questions in sections.items():
        st.header(section_name)
        for q in questions:
            with st.expander(q["label"], expanded=True):
                render_question_teacher(q, filtered)
        st.divider()


def main() -> None:
    st.title("SAIL Survey — Teacher AI Usage Analysis")

    df = load_teachers()
    countries, genders, age_groups, experiences = _sidebar(df)
    filtered = _apply_filters(df, countries, genders, age_groups, experiences)
    _sidebar_filtered_caption(len(df), len(filtered))

    tab_desc, tab_corr = st.tabs(["📋 Descriptive Analysis", "🔗 Correlation Analysis"])

    with tab_desc:
        _descriptive_tab(filtered, len(df), countries)

    with tab_corr:
        render_correlation_tab_teachers(filtered)


if __name__ == "__main__":
    main()
