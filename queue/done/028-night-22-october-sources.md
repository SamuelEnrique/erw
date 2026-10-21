# Chain of the night of 21 to 22 October 2026: sessions 523 to 529, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 522, the last session of `queue/done/027-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 523 to 529 were free in every queue file and branch when this was written; 530 is free too, and 531 on is the old laptop's chain 024. Each route below answered EIA's metadata call on 21 October (session 522: four requests).

Each source session goes through the erw-add-connector skill, with chain 027's form:

- the robots file and terms first (EIA: record 1, public);
- a probe;
- a trial with `--out-dir`, whose saved pages the write reuses with `--offline`;
- a cross-check against a table the ERW holds;
- the write with `runs/write_table.sh <session> <table> <connector> [args]` and `runs/finish_table.sh <session> <table> public` (both on the data machine, in `runs/`, not in git: sessions 516 and 518's reports say what they do);
- a sector rule, both holds (`catalogue_hold`, `STORAGE_HELD`), tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/027-night-22-october-sources.md` hold, word for word, with its lessons. Three are added from chain 027:

- **EIA's `total` is not always the number of rows the data hold** (session 516: the plants' outages). Where pages run in a sort order, read until a short page and check the order and the missing periods yourself.
- **Two sessions' metadata next to each other conflict as a patch.** Both sides only add lines: resolve with `runs/union_resolve.py`.
- **A table already written that gains rows needs its release row replaced**, not added (session 520).

Read `docs/state/note_2026-10-23_sources_data.md` and sessions 516 to 521's reports first.

## Session 523: EIA's nuclear outages by plant, 2007 to 2014

Long end 1:30. Pulls: at most 100 requests (about 36,000 rows a year, so about 58 pages).

- Add `--to` to `eia_nuclear_outages_facility.py` (EIA's `end` parameter). Run `--from 2007-01-01 --to 2014-12-31` in a trial, then write it merged with the table's 2015 on. The writer is a snapshot: write both windows in one run from saved pages, or change the writer to a merge on the key, with a test.
- Cross-check: the plants' sums against `eia_nuclear_outages_daily`, 2007 to 2014.

## Session 524: EIA-923's back years

Long end 2:00. Pulls: at most 130 requests (about 6 pages a year).

- `eia923_plant_fuel.py --from 2001 --to 2019`, written with 2020 to 2024 (the same snapshot rule as 523).
- Cross-check: the U.S. total each year against `eia_state_generation_monthly`.

## Session 525: natural gas in underground storage by state

Long end 1:30. Pulls: EIA's API v2, route `natural-gas/stor/sum`, monthly, at most 30 requests.

- Working gas, base gas and total capacity by state, as `eia_gas_storage_state_monthly`, in `MMcf`. Read the processes from the facet first; take no share or percent series.
- Cross-check: the U.S. working gas at each month's end against `eia_gas_storage_weekly`'s nearest week.

## Session 526: the state electricity profiles' capacity

Long end 1:30. Pulls: EIA's API v2, route `electricity/state-electricity-profiles/capability`, annual 1990 to 2024, at most 20 requests.

- Each state's capacity by energy source and producer type, as `eia_state_capacity_annual` (MW).
- Cross-check: 2024 against `eia860m_operating_generators` summed by state.

## Session 527: crude oil production by state

Long end 1:30. Pulls: EIA's API v2, route `petroleum/crd/crpdn`, monthly, at most 20 requests.

- Field production by state and the federal offshore areas, as `eia_crude_production_state_monthly`, in `kbbl` or `kbbl/d` as EIA gives them; a unit the vocabulary lacks waits for a ruling.
- Cross-check: the U.S. total against `eia_basin_production_monthly` or STEO's (`eia_steo_forecasts`) history.

## Session 528: natural gas production by state

Long end 1:30. Pulls: EIA's API v2, route `natural-gas/prod/sum`, monthly, at most 30 requests.

- Gross withdrawals and marketed production by state, as `eia_gas_production_state_monthly`, in `MMcf`.
- Cross-check: the U.S. marketed production against SEDS (`eia_seds_state_energy`) or STEO's history.

## Session 529: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-23_night_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (530, then past the old laptop's 542 if more are needed: check `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
