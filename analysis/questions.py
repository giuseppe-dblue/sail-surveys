from analysis.constants import (
    CONCERN5_ORDER,
    CONFIDENCE_COLORS,
    CONFIDENCE_ORDER,
    COUNTRY_COLOR_MAP,
    FREQ_ORDER,
    GENDER_COLOR_MAP,
    GRADE_COLORS,
    GRADE_ORDER,
    KNOWLEDGE_ORDER,
    KNOWLEDGE_SHORT,
    LIKERT4_ORDER,
    ordinal_colors,
)

# Each entry is a dict with:
#   col           — exact DataFrame column name
#   label         — short topic shown in the expander header
#   section       — section grouping
#   type          — one of: categorical | ordered_categorical | likert4 | concern5 | multiselect
#   question_text — full survey wording shown inside the expander
#   order         — (ordered_categorical) list of values in display order
#   short_labels  — (ordered_categorical) optional display-name map for long values
#   colors        — optional list of hex colors matching the order/counts

QUESTIONS: list[dict] = [
    # ── Demographics ───────────────────────────────────────────────────────────
    dict(
        col="1. Country", label="Country", section="Demographics", type="categorical",
        color_map=COUNTRY_COLOR_MAP,
        question_text="Which country are you from?",
    ),
    dict(
        col="2. Gender", label="Gender", section="Demographics", type="categorical",
        color_map=GENDER_COLOR_MAP,
        question_text="What is your gender?",
    ),
    dict(
        col="3. Grade/Year of Study", label="Grade / Year of Study", section="Demographics",
        type="ordered_categorical", order=GRADE_ORDER, colors=GRADE_COLORS,
        question_text="What is your current grade or year of study?",
    ),
    dict(
        col="4. Self-Assessed Knowledge", label="Self-Assessed AI Knowledge", section="Demographics",
        type="ordered_categorical", order=KNOWLEDGE_ORDER, short_labels=KNOWLEDGE_SHORT,
        colors=ordinal_colors(5),
        question_text="How would you rate your own knowledge and experience with AI tools?",
    ),
    # ── Section 2 — AI Usage Behavior ─────────────────────────────────────────
    dict(
        col="2.1 Frequency of Use", label="2.1 Frequency of Use", section="AI Usage Behavior",
        type="ordered_categorical", order=FREQ_ORDER, colors=ordinal_colors(5),
        question_text="How often do you use AI tools (e.g. ChatGPT, Copilot, Gemini…)?",
    ),
    dict(
        col="2.2 Primary Use Cases", label="2.2 Primary Use Cases", section="AI Usage Behavior",
        type="multiselect",
        question_text="For what purposes do you mainly use AI tools? (select all that apply)",
    ),
    dict(
        col="2.2.1 Output Reworking (Human-AI Teaming)", label="2.2.1 How is AI output used?",
        section="AI Usage Behavior", type="categorical",
        question_text="When you use an AI tool for a task, how do you typically handle the output it produces?",
    ),
    dict(
        col="2.2.2 Quality Perception", label="2.2.2 Quality Perception",
        section="AI Usage Behavior", type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "The AI's output was poor/incorrect, and I had to redo most of it.",
            "My original work would have been better, but the AI was faster.",
            "The AI and I would have produced a similar result.",
            "The AI produced a much better result than I could have.",
        ],
        question_text="Compared to what you could have produced on your own, how would you evaluate the quality of AI-generated output?",
    ),
    dict(
        col="2.2.3 Efficiency and Value", label="2.2.3 Efficiency and Value",
        section="AI Usage Behavior", type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "It is a waste of time (I spend more time prompting and correcting than doing it myself).",
            "It has no significant impact on my time or effort.",
            "It enriches my work (gives me ideas I wouldn't have had), but takes about the same amount of time.",
            "It is a huge time saver.",
        ],
        question_text="How does using AI tools affect your overall efficiency and the value of your work?",
    ),
    dict(
        col="2.2.4 Interaction Effort (Prompting)", label="2.2.4 Interaction Effort",
        section="AI Usage Behavior", type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "Very little time (I usually accept the first answer it provides).",
            "A moderate amount of time (I ask for a few adjustments or refinements).",
            "A significant amount of time (I engage in long conversations, going back and forth until the output is perfect).",
            "It takes so much time that sometimes I just give up and do the work myself.",
        ],
        question_text="How much time do you typically spend interacting with AI to get a useful result?",
    ),
    dict(
        col="2.3 Confidence in Detection (Media Literacy)",
        label="2.3 Confidence in Detecting AI Content", section="AI Usage Behavior",
        type="ordered_categorical", order=CONFIDENCE_ORDER, colors=ordinal_colors(4),
        question_text="How confident are you in your ability to detect AI-generated content (text, images, audio)?",
    ),
    dict(
        col="2.3.1 Fact-Checking Habits", label="2.3.1 Fact-Checking Habits",
        section="AI Usage Behavior", type="categorical",
        question_text="When an AI tool provides information or facts, what do you typically do?",
    ),
    dict(
        col="2.3.2 Awareness of Hallucinations", label="2.3.2 Awareness of Hallucinations",
        section="AI Usage Behavior", type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "I didn't know AI could do that.",
            "No, never.",
            "Yes, occasionally.",
            "Yes, frequently.",
        ],
        question_text="Have you ever noticed an AI tool generating false, made-up, or incorrect information (so-called 'hallucinations')?",
    ),
    dict(
        col="2.3.3 Awareness of Bias", label="2.3.3 Awareness of Bias",
        section="AI Usage Behavior", type="ordered_categorical", colors=ordinal_colors(4),
        order=[
            "I have never paid attention to this aspect.",
            "No, never.",
            "Yes, occasionally.",
            "Yes, frequently.",
        ],
        question_text="Have you ever noticed an AI tool showing biased, one-sided, or stereotyped perspectives?",
    ),
    dict(
        col="2.4 General Feeling", label="2.4 General Feeling about AI",
        section="AI Usage Behavior", type="multiselect",
        question_text="When you think about AI tools in general, what feelings do they evoke in you? (select all that apply)",
    ),
    # ── DS1 — General AI Adoption ──────────────────────────────────────────────
    dict(
        col="DS1.1 Technology Adoption Profile", label="DS1.1 Technology Adoption Profile",
        section="DS1: General AI Adoption", type="categorical",
        question_text="Which statement best describes your approach to adopting new technology?",
    ),
    dict(
        col="DS1.2 Specific Frequency of Use", label="DS1.2 Specific Frequency of Use",
        section="DS1: General AI Adoption", type="ordered_categorical", order=FREQ_ORDER,
        colors=ordinal_colors(5),
        question_text="Thinking specifically about AI tools for studying or working, how often do you use them?",
    ),
    dict(
        col="DS1.3 AI Perception", label="DS1.3 How Students Perceive AI",
        section="DS1: General AI Adoption", type="categorical",
        question_text="Which of the following best describes how you think of AI as a tool?",
    ),
    dict(
        col="DS1.5 Guidelines on AI", label="DS1.5 Support for AI Guidelines",
        section="DS1: General AI Adoption", type="likert4",
        question_text="I believe schools and universities should establish clear guidelines on the acceptable use of AI tools for academic work.",
    ),
    # ── DS2 — Understanding & Misconceptions ──────────────────────────────────
    dict(
        col='DS2.1 AI tools truly "understand" the meaning of the text they generate.',
        label='DS2.1 AI truly "understands" text',
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text='AI tools truly "understand" the meaning of the text they generate.',
    ),
    dict(
        col="DS2.2 The information provided by AI is generally neutral, objective, and unbiased.",
        label="DS2.2 AI is neutral and unbiased",
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text="The information provided by AI is generally neutral, objective, and unbiased.",
    ),
    dict(
        col="DS2.3 I think AI is inherently smarter and more capable than human beings.",
        label="DS2.3 AI is smarter than humans",
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text="I think AI is inherently smarter and more capable than human beings.",
    ),
    dict(
        col="DS2.4 I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.",
        label="DS2.4 Trust AI factual accuracy without checking",
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text="I usually trust the factual accuracy of AI-generated answers without feeling the need to double-check other sources.",
    ),
    dict(
        col="DS2.5 I clearly understand how a GenAI assistant generates its responses.",
        label="DS2.5 Understand how GenAI generates responses",
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text="I clearly understand how a GenAI assistant generates its responses.",
    ),
    dict(
        col="DS2.6 The way I request something to AI doesn’t have any impact on the quality of the result produced",
        label="DS2.6 Prompting has no impact on output quality",
        section="DS2: Understanding & Misconceptions", type="likert4",
        question_text="The way I request something to AI doesn’t have any impact on the quality of the result produced.",
    ),
    # ── DS3 — Concerns & Risks ─────────────────────────────────────────────────
    dict(
        col="DS3.1 Teachers will unfairly accuse me of using AI for my assignments even when I do not.",
        label="DS3.1 Fear of unfair AI accusations",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="Teachers will unfairly accuse me of using AI for my assignments even when I do not.",
    ),
    dict(
        col="DS3.2 Using AI to do my homework will make me lose the ability to think critically and learn independently.",
        label="DS3.2 AI harms critical thinking",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="Using AI to do my homework will make me lose the ability to think critically and learn independently.",
    ),
    dict(
        col="DS3.3 The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).",
        label="DS3.3 Difficulty distinguishing AI from human content",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="The difficulty of distinguishing between human-created and AI-generated content (e.g., fake news, deepfakes).",
    ),
    dict(
        col="DS3.5 AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).",
        label="DS3.5 AI reinforces social biases",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="AI tools might reinforce existing social biases and discrimination (e.g., gender, race, cultural stereotypes).",
    ),
    dict(
        col="DS3.6 Unequal access to premium (paid) AI tools will create unfair advantages among students.",
        label="DS3.6 Unequal access to AI tools",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="Unequal access to premium (paid) AI tools will create unfair advantages among students.",
    ),
    dict(
        col="DS3.8 I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.",
        label="DS3.8 AI reliance reduces self-efficacy",
        section="DS3: Concerns & Risks", type="concern5",
        question_text="I worry that relying on AI to produce high-quality work makes me feel less capable or smart when I have to complete similar tasks on my own.",
    ),
    # ── DS4 — Expectations & Benefits ─────────────────────────────────────────
    dict(
        col="DS4.1 I expect AI to significantly speed up my daily study/work tasks, making me more efficient.",
        label="DS4.1 AI speeds up study tasks",
        section="DS4: Expectations & Benefits", type="likert4",
        question_text="I expect AI to significantly speed up my daily study/work tasks, making me more efficient.",
    ),
    dict(
        col="DS4.2 I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.",
        label="DS4.2 AI can personalise learning",
        section="DS4: Expectations & Benefits", type="likert4",
        question_text="I believe AI can perfectly tailor learning materials to match the individual learning pace and style of each student.",
    ),
    dict(
        col="DS4.3 I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.",
        label="DS4.3 AI improves accessibility",
        section="DS4: Expectations & Benefits", type="likert4",
        question_text="I expect AI to make learning more accessible and inclusive for students with diverse cognitive needs or language barriers.",
    ),
    dict(
        col="DS4.4 I see AI as a non-judgmental tutor that is available 24/7 to answer my questions without making me feel inadequate.",
        label="DS4.4 AI as 24/7 non-judgmental tutor",
        section="DS4: Expectations & Benefits", type="likert4",
        question_text="I see AI as a non-judgmental tutor that is available 24/7 to answer my questions without making me feel inadequate.",
    ),
    dict(
        col="DS4.5 I expect AI to provide better guidance for my future university or career choices than traditional school counselling.",
        label="DS4.5 AI for career/university guidance",
        section="DS4: Expectations & Benefits", type="likert4",
        question_text="I expect AI to provide better guidance for my future university or career choices than traditional school counselling.",
    ),
]
