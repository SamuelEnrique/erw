# Session 446 report: the paper, outlined on what the warehouse can show

21 October 2026, about 07:16 to 07:30 UTC, unattended, on portable-laptop (the code role), in the main checkout on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 446). Model spend USD 0; no pull, no web request; no warehouse data written; no `site/` change, so no build. Files were written by this session and committed by the chain's parent session.

## Read these first

- **`docs/paper/outline.md` is extended, not rewritten.** Session 139's outline of 7 October is unchanged to the byte (its sha256 is pinned in the test); one section follows it, "The outline on what the warehouse can show, session 446, 21 October 2026": the paper in the IRW paper's shape (the data standard, the harmonization, the coverage, the licensing ledger, the validator, the citable release, the uses), each part with what the warehouse can produce today, named by table and key, and what needs work, named with what.
- **Eight counts of today replace session 139's of 7 October**: 212 tables, 40,332,903 rows, 179 public and 33 internal by flag, 212 of 212 passing the validator, 338 sources from 148 publisher names, 84 publishers in the license record, the ERW verdict 130 public, 33 internal, 49 unsettled, and v1 as packaged: 135 tables and 3 metadata tables, 42 held for a license, 2 for storage. Each is computed by `runs/chain_oct21_third/s446/counts.py` from the records named in the section.
- **Ten figures, seven of them can be drawn today from tables in v1.** Three need work: the California demonstration's hourly offset (the hourly EIA-930 generation of November 2023 to December 2025 is in no held table: `eia930_all_generation` begins 2026-08-26), the flat and flexible cost of a large load (`cost_of_power_monthly` is held out of v1 for ISO-NE's, MISO's and NYISO's rows), and the run log's validator blocks (0 of 6,312 `run_status.csv` details name the validator).
- **The master plan is not in the repository.** A search for `02_master_plan` and "master plan" finds only references to it. The author roles are therefore not quoted; the section gives what the repository records about Samuel and Ben, for their ruling.
- **Every cross-grid price table is held out of v1** (`iso_dam_hub_prices`, `hub_price_comparison`, `cost_of_power_monthly`). Until release ruling 2 (a copy without the held grids' rows) is made, the paper can show the harmonization of prices for ERCOT alone or on tables a reader cannot download from the release. This is decision 3 of the cover note.

## What to review

- The new section: `docs/paper/outline.md`, from the heading "The outline on what the warehouse can show, session 446".
- Its cover note, "Five decisions the paper needs from Samuel and Ben": authors and their order; which release and under whose name; the held tables; the standard as cited (v0 with 48 decisions, frozen at the release); the demonstrations (the hourly California figure, and whether the 20 model-extracted tables are in scope).
- The test: `tests/test_session446.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s446/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `counts.py` (the counts, and 20 figure tables looked up in `coverage.csv`) | 0 | `counts.json`; every figure table in `coverage.csv` |
| `tests.test_session446` | 0 | 9 tests OK: session 139's text unchanged (length and sha256); the heading once; no em or en dash in the section or the test; the seven IRW sections, the figure list, the author roles and the cover note present; every snake-case name in backticks a `coverage.csv` table, a v1 metadata table, a column of the records or a variable of `variables.csv`; every table of the figure list in `coverage.csv`; five numbered decisions; the counts against the records (skips once `coverage.csv` moves on); the master plan said to be absent |
| The same tests against a copy with an em dash and an unknown table added | 1 | 2 failures, as it should (`test_negative.out`) |
| The whole suite | not run | the chain's sessions ran in parallel on one checkout; the parent runs it once for the chain |
| Build, snapshot, browser checks | none | no `site/` change |

Session 139's text holds no em or en dash (counted: 0 and 0).

## Decisions made without you

1. **Appended, not rewritten.** The outline existed; non-negotiable 3 keeps it. Where session 139 already covers a part (the method's 3.1 to 3.6, the three demonstrations, the limits), the new section refers to it by number.
2. **"Key" read as the table's key under the standard and the variables a figure reads**, each variable checked against `docs/redivis/release-v1/variables.csv`. No `check-values` key is given: the paper's figures are not yet on a page.
3. **Figures are judged against v1, not against the warehouse.** A figure counts as "today" only if its tables are in v1 as packaged, so that a reader can reproduce it from the release the paper would cite.
4. **The author roles are not written from memory or from the chain's wording.** The master plan is not in the repository; the section says so and lists what the repository records.
5. **The count tests skip, not fail, once `coverage.csv` moves on**: the numbers are the records' of 21 October, and the daily run will change them; the section says they are to be recounted on the day of the release.
6. **The counting script lives under `runs/`**, which git ignores, as the chain asked; its output is described in the section so that the figures can be traced without it.

## For Samuel's ruling

- The five decisions of the cover note (with Ben).
- The master plan's lines on authorship: paste them into the outline, or rule the roles there.
- Whether the hourly EIA-930 generation for November 2023 to December 2025 is pulled again into a table (the data machine's; no chain has approved it), or demonstration 5.1 keeps only its monthly figure.
- Whether the validator's exit is logged with its rule from now on, so the paper can count what it blocks.

## To finish

- Land `wip/441-450-third`'s `docs/paper/outline.md` and `tests/test_session446.py` with the code machine's next landing (docs and a test only; no build needed for them).

## Files

- `docs/paper/outline.md` (extended: one section appended).
- `tests/test_session446.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s446/counts.py`, `counts.json`, `counts.out`, `counts0.out`, `section.md` (the appended text as written), `test.out`, `test_negative.out`.
