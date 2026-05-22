import pandas as pd


def describe_categorical(series: pd.Series, short_labels: dict | None = None) -> str:
    n = series.count()
    counts = series.value_counts()
    top_raw = str(counts.index[0])
    top_label = short_labels.get(top_raw, top_raw) if short_labels else top_raw
    top_pct = counts.iloc[0] / n * 100
    parts = [f"**N = {n}.**", f'Most frequent: "{top_label}" ({top_pct:.1f}%).']
    if len(counts) > 1:
        second_raw = str(counts.index[1])
        second_label = short_labels.get(second_raw, second_raw) if short_labels else second_raw
        second_pct = counts.iloc[1] / n * 100
        parts.append(f'Second: "{second_label}" ({second_pct:.1f}%).')
    return " ".join(parts)


def describe_likert4(series: pd.Series) -> str:
    n = series.count()
    counts = series.value_counts()
    agree = counts.get("Agree", 0) + counts.get("Strongly Agree", 0)
    disagree = counts.get("Disagree", 0) + counts.get("Strongly Disagree", 0)
    agree_pct = agree / n * 100
    disagree_pct = disagree / n * 100
    direction = "agreement" if agree_pct > disagree_pct else "disagreement"
    return (
        f"**N = {n}.** "
        f"Agreement (Agree + Strongly Agree): **{agree_pct:.1f}%**. "
        f"Disagreement (Disagree + Strongly Disagree): **{disagree_pct:.1f}%**. "
        f"Overall sentiment leans toward **{direction}**."
    )


def describe_concern5(series: pd.Series) -> str:
    n = series.count()
    counts = series.value_counts()
    concerned = sum(counts.get(k, 0) for k in ["Moderately concerned", "Very concerned", "Extremely concerned"])
    low_concern = sum(counts.get(k, 0) for k in ["Not at all concerned", "Slightly concerned"])
    con_pct = concerned / n * 100
    low_pct = low_concern / n * 100
    level = "high" if con_pct > low_pct else "low"
    return (
        f"**N = {n}.** "
        f"Concerned (Moderately + Very + Extremely): **{con_pct:.1f}%**. "
        f"Low concern (Not at all + Slightly): **{low_pct:.1f}%**. "
        f"Overall concern level is **{level}**."
    )


def describe_multiselect(series: pd.Series) -> str:
    n = series.count()
    items = series.dropna().str.split(", ").explode()
    counts = items.value_counts()
    top3 = counts.head(3)
    parts = [f"**N = {n}** respondents ({len(items)} total selections, multi-select)."]
    for opt, cnt in top3.items():
        pct = cnt / n * 100
        parts.append(f'"{opt}" selected by {pct:.1f}% of respondents.')
    return " ".join(parts)
