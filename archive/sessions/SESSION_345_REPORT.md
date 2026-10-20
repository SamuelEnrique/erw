# Session 345 report: the JEDI multipliers table

20 October 2026, from about 07:50 UTC, unattended, on portable-laptop (the third machine, Samuel's personal laptop), the second session of the chain of 20 October, night (sessions 344 to 350). Branch `wip/345-impact`, not landed (this machine lands nothing). Model spend USD 0. Ruling: Samuel, 20 October 00:25, in chat (tool 17, the economic impact tool, phase one).

## Read these first

- **The table is `nlr_jedi_multipliers`, not `jedi_multipliers`:** a series table's name has three parts (Decision 19), as `battery_sourced_ranges` was named in session 306.
- **The figures are JEDI's own formulas, recomputed for every state.** A JEDI workbook holds the results of the one project it is saved with (wind: 300 MW in Connecticut). `warehouse/connectors/jedi_recalc.py` evaluates each workbook's formulas with pycel, with Project Location set to each state of the model's own list, after reproducing all 30 saved summary figures of each model from its constants. Nothing else is changed except the PV model's System Application, set to its own Utility option.
- **A fault was found and fixed before anything was written.** pycel builds each formula cell holding its saved value, so a first version that only changed the location gave every state Connecticut's supply chain and induced jobs, and its "reproduced exactly" check proved nothing. The script now empties every formula cell before each computation, and checks each total against its three lines at every location (docs/methods/economic_impact.md, section 1).
- **No battery row:** NLR publishes no JEDI model for battery storage.
- **5,562 rows** (from session 347: 4,944 at first, then each location's project MW and two local shares as rows of their own), loaded to Supabase (`review_hold`), drafted to Redivis and archived.

## What to review

1. `docs/methods/economic_impact.md`, section 1.
2. `warehouse/connectors/jedi_recalc.py`: `fresh()`, `local_names()`, the five Excel functions.
3. `warehouse/connectors/jedi_multipliers.py` and the table's header.

## Pulls against their ceilings

| Request | Count | Ceiling |
|---|---|---|
| NLR's robots file (`www.nlr.gov/robots.txt`: allows every path) | 1 | (before any new host) |
| NLR's terms (`https://www.nlr.gov/disclaimer`: the same SHA-256 as license read 65) | 1 | (terms first) |
| The JEDI models page and the four model pages | 5 | 12 |
| The four workbooks (wind W9.14.18, PV PV05.20.21, gas NG4.17.17, geothermal GT12.23.16) | 4 | |
| **JEDI requests in all** | **9** | **12** |

Every request is in `runs/s345/requests.csv` (not in git). Nothing from NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py` | 0 | portable-laptop on duty |
| `jedi_recalc.py` (the final version) | 0 | four models: 30 of 30 saved figures each, computed from 12,798 to 21,976 cells; 52 locations each; gas: JEDI's own `#DIV/0!` at DC and Hawaii, no row |
| `jedi_multipliers.py` under the data lock | 0 | 4,944 rows (5,562 from session 347) |
| `erw_validate.py warehouse/output/nlr_jedi_multipliers.csv` | 0 | PASS, 0 errors, 0 warnings |
| `build_coverage.py --only '^nlr_jedi_multipliers$'` | 0 | one row rebuilt, every other carried over |
| `load.py --only '^nlr_jedi_multipliers$'` under the lock | 0 | match: CSV 4,944, Supabase 4,944 |
| `upload.py --tables nlr_jedi_multipliers` under the lock | 0 | Redivis count 4,944; draft only, nothing released; `erw_headers` skipped (the Redivis export cap) |
| `archive.py write --tables '^nlr_jedi_multipliers$'` under the lock | 0 | 4,944 rows |
| `licenses.py write`, `check` | 0, 0 | 205 tables, 0 problems; the new table agrees (public, NLR's notice) |
| `tests.test_session345` | 0 | 12 tests (11 at first) |

## Decisions made without you

1. **The table name** `nlr_jedi_multipliers` (above).
2. **pycel, in an environment of its own** (`.venv-jedi`, ignored by git): pycel needs networkx below 2.7, and the repository's environment holds networkx 3 for mapclassify. Installing pycel into `.venv` first downgraded networkx to 2.6.3; it was uninstalled at once and networkx put back (3.7; `mapclassify` imports). Noted for the venv rule: nothing of `requirements.txt` changed.
3. **Recalculation rather than the saved project alone.** Reading only the saved project would give one state a model; the workbook's own formulas give every state the model's own answer, and the saved project's exact reproduction is the proof.
4. **Utility-scale PV** is the PV model with its System Application set to its own Utility option, so JEDI takes its own utility defaults (the prompt asks for utility-scale; the workbook is saved with residential systems).
5. **The land-based wind workbook W9.14.18, not the Beta W10.30.20,** which NLR offers as a program in a zip file: the ERW runs no publisher's program.
6. **The effect is part of the row** (on site, supply chain, induced, total): the prompt's grain is technology, state, phase and measure; the methods note asks for direct, indirect and induced effects.
7. **Two misspelled locations** of the gas model's list ("NORTH DAKOTO", "SOUTH DAKOTO") are mapped to ND and SD by name; `x_location` keeps JEDI's word.
8. **Three units** join the vocabulary (Decision 48): `FTE-year/MW`, `FTE/MW`, `USD/MW-year`.
9. **The tier is `derived`**: the figures are computed by ERW code with JEDI's formulas, not published as they stand.

## For Samuel's ruling

- The questions of the review pack's part 9 (`docs/reviews/packs/impact.md`), of which 5, 6, 8, 9 and 10 are about this table.

## Files

- New: `warehouse/connectors/jedi_recalc.py`, `warehouse/connectors/jedi_multipliers.py`, `docs/methods/economic_impact.md` (section 1), `tests/test_session345.py`, this report.
- Changed: `.gitignore` (`.venv-jedi/`), `warehouse/validate/erw_validate.py` (three units), `docs/datastandard.md` (Decision 48), `warehouse/metadata/build_coverage.py`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `warehouse/supabase/live_set.yaml`, `redivis_uploads.csv`, `archive_manifest.csv`, `license_tables.csv`, `license_verdicts.csv`, `docs/licenses.md`.
- Not in git: `warehouse/raw/nlr_jedi/` (the four workbooks and the recalculation's files), `warehouse/output/nlr_jedi_multipliers.csv`, `runs/s345/`.
