import pandas as pd
import plotly.express as px
import streamlit as st

from analysis.charts import plot_bar, plot_multiselect_bar
from analysis.constants import (
    CONCERN5_ORDER,
    LIKERT4_COLORS,
    LIKERT4_ORDER,
    CONCERN5_COLORS,
)
from analysis.insights import (
    describe_categorical,
    describe_concern5,
    describe_likert4,
    describe_multiselect,
)


def render_question(q: dict, df: pd.DataFrame) -> None:
    col = q["col"]
    qtype = q["type"]
    label = q["label"]
    question_text = q.get("question_text", "")
    series = df[col]

    if question_text:
        st.markdown(f"*{question_text}*")

    if qtype == "multiselect":
        fig = plot_multiselect_bar(series, title=label)
        text = describe_multiselect(series)

    elif qtype == "categorical":
        counts = series.value_counts()
        color_map = q.get("color_map", {})
        if color_map:
            colors = [color_map.get(str(k), "#cccccc") for k in counts.index]
        else:
            colors = q.get("colors") or px.colors.qualitative.Set2[: len(counts)]
        fig = plot_bar(counts, colors=colors, title=label)
        text = describe_categorical(series)

    elif qtype == "ordered_categorical":
        order = q.get("order", [])
        short_labels = q.get("short_labels", {})
        raw_counts = series.value_counts()
        ordered = pd.Series(
            [raw_counts.get(k, 0) for k in order],
            index=[short_labels.get(k, k) for k in order],
        )
        ordered = ordered[ordered > 0]
        colors = q.get("colors") or px.colors.qualitative.Set2[: len(ordered)]
        fig = plot_bar(ordered, colors=colors, title=label)
        text = describe_categorical(series, short_labels=short_labels or None)

    elif qtype == "likert4":
        counts = pd.Series(
            [series.value_counts().get(k, 0) for k in LIKERT4_ORDER],
            index=LIKERT4_ORDER,
        )
        fig = plot_bar(counts, colors=LIKERT4_COLORS, title=label)
        text = describe_likert4(series)

    elif qtype == "concern5":
        counts = pd.Series(
            [series.value_counts().get(k, 0) for k in CONCERN5_ORDER],
            index=CONCERN5_ORDER,
        )
        fig = plot_bar(counts, colors=CONCERN5_COLORS, title=label)
        text = describe_concern5(series)

    else:
        st.warning(f"Unknown question type: {qtype}")
        return

    st.plotly_chart(fig, use_container_width=True)
    st.info(text)
