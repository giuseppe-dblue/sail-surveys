from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data/students/Students Responses - merged-en.csv"

PRIMARY_COUNTRIES = ["Italy", "Spain", "Slovenia", "Turkey"]

LIKERT4_ORDER = ["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"]
LIKERT4_COLORS = ["#d73027", "#fc8d59", "#91bfdb", "#4575b4"]

CONCERN5_ORDER = [
    "Not at all concerned", "Slightly concerned",
    "Moderately concerned", "Very concerned", "Extremely concerned",
]
CONCERN5_COLORS = ["#C5CAE9", "#9FA8DA", "#7986CB", "#3949AB", "#1A237E"]

CONFIDENCE_ORDER = ["Not at all confident", "Not very confident", "Somewhat confident", "Very confident"]
CONFIDENCE_COLORS = ["#C5CAE9", "#9FA8DA", "#3949AB", "#1A237E"]  # 4 shades, skip middle

# ── Ordinal sequential (indigo, light → dark) ─────────────────────────────────
# Used for all ordered scales that are NOT agree/disagree Likert:
# knowledge, frequency, efficiency, interaction effort, confidence, concern,
# hallucination awareness, bias awareness.
_ORDINAL_SEQ = ["#C5CAE9", "#9FA8DA", "#7986CB", "#3949AB", "#1A237E"]


def ordinal_colors(n: int) -> list[str]:
    """Return n evenly-spaced indigo shades from the 5-step sequential palette."""
    if n == 1:
        return [_ORDINAL_SEQ[2]]
    indices = [round(i * (len(_ORDINAL_SEQ) - 1) / (n - 1)) for i in range(n)]
    return [_ORDINAL_SEQ[i] for i in indices]

FREQ_ORDER = ["Never", "Rarely", "A few times a month", "A few times a week", "Daily"]
GRADE_ORDER = ["1st year", "2nd year", "3rd year", "4th year", "5th year"]

AGE_ORDER = ["Under 30", "30-40", "41-50", "51-60", "Over 60"]
EXPERIENCE_ORDER = ["0-5 years", "6-15 years", "16-25 years", "Over 25 years"]

# ── Qualitative palettes ───────────────────────────────────────────────────────
# Each palette occupies a distinct hue zone so Country, Gender, Grade, and the
# Likert/Concern scales never share a color family.
#
# Taken zones: red/salmon (Likert neg, Concern high), yellow/lime-green (Concern
# low-mid), periwinkle/dark-blue (Likert pos).
#
# Country  → teal · amber-gold · deep-magenta · slate   (zones: ~170°, ~42°, ~336°, ~198°)
# Gender   → soft-pink · sky-blue · sage-green · gray   (zones: ~340°, ~200°, ~125°, neutral)
# Grade    → violet-purple sequential 5 shades            (zone: ~275° — used nowhere else)

COUNTRY_COLOR_MAP = {
    "Italy":    "#00897B",  # teal
    "Spain":    "#FFB300",  # amber-gold
    "Slovenia": "#D81B60",  # deep magenta
    "Turkey":   "#546E7A",  # slate blue-gray
}

GENDER_COLOR_MAP = {
    "Female":            "#F48FB1",  # soft pink
    "Male":              "#90CAF9",  # light sky-blue
    "Non-binary":        "#A5D6A7",  # sage green
    "Prefer not to say": "#B0BEC5",  # cool gray
}

# Violet-purple, light → dark (Material Design Purple 100 → 900)
GRADE_COLORS = ["#E1BEE7", "#CE93D8", "#AB47BC", "#7B1FA2", "#4A0072"]

KNOWLEDGE_ORDER = [
    "1 - Absolute Beginner: I know almost nothing. I have heard the term but don't really know what it is or how to use it.",
    "2 - Novice: I know the basic concepts and have seen AI tools, but I rarely or never use them myself.",
    "3 - Intermediate: I use some AI tools occasionally for simple tasks and understand their basic functions.",
    "4 - Advanced: I use AI tools regularly for various tasks and have a good understanding of their capabilities, limits, and potential biases.",
    "5 - Expert: I have a deep understanding of how AI works, use it extensively, and could comfortably teach others how to use it responsibly.",
]
KNOWLEDGE_SHORT = {k: k.split(":")[0].strip() for k in KNOWLEDGE_ORDER}
