# SAIL Survey — Teacher Analysis Notes

**Dataset:** final-translated-responses 8-04-2026.csv  
**Respondents:** 73 teachers from Spain (27), Slovenia (22), Italy (15), Turkey (9)  
**Questions analysed:** 40 survey questions across demographics, AI usage behaviour, and four thematic scales (DT1–DT4)

---

## 1. Data Peculiarities

### 1.1 Multilingual source files required explicit value maps

The raw CSV was produced by merging country-level files translated through an automated pipeline. The pipeline was not perfect: several responses were left in their original language and had to be remapped manually in `analysis/data_teachers.py`.

| Column | Issue | Fix |
|---|---|---|
| Q6 Self-Assessed Knowledge | Three Turkish-language responses not translated | Explicit Turkish → English map |
| Q12 Interaction Effort | One Italian response with curly apostrophe (U+2019) | Added U+2019 variant to value map |
| Q14 Quality Perception | Four Italian responses not translated | Explicit Italian → English map |
| Q18 Fact-Checking Habits | One Italian response not translated | Explicit Italian → English map |
| Q22 Hallucination Awareness | One Italian response with curly apostrophe | Added U+2019 variant |
| DT3.7, DT3.8 | Mixed case (e.g. "strongly agree" vs "Strongly Agree") | Case-normalised to title case |

### 1.2 DT2.6 column name Mojibake

The column header for DT2.6 ("The way I request something to AI **doesn't** have any impact…") was corrupted during the file encoding chain. The UTF-8 sequence for the curly apostrophe in "doesn't" was misread as Windows-1252, producing the three-character sequence `‚Äô` (U+201A U+00C4 U+00F4). The column was renamed in `load_teachers()` before any analysis.

### 1.3 Multi-select parsing required substring matching

Questions 2.2 (Primary Use Cases) and 2.4 (General Feeling) allow multiple selections per respondent, stored as comma-separated strings. A naive comma-split fails because several options contain commas inside parentheses — e.g. the Italian drafting option reads *"Scrivere/abbozzare testi (email, saggi, relazioni)"*. The parser was rewritten to use **substring matching** against a token map of known option strings in all four languages.

Each multi-select question was expanded into **binary indicator columns** (0/1) — one per option — rather than being encoded as a single ordinal variable.

### 1.4 Catalan respondents remapped to Spain

Twenty-seven teachers reported their country as "Spain", but a subset reported "CATALUNYA". These were remapped to `Spain` before any analysis.

### 1.5 Turkish subsample is small (N = 9)

Turkey contributes only 9 of 73 teachers. This limits the reliability of within-Turkey descriptive statistics and reduces the statistical power of country comparisons involving Turkey. Kruskal-Wallis results involving Turkey should be read with this caveat in mind.

### 1.6 Sample is heavily female and mid-career

| Dimension | Dominant group | N |
|---|---|---|
| Gender | Female | 60 of 73 (82%) |
| Age | 41–50 | 34 of 73 (47%) |
| Experience | 16–25 years | 28 of 73 (38%) |

The gender imbalance means that gender-filtered sub-group results for males (N = 13) have very limited statistical power and should not support inferential claims.

### 1.7 Subject field not used for sub-group analysis

The "Main Subject Taught" field contains a mix of English and untranslated values (Italian, Slovenian) and several fine-grained categories that could not be reliably collapsed into a small number of groups. Sub-group analysis by subject was not carried out.

---

## 2. Scope Decision: Effect Size Threshold Raised for Small N

With only 73 teachers, Spearman correlations are much more sensitive to sampling noise than with the student dataset (N = 689). A threshold of |ρ| ≥ 0.25 (used for students) would return associations that explain as little as 6% of shared variance and would be hard to distinguish from noise at this sample size.

The teacher correlation analysis uses |ρ| ≥ **0.30** as the minimum effect-size filter. This still corresponds to a modest practical effect but provides a more conservative lower bound given the small N. Strength labels:

| Label | Range |
|---|---|
| Weak | 0.30 ≤ \|ρ\| < 0.35 |
| Moderate | 0.35 ≤ \|ρ\| < 0.50 |
| Strong | \|ρ\| ≥ 0.50 |

---

## 3. Analytical Techniques

### 3.1 Descriptive analysis

Each question is visualised as a horizontal bar chart showing count and percentage for each response option. Questions with a natural order (Likert, frequency, concern, knowledge scales) preserve that order and use a sequential colour palette. Multi-select questions are visualised as bar charts of binary indicator columns, one bar per option, each showing the percentage of teachers who selected it.

Charts are filterable by country, gender, age group, and teaching experience via the sidebar.

### 3.2 Correlation analysis

#### Why Spearman, not Pearson

All survey responses are **ordinal** — the categories have a natural order but the intervals between them are not guaranteed to be equal. Spearman rank correlation makes no distributional assumptions and operates on rank order rather than raw values, which is appropriate for this data. Binary indicator columns are included directly: point-biserial correlation is a special case of Spearman for binary variables.

#### Why Benjamini-Hochberg (BH) correction

With 46 variables in the matrix there are 1,035 unique pairs to test. The **Benjamini-Hochberg procedure** controls the expected proportion of false discoveries (FDR) rather than requiring zero false positives. It is less conservative than Bonferroni correction and appropriate for exploratory research where the goal is pattern identification rather than hypothesis confirmation.

#### Ordinal encoding

Each ordinal variable was assigned integer scores following the natural order of its response scale (e.g. Never = 1, Rarely = 2, … Daily = 5). Fourteen ordinal questions and twelve binary indicator columns were included, yielding 46 variables in the correlation matrix.

Two non-ordinal categorical questions — Technology Adoption Profile (DT1.3) and Output Reworking (2.2.1) — were treated as ordered scales based on their content (from most passive/copy-paste to most effortful/critical).

#### Hierarchical clustering

Questions in the heatmap are reordered using **hierarchical clustering** (average linkage, distance = 1 − ρ). This groups questions that correlate with each other close together, making patterns visible as coloured blocks.

### 3.3 Country comparison (Kruskal-Wallis)

Because the sample is too small (N = 73, four countries) to run within-country correlation sub-analyses reliably, country differences are examined using the **Kruskal-Wallis H test** — a non-parametric one-way ANOVA that compares rank distributions across groups without assuming normality. It is appropriate for ordinal data and unequal group sizes.

**ε² (epsilon-squared)** converts H into a 0–1 effect-size scale:
- ε² ≥ 0.06 → medium country effect
- ε² ≥ 0.14 → large country effect

Formula: ε² = max(0, (H − k + 1) / (N − k)), where k = number of groups and N = total sample size.

---

## 4. How to Read the Correlation Tab

The tab has five components, from least to most technical.

### 4.1 Overview map

A grid where each cell represents a pair of variables. Colour encodes the relationship:

- **Blue** — tend to go together: teachers who score high on one tend to score high on the other
- **Red** — go in opposite directions: teachers who score high on one tend to score low on the other
- **Grey** — no meaningful association (not significant after BH correction, or effect too small)

Look for **blue blocks** (coherent clusters of related attitudes) and **isolated red cells** (tensions between attitudes). With 73 respondents, individual cells are less reliable than in the student analysis — focus on patterns across whole blocks.

### 4.2 Notable associations table

Lists only the pairs that pass both the BH significance test and |ρ| ≥ 0.30. Includes the ρ coefficient alongside the plain-language "What it means" sentence. The ρ column is included (unlike in the student table) to help partners judge whether a moderate and a strong association differ in a practically meaningful way, given the smaller N.

### 4.3 Country comparison

A Kruskal-Wallis table sorted by ε², followed by a drill-down chart for any selected variable:
- For **ordinal variables**: a stacked percentage bar chart (one bar per country, stacked by response level)
- For **binary indicators**: a simple percentage bar showing the selection rate per country

The ε² effect-size column uses ◆ for large and ◇ for medium effects to make the strongest country differences immediately visible.

### 4.4 Explore a relationship

Select any notable pair to see its joint distribution. For two ordinal questions, a percentage-normalised heatmap shows what proportion of teachers who gave a particular answer to Question A chose each answer to Question B. For pairs involving a binary indicator, a bar chart shows how the selection rate varies across ordinal levels of the other question.

### 4.5 Full correlation matrix (expert view)

The complete Spearman ρ matrix for all 46 variables, clustered in the same order as the overview map. Cells show the coefficient only where the association is BH-significant; non-significant cells are blank. Intended for internal review, not partner communication.

---

## 5. Main Findings from the Correlation Analysis

Forty-four pairs meet the threshold (|ρ| ≥ 0.30, BH-significant). They organise into five interpretive clusters.

### Cluster A — AI use and knowledge: the adoption profile

The strongest association in the dataset is between **general AI use frequency** and **school/work-specific AI use** (ρ = +0.845). This is largely definitional — teachers who use AI regularly do so across all contexts — and confirms the encoding is internally consistent.

More substantively, **self-assessed AI knowledge** is a hub that connects to many other variables:

| Pair | ρ |
|---|---|
| Self-assessed knowledge × school/work AI frequency | +0.583 |
| Self-assessed knowledge × general AI frequency | +0.540 |
| Self-assessed knowledge × technology adoption profile | +0.434 |
| Self-assessed knowledge × pedagogical AI readiness | +0.407 |
| Self-assessed knowledge × AI understanding (DT2.5) | +0.396 |
| Self-assessed knowledge × expected AI speed-up (DT4.1) | +0.401 |
| Self-assessed knowledge × expected AI personalisation (DT4.2) | +0.400 |

Teachers who rate their AI knowledge highly use AI more, adopt technology earlier, feel more pedagogically ready to integrate AI, and expect greater benefits from it. The pattern is consistent with a **competence-confidence cycle**: knowing more leads to using more, which reinforces confidence.

The two negative associations from this hub are analytically important (see Cross-cluster findings below).

### Cluster B — AI concerns (DT3): a coherent worry package

The six DT3 concern items and the two personal-stress items form the tightest cluster in the analysis. Teachers concerned about one societal risk from AI tend to be concerned about all of them:

| Pair | ρ |
|---|---|
| Critical thinking ↓ × detection difficulty | +0.727 |
| Student data privacy × social bias | +0.698 |
| Detection difficulty × student data privacy | +0.678 |
| Social bias × unequal access | +0.610 |
| Student data privacy × unequal access | +0.568 |
| Detection difficulty × social bias | +0.544 |
| Critical thinking ↓ × social bias | +0.528 |
| Learning pressure stress × AI reliance reduces self-efficacy | +0.691 |

The two personal stress items (DT3.7 and DT3.8) form their own tight pair within this cluster. A teacher who feels stressed by the pressure to keep up with AI tools also tends to worry that relying on AI makes them feel less capable — two sides of the same **technological anxiety** construct.

DT3.1 (AI undermines student assessment accuracy) correlates moderately with the rest of the cluster (ρ = 0.42–0.44) rather than strongly, suggesting it is perceived as a more specific, classroom-level concern rather than a broad societal one.

### Cluster C — AI expectations (DT4): the optimist package

The four DT4 expectation items correlate strongly with each other:

| Pair | ρ |
|---|---|
| AI improves accessibility × AI handles admin/grading | +0.606 |
| AI personalises learning × AI improves accessibility | +0.542 |
| AI speeds up tasks × AI improves accessibility | +0.532 |
| AI speeds up tasks × AI personalises learning | +0.526 |
| AI speeds up tasks × AI handles admin/grading | +0.486 |

Teachers are either broadly optimistic about AI's transformative potential or broadly reserved — not selectively optimistic about specific applications. This mirrors the student DS4 cluster and suggests **AI optimism** is a stable dispositional trait rather than a function of which specific capability is being evaluated.

### Cluster D — AI beliefs (DT2): partial coherence

The DT2 misconception items show weaker internal coherence than in the student analysis, with only some pairs reaching the threshold:

| Pair | ρ |
|---|---|
| AI truly understands text × AI is neutral/unbiased | +0.469 |
| Trust AI accuracy × understands how GenAI works | +0.394 |
| Trust AI accuracy × prompting doesn't affect quality | +0.366 |
| AI is smarter than humans × prompting doesn't affect quality | +0.438 |

The pairing of "AI is smarter than humans" with "prompting doesn't affect quality" (ρ = +0.438) is particularly interpretable: if a teacher believes AI is inherently superior, it is logically consistent to also believe that how you ask a question does not matter much.

### Cross-cluster findings

The most analytically interesting associations span section boundaries.

**Knowledge as a protective factor (negative associations):**
- Self-assessed knowledge × learning pressure stress (DT3.7): ρ = **−0.489**. Teachers who rate their AI knowledge highly are substantially less stressed by the pressure to keep up with AI tools. Knowledge appears to reduce anxiety — or alternatively, anxious teachers may underestimate their own competence.
- Self-assessed knowledge × concern about AI-generated content detection (DT3.3): ρ = **−0.404**. More knowledgeable teachers are less worried about the difficulty of detecting AI-generated content, possibly because they feel more equipped to deal with it.

**Technology adoption and curiosity:**
- Early tech adopters are more likely to feel curious about AI (ρ = +0.405) and aware of AI bias (ρ = +0.430). Early adopters have likely encountered AI's limitations and biases through direct experimentation — lived experience rather than awareness campaigns.

**Age, experience, and translation use:**
- Age group and teaching experience are strongly correlated (ρ = +0.737), as expected — older teachers have had more time to accumulate experience.
- Older teachers are **less** likely to use AI for translation (ρ = **−0.373** with age group). This may reflect language confidence accumulated over a career, or a preference for established translation workflows.

**Efficiency perception feeds optimism:**
- Teachers who find AI a "huge time saver" (2.2.3) are more likely to expect AI to significantly speed up their work (DT4.1, ρ = +0.385). Experience-based conviction reinforces forward-looking expectations.

---

## 6. Country Comparison Findings (Kruskal-Wallis)

Seventeen of 46 variables show a statistically significant country effect (p < 0.05). The largest effects:

| Variable | ε² | Effect |
|---|---|---|
| DT4.3 AI improves accessibility | 0.279 | Large |
| Teaching Experience | 0.242 | Large |
| DT4.4 AI handles admin/grading tasks | 0.237 | Large |
| Feels: Anxiety | 0.223 | Large |
| DT4.1 AI speeds up work tasks | 0.168 | Large |
| Feels: Skepticism | 0.148 | Large |
| 2.3.3 Awareness of Bias | 0.147 | Large |
| Uses AI: Images/presentations | 0.143 | Large |
| DT2.4 Trust AI accuracy without checking | 0.137 | Medium |
| Feels: Curiosity | 0.118 | Medium |

The strongest country differences concentrate in **AI expectations (DT4)** and **emotional responses**. Countries do not differ significantly on core concern items (DT3.1–DT3.6), AI beliefs (DT2.1–DT2.3), or school guideline awareness (DT1.5) — these are consistent across all four countries. The divergence is about what teachers *hope for* and *feel*, not about what they *worry about*.

The large country effect on **teaching experience** (ε² = 0.242) is a structural artefact: different countries contributed respondents with systematically different career stages, which must be considered when interpreting any country comparison that involves experience-related items.

---

## 7. Variables with No Notable Associations

Several variables were included in the analysis but produced no pairs at the threshold. These can be interpreted as items that are either very consistent across the sample (low variance) or genuinely independent of all other measured attitudes:

- DT1.5 School Guidelines on AI — no association with teacher knowledge, frequency, or concerns
- 2.2.1 Output Reworking approach — independent of AI knowledge and frequency
- 2.3 Confidence in detecting AI content — does not correlate with concern about detection difficulty
- Fact-checking habits (2.3.1) — not correlated with any other variable at this threshold

---

## 8. Limitations

| Limitation | Impact |
|---|---|
| Small N (73) | Higher threshold (|ρ| ≥ 0.30) still leaves correlations sensitive to sampling noise; results should be treated as suggestive rather than confirmatory |
| Unbalanced country representation | Turkey (N = 9) is too small for reliable sub-group inference; Spain (N = 27) dominates the aggregate |
| Heavy gender imbalance (82% female) | Gender sub-group analysis for males (N = 13) is unreliable |
| Ordinal encoding assumes ordered intervals | Spearman mitigates this but does not eliminate it; the distance between scale points is not guaranteed to be uniform |
| Acquiescence bias | Some teachers agree with everything; this inflates within-section correlations (especially DT3 and DT4) |
| Common method variance | All items from the same self-report survey; correlations may be slightly inflated compared to multi-source data |
| Cross-sectional design | Correlations cannot establish direction of causality |
| Subject field unreliable | "Main Subject Taught" was not usable for sub-group analysis due to mixed languages and insufficient standardisation |
