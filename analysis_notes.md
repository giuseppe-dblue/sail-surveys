# SAIL Survey — Analysis Notes

**Dataset:** Students Responses — merged-en.csv  
**Respondents:** 689 students from Italy (101), Spain (113), Slovenia (152), Turkey (323)  
**Questions analysed:** 36 survey questions across demographics, AI usage behaviour, and five thematic scales (DS1–DS4)

---

## 1. Data Peculiarities

### 1.1 Country field required remapping
Eight students reported their **country of origin** rather than the country of their school. These were remapped to the school country before any analysis:

| Reported | Remapped to |
|---|---|
| Afghanistan, Germany | Turkey |
| Ghana, Spain (Catalonia) | Spain |
| Portugal | Slovenia |

### 1.2 Unbalanced grade distribution
| Grade | N |
|---|---|
| 1st year | 248 |
| 2nd year | 200 |
| 3rd year | 135 |
| 4th year | 92 |
| 5th year | 14 |

The 5th-year group (N=14) is too small for any sub-group inference. Additionally, grade year and country are **correlated** in this dataset — Turkey contributes disproportionately to the lower years. This makes it impossible to separate a "grade effect" from a "country effect" without controlling for country, which further reduces subgroup sizes. For this reason, **no grade-level comparison analysis was carried out**.

### 1.3 DS3.8 survey labeling error
The question *"I worry that relying on AI to produce high-quality work makes me feel less capable…"* (DS3.8) contains a data quality issue: 324 of 689 respondents saw the DS3.6 question text instead of DS3.8, and their responses are flagged as invalid. Only the 365 remaining valid responses (recorded on a Likert agree/disagree scale) are used in the correlation analysis. Results involving DS3.8 should be interpreted with caution.

### 1.4 Multi-select questions excluded from correlation
Questions 2.2 (Primary Use Cases) and 2.4 (General Feeling) allow multiple selections per respondent. Because they cannot be encoded as a single ordinal variable, they are included in the descriptive analysis only and excluded from the correlation analysis.

### 1.5 All questions are ordinal, not continuous
Likert scales, frequency scales, concern scales, and awareness scales are all **ordinal**: the categories have a natural order, but the intervals between them are not guaranteed to be equal (the gap between "Never" and "Rarely" is not the same as the gap between "A few times a week" and "Daily"). This directly shapes the choice of statistical technique.

---

## 2. Scope Decision: Grade-Year Comparison Not Carried Out

One candidate analysis was comparing student responses **across grade years** — identifying, for each question, whether 1st-year students answered differently from 2nd-year students, and so on. This section documents why that analysis was considered and ultimately excluded.

### 2.1 The intended technique

The approach would have been:

1. **Chi-square test of independence** for each question: build a contingency table (grade year × answer options) and test whether the distribution of answers is statistically independent of grade year. One p-value per question.
2. **Cramér's V** as an effect-size filter: with N = 689, even trivially small differences reach statistical significance. Cramér's V (ranging from 0 to 1) normalises the chi-square statistic by sample size and table dimensions, making it possible to focus only on associations of practical interest (V ≥ 0.10 as a minimum threshold).
3. **Standardised residuals** to locate which year drives the difference: cells with a residual above +2 or below −2 indicate where a specific grade year answered more or less frequently than chance would predict, directly answering "which year is different and on which option."
4. **Benjamini-Hochberg correction** across all 36 questions to control for multiple testing.

This is a legitimate and relatively simple approach. Chi-square handles unequal group sizes natively, and Cramér's V addresses the large-N inflation problem. On technical grounds alone the analysis would have been feasible.

### 2.2 Why it was not implemented

Three compounding problems make the results uninterpretable rather than merely imprecise.

**Problem 1 — The country–grade confound (primary reason)**
Grade year and country are correlated in this dataset. Turkey contributes disproportionately to the lower years; the upper years are dominated by other countries. Any finding of the form "1st-year students answered differently" could equally be described as "Turkish students answered differently." There is no statistical way to separate the two effects without running within-country analyses, which immediately reduces each cell to a size too small to support inference.

**Problem 2 — Grade year means different things across countries**
A "1st-year student" in a three-year bachelor's programme (common in Italy and Spain under the Bologna system) is not the same as a "1st-year student" in a four-year programme (common in Turkey). The 4th and 5th years likely include master's students in some countries and final-year undergraduates in others. The variable "grade year" therefore lacks construct validity as a cross-country comparison unit: it does not measure the same thing in each country.

**Problem 3 — 5th year is too small (N = 14)**
With 14 respondents in 5th year and typically 4–6 answer options per question, many expected cell counts fall below 5 — the standard minimum for chi-square to be reliable. Merging 4th and 5th year would mask the very distinction the analysis is trying to detect.

### 2.3 What was done instead

The descriptive analysis sidebar allows filtering by grade year, so any partner or researcher who wants to inspect a specific year's distribution on a specific question can do so directly in the app. This provides the factual picture without making cross-year inferential claims the data cannot support.

---

## 3. Analytical Techniques (What Was Implemented)

### 2.1 Descriptive analysis
Each question is visualised as a horizontal bar chart showing the count and percentage for each response option. Questions with a natural order (Likert, frequency, concern, awareness scales) are displayed with that order preserved and a sequential colour palette so the reader can immediately see where responses concentrate. Multi-select questions are exploded: each option is counted independently across all respondents.

Charts are filterable by country, gender, and grade year via the sidebar. An auto-generated insight box below each chart summarises the dominant response and, for Likert and concern scales, the balance between positive and negative poles.

### 2.2 Correlation analysis

#### Why Spearman, not Pearson
Pearson correlation assumes the data is continuous and normally distributed and that the intervals between values are equal. None of these hold for Likert or ordinal scale data. **Spearman rank correlation** makes no distributional assumptions and works on the rank order of values rather than their absolute magnitude. It measures whether two variables move in the same direction (monotonic relationship), which is exactly the question of interest for ordinal survey data.

#### Why Benjamini-Hochberg (BH) correction
With 30 questions, there are 435 unique pairs to test. At a significance threshold of α = 0.05, roughly 22 pairs would appear significant purely by chance even if there were no real associations. The **Benjamini-Hochberg procedure** controls the expected proportion of false discoveries (false discovery rate, FDR) rather than the probability of even one false positive. It is less conservative than Bonferroni correction, which is appropriate for exploratory research where the goal is to identify patterns rather than confirm specific hypotheses.

#### Why an effect size filter (|r| ≥ 0.25)
With N = 689, even associations with negligible practical importance can reach statistical significance. The filter |r| ≥ 0.25 retains only pairs where the association is both statistically significant (after BH correction) and of practical interest. In survey research, r = 0.25 corresponds roughly to a small-to-medium effect and explains about 6% of shared variance — the threshold below which a finding would be hard to interpret meaningfully for an audience without statistical training.

Strength labels used in the app:

| Label | Range |
|---|---|
| Weak | 0.25 ≤ \|r\| < 0.35 |
| Moderate | 0.35 ≤ \|r\| < 0.50 |
| Strong | \|r\| ≥ 0.50 |

#### Clustering
Questions in the heatmap are reordered using **hierarchical clustering** (average linkage, distance = 1 − r). This groups questions that correlate with each other close together, making patterns visible as coloured blocks rather than a scattered mosaic.

---

## 4. How to Read the Correlation Tab

The tab has four components, from least to most technical.

### 3.1 Overview map
A grid where each cell represents a pair of questions. Colour encodes the relationship:

- **Blue** — the two questions tend to go together: students who score high on one tend to score high on the other
- **Red** — the two questions go in opposite directions: students who score high on one tend to score low on the other
- **Grey** — no meaningful association (either not statistically significant or effect too small to matter)

Questions are grouped by similarity, so clusters of blue cells reveal groups of questions that measure overlapping attitudes. You do not need to read individual cells to get value from this chart — look for **blue blocks** (consistent clusters) and **isolated red cells** (unexpected tensions between attitudes).

### 3.2 Notable associations table
Lists only the pairs that pass both the significance test and the effect-size filter. For each pair:

- **Question A / Question B** — the two questions involved
- **Link** — whether they go together (↑) or in opposite directions (↓)
- **Strength** — Weak / Moderate / Strong
- **What it means** — a plain-language sentence describing the relationship

This table is the primary partner-facing output. It can be copied directly into a report or presentation.

### 3.3 Explore a relationship
Select any pair from the notable associations list. A heatmap shows the **joint distribution**: rows are the answer options for Question A, columns are the answer options for Question B, and each cell shows the percentage of students who gave that combination of answers. Darker cells = more students.

If the two questions are positively associated, the darkest cells will run diagonally from top-left to bottom-right (low-A students give low-B answers, high-A students give high-B answers). A negative association produces the opposite diagonal.

### 3.4 Full correlation matrix (expert view)
The complete Spearman ρ matrix for all 30 questions, clustered in the same order as the overview map. Cells show the numerical coefficient only where the association is BH-significant; non-significant cells are left blank. This view is intended for internal use and review, not for partner communication.

---

## 5. Main Findings from the Correlation Analysis

Thirty-three pairs meet the threshold. They organise into four interpretive clusters.

### Cluster A — AI Expectations (DS4): the optimist profile
Questions DS4.1 through DS4.5 correlate strongly with each other (r = 0.36–0.51). Students who expect AI to speed up their work also tend to expect it to personalise learning, improve accessibility, serve as a tutor, and guide career choices. This suggests a latent **"AI optimism"** disposition: students are either broadly optimistic about AI's potential benefits or broadly reserved, rather than selectively optimistic about specific applications.

The single strongest association in the dataset is between DS4.1 (*AI speeds up tasks*) and DS4.3 (*AI improves accessibility*), r = +0.51.

### Cluster B — AI Concerns (DS3): the worry profile
Concerns about AI form a coherent cluster. Students worried about AI harming critical thinking (DS3.2) also tend to be worried about fake news and deepfakes (DS3.3), social bias reinforcement (DS3.5), and unequal access (DS3.6). These are **macro-societal concerns** that come as a package: a student alert to one societal risk tends to be alert to all of them.

Concern about unfair teacher accusations (DS3.1) correlates only weakly with the rest, suggesting it is more personal and situational than the broader societal worries.

### Cluster C — AI Misconceptions (DS2): the credulous profile
DS2.1 (*AI understands text*), DS2.2 (*AI is neutral*), DS2.3 (*AI is smarter than humans*), and DS2.4 (*trust AI without checking*) correlate moderately with each other (r = 0.29–0.40). Students who hold one misconception about how AI works tend to hold others. This points to a **"credulous AI believer"** profile — a cluster of related overestimations of AI's capabilities and objectivity.

### Cross-cluster findings
The most analytically interesting associations cross section boundaries:

- **DS2 misconceptions → DS4 over-expectations:** Students who believe AI truly understands text (DS2.1) are more likely to expect it to personalise learning (DS4.2, r = +0.26) and serve as a tutor (DS4.4, r = +0.26). Misconceptions about how AI works may fuel unrealistic expectations of its benefits.
- **Frequency of use → efficiency expectations:** Students who use AI more frequently also tend to report expecting AI to speed up their work (r ≈ +0.26–0.27). Heavy users may have formed this expectation through experience, or may use AI more precisely because they already hold this expectation.
- **Self-knowledge → frequency of use:** Higher self-assessed AI knowledge correlates with more frequent AI use (r = +0.34), as expected.
- **Fact-checking ↔ trust:** The only meaningful negative cross-cluster association: students with more rigorous fact-checking habits tend to trust AI factual accuracy less (r = −0.31). This is an internal consistency check — it confirms the data is behaving sensibly.
- **Reworking output → fact-checking:** Students who invest more human effort in reworking AI output also tend to fact-check more rigorously (r = +0.26). Both behaviours reflect a more critical, effortful relationship with AI.

### What the correlations do NOT show
- No notable association was found between concern levels (DS3) and expectations (DS4). Students can be simultaneously worried about AI's risks and optimistic about its benefits — these are not opposite poles of a single attitude.
- Frequency of use does not strongly correlate with concern levels. Using AI more often does not appear to make students either more or less worried about it.

---

## 6. Limitations

| Limitation | Impact |
|---|---|
| Ordinal encoding assumes equal intervals | Spearman mitigates this but does not eliminate it entirely |
| Acquiescence bias | Some students agree with everything; this inflates within-section correlations |
| Common method variance | All items from the same self-report survey; correlations may be slightly inflated |
| Cross-sectional data | Correlations cannot establish direction of causality |
| DS3.8 data quality issue | Results involving DS3.8 based on only 365 of 689 respondents |
| Country composition differs by grade | Grade-level sub-group analysis not carried out for this reason |
