# Session 346 report: the tax side

20 October 2026, about 08:25 to 08:40 UTC, unattended, on portable-laptop (the third machine), the third session of the chain of 20 October, night. Branch `wip/345-impact`, not landed. Model spend USD 0. No pull.

## Read these first

- **`impact_tax_rules`: 49 rows in the events shape, every row with its citation.** 42 are the severance rules the /severance page holds for Texas, Louisiana and New Mexico (`site/data/severance_rules.json`, sessions 40 and 41), each with the page's own sentence and, where held, the statute's section and words: 14 base rates, Louisiana's two oil rates by completion date, 2 Texas fees and 24 reduced rates or exemptions. Nothing was read again and no rate changed.
- **Property tax: no rule held, in all three states.** No public statute on the property tax of a generating project, nor on Texas Tax Code chapters 312 and 313, Louisiana's ITEP or New Mexico's IRB, is held in the repository (searched: `docs/`, `site/data/`, `warehouse/metadata/`, `archive/sessions/`). Each is a row with status `no_rule_held` (7 rows), which states no rate and no figure.
- **The table is "not settled" in `docs/licenses.md`**: the four publishers' terms (the Texas Comptroller, the Louisiana Legislature and Department of Revenue, New Mexico's Taxation and Revenue Department) were never read, and this session made no request. The impact page does not offer it for download.

## What to review

1. `docs/methods/economic_impact.md`, section 2.
2. `warehouse/derived/impact_tax_rules.py` and the table's header.

## Checks

| Check | Exit | Result |
|---|---|---|
| `impact_tax_rules.py` under the data lock | 0 | 49 rows (42 held, 7 no rule held) |
| `erw_validate.py warehouse/output/impact_tax_rules.csv` | 0 | PASS, events shape, 0 errors |
| `build_coverage.py --only '^impact_tax_rules$'` | 0 | one row rebuilt, 205 carried over |
| `load.py --only '^impact_tax_rules$'` under the lock | 0 | match: CSV 49, Supabase 49 |
| `upload.py --tables impact_tax_rules` | 0 | Redivis count 49, draft only |
| `archive.py write --tables '^impact_tax_rules$'` | 0 | 49 rows |
| `licenses.py write`, `check` | 0, 0 | 206 tables, 0 problems; the new table "not settled" |
| `tests.test_session346` | 0 | 6 tests |

**One fault fixed in the session:** Louisiana's gas rate is per unit (USD 0.1514 per Mcf), and the first build left its unit blank. The builder was fixed and the table written again; the load of that second build was **refused** by the loader because coverage still described the first file (the guard of session 65), so coverage was rebuilt and the load, the draft and the archive run again (1 row changed). The second run's upload and archive lines were first read from the first run's logs; the logs were cleared and the three steps run again, each line read fresh.

## Decisions made without you

1. **The events shape**, one row a rule: a rule has an effective date and a citation, not an observation; `event_date` is the effective date the citation gives as a date, else the day the rule was read (30 September 2026) or checked (20 October 2026), and `x_date_kind` says which.
2. **Severance is not computed for a plant**: none of the tool's technologies produces oil or gas (`x_applies_to`). A gas plant's fuel is a question for you (the pack's question 4).
3. **The rows' sources are registered** as public state law and agency pages (`sources.csv`), and the table stays "not settled" until the terms are read: the flag says what the ERW believes, the license record what was read.
4. **"Read from:", not "Derived from:"** in the header: the rules come from a file of the site, not from an ERW table, so the coverage builder's derived-license rule does not apply; the tier is `source` (the publishers' sentences, reshaped).

## For Samuel's ruling

- The pack's questions 1 (the four publishers' terms) and 2 (pull the property-tax statutes).

## Files

- New: `warehouse/derived/impact_tax_rules.py`, `tests/test_session346.py`, the methods note's section 2, this report.
- Changed: `build_coverage.py`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `live_set.yaml`, `redivis_uploads.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
