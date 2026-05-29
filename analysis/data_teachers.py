import pandas as pd
import streamlit as st
from pathlib import Path

TEACHERS_DATA_PATH = (
    Path(__file__).parent.parent
    / "data/teachers/final-translated-responses 8-04-2026.csv"
)

COUNTRY_REMAP = {
    "CATALUNYA": "Spain",
}

# Untranslated single-select responses → English equivalents.
# Keyed by exact column name; values use ’ (curly apostrophe) where the
# raw CSV has it (Italian/Turkish responses retain original Unicode punctuation).
_VALUE_MAPS: dict[str, dict[str, str]] = {
    # Q6 — Self-Assessed Knowledge: three Turkish responses not translated
    "6. Self-Assessed Knowledge: How knowledgeable do you consider yourself about Artificial Intelligence?": {
        "4 - İleri Seviye: Yapay zeka araçlarını çeşitli görevler için düzenli olarak kullanıyorum; yetenekleri, sınırları ve potan"
        "siyel yanlılıkları hakkında iyi bir anlayışa sahibim.":
            "4 - Advanced: I use AI tools regularly for various tasks and have a good understanding of their capabilities, limits, and potential biases.",
        "3 - Orta Seviye: Bazı yapay zeka araçlarını basit görevler için ara sıra kullanıyorum ve temel işlevlerini anlıyorum.":
            "3 - Intermediate: I use some AI tools occasionally for simple tasks and understand their basic functions.",
        "1 - Tamamen Başlangıç Seviyesi: Neredeyse hiçbir şey bilmiyorum. Terimi duydum ama ne olduğunu veya nasıl kullanıldığını bilmiyorum.":
            "1 - Absolute Beginner: I know almost nothing. I have heard the term but don't really know what it is or how to use it.",
    },
    # Q12 — Interaction Effort: one Italian response; apostrophe is U+2019
    "2.2.4 Interaction Effort (Prompting): How much time and effort do you usually spend interacting with the AI to get a satisfactory result?": {
        "Una quantità significativa di tempo (mi impegno in lunghe conversazioni, facendo diverse revisioni finché l’output è perfetto).":
            "A significant amount of time (I engage in long conversations, going back and forth until the output is perfect).",
    },
    # Q14 — Fact-Checking: one Italian response
    "2.3.1 Fact-Checking Habits: When an AI tool provides you with new historical, scientific, or factual information, what do you usually do?": {
        "Mi fido completamente e le uso così come sono.":
            "I trust it completely and use it as is.",
    },
    # Q18 — Technology Adoption: one Italian response
    "DT1.1 Technology Adoption Profile: When a new digital technology is released": {
        "La usi solo se è strettamente necessaria per la scuola.":
            "You only use it if it is strictly required for school or work.",
    },
    # Q22 — Guidelines: one Italian response; apostrophe is U+2019
    "DT1.5 Guidelines on AI: My school provides clear guidelines and support on how to use AI in the classroom.": {
        "Non sono d’accordo": "Disagree",
    },
    # DT3.7 and DT3.8 use sentence-case Likert; normalise to Title Case to match
    # all other Likert columns and the shared LIKERT4_ORDER constant.
    "DT3.7 The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.": {
        "Strongly agree": "Strongly Agree",
        "Strongly disagree": "Strongly Disagree",
    },
    "DT3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": {
        "Strongly agree": "Strongly Agree",
        "Strongly disagree": "Strongly Disagree",
    },
}

# DT2.6 column name has Mojibake: UTF-8 bytes for U+2019 were decoded as cp1252,
# producing the three-character sequence U+201A U+00C4 U+00F4 ("‚Äô").
_COLUMN_RENAMES = {
    "DT2.6 The way I request something to AI doesn‚Äôt have any impact on the quality of the result produced":
        "DT2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced",
}

# ── Multi-select: Q8 Primary Use Cases ────────────────────────────────────────
# Canonical English option → binary column name
USE_CASE_OPTIONS: dict[str, str] = {
    "Brainstorming ideas and getting inspiration":      "use_brainstorming",
    "Translating texts or learning a language":        "use_translating",
    "Summarizing long documents or articles":          "use_summarizing",
    "Writing/drafting text (emails, essays, reports)": "use_writing",
    "Solving math/logic problems or coding":           "use_coding",
    "Helping with homework / Lesson planning":         "use_lesson_planning",
    "Generating images or presentations":              "use_generating_images",
    "I do not use AI tools":                           "use_none",
}
USE_CASE_COL = "2.2 Primary Use Cases: What are the main tasks you use AI for?"

# Non-English substrings found in Q8 raw values → canonical English option.
# These all contain commas inside parentheses, which breaks naive comma-splitting,
# so we use substring matching instead (see _expand_multiselect).
_USE_CASE_TOKEN_MAP: dict[str, str] = {
    "Scrivere/abbozzare testi (email, saggi, relazioni)":
        "Writing/drafting text (emails, essays, reports)",
    "Preparazione compiti":
        "Helping with homework / Lesson planning",
    "Pisanje/osnutek besedila (e-poštna sporočila, eseji, poročila)":
        "Writing/drafting text (emails, essays, reports)",
    "Escriptura/redacció de textos (correus electrònics, assaigs, informes)":
        "Writing/drafting text (emails, essays, reports)",
    "Metin yazmak/taslak oluşturmak (e-posta, makale, rapor)":
        "Writing/drafting text (emails, essays, reports)",
}

# ── Multi-select: Q17 General Feeling ─────────────────────────────────────────
FEELING_OPTIONS: dict[str, str] = {
    "Anxiety":    "feeling_anxiety",
    "Curiosity":  "feeling_curiosity",
    "Enthusiasm": "feeling_enthusiasm",
    "Excitement": "feeling_excitement",
    "Fear":       "feeling_fear",
    "Hope":       "feeling_hope",
    "Skepticism": "feeling_skepticism",
    "Suspicion":  "feeling_suspicion",
}
FEELING_COL = (
    "2.4 General Feeling: When you think about the integration of AI in school "
    "and education, which of the following feelings prevail?"
)

# Non-English substrings in Q17 raw values → canonical English feeling
_FEELING_TOKEN_MAP: dict[str, str] = {
    "Desconfiança": "Suspicion",   # Catalan "distrust"
    "curiositat":   "Curiosity",   # Catalan "curiosity" (may have free text appended)
}

# Noise tokens to strip when computing "other" residual
_NOISE_TOKENS = ("Other _______", "Option 1")


def _expand_multiselect(
    df: pd.DataFrame,
    col: str,
    canonical_options: dict[str, str],
    token_map: dict[str, str],
) -> pd.DataFrame:
    """Expand a multi-select column into binary indicator columns.

    Uses substring matching rather than comma-splitting so that canonical and
    foreign options that contain commas (e.g. inside parentheses) are handled
    correctly.  After matching all known tokens the residual text is checked:
    if anything non-trivial remains the row is flagged as '_other_flag'.
    """
    for flag_col in canonical_options.values():
        df[flag_col] = 0
    df["_other_flag"] = 0

    all_known = list(canonical_options.keys()) + list(token_map.keys())

    for idx, raw in df[col].items():
        if pd.isna(raw):
            continue
        raw_str = str(raw)

        # Match canonical English options
        for canonical, flag_col in canonical_options.items():
            if canonical in raw_str:
                df.at[idx, flag_col] = 1

        # Match known foreign tokens
        for foreign, canonical in token_map.items():
            if foreign in raw_str:
                if canonical in canonical_options:
                    df.at[idx, canonical_options[canonical]] = 1

        # Detect free-text "Other": strip every known token, then strip noise
        # placeholders and punctuation; flag if anything meaningful remains.
        residual = raw_str
        for token in all_known:
            residual = residual.replace(token, "")
        for noise in _NOISE_TOKENS:
            residual = residual.replace(noise, "")
        residual = residual.replace(",", " ").strip()
        if residual:
            df.at[idx, "_other_flag"] = 1

    return df


@st.cache_data
def load_teachers() -> pd.DataFrame:
    df = pd.read_csv(TEACHERS_DATA_PATH, encoding="utf-8")

    # Fix Mojibake column name
    df = df.rename(columns=_COLUMN_RENAMES)

    # Country normalisation
    df["1. Country"] = df["1. Country"].replace(COUNTRY_REMAP)

    # Normalise untranslated single-select values
    for col, mapping in _VALUE_MAPS.items():
        if col in df.columns:
            df[col] = df[col].replace(mapping)

    # Expand multi-select: Use Cases → use_* indicator columns
    df = _expand_multiselect(df, USE_CASE_COL, USE_CASE_OPTIONS, _USE_CASE_TOKEN_MAP)
    df = df.rename(columns={"_other_flag": "use_other"})

    # Expand multi-select: General Feeling → feeling_* indicator columns
    df = _expand_multiselect(df, FEELING_COL, FEELING_OPTIONS, _FEELING_TOKEN_MAP)
    df = df.rename(columns={"_other_flag": "feeling_other"})

    return df
