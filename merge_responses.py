#!/usr/bin/env python3
"""
Merge student survey responses (IT, ES, SL, TU) into a single English CSV.

Col[6]  (Use Cases) and col[15] (Feelings) are multi-select; both use smart
parsing. Col[15] is translated via an explicit dictionary; col[6] via
positional map lookup with greedy prefix matching for options that contain
internal commas.  TU col[31] is flagged as invalid (labeling error in the
original survey form: respondents saw DS3.6 question text, not DS3.8).
"""

import csv
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = '/Users/frau/dev/sail-surveys/data/students'
MAP_DIR = os.path.join(BASE, 'students-responses-map')
OUTPUT = os.path.join(BASE, 'Students Responses - merged-en.csv')

LANG_RESPONSE = {
    'it': os.path.join(BASE, 'Students Responses - it.csv'),
    'es': os.path.join(BASE, 'Students Responses - es.csv'),
    'sl': os.path.join(BASE, 'Students Responses - sl.csv'),
    'tu': os.path.join(BASE, 'Students Responses - tu.csv'),
}
LANG_MAP = {
    'en': os.path.join(MAP_DIR, 'Students Responses Map - en.csv'),
    'it': os.path.join(MAP_DIR, 'Students Responses Map - it.csv'),
    'es': os.path.join(MAP_DIR, 'Students Responses Map - es.csv'),
    'sl': os.path.join(MAP_DIR, 'Students Responses Map - sl.csv'),
    'tu': os.path.join(MAP_DIR, 'Students Responses Map - tu.csv'),
}

EXPECTED_ROWS = {'it': 98, 'es': 114, 'sl': 153, 'tu': 324}

TU_COL31_FLAG = (
    '[INVALID - survey labeling error: respondents saw DS3.6 question text, not DS3.8]'
)

# ---------------------------------------------------------------------------
# Translation tables
# ---------------------------------------------------------------------------

# col[1] Country
COUNTRY_TRANSLATIONS = {
    # IT
    'Italia': 'Italy', 'Spagna': 'Spain', 'Slovenia': 'Slovenia',
    'Germania': 'Germany', 'Turchia': 'Turkey', 'Other': 'Other',
    # ES
    'Itàlia': 'Italy', 'Espanya': 'Spain',
    'Catalunya': 'Spain (Catalonia)', 'Ghana': 'Ghana',
    # SL
    'Slovenija': 'Slovenia', 'Italija': 'Italy', 'Portugalska': 'Portugal',
    # TU
    'Türkiye': 'Turkey', 'Almanya': 'Germany',
    'İspanya': 'Spain', 'Afganistan': 'Afghanistan',
}

# col[15] Feelings – per-token lookup
FEELING_TRANSLATIONS = {
    # IT
    'Ansia': 'Anxiety', 'Curiosità': 'Curiosity', 'Paura': 'Fear',
    'Speranza': 'Hope', 'Scetticismo': 'Skepticism',
    'Entusiasmo': 'Enthusiasm', 'Diffidenza': 'Suspicion',
    # ES
    'Ansietat': 'Anxiety', 'Curiositat': 'Curiosity',
    'Emoció': 'Excitement',    # extra ES option; maps to Excitement
    'Por': 'Fear', 'Esperança': 'Hope', 'Escepticisme': 'Skepticism',
    'Entusiasme': 'Enthusiasm', 'Sospita': 'Suspicion',
    # SL
    'Tesnoba': 'Anxiety', 'Radovednost': 'Curiosity', 'Strah': 'Fear',
    'Upanje': 'Hope', 'Skepticizem': 'Skepticism',
    'Navdušenje': 'Enthusiasm', 'Sum': 'Suspicion',
    # SL artifact: first checkbox showed as "Option 1" = Tesnoba = Anxiety
    'Option 1': 'Anxiety',
    # TU
    'Kaygı': 'Anxiety', 'Merak': 'Curiosity', 'Korku': 'Fear',
    'Umut': 'Hope', 'Şüphecilik': 'Skepticism',
    'Coşku': 'Enthusiasm',
    'Heyecan': 'Excitement',   # extra TU option; maps to Excitement
    'Kuşku': 'Suspicion',
}

# Non-canonical feelings that appear as free-text responses
FEELING_OTHER_TRANSLATIONS = {
    'Rabbia': 'Other (anger)',
    'Preoccupazione': 'Other (worry)',
    'Indifferenza': 'Other (indifference)',
    'Pigrezza': 'Other (laziness)',
    'Criticismo': 'Other (criticism)',
    'Zaskrbljenost': 'Other (concern)',
    'Irkçılık': 'Other (racism concerns)',
    'İlgi alanıma girdiği için iyi hissediyorum': 'Other (positive interest)',
}

# Noise tokens in col[15] to discard silently
FEELING_NOISE = {
    ';)', 'Ns', 'res', 'Pq hauria de produirme un sentiment',
    'Tan fa', 'esta be', 'tant me fa',
    'Hiç', 'hiç', 'Saçma', 'Nevem', 'mezunuz', 'kopya',
}

# Entire-cell noise values for col[15] (before splitting)
FEELING_CELL_NOISE = {
    'Tan fa , esta be', 'tant me fa', 'Ns', 'res',
    'Pq hauria de produirme un sentiment',
    'Hiç', 'hiç', 'Saçma',
}

# col[6] Other / open-text fragments
USE_CASE_TRANSLATIONS = {
    # IT
    'Ricerca di vari argomenti':
        'Other (searching for various topics)',
    'facendo dei test per prepararmi per le verifiche':
        'Other (practice tests)',
    'Immagini per divertimento':
        'Other (images for fun)',
    'fare ricerche':
        'Other (information searching)',
    "utilizzo l'IA quando necessito di sapere qualcosa in modo più specifico":
        'Other (specific questions)',
    'Spiegazioni':
        'Other (explanations)',
    "Spesso uso l'intelligenza artificiale per farmi spiegare un argomento che non ho capito in classe":
        'Other (topic explanations)',
    "chiedo di generare domande in base all'argomento dell'interrogazione":
        'Other (practice question generation)',
    'palestra':
        'Other (gym/fitness)',
    'aiuto con i compiti e idee per progetti':
        'Other (homework and project ideas)',
    # ES
    'Buscar informacio':
        'Other (information search)',
    'Coses personals':
        'Other (personal matters)',
    'Recopilar informació':
        'Other (collecting information)',
    'diverció':
        'Other (entertainment)',
    'Ajuda amb planificar una dieta':
        'Other (diet planning)',
    'Per consultar problemes reals, ajudar amb rutines diaries/GYM...':
        'Other (real problems and daily routines)',
    'Resoldre problemes diversos':
        'Other (solving various problems)',
    # SL
    'Iskanje podatkov':
        'Other (data search)',
    'Delanje zapiskov za učenje.':
        'Other (making study notes)',
    'trening plan in random stvari':
        'Other (training plans and miscellaneous)',
    'Vse':
        'Other (everything)',
    # TU
    'Araştırma yapmak ve bilgi edinmek':
        'Other (research and information gathering)',
    'Kodlama yapmak':
        'Other (coding)',
    'Günlük kalori hesabı yapmak':
        'Other (daily calorie calculation)',
    'anket doldurmak':
        'Other (filling out surveys)',
    'Alışveriş yaparken ürün karşılaştırması için':
        'Other (product comparison for shopping)',
    'Derslerde anlamadığım konular hakkında özet, anlamadığım sorular':
        'Other (topic summaries and unclear questions)',
    'Günlük hayattaki bazı problemler için görüşünü almak':
        'Other (daily life advice)',
    'Resım vb. Sanatsal çalışmalarda':
        'Other (artistic work)',
    'psikolojik destek':
        'Other (psychological support)',
    'Sosyal':
        'Other (social use)',
}

# ---------------------------------------------------------------------------
# Helpers: col[15] feelings
# ---------------------------------------------------------------------------

def _translate_feeling_token(tok: str) -> str | None:
    tok = tok.strip()
    if not tok:
        return None
    if tok in FEELING_NOISE:
        return None
    if tok in FEELING_TRANSLATIONS:
        return FEELING_TRANSLATIONS[tok]
    if tok in FEELING_OTHER_TRANSLATIONS:
        return FEELING_OTHER_TRANSLATIONS[tok]
    # Canonical feeling used as a prefix of a longer open-text phrase
    # e.g. "Esperança de que s'utilitzi correctament."
    for local_tok, en_tok in FEELING_TRANSLATIONS.items():
        if tok.startswith(local_tok + ' ') or tok.startswith(local_tok + ','):
            return en_tok
    if len(tok) > 12:
        return 'Other'
    return f'[UNMAPPED_FEELING:{tok}]'


def translate_col15(value: str) -> str:
    value = value.strip()
    if not value:
        return ''
    # Discard whole-cell noise
    if value in FEELING_CELL_NOISE:
        return ''
    value = value.rstrip(',').strip()
    if not value:
        return ''
    tokens = [t.strip() for t in value.split(',')]
    results: list[str] = []
    seen: set[str] = set()
    for tok in tokens:
        translated = _translate_feeling_token(tok)
        if translated and translated not in seen:
            results.append(translated)
            seen.add(translated)
    return ', '.join(results)


# ---------------------------------------------------------------------------
# Helpers: col[6] use cases (greedy prefix parser for internal commas)
# ---------------------------------------------------------------------------

def _parse_col6(value: str, options_desc: list[str]) -> list[str]:
    """Greedy left-to-right parser; options_desc sorted longest-first."""
    value = value.strip().rstrip(',').strip()
    if not value:
        return []
    results: list[str] = []
    remaining = value
    while remaining:
        matched = False
        for opt in options_desc:
            if remaining == opt:
                results.append(opt)
                remaining = ''
                matched = True
                break
            if remaining.startswith(opt + ', '):
                results.append(opt)
                remaining = remaining[len(opt) + 2:]
                matched = True
                break
        if not matched:
            # Locate the start of the next known option
            next_pos = len(remaining)
            for opt in options_desc:
                sep = ', ' + opt
                idx = remaining.find(sep)
                if 0 <= idx < next_pos:
                    next_pos = idx
            fragment = remaining[:next_pos].strip().rstrip(',').strip()
            if fragment:
                results.append('__OTHER__:' + fragment)
            remaining = remaining[next_pos:]
            if remaining.startswith(', '):
                remaining = remaining[2:]
    return results


def translate_col6(value: str, local_opts_desc: list[str],
                   col6_lookup: dict[str, str]) -> str:
    parts = _parse_col6(value, local_opts_desc)
    en_parts: list[str] = []
    seen: set[str] = set()
    for part in parts:
        if part.startswith('__OTHER__:'):
            fragment = part[len('__OTHER__:'):]
            translated = USE_CASE_TRANSLATIONS.get(fragment,
                                                    f'Other ({fragment[:50]})')
        else:
            translated = col6_lookup.get(part, f'[UNMAPPED_USE_CASE:{part}]')
        if translated and translated not in seen:
            en_parts.append(translated)
            seen.add(translated)
    return ', '.join(en_parts)


# ---------------------------------------------------------------------------
# Map loading
# ---------------------------------------------------------------------------

def load_map_option_rows(path: str, n: int = 9) -> list[list[str]]:
    """Return the first n data rows (option rows) from a map file."""
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return rows[1:n + 1]


def build_col_lookup(local_rows: list[list[str]],
                     en_rows: list[list[str]],
                     col: int) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for lr, er in zip(local_rows, en_rows):
        lv = lr[col].strip() if col < len(lr) else ''
        ev = er[col].strip() if col < len(er) else ''
        if lv and ev:
            lookup[lv] = ev
    return lookup


# ---------------------------------------------------------------------------
# Row translation
# ---------------------------------------------------------------------------

def translate_row(row: list[str], lang: str,
                  col_lookups: dict[int, dict[str, str]],
                  col6_opts_desc: list[str],
                  col6_lookup: dict[str, str],
                  n_cols: int) -> list[str]:
    out = [''] * n_cols
    for i in range(n_cols):
        val = row[i].strip() if i < len(row) else ''

        if i == 0:
            out[i] = val  # timestamp: pass through

        elif i == 1:
            out[i] = (COUNTRY_TRANSLATIONS.get(val, f'[UNMAPPED_COUNTRY:{val}]')
                      if val else '')

        elif i == 6:
            out[i] = translate_col6(val, col6_opts_desc, col6_lookup)

        elif i == 15:
            out[i] = translate_col15(val)

        elif i == 31 and lang == 'tu':
            # Mislabeled column: flag instead of translating
            out[i] = TU_COL31_FLAG if val else ''

        else:
            lookup = col_lookups.get(i, {})
            out[i] = lookup.get(val, f'[UNMAPPED:{val}]') if val else ''

    return out


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge() -> dict[str, int]:
    with open(LANG_MAP['en'], encoding='utf-8') as f:
        en_all = list(csv.reader(f))
    en_header = en_all[0]
    en_opts = en_all[1:10]
    n_cols = len(en_header)

    out_header = en_header + ['Source Language']
    merged: list[list[str]] = []
    counts: dict[str, int] = {}

    for lang in ['it', 'es', 'sl', 'tu']:
        print(f'Processing {lang}...')
        local_opts = load_map_option_rows(LANG_MAP[lang])

        # Per-column standard lookups (exclude specially-handled cols)
        col_lookups: dict[int, dict[str, str]] = {}
        for c in range(n_cols):
            if c in (0, 1, 6, 15):
                continue
            lk = build_col_lookup(local_opts, en_opts, c)
            if lk:
                col_lookups[c] = lk

        # col[6] lookup and sorted option list
        col6_lookup: dict[str, str] = {}
        col6_local_opts: list[str] = []
        for lr, er in zip(local_opts, en_opts):
            lv = lr[6].strip() if 6 < len(lr) else ''
            ev = er[6].strip() if 6 < len(er) else ''
            if lv and ev:
                col6_lookup[lv] = ev
                col6_local_opts.append(lv)
        col6_opts_desc = sorted(col6_local_opts, key=len, reverse=True)

        with open(LANG_RESPONSE[lang], encoding='utf-8') as f:
            resp = list(csv.reader(f))

        count = 0
        for row in resp[1:]:
            en_row = translate_row(row, lang, col_lookups,
                                   col6_opts_desc, col6_lookup, n_cols)
            en_row.append(lang)
            merged.append(en_row)
            count += 1

        counts[lang] = count
        print(f'  {count} rows translated')

    with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(out_header)
        w.writerows(merged)

    print(f'\nOutput: {OUTPUT}')
    print(f'Total rows written: {len(merged)}')
    return counts


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(counts: dict[str, int]) -> None:
    print('\n=== VALIDATION ===')

    with open(OUTPUT, encoding='utf-8') as f:
        rows = list(csv.reader(f))

    header = rows[0]
    data = rows[1:]
    src_idx = header.index('Source Language')

    # 1. Total row count
    expected_total = sum(EXPECTED_ROWS.values())
    actual_total = len(data)
    status = '✓' if actual_total == expected_total else '✗'
    print(f'{status} Total rows: expected {expected_total}, got {actual_total}')

    # 2. Per-language counts
    for lang in ['it', 'es', 'sl', 'tu']:
        actual = sum(1 for r in data if len(r) > src_idx and r[src_idx] == lang)
        exp = EXPECTED_ROWS[lang]
        s = '✓' if actual == exp else '✗'
        print(f'  {s} {lang}: expected {exp}, got {actual}')

    # 3. UNMAPPED entries
    unmapped: list[tuple] = []
    for ri, row in enumerate(data, start=2):
        for ci, val in enumerate(row):
            if '[UNMAPPED' in val:
                col_name = header[ci] if ci < len(header) else f'col{ci}'
                unmapped.append((ri, ci, col_name, val[:80]))
    if unmapped:
        print(f'\n! {len(unmapped)} unmapped value(s):')
        for ri, ci, name, val in unmapped[:40]:
            print(f'  row {ri}, col {ci} ({name[:40]}): {val}')
        if len(unmapped) > 40:
            print(f'  ... and {len(unmapped) - 40} more')
    else:
        print('✓ No unmapped values')

    # 4. TU col[31] flags
    col31_idx = next((i for i, h in enumerate(header) if 'DS3.8' in h), None)
    if col31_idx is not None:
        tu_rows = [r for r in data if len(r) > src_idx and r[src_idx] == 'tu']
        flagged = sum(1 for r in tu_rows
                      if col31_idx < len(r) and TU_COL31_FLAG in r[col31_idx])
        non_empty = sum(1 for r in tu_rows
                        if col31_idx < len(r) and r[col31_idx].strip())
        print(f'\nTU DS3.8 col: {flagged}/{non_empty} non-empty cells flagged '
              f'(out of {len(tu_rows)} TU rows)')
    else:
        print('! DS3.8 column not found in header')

    # 5. Non-ASCII check (heuristic — English values should be ASCII)
    # Allow curly quotes (‘-”), em-dash (—), ellipsis (…)
    ALLOWED_NON_ASCII = set('‘’“”—–…éàü')
    skip_cols = {0, src_idx}  # timestamp and source-lang cols are pass-through
    non_ascii: list[tuple] = []
    for ri, row in enumerate(data, start=2):
        lang = row[src_idx] if src_idx < len(row) else ''
        for ci, val in enumerate(row):
            if ci in skip_cols:
                continue
            if '[INVALID' in val or '[UNMAPPED' in val:
                continue
            suspect = [c for c in val if ord(c) > 127 and c not in ALLOWED_NON_ASCII]
            if suspect:
                col_name = header[ci] if ci < len(header) else f'col{ci}'
                non_ascii.append((ri, ci, col_name, lang, val[:70]))

    if non_ascii:
        print(f'\n! {len(non_ascii)} cell(s) with unexpected non-ASCII characters:')
        for ri, ci, name, lang, val in non_ascii[:20]:
            print(f'  row {ri} ({lang}), col {ci} ({name[:35]}): {val}')
        if len(non_ascii) > 20:
            print(f'  ... and {len(non_ascii) - 20} more')
    else:
        print('✓ No unexpected non-ASCII characters in translated values')

    print('=== VALIDATION COMPLETE ===\n')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    counts = merge()
    validate(counts)
