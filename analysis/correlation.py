"""
Ordinal encodings, Spearman correlation computation, BH correction, and clustering
for the correlation analysis tab.
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from statsmodels.stats.multitest import multipletests

from analysis.questions import QUESTIONS

# Reuse short labels already defined in the question registry
CORR_LABELS: dict[str, str] = {q["col"]: q["label"] for q in QUESTIONS}

# ── Ordinal encodings ─────────────────────────────────────────────────────────
# Score direction: 1 = low / negative / rare, N = high / positive / frequent.
# This convention is used to generate plain-language descriptions.

_LIKERT4 = {"Strongly Disagree": 1, "Disagree": 2, "Agree": 3, "Strongly Agree": 4}
_CONCERN5 = {
    "Not at all concerned": 1, "Slightly concerned": 2,
    "Moderately concerned": 3, "Very concerned": 4, "Extremely concerned": 5,
}
_FREQ5 = {"Never": 1, "Rarely": 2, "A few times a month": 3, "A few times a week": 4, "Daily": 5}

ORDINAL_ENCODINGS: dict[str, dict[str, int]] = {
    "4. Self-Assessed Knowledge": {
        "1 - Absolute Beginner: I know almost nothing. I have heard the term but don't really know what it is or how to use it.": 1,
        "2 - Novice: I know the basic concepts and have seen AI tools, but I rarely or never use them myself.": 2,
        "3 - Intermediate: I use some AI tools occasionally for simple tasks and understand their basic functions.": 3,
        "4 - Advanced: I use AI tools regularly for various tasks and have a good understanding of their capabilities, limits, and potential biases.": 4,
        "5 - Expert: I have a deep understanding of how AI works, use it extensively, and could comfortably teach others how to use it responsibly.": 5,
    },
    "2.1 Frequency of Use": _FREQ5,
    "2.2.1 Output Reworking (Human-AI Teaming)": {
        "I copy and paste it directly without reading it thoroughly.": 1,
        "I read it to check for major errors, but keep it mostly intact.": 2,
        "I review the AI-generated output to identify potential errors and refine the text as necessary.": 3,
        "I use it as a draft or inspiration and rewrite it heavily.": 4,
        "I only use AI to review or correct content I have entirely written myself.": 5,
    },
    "2.2.2 Quality Perception": {
        "The AI's output was poor/incorrect, and I had to redo most of it.": 1,
        "My original work would have been better, but the AI was faster.": 2,
        "The AI and I would have produced a similar result.": 3,
        "The AI produced a much better result than I could have.": 4,
    },
    "2.2.3 Efficiency and Value": {
        "It is a waste of time (I spend more time prompting and correcting than doing it myself).": 1,
        "It has no significant impact on my time or effort.": 2,
        "It enriches my work (gives me ideas I wouldn't have had), but takes about the same amount of time.": 3,
        "It is a huge time saver.": 4,
    },
    "2.2.4 Interaction Effort (Prompting)": {
        "Very little time (I usually accept the first answer it provides).": 1,
        "A moderate amount of time (I ask for a few adjustments or refinements).": 2,
        "A significant amount of time (I engage in long conversations, going back and forth until the output is perfect).": 3,
        "It takes so much time that sometimes I just give up and do the work myself.": 4,
    },
    "2.3 Confidence in Detection (Media Literacy)": {
        "Not at all confident": 1, "Not very confident": 2,
        "Somewhat confident": 3, "Very confident": 4,
    },
    "2.3.1 Fact-Checking Habits": {
        "I trust it completely and use it as is.": 1,
        "I ask the AI itself if it is sure about the answer.": 2,
        "I do a quick search (e.g., Google, Wikipedia) to verify it.": 3,
        "I systematically check primary and authoritative sources to confirm the data.": 4,
    },
    "2.3.2 Awareness of Hallucinations": {
        "I didn't know AI could do that.": 1,
        "No, never.": 2, "Yes, occasionally.": 3, "Yes, frequently.": 4,
    },
    "2.3.3 Awareness of Bias": {
        "I have never paid attention to this aspect.": 1,
        "No, never.": 2, "Yes, occasionally.": 3, "Yes, frequently.": 4,
    },
    "DS1.1 Technology Adoption Profile": {
        "You only use it if it is strictly required for school or work.": 1,
        "You wait until it becomes mainstream and most people are using it.": 2,
        "You try it out after hearing good things from friends or colleagues.": 3,
        "You are one of the first to try it out.": 4,
    },
    "DS1.2 Specific Frequency of Use": _FREQ5,
    "DS1.5 Guidelines on AI": _LIKERT4,
    'DS2.1 AI tools truly "understand" the meaning of the text they generate.': _LIKERT4,
    "DS2.2 The information provided by AI is generally neutral, objective, and unbiased.": _LIKERT4,
    "DS2.3 I think AI is inherently smarter and more capable than human beings.": _LIKERT4,
    "DS2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": _LIKERT4,
    "DS2.5 I clearly understand how a GenAI assistant generates its responses.": _LIKERT4,
    "DS2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": _LIKERT4,
    "DS3.1 Teachers will unfairly accuse me of using AI for my assignments even when I do not.": _CONCERN5,
    "DS3.2 Using AI to do my homework will make me lose the ability to think critically and learn independently.": _CONCERN5,
    "DS3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": _CONCERN5,
    "DS3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": _CONCERN5,
    "DS3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": _CONCERN5,
    # DS3.8 has a survey labeling error: respondents saw DS3.6 text, so responses
    # were recorded on a Likert4 scale rather than the Concern5 scale used by
    # the other DS3 items. ~324 responses are marked invalid; the rest encode fine.
    "DS3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": _LIKERT4,
    "DS4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": _LIKERT4,
    "DS4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": _LIKERT4,
    "DS4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": _LIKERT4,
    "DS4.4 I see AI as a non-judgmental tutor that is available 24/7 to answer my questions without making me feel inadequate.": _LIKERT4,
    "DS4.5 I expect AI to provide better guidance for my future university or career choices than traditional school counselling.": _LIKERT4,
}

# ── Plain-language descriptions ───────────────────────────────────────────────
# Used to auto-generate the partner-facing table.
# high_phrase = what it means to score high on this variable.

HIGH_PHRASE: dict[str, str] = {
    "4. Self-Assessed Knowledge": "high self-assessed AI knowledge",
    "2.1 Frequency of Use": "frequent AI use",
    "2.2.1 Output Reworking (Human-AI Teaming)": "heavy human reworking of AI output",
    "2.2.2 Quality Perception": "perceiving AI output as high quality",
    "2.2.3 Efficiency and Value": "finding AI a big time saver",
    "2.2.4 Interaction Effort (Prompting)": "spending a lot of time prompting AI",
    "2.3 Confidence in Detection (Media Literacy)": "high confidence in detecting AI content",
    "2.3.1 Fact-Checking Habits": "rigorous fact-checking of AI",
    "2.3.2 Awareness of Hallucinations": "frequent awareness of AI hallucinations",
    "2.3.3 Awareness of Bias": "frequent awareness of AI bias",
    "DS1.1 Technology Adoption Profile": "being an early technology adopter",
    "DS1.2 Specific Frequency of Use": "frequent AI use for study",
    "DS1.5 Guidelines on AI": "support for AI guidelines in education",
    'DS2.1 AI tools truly "understand" the meaning of the text they generate.': "believing AI truly understands text",
    "DS2.2 The information provided by AI is generally neutral, objective, and unbiased.": "believing AI is neutral and unbiased",
    "DS2.3 I think AI is inherently smarter and more capable than human beings.": "believing AI is smarter than humans",
    "DS2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": "trusting AI accuracy without checking",
    "DS2.5 I clearly understand how a GenAI assistant generates its responses.": "understanding how GenAI works",
    "DS2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": "believing prompting style doesn't matter",
    "DS3.1 Teachers will unfairly accuse me of using AI for my assignments even when I do not.": "concern about unfair AI accusations",
    "DS3.2 Using AI to do my homework will make me lose the ability to think critically and learn independently.": "concern about AI harming critical thinking",
    "DS3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": "concern about detecting AI-generated content",
    "DS3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": "concern about AI reinforcing social biases",
    "DS3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": "concern about unequal AI access",
    "DS3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": "concern about AI reducing self-efficacy",
    "DS4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": "expecting AI to speed up study tasks",
    "DS4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": "expecting AI to personalise learning",
    "DS4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": "expecting AI to improve accessibility",
    "DS4.4 I see AI as a non-judgmental tutor that is available 24/7 to answer my questions without making me feel inadequate.": "seeing AI as a 24/7 non-judgmental tutor",
    "DS4.5 I expect AI to provide better guidance for my future university or career choices than traditional school counselling.": "expecting AI to guide career choices",
}

LOW_PHRASE: dict[str, str] = {
    "4. Self-Assessed Knowledge": "low self-assessed AI knowledge",
    "2.1 Frequency of Use": "rare AI use",
    "2.2.1 Output Reworking (Human-AI Teaming)": "copy-pasting AI output with little review",
    "2.2.2 Quality Perception": "perceiving AI output as low quality",
    "2.2.3 Efficiency and Value": "finding AI inefficient or wasteful",
    "2.2.4 Interaction Effort (Prompting)": "spending very little time prompting AI",
    "2.3 Confidence in Detection (Media Literacy)": "low confidence in detecting AI content",
    "2.3.1 Fact-Checking Habits": "trusting AI without fact-checking",
    "2.3.2 Awareness of Hallucinations": "low awareness of AI hallucinations",
    "2.3.3 Awareness of Bias": "low awareness of AI bias",
    "DS1.1 Technology Adoption Profile": "being a late/reluctant technology adopter",
    "DS1.2 Specific Frequency of Use": "rare AI use for study",
    "DS1.5 Guidelines on AI": "opposition to AI guidelines in education",
    'DS2.1 AI tools truly "understand" the meaning of the text they generate.': "doubting AI understands text",
    "DS2.2 The information provided by AI is generally neutral, objective, and unbiased.": "doubting AI neutrality",
    "DS2.3 I think AI is inherently smarter and more capable than human beings.": "doubting AI surpasses humans",
    "DS2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": "verifying AI accuracy before trusting it",
    "DS2.5 I clearly understand how a GenAI assistant generates its responses.": "limited understanding of how GenAI works",
    "DS2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": "believing prompting style matters",
    "DS3.1 Teachers will unfairly accuse me of using AI for my assignments even when I do not.": "little concern about unfair AI accusations",
    "DS3.2 Using AI to do my homework will make me lose the ability to think critically and learn independently.": "little concern about AI harming critical thinking",
    "DS3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": "little concern about detecting AI content",
    "DS3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": "little concern about AI reinforcing biases",
    "DS3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": "little concern about unequal AI access",
    "DS3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": "little concern about AI reducing self-efficacy",
    "DS4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": "not expecting AI to speed up tasks",
    "DS4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": "not expecting AI to personalise learning",
    "DS4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": "not expecting AI to improve accessibility",
    "DS4.4 I see AI as a non-judgmental tutor that is available 24/7 to answer my questions without making me feel inadequate.": "not seeing AI as a non-judgmental tutor",
    "DS4.5 I expect AI to provide better guidance for my future university or career choices than traditional school counselling.": "not expecting AI to guide career choices",
}


# ── Computation ───────────────────────────────────────────────────────────────

def encode_ordinal(df: pd.DataFrame) -> pd.DataFrame:
    encoded = {col: df[col].map(mapping) for col, mapping in ORDINAL_ENCODINGS.items() if col in df.columns}
    return pd.DataFrame(encoded, index=df.index)


def compute_spearman(encoded: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = encoded.columns.tolist()
    n = len(cols)
    corr_vals = np.ones((n, n))
    pval_vals = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            mask = encoded.iloc[:, i].notna() & encoded.iloc[:, j].notna()
            r, p = stats.spearmanr(encoded.iloc[mask.values, i], encoded.iloc[mask.values, j])
            corr_vals[i, j] = corr_vals[j, i] = r
            pval_vals[i, j] = pval_vals[j, i] = p
    return (
        pd.DataFrame(corr_vals, index=cols, columns=cols),
        pd.DataFrame(pval_vals, index=cols, columns=cols),
    )


def bh_significant(pvals: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    n = pvals.shape[0]
    idx = np.triu_indices(n, k=1)
    flat_p = pvals.values[idx]
    reject, *_ = multipletests(flat_p, alpha=alpha, method="fdr_bh")
    sig = pd.DataFrame(False, index=pvals.index, columns=pvals.columns)
    for k, (i, j) in enumerate(zip(*idx)):
        sig.iloc[i, j] = sig.iloc[j, i] = bool(reject[k])
    return sig


def cluster_order(corr: pd.DataFrame) -> list[str]:
    vals = corr.values.copy()
    vals = np.nan_to_num(vals, nan=0.0)  # treat missing correlations as uncorrelated
    dist = np.clip(1 - vals, 0, None)
    dist = (dist + dist.T) / 2          # enforce exact symmetry
    np.fill_diagonal(dist, 0)
    condensed = squareform(dist, checks=False)
    linkage = hierarchy.linkage(condensed, method="average")
    order = hierarchy.leaves_list(hierarchy.optimal_leaf_ordering(linkage, condensed))
    return [corr.columns[i] for i in order]


def notable_pairs(
    corr: pd.DataFrame,
    sig: pd.DataFrame,
    threshold: float = 0.25,
) -> list[dict]:
    cols = corr.columns.tolist()
    pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            c1, c2 = cols[i], cols[j]
            r = corr.loc[c1, c2]
            if not sig.loc[c1, c2] or abs(r) < threshold:
                continue
            abs_r = abs(r)
            strength = "Strong" if abs_r >= 0.5 else ("Moderate" if abs_r >= 0.35 else "Weak")
            direction = "positive" if r > 0 else "negative"
            if r > 0:
                sentence = (
                    f"Students with {HIGH_PHRASE.get(c1, c1)} "
                    f"tend to also show {HIGH_PHRASE.get(c2, c2)}."
                )
            else:
                sentence = (
                    f"Students with {HIGH_PHRASE.get(c1, c1)} "
                    f"tend to show {LOW_PHRASE.get(c2, c2)}."
                )
            pairs.append({
                "col_a": c1,
                "col_b": c2,
                "label_a": CORR_LABELS.get(c1, c1),
                "label_b": CORR_LABELS.get(c2, c2),
                "r": round(r, 3),
                "abs_r": round(abs_r, 3),
                "strength": strength,
                "direction": direction,
                "sentence": sentence,
            })
    return sorted(pairs, key=lambda x: x["abs_r"], reverse=True)
