"""
Render the Correlation Analysis tab for the Teachers page.

Five sections:
  1. Simplified overview heatmap  (non-expert friendly)
  2. Notable pairs table          (plain-language sentences + stats)
  3. Country comparison           (Kruskal-Wallis H + ε² effect size)
  4. Pair drill-down              (joint distribution of any selected pair)
  5. Full correlation matrix      (expert view, collapsed by default)
"""
import textwrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale

from analysis.constants import PRIMARY_COUNTRIES
from analysis.correlation import bh_significant, cluster_order, compute_spearman
from analysis.correlation_teachers import (
    CORR_LABELS_T,
    INDICATOR_COLS,
    ORDINAL_ENCODINGS_T,
    compute_kruskal_wallis_country,
    encode_ordinal_teachers,
    notable_pairs_teachers,
)

_THRESHOLD = 0.30
_COUNTRY_COLORS = {
    "Italy": "#1f77b4",
    "Spain": "#ff7f0e",
    "Slovenia": "#2ca02c",
    "Turkey": "#d62728",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _short(col: str, max_len: int = 28) -> str:
    label = CORR_LABELS_T.get(col, col)
    return label if len(label) <= max_len else label[: max_len - 1] + "…"


def _wrap(s: str, w: int = 35) -> str:
    return "<br>".join(textwrap.wrap(s, w))


# ── Heatmaps ──────────────────────────────────────────────────────────────────

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
        [0.0, "#d73027"],
        [0.5, "#f5f5f5"],
        [1.0, "#4575b4"],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        colorscale=colorscale,
        zmin=-1,
        zmax=1,
        showscale=False,
        hoverongaps=False,
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


def _full_heatmap(corr: pd.DataFrame, sig: pd.DataFrame, order: list[str]) -> go.Figure:
    c = corr.loc[order, order]
    s = sig.loc[order, order]
    labels = [_short(col) for col in order]
    z = c.values.tolist()
    n = len(order)

    text = [
        [
            f"{c.iloc[i, j]:.2f}" if (i != j and s.iloc[i, j]) else ("1.00" if i == j else "")
            for j in range(n)
        ]
        for i in range(n)
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
        colorbar=dict(title="ρ", thickness=12, len=0.6),
        hoverongaps=False,
    ))
    fig.update_layout(
        title="Full Spearman Correlation Matrix (BH-significant cells show ρ value)",
        height=max(500, 22 * n + 120),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


# ── Drill-down charts ─────────────────────────────────────────────────────────

def _ordinal_ordinal_chart(col_a: str, col_b: str, df: pd.DataFrame) -> go.Figure:
    """Percentage-normalised heatmap: for each row-answer, show % choosing each column-answer."""
    enc_a = ORDINAL_ENCODINGS_T[col_a]
    enc_b = ORDINAL_ENCODINGS_T[col_b]
    inv_a = {v: k for k, v in enc_a.items()}
    inv_b = {v: k for k, v in enc_b.items()}

    mask = df[col_a].notna() & df[col_b].notna()
    sub = df.loc[mask, [col_a, col_b]]

    a_vals = sorted(enc_a.values())
    b_vals = sorted(enc_b.values())
    a_labels = [_wrap(inv_a[v]) for v in a_vals]
    b_labels = [_wrap(inv_b[v]) for v in b_vals]

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
    label_a = CORR_LABELS_T.get(col_a, col_a)
    label_b = CORR_LABELS_T.get(col_b, col_b)
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


def _ordinal_binary_chart(col_ord: str, col_bin: str, df: pd.DataFrame) -> go.Figure:
    """
    For each level of the ordinal variable, show % of respondents who selected the binary option.
    Reveals whether higher ordinal scores are associated with picking the binary choice.
    """
    enc = ORDINAL_ENCODINGS_T[col_ord]
    inv = {v: k for k, v in enc.items()}
    vals = sorted(enc.values())
    labels = [_wrap(inv[v]) for v in vals]

    mask = df[col_ord].notna() & df[col_bin].notna()
    sub = df.loc[mask].copy()
    sub["_enc"] = sub[col_ord].map(enc)

    pcts, ns = [], []
    for v in vals:
        grp = sub.loc[sub["_enc"] == v, col_bin]
        pcts.append(round(grp.mean() * 100, 1) if len(grp) > 0 else 0.0)
        ns.append(len(grp))

    bin_label = CORR_LABELS_T.get(col_bin, col_bin)
    ord_label = CORR_LABELS_T.get(col_ord, col_ord)

    fig = go.Figure(go.Bar(
        x=labels,
        y=pcts,
        text=[f"{p:.0f}%<br>(n={n})" for p, n in zip(pcts, ns)],
        textposition="outside",
        marker_color="#4575b4",
    ))
    fig.update_layout(
        title=f"% who selected '{bin_label}' — by answer to '{ord_label}'",
        xaxis_title=ord_label,
        yaxis_title=f"% selecting: {bin_label}",
        yaxis=dict(range=[0, max(pcts + [0]) * 1.3 + 5]),
        height=420,
        margin=dict(l=20, r=20, t=60, b=140),
        xaxis=dict(tickangle=-25, tickfont=dict(size=10)),
    )
    return fig


def _binary_binary_chart(col_a: str, col_b: str, df: pd.DataFrame) -> go.Figure:
    """% who selected col_b, split by whether they also selected col_a."""
    mask = df[col_a].notna() & df[col_b].notna()
    sub = df.loc[mask]

    label_a = CORR_LABELS_T.get(col_a, col_a)
    label_b = CORR_LABELS_T.get(col_b, col_b)

    groups = {
        f"Did NOT select:\n{label_a}": sub.loc[sub[col_a] == 0, col_b],
        f"DID select:\n{label_a}": sub.loc[sub[col_a] == 1, col_b],
    }
    names, pcts, ns = [], [], []
    for name, grp in groups.items():
        names.append(name)
        pcts.append(round(grp.mean() * 100, 1) if len(grp) > 0 else 0.0)
        ns.append(len(grp))

    fig = go.Figure(go.Bar(
        x=names,
        y=pcts,
        text=[f"{p:.0f}%<br>(n={n})" for p, n in zip(pcts, ns)],
        textposition="outside",
        marker_color=["#aec7e8", "#4575b4"],
    ))
    fig.update_layout(
        title=f"% who selected '{label_b}' — by whether they also selected '{label_a}'",
        yaxis_title=f"% selecting: {label_b}",
        yaxis=dict(range=[0, max(pcts + [0]) * 1.3 + 5]),
        height=380,
        margin=dict(l=20, r=20, t=60, b=80),
    )
    return fig


def _drilldown_chart(col_a: str, col_b: str, df: pd.DataFrame) -> go.Figure:
    bin_a = col_a in INDICATOR_COLS
    bin_b = col_b in INDICATOR_COLS
    if bin_a and bin_b:
        return _binary_binary_chart(col_a, col_b, df)
    elif bin_b:
        return _ordinal_binary_chart(col_a, col_b, df)
    elif bin_a:
        return _ordinal_binary_chart(col_b, col_a, df)
    else:
        return _ordinal_ordinal_chart(col_a, col_b, df)


# ── Country comparison chart ──────────────────────────────────────────────────

def _country_dist_chart(col: str, df: pd.DataFrame) -> go.Figure:
    """Stacked % bar per country for ordinal variables; simple % bar for binary."""
    country_col = "1. Country"
    countries = [c for c in PRIMARY_COUNTRIES if c in df[country_col].values]
    label = CORR_LABELS_T.get(col, col)

    if col in INDICATOR_COLS:
        pcts, ns = [], []
        for country in countries:
            grp = df.loc[df[country_col] == country, col].dropna()
            pcts.append(round(grp.mean() * 100, 1) if len(grp) > 0 else 0.0)
            ns.append(len(grp))
        fig = go.Figure(go.Bar(
            x=countries,
            y=pcts,
            text=[f"{p:.0f}%<br>(n={n})" for p, n in zip(pcts, ns)],
            textposition="outside",
            marker_color=[_COUNTRY_COLORS.get(c, "#888") for c in countries],
        ))
        fig.update_layout(
            title=f"'{label}' — % selected by country",
            yaxis_title="% selecting",
            yaxis=dict(range=[0, max(pcts + [0]) * 1.3 + 5]),
            height=380,
            margin=dict(l=20, r=20, t=60, b=60),
        )
        return fig

    enc = ORDINAL_ENCODINGS_T.get(col, {})
    inv = {v: k for k, v in enc.items()}
    vals = sorted(enc.values())
    colors = sample_colorscale("Blues", [i / max(len(vals) - 1, 1) for i in range(len(vals))])

    fig = go.Figure()
    for idx, v in enumerate(vals):
        lv_label = _wrap(inv[v], 40)
        ys, texts = [], []
        for country in countries:
            grp = df.loc[df[country_col] == country, col].dropna()
            n_country = len(grp)
            n_level = (grp.map(enc) == v).sum()
            pct = round(n_level / n_country * 100, 1) if n_country > 0 else 0.0
            ys.append(pct)
            texts.append(f"{pct:.0f}%" if pct >= 5 else "")
        fig.add_trace(go.Bar(
            name=lv_label,
            x=countries,
            y=ys,
            text=texts,
            textposition="inside",
            textfont=dict(size=10),
            marker_color=colors[idx],
        ))

    fig.update_layout(
        barmode="stack",
        title=f"Distribution of '{label}' by country",
        yaxis_title="% of respondents",
        yaxis=dict(range=[0, 105]),
        legend=dict(orientation="v", x=1.01, y=1, xanchor="left", font=dict(size=10)),
        height=430,
        margin=dict(l=20, r=220, t=60, b=60),
    )
    return fig


# ── Tab entry point ───────────────────────────────────────────────────────────

def render_correlation_tab_teachers(df: pd.DataFrame) -> None:
    st.header("Questions That Tend to Go Together")
    st.markdown(
        "This section explores which survey questions are statistically associated — "
        "i.e. teachers who answered a certain way on one question tended to answer "
        "a certain way on another. Only associations that are both statistically "
        "significant (Benjamini-Hochberg FDR correction) and of practical size "
        f"(|ρ| ≥ {_THRESHOLD}) are highlighted. "
        "With N = 73 the threshold is set slightly higher than for students "
        "to focus on the clearest signals."
    )

    encoded = encode_ordinal_teachers(df)
    with st.spinner("Computing correlations…"):
        corr, pvals = compute_spearman(encoded)
    sig = bh_significant(pvals)
    order = cluster_order(corr)
    pairs = notable_pairs_teachers(corr, sig, threshold=_THRESHOLD)

    n_sig = len(pairs)
    st.caption(
        f"**{n_sig} notable associations** found across {len(encoded.columns)} variables "
        f"(N = {len(df)} teachers)."
    )
    st.divider()

    # ── Section 1: Simplified heatmap ─────────────────────────────────────────
    st.subheader("1 · Overview map")
    st.markdown(
        "Each cell shows whether two questions tend to go together (**blue**), "
        "go in opposite directions (**red**), or have no meaningful link (**grey**). "
        "Only cells that pass both the statistical significance test (BH-corrected) "
        f"and the minimum effect-size threshold (|ρ| ≥ {_THRESHOLD}) are coloured. "
        "Questions are grouped by similarity (hierarchical clustering on correlations)."
    )
    st.plotly_chart(_simplified_heatmap(corr, sig, order), use_container_width=True)

    # ── Section 2: Notable pairs table ────────────────────────────────────────
    st.divider()
    st.subheader("2 · Notable associations")
    st.markdown(
        "Each row is a pair of questions whose answers are meaningfully linked. "
        "**Strength** is based on Spearman ρ: "
        "Weak = 0.30–0.35, Moderate = 0.35–0.50, Strong ≥ 0.50."
    )
    if not pairs:
        st.info("No pairs meet the significance and effect-size threshold.")
    else:
        rows = []
        for p in pairs:
            dir_label = "Together ↑" if p["direction"] == "positive" else "Opposite ↓"
            rows.append({
                "Question A": p["label_a"],
                "Question B": p["label_b"],
                "Link": dir_label,
                "Strength": p["strength"],
                "ρ": p["r"],
                "What it means": p["sentence"],
            })
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Question A": st.column_config.TextColumn(width="medium"),
                "Question B": st.column_config.TextColumn(width="medium"),
                "Link": st.column_config.TextColumn(width="small"),
                "Strength": st.column_config.TextColumn(width="small"),
                "ρ": st.column_config.NumberColumn(format="%.3f", width="small"),
                "What it means": st.column_config.TextColumn(width="large"),
            },
        )

    # ── Section 3: Country comparison ─────────────────────────────────────────
    st.divider()
    st.subheader("3 · Country comparison")
    st.markdown(
        "Does a teacher's country predict how they answered? "
        "The **Kruskal-Wallis H test** is a non-parametric one-way ANOVA that compares "
        "the rank distributions of four groups without assuming a normal distribution — "
        "appropriate for ordinal survey data. "
        "**ε² (epsilon-squared)** converts the H statistic into a 0–1 effect-size scale: "
        "values ≥ 0.06 indicate a medium country effect, ≥ 0.14 a large one. "
        "The table is sorted from strongest to weakest country difference."
    )
    kw = compute_kruskal_wallis_country(df, encoded)
    if kw.empty:
        st.info("Not enough data per country to run comparisons.")
    else:
        kw_display = kw.copy()
        kw_display["p_value_fmt"] = kw_display["p_value"].apply(lambda x: f"{x:.4f}")
        kw_display["sig_mark"] = kw_display["significant"].map({True: "✓", False: ""})
        kw_display["eps2_fmt"] = kw_display["eps2"].apply(
            lambda x: f"{x:.3f}  {'◆' if x >= 0.14 else ('◇' if x >= 0.06 else '')}"
        )
        st.dataframe(
            kw_display[["label", "H", "p_value_fmt", "eps2_fmt", "sig_mark"]].rename(columns={
                "label": "Variable",
                "H": "H statistic",
                "p_value_fmt": "p-value",
                "eps2_fmt": "ε²  (◆ large  ◇ medium)",
                "sig_mark": "p < 0.05",
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Variable": st.column_config.TextColumn(width="large"),
                "H statistic": st.column_config.NumberColumn(format="%.2f", width="small"),
                "p-value": st.column_config.TextColumn(width="small"),
                "ε²  (◆ large  ◇ medium)": st.column_config.TextColumn(width="medium"),
                "p < 0.05": st.column_config.TextColumn(width="small"),
            },
        )

        st.markdown("**Drill down — pick a variable to see its distribution per country:**")
        selected_kw = st.selectbox(
            "Variable", options=kw["label"].tolist(), key="kw_select"
        )
        row = kw.loc[kw["label"] == selected_kw].iloc[0]
        selected_col = row["col"]

        effect_desc = "large" if row["eps2"] >= 0.14 else ("medium" if row["eps2"] >= 0.06 else "small")
        sig_txt = "statistically significant (p < 0.05)" if row["significant"] else "not statistically significant"
        st.caption(
            f"H = {row['H']:.2f}, p = {row['p_value']:.4f}, ε² = {row['eps2']:.3f} "
            f"({effect_desc} country effect) — {sig_txt}."
        )
        st.plotly_chart(_country_dist_chart(selected_col, df), use_container_width=True)

    # ── Section 4: Pair drill-down ─────────────────────────────────────────────
    if pairs:
        st.divider()
        st.subheader("4 · Explore a relationship")
        st.markdown(
            "Select any notable pair to see the full joint distribution. "
            "For two ordinal questions, the heatmap shows what % of teachers who gave "
            "a particular answer to Question A chose each answer to Question B. "
            "For pairs involving a binary (use-case / feeling) variable, the bar chart "
            "shows how selection rates change across ordinal levels."
        )
        pair_options = [f"{p['label_a']}  ×  {p['label_b']}" for p in pairs]
        selected = st.selectbox("Select a pair to inspect", options=pair_options, key="pair_select")
        idx = pair_options.index(selected)
        p = pairs[idx]

        direction_word = "positive" if p["direction"] == "positive" else "negative"
        st.markdown(
            f"**{p['label_a']}** × **{p['label_b']}** — "
            f"{p['strength'].lower()} {direction_word} association (ρ = {p['r']})."
        )
        st.markdown(f"*{p['sentence']}*")
        st.plotly_chart(_drilldown_chart(p["col_a"], p["col_b"], df), use_container_width=True)

    # ── Section 5: Full heatmap (expert view) ─────────────────────────────────
    st.divider()
    with st.expander("5 · Full correlation matrix (expert view)", expanded=False):
        st.markdown(
            "Spearman ρ for all variable pairs (ordinal + binary indicators). "
            "Cells show the coefficient only where the association survives "
            "Benjamini-Hochberg correction at FDR = 5%; all others are blank. "
            "Colour scale: blue = positive, red = negative. "
            "Variables are arranged by hierarchical clustering."
        )
        st.plotly_chart(_full_heatmap(corr, sig, order), use_container_width=True)
