# Session 443 report: the company database, seeded

21 October 2026, about 07:15 to 07:40 UTC, unattended, on portable-laptop (the code machine), on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 443). Model spend USD 0; no pull, no web request; no warehouse data written; no `site/` change, so no build.

## Read these first

- **The seed is `docs/reviews/companies-seed.csv`: 8,273 companies**, one row each, from 33,741 table references. 7,760 are operators or developers in `energy_projects` (7,744 named nowhere else), 448 deal parties, 100 and 96 in the two datacenter tables, 8 datacenter operators, 3 in the datacenter queue positions, 21 the Thesis Builder researched. The note beside it, `docs/reviews/companies-seed.md`, gives the method, the counts with their source (`build.out`), the load and the pulls.
- **The ERW already has a company table**, `energy_companies` (469 rows here, public, tool 10 "partial" since session 25): every deal party and the Thesis Builder's companies. The seed holds 468 of its rows and adds 7,805 names it does not have, all from the datacenter and project tables.
- **Almost nothing beyond the name is known**: 21 rows have a description, 18 a stage, 468 a segment, each from an `energy_companies` row and cited to it. 8,252 of 8,273 rows (99.7 percent) carry only the name and where it stands. No field was invented.
- **The master plan has no segment taxonomy.** `02_master_plan.md` (outside the repository, in Samuel's Downloads) names tool 10's fields, "what each does, stage, funding, thesis fit", and tool 11 "by segment, stage, and investor", with no list of segments. `segment` is `energy_companies.sector` where there is one, and its source column says what that is: for a deal party, the news scorer's sector of its deals' stories, not a segment of the company.
- **The policy tables name no company in a column** (their parties are agencies). 84 companies gain 264 mentions where their full name stands in the publishers' text; they are in their own column, `policy_mentions`, as leads to check.

## What to review

- The seed: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/companies-seed.csv` (1.4 MB; open the note first).
- The note: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/companies-seed.md`.
- The test: `tests/test_session443.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s443/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `build_seed.py` (the last of five runs) | 0 | `build.out`: the counts quoted in the note |
| `tests.test_session443` | 0 | 8 tests OK: no em or en dash in either file; the columns; a name, a table and a row on every row; every table cited in `coverage.csv` or `warehouse/output`; a source beside every filled description, segment and stage, and only from `energy_companies`; no name or `name_key` twice; "not disclosed" never a stage |
| `tests.test_session443` against a copy with a dash and an unknown table | 1 (as it should) | 2 failures (`test_negative.out`) |
| The whole suite | not run | a docs and test session; the chain's last session runs it for the branch |
| Build, snapshot, browser checks | none | no `site/` change |

## Decisions made without you

1. **The thesis's company list is the Thesis Builder's**: the 21 `energy_companies` rows from `erw:thesis_builder` and the Landscape and Incumbents sheets of the five workbooks in `docs/thesis/`. Two names there, "Nabors Industries" and "Ormat Technologies", are in no ERW table and are not rows (the test asks a table of every row); the note names them.
2. **Normalization and merging are the project's own** (`seed_from_deals.split_names`, `not_a_company`, `build.name_key`), with nothing merged beyond `name_key`: "Amazon" and "Amazon Web Services", "Ormat" and "Ormat Nevada Inc" stay apart.
3. **A rule added to session 28's**: a name with "Department of", "Dept of", "Bureau of" or a military word is a government department and is left out (19 names, the Department of Energy and the Los Angeles Department of Water & Power among them). Utilities named "City of" (384), public power districts, authorities and cooperatives are kept. 243 names left out in all, each with its reason in `left_out.csv`.
4. **`energy_projects` names are not split** on "and" or commas: they are registered names, not news text.
5. **Policy mentions are text matches, kept apart**: whole, case-sensitive full names in publisher text only, a one-word name of six letters or more, not counted when a capitalized word stands next to it or inside a list of places. One kept match, "Liberty has 30 days", may not be the deal party "Liberty".
6. **`row_ids` lists 10 ids a table** with the count of the rest; every reference uncapped is in `company_rows.csv` beside the script (not in git), rebuilt by the script.
7. **The seed is a review file in `docs/reviews/`**, not a table: nothing in `warehouse/output` or `warehouse/metadata` changed.

## For Samuel's ruling

- **A segment taxonomy for tool 10** (the master plan has none). Until one exists, `segment` is the deals' story sectors, which describe deals, not companies.
- **Whether the seed is folded into `energy_companies`** (one company table, a third origin beside deals and the Thesis Builder) or loaded as its own table; and whether EIA-860M's 6,457 plant operators belong in a directory the master plan describes as "energy-intelligence startups" at all, or in a separate operators table.
- **Government departments and universities**: left out by session 28's rule and this session's addition (31 government bodies, 91 universities); municipal utilities and cooperatives kept. Rule on both.
- **The seed carries names and row ids from tables held for a license since 21 October** (`energy_deals`, the datacenter tables, `energy_projects` through ISO-NE). Whether a review file listing them may stay in the repository as it is, or waits for the per-row license of session 441's method.
- **`energy_companies` holds "Department of Energy"** (`erwco:department-of-energy`), a deal buyer session 28's rule missed: remove it from the table on the next run, or keep it.

## To finish

- Land `docs/reviews/companies-seed.csv`, `docs/reviews/companies-seed.md` and `tests/test_session443.py` with the next landing of `wip/441-450-third` (docs and a test; no build needed).
- The data machine, after the rulings above: the load described in the note's "What the data machine needs".

## Files

- `docs/reviews/companies-seed.csv` (new, 8,273 rows).
- `docs/reviews/companies-seed.md` (new).
- `tests/test_session443.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s443/build_seed.py` (the builder; reads `warehouse/output` only), `build.out`, `company_rows.csv` (33,741 references), `left_out.csv` (243 names), `test.out`, `test_negative.out`. The builder belongs in git if the seed is to be rebuilt by the data machine: the code machine may move it to `warehouse/companies/seed_from_tables.py` when it lands the seed.
