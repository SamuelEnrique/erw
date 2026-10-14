# Session 272 report: the 341 large-load statements, public

14 October 2026, 09:42 to 10:00 UTC, unattended, on lab-desktop (the data machine), the second session of the overnight chain of 14 October. Branch `task/272-large-load-public`, cut from session 271's branch. Model spend USD 0: no model call. Pulls: none. Writes under the data lock: `large_load_public` and `large_load_document_verdicts` rebuilt and stored, `large_load_public` loaded into the live set.

## Read these first

- **`large_load_public` is public, by your ruling: 341 statements, 67 entities, as facts with a link and no quoted text.** Its header, its source (`erw:large_load_public`), coverage, the catalogue entry, the draft of the public Redivis dataset (341 rows; nothing released) and the live set (341 rows, read through `events` with the anon key) all say so.
- **The one read helper: `largeLoadStatements(grid?)` in `site/lib/largeloadpublic.ts`.** Newest first; with a grid, that grid's rows only (`ercot` gives 67, as session 255 counted). It reads the columns of the table and none of a document's words. No page calls it yet: the code machine's session 265 wires the page.
- **Coverage needed one exception, written as a rule:** a derived table takes its inputs' license, and this one's input (`large_load_statements`) is internal. `PUBLIC_SELECTIONS` in `build_coverage.py` names `large_load_public` alone as a public selection of an internal table; any other table with an internal input and a public flag still stops the build.
- **The license table for 21 October: 125 public (124 before), 40 "license needed", 34 internal.** `large_load_public` is public with no deciding publisher (each row's own document).
- **`large_load_document_verdicts` stays internal** (it lists the documents of internal tables). The copy of `large_load_public` in the internal Redivis draft (session 255's) is left for a person to remove.

## What changed

| Where | Before | After |
|---|---|---|
| `large_load_public.csv` header | `License: internal until the owner rules` | `License: public, by the owner's ruling of 14 October 2026 (session 272)` |
| `sources.csv`, `erw:large_load_public` | internal | public |
| `coverage.csv` | internal | public (341 rows, tier `model_extracted`) |
| Redivis | the internal dataset's draft | the public dataset's draft (`ok large_load_public: CSV 341 rows, Redivis count(*) 341`) |
| `live_set.yaml` | `catalogue_hold`, `sources_hold` | `full: '^large_load_public$'`; the verdicts stay held |
| Supabase | not loaded | 341 rows written; the catalogue row says public, 341 rows; database 1,671.2 MB of 7,500 |
| `site/lib/largeloadpublic.ts` | none | the read helper |
| `docs/methods/large_load_public.md` | | a paragraph on the ruling |

## The landing of session 271

- Freeze: exit 0, no freeze. Main had moved (the code machine's sessions 257 to 260, `b74959ed`); merged into the branch before the push.
- Before snapshot `s271-before`: 09:41:54 UTC, 25 pages, 0 failed. Pushed 09:42:03 UTC (`task/271-green-days`, `70291c7e`).
- Check run 38544272684: success at 09:51:51 UTC; it merged the branch as `43366ecf`. Deployment of `43366ecf`: success at 09:53:40 UTC.
- After snapshot `s271-after`: 09:53:52 UTC, 25 pages, 0 failed. `compare s271-before s271-after`: exit 0, **0 differences in all**. Expected: no page is live, and nothing session 271 changed is read by the 25 pages as a visitor sees them.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 272"` | 0 | six of six; on duty |
| `lock.py run -- large_load_public.py` | 0 | 427 verdicts, 341 public rows |
| `lock.py run -- table_stores.py large_load_public large_load_document_verdicts` | 0 | validate, coverage, archive, Redivis each 0, for both |
| `lock.py run -- load.py --no-vacuum --only '^large_load_public$'` | 0 | match, 341 written |
| the anon key's read of `events?table_name=eq.large_load_public` | | rows, and `extra->>grid=eq.ercot` gives 67 |
| `licenses.py tables`, `write`, `status`, `check` | 0 each | 199 tables, 0 problems |
| `npx tsc --noEmit` in `site/` | 2 | 20 errors, every one in `.next/` generated route types or `app/research/[week]`, none in the new file |
| `tests.test_session272` with 255, 207, `test_redivis_gates`, 271 | 0 | 78 tests |
| the 47 modules that read licenses, the live set or coverage | 1 | 987 tests, 2 failures: this machine's standing `test_session51` and `test_session125` |

## Decisions made without you

1. **The flag is a rule in `build_coverage.py`, not a hand edit of `coverage.csv`:** a rebuild anywhere gives the same answer, and only the one table may be public over an internal input.
2. **The helper reads the live set, not a file in `site/data/`:** the table is small (341 rows), public now, and a page's read of an events table is how the site reads every other events table.
3. **The helper asks for every public column but none of the document's words,** so the page chooses what to show; `stage_class` is the ERW's class.
4. **Nothing was released on Redivis,** as always: the public draft holds the table until a person releases a version.
5. **The internal draft's old copy is left,** as session 207 left FRED's: removing a table from a Redivis dataset is a person's step.

## For Samuel's ruling

1. Remove `large_load_public` from the internal Redivis dataset's draft, now that the public draft holds it?
2. Session 255's eight rulings beyond this one (the Kentucky addresses, the filer's own site, ERCOT's and CAISO's documents, the stage in words, the federal bodies, the unread hosts, PJM) still stand; each would change the 341.

## Files

- New: `site/lib/largeloadpublic.ts`, `tests/test_session272.py`, this report.
- Changed: `warehouse/derived/large_load_public.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/methods/large_load_public.md`, `tests/test_session255.py`, and the metadata the stores and the license scripts wrote.

## The landing

- In session 273's report.
