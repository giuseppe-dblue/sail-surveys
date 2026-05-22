import textwrap

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _wrap(label: str, width: int = 38) -> str:
    lines = textwrap.wrap(str(label), width=width)
    return "<br>".join(lines) if lines else str(label)


def plot_bar(counts: pd.Series, colors=None, title: str = "") -> go.Figure:
    total = counts.sum()
    labels = [_wrap(str(l)) for l in counts.index]
    n_lines = max(lbl.count("<br>") + 1 for lbl in labels) if labels else 1
    row_height = 44 + 18 * (n_lines - 1)
    pct_text = [f"{v / total * 100:.1f}%" for v in counts.values]

    fig = go.Figure(
        go.Bar(
            x=counts.values,
            y=labels,
            orientation="h",
            text=pct_text,
            textposition="outside",
            marker_color=colors or px.colors.qualitative.Set2[: len(counts)],
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        height=max(300, row_height * len(counts) + 90),
        margin=dict(l=20, r=90, t=50, b=20),
        xaxis_title="Count",
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eeeeee"),
    )
    return fig


def plot_multiselect_bar(series: pd.Series, title: str = "") -> go.Figure:
    counts = series.dropna().str.split(", ").explode().value_counts()
    return plot_bar(counts, title=title)
