import pandas as pd
import streamlit as st

from analysis.charts import plot_indicator_bar
from analysis.insights import describe_indicator_multiselect
from analysis.ui import render_question


def render_question_teacher(q: dict, df: pd.DataFrame) -> None:
    """Render a teacher question.

    Delegates to the shared render_question for all types except multiselects
    that have already been expanded into binary indicator columns.
    """
    if q.get("type") == "multiselect" and "indicator_cols" in q:
        _render_indicator_multiselect(q, df)
    else:
        render_question(q, df)


def _render_indicator_multiselect(q: dict, df: pd.DataFrame) -> None:
    question_text = q.get("question_text", "")
    if question_text:
        st.markdown(f"*{question_text}*")

    indicator_cols = q["indicator_cols"]
    fig = plot_indicator_bar(df, indicator_cols, title=q["label"])
    text = describe_indicator_multiselect(df, indicator_cols)

    st.plotly_chart(fig, use_container_width=True)
    st.info(text)
