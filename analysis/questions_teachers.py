from analysis.constants import (
    AGE_ORDER,
    CONCERN5_ORDER,
    CONFIDENCE_ORDER,
    COUNTRY_COLOR_MAP,
    EXPERIENCE_ORDER,
    FREQ_ORDER,
    GENDER_COLOR_MAP,
    KNOWLEDGE_ORDER,
    KNOWLEDGE_SHORT,
    LIKERT4_ORDER,
    ordinal_colors,
)
from analysis.data_teachers import (
    FEELING_COL,
    FEELING_OPTIONS,
    USE_CASE_COL,
    USE_CASE_OPTIONS,
)

# Indicator-col dicts for multiselect questions, including "other" bucket
_USE_CASE_INDICATORS = {
    **USE_CASE_OPTIONS,
    "Other (free text)": "use_other",
}

_FEELING_INDICATORS = {
    **FEELING_OPTIONS,
    "Other": "feeling_other",
}

# ── Question registry ──────────────────────────────────────────────────────────
# Each entry mirrors the student QUESTIONS schema with an extra optional key:
#   indicator_cols — dict[display_label, col_name] for multiselects that have
#                    already been expanded into binary indicator columns.

QUESTIONS_TEACHERS: list[dict] = [
    # ── Demographics ──────────────────────────────────────────────────────────
    dict(
        col="1. Country", label="Country", section="Demographics",
        type="categorical", color_map=COUNTRY_COLOR_MAP,
        question_text="Which country are you from?",
    ),
    dict(
        col="2. Gender", label="Gender", section="Demographics",
        type="categorical", color_map=GENDER_COLOR_MAP,
        question_text="What is your gender?",
    ),
    dict(
        col="3. Age Group", label="Age Group", section="Demographics",
        type="ordered_categorical", order=AGE_ORDER, colors=ordinal_colors(5),
        question_text="What is your age group?",
    ),
    dict(
        col="4. Years of Teaching Experience", label="Teaching Experience",
        section="Demographics", type="ordered_categorical",
        order=EXPERIENCE_ORDER, colors=ordinal_colors(4),
        question_text="How many years of teaching experience do you have?",
    ),
    dict(
        col="5. Main Subject Taught", label="Main Subject Taught",
        section="Demographics", type="categorical",
        question_text="What is the main subject you teach?",
    ),
    # ── Section 2 — AI Usage Behavior ─────────────────────────────────────────
    dict(
        col="6. Self-Assessed Knowledge: How knowledgeable do you consider yourself about Artificial Intelligence?",
        label="Self-Assessed AI Knowledge", section="AI Usage Behavior",
        type="ordered_categorical", order=KNOWLEDGE_ORDER,
        short_labels=KNOWLEDGE_SHORT, colors=ordinal_colors(5),
        question_text="How knowledgeable do you consider yourself about Artificial Intelligence?",
    ),
    dict(
        col="2.1 Frequency of Use: How often do you currently use Generative AI tools?",
        label="2.1 Frequency of Use", section="AI Usage Behavior",
        type="ordered_categorical", order=FREQ_ORDER, colors=ordinal_colors(5),
        question_text="How often do you currently use Generative AI tools?",
    ),
    dict(
        col=USE_CASE_COL,
        indicator_cols=_USE_CASE_INDICATORS,
        label="2.2 Primary Use Cases", section="AI Usage Behavior",
        type="multiselect",
        question_text="What are the main tasks you use AI for? (select all that apply)",
    ),
    dict(
        col="2.2.1 Output Reworking: When you generate text or content using AI, how do you typically handle the output?",
        label="2.2.1 Output Reworking", section="AI Usage Behavior",
        type="categorical",
        question_text="When you generate text or content using AI, how do you typically handle the output?",
    ),
    dict(
        col="2.2.2 Quality Perception: How do you usually evaluate the quality of the AI-generated output compared to what you could have done on your own?",
        label="2.2.2 Quality Perception", section="AI Usage Behavior",
        type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "The AI's output was poor/incorrect, and I had to redo most of it.",
            "My original work would have been better, but the AI was faster.",
            "The AI and I would have produced a similar result.",
            "The AI produced a much better result than I could have.",
        ],
        question_text="How do you usually evaluate the quality of the AI-generated output compared to what you could have done on your own?",
    ),
    dict(
        col="2.2.3 Efficiency and Value: Overall, how does using AI affect the time and effort required for your tasks?",
        label="2.2.3 Efficiency and Value", section="AI Usage Behavior",
        type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "It is a waste of time (I spend more time prompting and correcting than doing it myself).",
            "It has no significant impact on my time or effort.",
            "It enriches my work (gives me ideas I wouldn't have had), but takes about the same amount of time.",
            "It is a huge time saver.",
        ],
        question_text="Overall, how does using AI affect the time and effort required for your tasks?",
    ),
    dict(
        col="2.2.4 Interaction Effort (Prompting): How much time and effort do you usually spend interacting with the AI to get a satisfactory result?",
        label="2.2.4 Interaction Effort", section="AI Usage Behavior",
        type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "Very little time (I usually accept the first answer it provides).",
            "A moderate amount of time (I ask for a few adjustments or refinements).",
            "A significant amount of time (I engage in long conversations, going back and forth until the output is perfect).",
            "It takes so much time that sometimes I just give up and do the work myself.",
        ],
        question_text="How much time and effort do you usually spend interacting with the AI to get a satisfactory result?",
    ),
    dict(
        col="2.3 Confidence in Detection: How confident are you in your ability to distinguish a text or image created by a human from one generated by AI?",
        label="2.3 Confidence in Detecting AI Content", section="AI Usage Behavior",
        type="ordered_categorical", order=CONFIDENCE_ORDER, colors=ordinal_colors(4),
        question_text="How confident are you in your ability to distinguish a text or image created by a human from one generated by AI?",
    ),
    dict(
        col="2.3.1 Fact-Checking Habits: When an AI tool provides you with new historical, scientific, or factual information, what do you usually do?",
        label="2.3.1 Fact-Checking Habits", section="AI Usage Behavior",
        type="categorical",
        question_text="When an AI tool provides you with new factual information, what do you usually do?",
    ),
    dict(
        col="2.3.2 Awareness of Hallucinations: Have you ever noticed an AI tool completely inventing a source, fact, or name that sounded extremely convincing but was actually fake?",
        label="2.3.2 Awareness of Hallucinations", section="AI Usage Behavior",
        type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "I didn't know AI could do that.",
            "No, never.",
            "Yes, occasionally.",
            "Yes, frequently.",
        ],
        question_text="Have you ever noticed an AI tool completely inventing a source, fact, or name that sounded convincing but was actually fake?",
    ),
    dict(
        col="2.3.3 Awareness of Bias: Have you ever noticed that AI-generated images or texts tend to reflect cultural or gender stereotypes?",
        label="2.3.3 Awareness of Bias", section="AI Usage Behavior",
        type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "I have never paid attention to this aspect.",
            "No, never.",
            "Yes, occasionally.",
            "Yes, frequently.",
        ],
        question_text="Have you ever noticed that AI-generated images or texts tend to reflect cultural or gender stereotypes?",
    ),
    dict(
        col=FEELING_COL,
        indicator_cols=_FEELING_INDICATORS,
        label="2.4 General Feeling about AI in Education", section="AI Usage Behavior",
        type="multiselect",
        question_text="When you think about the integration of AI in school and education, which of the following feelings prevail? (select all that apply)",
    ),
    # ── DT1 — Technology Adoption ─────────────────────────────────────────────
    dict(
        col="DT1.1 Technology Adoption Profile: When a new digital technology is released",
        label="DT1.1 Technology Adoption Profile", section="DT1: Technology Adoption",
        type="categorical",
        question_text="When a new digital technology is released, which describes you best?",
    ),
    dict(
        col="DT1.2 Specific Frequency of Use: How often do you use Generative AI tools specifically for school-related or work-related tasks?",
        label="DT1.2 Frequency for School/Work Tasks", section="DT1: Technology Adoption",
        type="ordered_categorical", order=FREQ_ORDER, colors=ordinal_colors(5),
        question_text="How often do you use Generative AI tools specifically for school-related or work-related tasks?",
    ),
    dict(
        col="DT1.3 AI Perception: You see AI primarily as",
        label="DT1.3 How Teachers Perceive AI", section="DT1: Technology Adoption",
        type="categorical",
        question_text="You see AI primarily as…",
    ),
    dict(
        col="DT1.4 I feel I possess the right pedagogical strategies to integrate AI into my lessons in a way that truly enhances learning, rather than just acting as a shortcut",
        label="DT1.4 Pedagogical Readiness for AI", section="DT1: Technology Adoption",
        type="likert4",
        question_text="I feel I possess the right pedagogical strategies to integrate AI into my lessons in a way that truly enhances learning, rather than just acting as a shortcut.",
    ),
    dict(
        col="DT1.5 Guidelines on AI: My school provides clear guidelines and support on how to use AI in the classroom.",
        label="DT1.5 School Guidelines on AI", section="DT1: Technology Adoption",
        type="likert4",
        question_text="My school provides clear guidelines and support on how to use AI in the classroom.",
    ),
    # ── DT2 — Beliefs about AI ────────────────────────────────────────────────
    dict(
        col='DT2.1 AI tools truly "understand" the meaning of the text they generate.',
        label='DT2.1 AI truly "understands" text',
        section="DT2: Beliefs about AI", type="likert4",
        question_text='AI tools truly "understand" the meaning of the text they generate.',
    ),
    dict(
        col="DT2.2 The information provided by AI is generally neutral, objective, and unbiased.",
        label="DT2.2 AI is neutral and unbiased",
        section="DT2: Beliefs about AI", type="likert4",
        question_text="The information provided by AI is generally neutral, objective, and unbiased.",
    ),
    dict(
        col="DT2.3 I think AI is inherently smarter and more capable than human beings.",
        label="DT2.3 AI is smarter than humans",
        section="DT2: Beliefs about AI", type="likert4",
        question_text="I think AI is inherently smarter and more capable than human beings.",
    ),
    dict(
        col="DT2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.",
        label="DT2.4 Trust AI accuracy without checking",
        section="DT2: Beliefs about AI", type="likert4",
        question_text="I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.",
    ),
    dict(
        col="DT2.5 I clearly understand how a GenAI assistant generates its responses.",
        label="DT2.5 Understand how GenAI generates responses",
        section="DT2: Beliefs about AI", type="likert4",
        question_text="I clearly understand how a GenAI assistant generates its responses.",
    ),
    dict(
        col="DT2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced",
        label="DT2.6 Prompting has no impact on output quality",
        section="DT2: Beliefs about AI", type="likert4",
        question_text="The way I request something to AI doesn't have any impact on the quality of the result produced.",
    ),
    # ── DT3 — Concerns ────────────────────────────────────────────────────────
    dict(
        col="DT3.1 The widespread use of AI makes it impossible to assess students' real learning and capabilities accurately.",
        label="DT3.1 AI undermines assessment accuracy",
        section="DT3: Concerns", type="concern5",
        question_text="The widespread use of AI makes it impossible to assess students' real learning and capabilities accurately.",
    ),
    dict(
        col="DT3.2 Relying on AI will reduce students' critical thinking, creativity, and problem-solving skills.",
        label="DT3.2 AI reduces students' critical thinking",
        section="DT3: Concerns", type="concern5",
        question_text="Relying on AI will reduce students' critical thinking, creativity, and problem-solving skills.",
    ),
    dict(
        col="DT3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).",
        label="DT3.3 Difficulty detecting AI-generated content",
        section="DT3: Concerns", type="concern5",
        question_text="The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).",
    ),
    dict(
        col="DT3.4 How AI platforms collect, use, and store the personal data and inputs of my students.",
        label="DT3.4 Student data privacy",
        section="DT3: Concerns", type="concern5",
        question_text="How AI platforms collect, use, and store the personal data and inputs of my students.",
    ),
    dict(
        col="DT3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).",
        label="DT3.5 AI reinforces social biases",
        section="DT3: Concerns", type="concern5",
        question_text="AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).",
    ),
    dict(
        col="DT3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.",
        label="DT3.6 Unequal access to AI tools",
        section="DT3: Concerns", type="concern5",
        question_text="Unequal access to premium (paid) AI tools will create unfair advantages among students.",
    ),
    dict(
        col="DT3.7 The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.",
        label="DT3.7 AI learning pressure causes stress",
        section="DT3: Concerns", type="likert4",
        question_text="The constant learning pressure to keep up with new digital and AI tools causes me stress and anxiety.",
    ),
    dict(
        col="DT3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.",
        label="DT3.8 AI reliance reduces self-efficacy",
        section="DT3: Concerns", type="likert4",
        question_text="I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.",
    ),
    # ── DT4 — Expectations ────────────────────────────────────────────────────
    dict(
        col="DT4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.",
        label="DT4.1 AI speeds up work tasks",
        section="DT4: Expectations", type="likert4",
        question_text="I expect AI to significantly speed up my daily study/work tasks, making me more efficient.",
    ),
    dict(
        col="DT4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.",
        label="DT4.2 AI can personalise learning",
        section="DT4: Expectations", type="likert4",
        question_text="I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.",
    ),
    dict(
        col="DT4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.",
        label="DT4.3 AI improves accessibility",
        section="DT4: Expectations", type="likert4",
        question_text="I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.",
    ),
    dict(
        col="DT4.4. I expect AI to take over administrative and grading tasks, freeing up my time to focus more on human interaction and mentoring.",
        label="DT4.4 AI takes over admin/grading tasks",
        section="DT4: Expectations", type="likert4",
        question_text="I expect AI to take over administrative and grading tasks, freeing up my time to focus more on human interaction and mentoring.",
    ),
]
