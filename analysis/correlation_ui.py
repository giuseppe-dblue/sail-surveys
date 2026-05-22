import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis.correlation import (
    CORR_LABELS,
    ORDINAL_ENCODINGS,
    bh_significant,
    cluster_order,
    compute_spearman,
    encode_ordinal,
    notable_pairs,
)

_THRESHOLD = 0.25
_STRENGTH_COLOR = {"Strong": "#1a5276", "Moderate": "#2e86c1", "Weak": "#85c1e9"}
_DIR_SYMBOL = {"positive": "↑", "negative": "↓"}


# ── Chart builders ─────────────────────────────────────────────────────────────

def _short(col: str, max_len: int = 28) -> str:
    label = CORR_LABELS.get(col, col)
    return label if len(label) <= max_len else label[: max_len - 1] + "…"


def _full_heatmap(corr: pd.DataFrame, sig: pd.DataFrame, order: list[str]) -> go.Figure:
    c = corr.loc[order, order]
    s = sig.loc[order, order]
    labels = [_short(col) for col in order]
    z = c.values.tolist()

    # Mark non-significant cells with a star-less text; significant cells get the value
    text = [
        [
            f"{c.iloc[i, j]:.2f}" if (i != j and s.iloc[i, j]) else ("1.00" if i == j else "")
            for j in range(len(order))
        ]
        for i in range(len(order))
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        text=text,
        texttemplate="%{text}",
        textfont=dict(size=9),
        colorscale="RdBu",
        zmid=0,
        zmin=-1,
        zmax=1,
        colorbar=dict(title="r", thickness=12, len=0.6),
        hoverongaps=False,
    ))
    n = len(order)
    fig.update_layout(
        title="Full Spearman Correlation Matrix (BH-significant cells show value)",
        height=max(500, 22 * n + 120),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


def _simplified_heatmap(corr: pd.DataFrame, sig: pd.DataFrame, order: list[str]) -> go.Figure:
    """Three-colour heatmap: meaningful positive / neutral / meaningful negative."""
    c = corr.loc[order, order]
    s = sig.loc[order, order]
    labels = [_short(col) for col in order]
    n = len(order)

    z = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            elif s.iloc[i, j] and abs(c.iloc[i, j]) >= _THRESHOLD:
                row.append(1 if c.iloc[i, j] > 0 else -1)
            else:
                row.append(0)
        z.append(row)

    colorscale = [
        [0.0, "#d73027"],   # meaningful negative
        [0.5, "#f5f5f5"],   # neutral / not meaningful
        [1.0, "#4575b4"],   # meaningful positive
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        colorscale=colorscale,
        zmin=-1,
        zmax=1,
        showscale=False,
        hovertemplate="%{y} × %{x}<extra></extra>",
    ))
    fig.update_layout(
        title="Association overview  (blue = tend together · red = tend opposite · grey = no meaningful link)",
        height=max(500, 22 * n + 120),
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


def _drilldown_chart(col_a: str, col_b: str, df: pd.DataFrame) -> go.Figure:
    """
    Percentage-normalised heatmap of the joint distribution of two ordinal columns.
    Rows = A categories, columns = B categories, cell = % of A respondents who gave that B answer.
    """
    enc_a = ORDINAL_ENCODINGS.get(col_a, {})
    enc_b = ORDINAL_ENCODINGS.get(col_b, {})
    inv_a = {v: k for k, v in enc_a.items()}
    inv_b = {v: k for k, v in enc_b.items()}

    mask = df[col_a].notna() & df[col_b].notna()
    sub = df.loc[mask, [col_a, col_b]]

    # Short display labels (wrap at ~35 chars)
    def _wrap(s: str, w: int = 35) -> str:
        import textwrap
        return "<br>".join(textwrap.wrap(s, w))

    a_vals = sorted(enc_a.values())
    b_vals = sorted(enc_b.values())
    a_labels = [_wrap(inv_a[v]) for v in a_vals]
    b_labels = [_wrap(inv_b[v]) for v in b_vals]

    # Cross-tabulate on encoded integer values so reindex matches
    ct = pd.crosstab(sub[col_a].map(enc_a), sub[col_b].map(enc_b))
    ct = ct.reindex(index=a_vals, columns=b_vals, fill_value=0)
    pct = ct.div(ct.sum(axis=1), axis=0) * 100

    fig = go.Figure(go.Heatmap(
        z=pct.values.tolist(),
        x=b_labels,
        y=a_labels,
        text=[[f"{v:.0f}%" for v in row] for row in pct.values],
        texttemplate="%{text}",
        textfont=dict(size=11),
        colorscale="Blues",
        zmin=0,
        colorbar=dict(title="%", thickness=12, len=0.6),
    ))
    label_a = CORR_LABELS.get(col_a, col_a)
    label_b = CORR_LABELS.get(col_b, col_b)
    fig.update_layout(
        title=f"% distribution of '{label_b}' for each answer to '{label_a}'",
        xaxis_title=label_b,
        yaxis_title=label_a,
        height=max(350, 80 * len(a_vals) + 120),
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


# ── Tab entry point ────────────────────────────────────────────────────────────

def render_correlation_tab(df: pd.DataFrame) -> None:
    st.header("Questions That Tend to Go Together")
    st.markdown(
        "This section explores which survey questions are statistically associated — "
        "i.e. students who answered a certain way on one question tended to answer "
        "a certain way on another. Only associations that are both statistically "
        "significant (Benjamini-Hochberg corrected) and of practical size "
        f"(|r| ≥ {_THRESHOLD}) are highlighted."
    )

    encoded = encode_ordinal(df)
    with st.spinner("Computing correlations…"):
        corr, pvals = compute_spearman(encoded)
    sig = bh_significant(pvals)
    order = cluster_order(corr)
    pairs = notable_pairs(corr, sig, threshold=_THRESHOLD)

    n_sig = len(pairs)
    st.caption(f"**{n_sig} notable associations** found across {len(encoded.columns)} questions.")
    st.divider()

    # ── Section 1: Simplified heatmap ─────────────────────────────────────────
    st.subheader("Overview map")
    st.markdown(
        "Each cell shows whether two questions tend to go together (**blue**), "
        "go in opposite directions (**red**), or have no meaningful link (**grey**). "
        "Questions are grouped by similarity."
    )
    fig_simple = _simplified_heatmap(corr, sig, order)
    st.plotly_chart(fig_simple, use_container_width=True)

    # ── Section 2: Notable pairs table ────────────────────────────────────────
    st.subheader("Notable associations")
    if not pairs:
        st.info("No pairs meet the significance and effect-size threshold.")
        return

    rows = []
    for p in pairs:
        dir_label = "Together ↑" if p["direction"] == "positive" else "Opposite ↓"
        rows.append({
            "Question A": p["label_a"],
            "Question B": p["label_b"],
            "Link": dir_label,
            "Strength": p["strength"],
            "What it means": p["sentence"],
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Question A": st.column_config.TextColumn(width="medium"),
            "Question B": st.column_config.TextColumn(width="medium"),
            "Link": st.column_config.TextColumn(width="small"),
            "Strength": st.column_config.TextColumn(width="small"),
            "What it means": st.column_config.TextColumn(width="large"),
        },
    )

    # ── Section 3: Drill-down ─────────────────────────────────────────────────
    st.divider()
    st.subheader("Explore a relationship")
    pair_options = [f"{p['label_a']}  ×  {p['label_b']}" for p in pairs]
    selected = st.selectbox("Select a pair to inspect", options=pair_options)
    idx = pair_options.index(selected)
    chosen = pairs[idx]

    p = chosen
    st.markdown(
        f"**{p['label_a']}** × **{p['label_b']}** — "
        f"{p['strength'].lower()} {'positive' if p['direction'] == 'positive' else 'negative'} "
        f"association (r = {p['r']})."
    )
    st.markdown(f"*{p['sentence']}*")
    st.plotly_chart(_drilldown_chart(p["col_a"], p["col_b"], df), use_container_width=True)

    # ── Section 4: Full heatmap (expert view) ─────────────────────────────────
    st.divider()
    with st.expander("Full correlation matrix (expert view)", expanded=False):
        st.markdown(
            "Spearman ρ for all question pairs. Cells show the coefficient only where "
            "the association is BH-significant; all others are blank. "
            "Colour scale: blue = positive, red = negative."
        )
        st.plotly_chart(_full_heatmap(corr, sig, order), use_container_width=True)
