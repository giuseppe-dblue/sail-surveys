"""
Ordinal encodings, Spearman correlation, BH correction, Kruskal-Wallis country
comparison, and notable-pair extraction for the teacher correlation analysis.

Reuses compute_spearman, bh_significant, cluster_order from correlation.py.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from analysis.constants import PRIMARY_COUNTRIES
from analysis.correlation import bh_significant, cluster_order, compute_spearman
from analysis.questions_teachers import QUESTIONS_TEACHERS

# ── Labels ────────────────────────────────────────────────────────────────────

CORR_LABELS_T: dict[str, str] = {q["col"]: q["label"] for q in QUESTIONS_TEACHERS}

_INDICATOR_LABELS: dict[str, str] = {
    "use_brainstorming":     "Uses AI: Brainstorming",
    "use_translating":       "Uses AI: Translation",
    "use_summarizing":       "Uses AI: Summarizing",
    "use_writing":           "Uses AI: Writing/drafting",
    "use_lesson_planning":   "Uses AI: Lesson planning",
    "use_generating_images": "Uses AI: Images/presentations",
    "feeling_curiosity":     "Feels: Curiosity",
    "feeling_skepticism":    "Feels: Skepticism",
    "feeling_suspicion":     "Feels: Suspicion",
    "feeling_hope":          "Feels: Hope",
    "feeling_fear":          "Feels: Fear",
    "feeling_anxiety":       "Feels: Anxiety",
}
CORR_LABELS_T.update(_INDICATOR_LABELS)

# Binary indicator columns included in the correlation matrix (count ≥ 13)
INDICATOR_COLS: list[str] = list(_INDICATOR_LABELS.keys())

# ── Ordinal encodings ─────────────────────────────────────────────────────────

_LIKERT4 = {"Strongly Disagree": 1, "Disagree": 2, "Agree": 3, "Strongly Agree": 4}
_CONCERN5 = {
    "Not at all concerned": 1, "Slightly concerned": 2,
    "Moderately concerned": 3, "Very concerned": 4, "Extremely concerned": 5,
}
_FREQ5 = {"Never": 1, "Rarely": 2, "A few times a month": 3, "A few times a week": 4, "Daily": 5}

ORDINAL_ENCODINGS_T: dict[str, dict[str, int]] = {
    "3. Age Group": {
        "Under 30": 1, "30-40": 2, "41-50": 3, "51-60": 4, "Over 60": 5,
    },
    "4. Years of Teaching Experience": {
        "0-5 years": 1, "6-15 years": 2, "16-25 years": 3, "Over 25 years": 4,
    },
    "6. Self-Assessed Knowledge: How knowledgeable do you consider yourself about Artificial Intelligence?": {
        "1 - Absolute Beginner: I know almost nothing. I have heard the term but don't really know what it is or how to use it.": 1,
        "2 - Novice: I know the basic concepts and have seen AI tools, but I rarely or never use them myself.": 2,
        "3 - Intermediate: I use some AI tools occasionally for simple tasks and understand their basic functions.": 3,
        "4 - Advanced: I use AI tools regularly for various tasks and have a good understanding of their capabilities, limits, and potential biases.": 4,
        "5 - Expert: I have a deep understanding of how AI works, use it extensively, and could comfortably teach others how to use it responsibly.": 5,
    },
    "2.1 Frequency of Use: How often do you currently use Generative AI tools?": _FREQ5,
    "2.2.1 Output Reworking: When you generate text or content using AI, how do you typically handle the output?": {
        "I copy and paste it directly without reading it thoroughly.": 1,
        "I read it to check for major errors, but keep it mostly intact.": 2,
        "I review the AI-generated output to identify potential errors and refine the text as necessary.": 3,
        "I use it as a draft or inspiration and rewrite it heavily.": 4,
        "I only use AI to review or correct content I have entirely written myself.": 5,
    },
    "2.2.2 Quality Perception: How do you usually evaluate the quality of the AI-generated output compared to what you could have done on your own?": {
        "The AI's output was poor/incorrect, and I had to redo most of it.": 1,
        "My original work would have been better, but the AI was faster.": 2,
        "The AI and I would have produced a similar result.": 3,
        "The AI produced a much better result than I could have.": 4,
    },
    "2.2.3 Efficiency and Value: Overall, how does using AI affect the time and effort required for your tasks?": {
        "It is a waste of time (I spend more time prompting and correcting than doing it myself).": 1,
        "It has no significant impact on my time or effort.": 2,
        "It enriches my work (gives me ideas I wouldn't have had), but takes about the same amount of time.": 3,
        "It is a huge time saver.": 4,
    },
    "2.2.4 Interaction Effort (Prompting): How much time and effort do you usually spend interacting with the AI to get a satisfactory result?": {
        "Very little time (I usually accept the first answer it provides).": 1,
        "A moderate amount of time (I ask for a few adjustments or refinements).": 2,
        "A significant amount of time (I engage in long conversations, going back and forth until the output is perfect).": 3,
        "It takes so much time that sometimes I just give up and do the work myself.": 4,
    },
    "2.3 Confidence in Detection: How confident are you in your ability to distinguish a text or image created by a human from one generated by AI?": {
        "Not at all confident": 1, "Not very confident": 2,
        "Somewhat confident": 3, "Very confident": 4,
    },
    "2.3.1 Fact-Checking Habits: When an AI tool provides you with new historical, scientific, or factual information, what do you usually do?": {
        "I trust it completely and use it as is.": 1,
        "I ask the AI itself if it is sure about the answer.": 2,
        "I do a quick search (e.g., Google, Wikipedia) to verify it.": 3,
        "I systematically check primary and authoritative sources to confirm the data.": 4,
    },
    "2.3.2 Awareness of Hallucinations: Have you ever noticed an AI tool completely inventing a source, fact, or name that sounded extremely convincing but was actually fake?": {
        "I didn't know AI could do that.": 1,
        "No, never.": 2, "Yes, occasionally.": 3, "Yes, frequently.": 4,
    },
    "2.3.3 Awareness of Bias: Have you ever noticed that AI-generated images or texts tend to reflect cultural or gender stereotypes?": {
        "I have never paid attention to this aspect.": 1,
        "No, never.": 2, "Yes, occasionally.": 3, "Yes, frequently.": 4,
    },
    "DT1.1 Technology Adoption Profile: When a new digital technology is released": {
        "You only use it if it is strictly required for school or work.": 1,
        "You wait until it becomes mainstream and most people are using it.": 2,
        "You try it out after hearing good things from friends or colleagues.": 3,
        "You are one of the first to try it out.": 4,
    },
    "DT1.2 Specific Frequency of Use: How often do you use Generative AI tools specifically for school-related or work-related tasks?": _FREQ5,
    "DT1.4 I feel I possess the right pedagogical strategies to integrate AI into my lessons in a way that truly enhances learning, rather than just acting as a shortcut": _LIKERT4,
    "DT1.5 Guidelines on AI: My school provides clear guidelines and support on how to use AI in the classroom.": _LIKERT4,
    'DT2.1 AI tools truly "understand" the meaning of the text they generate.': _LIKERT4,
    "DT2.2 The information provided by AI is generally neutral, objective, and unbiased.": _LIKERT4,
    "DT2.3 I think AI is inherently smarter and more capable than human beings.": _LIKERT4,
    "DT2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": _LIKERT4,
    "DT2.5 I clearly understand how a GenAI assistant generates its responses.": _LIKERT4,
    "DT2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": _LIKERT4,
    "DT3.1 The widespread use of AI makes it impossible to assess students' real learning and capabilities accurately.": _CONCERN5,
    "DT3.2 Relying on AI will reduce students' critical thinking, creativity, and problem-solving skills.": _CONCERN5,
    "DT3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": _CONCERN5,
    "DT3.4 How AI platforms collect, use, and store the personal data and inputs of my students.": _CONCERN5,
    "DT3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": _CONCERN5,
    "DT3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": _CONCERN5,
    "DT3.7 The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.": _LIKERT4,
    "DT3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": _LIKERT4,
    "DT4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": _LIKERT4,
    "DT4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": _LIKERT4,
    "DT4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": _LIKERT4,
    "DT4.4. I expect AI to take over administrative and grading tasks, freeing up my time to focus more on human interaction and mentoring.": _LIKERT4,
}

# ── Plain-language descriptions ───────────────────────────────────────────────

HIGH_PHRASE_T: dict[str, str] = {
    "3. Age Group": "being in an older age group",
    "4. Years of Teaching Experience": "extensive teaching experience",
    "6. Self-Assessed Knowledge: How knowledgeable do you consider yourself about Artificial Intelligence?": "high self-assessed AI knowledge",
    "2.1 Frequency of Use: How often do you currently use Generative AI tools?": "frequent general AI use",
    "2.2.1 Output Reworking: When you generate text or content using AI, how do you typically handle the output?": "heavy human reworking of AI output",
    "2.2.2 Quality Perception: How do you usually evaluate the quality of the AI-generated output compared to what you could have done on your own?": "perceiving AI output as high quality",
    "2.2.3 Efficiency and Value: Overall, how does using AI affect the time and effort required for your tasks?": "finding AI a big time saver",
    "2.2.4 Interaction Effort (Prompting): How much time and effort do you usually spend interacting with the AI to get a satisfactory result?": "spending a lot of time prompting AI",
    "2.3 Confidence in Detection: How confident are you in your ability to distinguish a text or image created by a human from one generated by AI?": "high confidence in detecting AI-generated content",
    "2.3.1 Fact-Checking Habits: When an AI tool provides you with new historical, scientific, or factual information, what do you usually do?": "rigorous fact-checking of AI output",
    "2.3.2 Awareness of Hallucinations: Have you ever noticed an AI tool completely inventing a source, fact, or name that sounded extremely convincing but was actually fake?": "frequent awareness of AI hallucinations",
    "2.3.3 Awareness of Bias: Have you ever noticed that AI-generated images or texts tend to reflect cultural or gender stereotypes?": "frequent awareness of AI bias",
    "DT1.1 Technology Adoption Profile: When a new digital technology is released": "being an early technology adopter",
    "DT1.2 Specific Frequency of Use: How often do you use Generative AI tools specifically for school-related or work-related tasks?": "frequent AI use for school/work tasks",
    "DT1.4 I feel I possess the right pedagogical strategies to integrate AI into my lessons in a way that truly enhances learning, rather than just acting as a shortcut": "confidence in pedagogical AI integration",
    "DT1.5 Guidelines on AI: My school provides clear guidelines and support on how to use AI in the classroom.": "agreement that school provides clear AI guidelines",
    'DT2.1 AI tools truly "understand" the meaning of the text they generate.': "believing AI truly understands text",
    "DT2.2 The information provided by AI is generally neutral, objective, and unbiased.": "believing AI is neutral and unbiased",
    "DT2.3 I think AI is inherently smarter and more capable than human beings.": "believing AI is smarter than humans",
    "DT2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": "trusting AI accuracy without checking",
    "DT2.5 I clearly understand how a GenAI assistant generates its responses.": "understanding how GenAI works",
    "DT2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": "believing prompting style doesn't affect output",
    "DT3.1 The widespread use of AI makes it impossible to assess students' real learning and capabilities accurately.": "high concern about AI undermining student assessment",
    "DT3.2 Relying on AI will reduce students' critical thinking, creativity, and problem-solving skills.": "high concern about AI reducing students' critical thinking",
    "DT3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": "high concern about detecting AI-generated content",
    "DT3.4 How AI platforms collect, use, and store the personal data and inputs of my students.": "high concern about student data privacy",
    "DT3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": "high concern about AI reinforcing social biases",
    "DT3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": "high concern about unequal AI access",
    "DT3.7 The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.": "feeling stressed by pressure to keep up with AI tools",
    "DT3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": "concern that AI reliance reduces own sense of capability",
    "DT4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": "expecting AI to significantly speed up work tasks",
    "DT4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": "expecting AI to personalise learning perfectly",
    "DT4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": "expecting AI to improve learning accessibility",
    "DT4.4. I expect AI to take over administrative and grading tasks, freeing up my time to focus more on human interaction and mentoring.": "expecting AI to free teachers from admin and grading",
    # Binary indicators
    "use_brainstorming":     "using AI for brainstorming",
    "use_translating":       "using AI for translation",
    "use_summarizing":       "using AI for summarising",
    "use_writing":           "using AI for writing/drafting",
    "use_lesson_planning":   "using AI for lesson planning",
    "use_generating_images": "using AI for images/presentations",
    "feeling_curiosity":     "feeling curious about AI in education",
    "feeling_skepticism":    "feeling skeptical about AI in education",
    "feeling_suspicion":     "feeling suspicious about AI in education",
    "feeling_hope":          "feeling hopeful about AI in education",
    "feeling_fear":          "feeling fearful about AI in education",
    "feeling_anxiety":       "feeling anxious about AI in education",
}

LOW_PHRASE_T: dict[str, str] = {
    "3. Age Group": "being in a younger age group",
    "4. Years of Teaching Experience": "early-career teaching (few years of experience)",
    "6. Self-Assessed Knowledge: How knowledgeable do you consider yourself about Artificial Intelligence?": "low self-assessed AI knowledge",
    "2.1 Frequency of Use: How often do you currently use Generative AI tools?": "rare general AI use",
    "2.2.1 Output Reworking: When you generate text or content using AI, how do you typically handle the output?": "copy-pasting AI output with little review",
    "2.2.2 Quality Perception: How do you usually evaluate the quality of the AI-generated output compared to what you could have done on your own?": "perceiving AI output as low quality",
    "2.2.3 Efficiency and Value: Overall, how does using AI affect the time and effort required for your tasks?": "finding AI inefficient or wasteful",
    "2.2.4 Interaction Effort (Prompting): How much time and effort do you usually spend interacting with the AI to get a satisfactory result?": "spending very little time prompting AI",
    "2.3 Confidence in Detection: How confident are you in your ability to distinguish a text or image created by a human from one generated by AI?": "low confidence in detecting AI-generated content",
    "2.3.1 Fact-Checking Habits: When an AI tool provides you with new historical, scientific, or factual information, what do you usually do?": "trusting AI output without fact-checking",
    "2.3.2 Awareness of Hallucinations: Have you ever noticed an AI tool completely inventing a source, fact, or name that sounded extremely convincing but was actually fake?": "low awareness of AI hallucinations",
    "2.3.3 Awareness of Bias: Have you ever noticed that AI-generated images or texts tend to reflect cultural or gender stereotypes?": "low awareness of AI bias",
    "DT1.1 Technology Adoption Profile: When a new digital technology is released": "being a late or reluctant technology adopter",
    "DT1.2 Specific Frequency of Use: How often do you use Generative AI tools specifically for school-related or work-related tasks?": "rare AI use for school/work tasks",
    "DT1.4 I feel I possess the right pedagogical strategies to integrate AI into my lessons in a way that truly enhances learning, rather than just acting as a shortcut": "limited confidence in pedagogical AI integration",
    "DT1.5 Guidelines on AI: My school provides clear guidelines and support on how to use AI in the classroom.": "disagreement that school provides clear AI guidelines",
    'DT2.1 AI tools truly "understand" the meaning of the text they generate.': "doubting AI truly understands text",
    "DT2.2 The information provided by AI is generally neutral, objective, and unbiased.": "doubting AI neutrality",
    "DT2.3 I think AI is inherently smarter and more capable than human beings.": "doubting AI surpasses human capability",
    "DT2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.": "verifying AI accuracy before trusting it",
    "DT2.5 I clearly understand how a GenAI assistant generates its responses.": "limited understanding of how GenAI works",
    "DT2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced": "believing prompting style matters for output quality",
    "DT3.1 The widespread use of AI makes it impossible to assess students' real learning and capabilities accurately.": "low concern about AI undermining student assessment",
    "DT3.2 Relying on AI will reduce students' critical thinking, creativity, and problem-solving skills.": "low concern about AI and critical thinking",
    "DT3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).": "low concern about detecting AI-generated content",
    "DT3.4 How AI platforms collect, use, and store the personal data and inputs of my students.": "low concern about student data privacy",
    "DT3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).": "low concern about AI reinforcing social biases",
    "DT3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.": "low concern about unequal AI access",
    "DT3.7 The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.": "not feeling stressed by AI learning pressure",
    "DT3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.": "no concern about AI reliance reducing self-efficacy",
    "DT4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.": "not expecting AI to speed up work tasks",
    "DT4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.": "not expecting AI to personalise learning",
    "DT4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.": "not expecting AI to improve accessibility",
    "DT4.4. I expect AI to take over administrative and grading tasks, freeing up my time to focus more on human interaction and mentoring.": "not expecting AI to handle admin and grading",
    # Binary indicators
    "use_brainstorming":     "not using AI for brainstorming",
    "use_translating":       "not using AI for translation",
    "use_summarizing":       "not using AI for summarising",
    "use_writing":           "not using AI for writing/drafting",
    "use_lesson_planning":   "not using AI for lesson planning",
    "use_generating_images": "not using AI for images/presentations",
    "feeling_curiosity":     "not feeling curious about AI in education",
    "feeling_skepticism":    "not feeling skeptical about AI in education",
    "feeling_suspicion":     "not feeling suspicious about AI in education",
    "feeling_hope":          "not feeling hopeful about AI in education",
    "feeling_fear":          "not feeling fearful about AI in education",
    "feeling_anxiety":       "not feeling anxious about AI in education",
}

# ── Computation ───────────────────────────────────────────────────────────────

def encode_ordinal_teachers(df: pd.DataFrame) -> pd.DataFrame:
    """Encode ordinal columns + binary indicator columns into a numeric DataFrame."""
    encoded = {
        col: df[col].map(mapping)
        for col, mapping in ORDINAL_ENCODINGS_T.items()
        if col in df.columns
    }
    for ind_col in INDICATOR_COLS:
        if ind_col in df.columns:
            encoded[ind_col] = df[ind_col].astype(float)
    return pd.DataFrame(encoded, index=df.index)


def compute_kruskal_wallis_country(
    df: pd.DataFrame,
    encoded: pd.DataFrame,
) -> pd.DataFrame:
    """
    For each ordinal variable run Kruskal-Wallis across the four countries.
    Returns a DataFrame sorted by ε² (epsilon-squared effect size).

    ε² = (H − k + 1) / (N − k)  where k = number of groups, N = total N.
    Ranges 0–1; ≥ 0.06 is a medium effect, ≥ 0.14 is large.
    """
    country_col = "1. Country"
    countries = [c for c in PRIMARY_COUNTRIES if c in df[country_col].values]
    results = []

    for col in encoded.columns:
        groups = [
            encoded.loc[df[country_col] == c, col].dropna().values
            for c in countries
        ]
        groups = [g for g in groups if len(g) >= 3]
        if len(groups) < 2:
            continue
        try:
            H, p = stats.kruskal(*groups)
        except ValueError:
            continue
        N = sum(len(g) for g in groups)
        k = len(groups)
        eps2 = max(0.0, (H - k + 1) / (N - k))
        results.append({
            "col":         col,
            "label":       CORR_LABELS_T.get(col, col),
            "H":           round(H, 2),
            "p_value":     p,
            "eps2":        round(eps2, 3),
            "significant": p < 0.05,
        })

    return (
        pd.DataFrame(results)
        .sort_values("eps2", ascending=False)
        .reset_index(drop=True)
    )


def notable_pairs_teachers(
    corr: pd.DataFrame,
    sig: pd.DataFrame,
    threshold: float = 0.30,
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
                    f"Teachers who show {HIGH_PHRASE_T.get(c1, c1)} "
                    f"tend to also show {HIGH_PHRASE_T.get(c2, c2)}."
                )
            else:
                sentence = (
                    f"Teachers who show {HIGH_PHRASE_T.get(c1, c1)} "
                    f"tend to show {LOW_PHRASE_T.get(c2, c2)}."
                )
            pairs.append({
                "col_a":     c1,
                "col_b":     c2,
                "label_a":   CORR_LABELS_T.get(c1, c1),
                "label_b":   CORR_LABELS_T.get(c2, c2),
                "r":         round(r, 3),
                "abs_r":     round(abs_r, 3),
                "strength":  strength,
                "direction": direction,
                "sentence":  sentence,
            })
    return sorted(pairs, key=lambda x: x["abs_r"], reverse=True)
