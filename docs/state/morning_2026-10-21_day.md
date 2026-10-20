# The morning note, 21 October 2026, after the day chain

Energy Research Warehouse (ERW), session 380, for Samuel. The data machine's chain of 20 October, day (sessions 373 to 380, `queue/done/011-day-20-october-data.md`), unattended on lab-desktop, from about 17:00 UTC on 20 October to this note's push. Model spend USD 0 in every session. The night chain's note, before this one: [`docs/state/morning_2026-10-21.md`](morning_2026-10-21.md).

## Read these first

- **This machine is whole again**: 71 tables restored from the archive (session 373), 8 more the load found older here (session 374), and the third machine's two tables put in place. `scripts/sync.py --check`: 156 current at 17:13 UTC, **201 current** at 20:19 UTC. 26 of the 71, and all 8, now hold the archive's revisions; their row counts did not move (the daily run's own sync had already caught them up by rows).
- **The live set's sources check is green** (session 374): Supabase 338, `sources.csv` 338. Eleven of the 12 missing rows came with the code machine's landing of sessions 345 to 347; `erw:iso_queue_statistics` was written from Supabase's own row, as **internal** (the live table takes only public or internal, and `docs/licenses.md` does not name the table yet). **`load.py` still exits 1**: 31 tables refused by the loader's guard as "older than the live copy", because a copy restored from the archive carries older `retrieved_at` stamps than GitHub's run loaded. The three read are equal value for value; nothing was rolled back. One is a real difference: `ferc_eqr_contracts`, 452 rows fewer here.
- **The release package is complete and checked** (session 375): 136 tables in v1, 41 held for a license, **`node_basis_daily` "held: Redivis storage"**; spliced, not rewritten, since a whole rewrite after the restore would give 63 tables the restore's note as their description.
- **The real-time node prices are kept each day** (session 376, `dm_node_rt`): real time held 28 September to 19 October, 22 days (20 before; 8 October was missing because ERCOT posted one interval twice). 0 requests: the step reads the files the node prices' own pull saves.
- **This machine's daily run of 20 October did not finish**: it ended at 18:06 UTC with 0xC000013A in `dm_battery_scenario_steps` and held the lock until it lapsed at 20:00 UTC (not broken). Its page files are uncommitted in the main checkout, with its metadata set aside in a named stash and applied back (session 374); tomorrow's run rebuilds and commits them.

## What each session landed

| Session | Landed |
|---|---|
| 373 | 71 tables of `docs/state/archive_proof_2026-10-20.csv` the archive's latest run, each validated, coverage rows rebuilt with `--only` (21 changed); rows before and after in its report |
| 374 | `erw:iso_queue_statistics` in `sources.csv`; 8 more tables restored; `nlr_jedi_multipliers` and `impact_tax_rules` in place; the live set loaded (73 matched, 31 refused as older, 0 differences on 25 pages) |
| 375 | The release v1 package spliced: `node_basis_daily` held, three publishers filled; the steps and the runbook's "The draft on 20 October 2026" brought to today |
| 376 | `dm_node_rt` in the daily run; one interval read once when ERCOT posts it twice; `table_stores.py --no-redivis` |
| 377 | A root cause for every failure of 6 to 20 October (19 causes; 17 fixed on main, 1 by 374, 1 waiting: the storage); a refusal for storage is a skip; "One alert policy", a draft for your ruling, in `docs/machines.md` |
| 378 | One verdict word a table in `docs/licenses.md` (130 public, 33 internal, 48 unsettled of 211 after the merge); four permission letters drafted, not sent; the publishers' prices (none stated on any page read) |
| 379 | (a) not run: the health gate was closed (`state_generation_mix_monthly`'s failure of 00:50 UTC); the task stays in `queue/todo/`. (b) ERCOT's 2021 4CP intervals not found in the Wayback Machine |
| 380 | This note, and `queue/next/013-night-20-october-data.md` |

Sessions 373 to 379 landed together on `task/373-379-day` (pushed 21:03 UTC, `66a45b60`; checks passed, run 39497170176; merged as `288ee9a9`; deployed 21:14 UTC): snapshots `s373-379-land-before` and `-after`, **0 differences on 25 pages**, expected. Session 380 lands this note on `task/380-morning`; `queue/next/013-night-20-october-data.md` went to main on its own.

## Pulls against their ceilings

| Session | Pull | Used | Ceiling |
|---|---|---|---|
| 373 | the ERW archive's bucket only | 0 publishers | 0 |
| 374 | none (the bucket, and Supabase's own tables read) | 0 | 0 |
| 375 | none (not even Redivis's metadata) | 0 | Redivis metadata reads |
| 376 | ERCOT | 0 | 40 |
| 377 | none (Supabase's health table read) | 0 | 0 |
| 378 | NYISO, SPP, PJM (the terms are in the record) | 0 | 2 each; MISO paused, 0 |
| 379 | CAISO 0 (stopped at its gate); the Wayback Machine 6 | 6 | 6 and 6 |
| 380 | none | 0 | 0 |

Nothing was asked of a paused publisher, and no new host.

## Decisions made without you (one line each; the reasons are in each report)

- 373: the restore waited for the lock; a staged copy checked against the run log at the swap and restored again when it does not match; old copies kept in `runs/s373_before/`.
- 374: `internal` for `erw:iso_queue_statistics` (no "unsettled" in the live table); no `--allow-older`; the 8 older tables restored before the load; main pulled through a named stash.
- 375: a splice of four rows; `nyiso_load_queue` kept public in coverage as main had it, against the builder's computation, until you rule.
- 376: rebuilt whole from the saved files; the later of two postings read; no Redivis step for the three tables.
- 377: a refusal for storage is a skip; a day's root causes kept across the daily rewrite.
- 378: "unsettled" covers the license-needed tables; `ercot_node_prices_hourly` ruled internal by its header; no request made.
- 379: (a)'s task file left in `queue/todo/`.

## Waiting for you, highest value first

1. **Redivis storage (10 GB, full)**: a paid tier, or tables out of the draft. `node_basis_daily` is "held" in v1 until then; every growing table's Redivis step is a skip, not a failure (session 377). Session 385 sets out the draft's largest tables for this.
2. **The four permission letters** (`docs/reviews/licenses/`): send, change or hold; the brackets to fill.
3. **`nyiso_load_queue`**: coverage says public, `sources.csv` (your ruling of 7 October) internal. Ruling internal takes it out of the license-needed count (41 to 40) with two tests and the site's `license_status.json` (session 375).
4. **The loader's guard**: refuse on values, not only on `retrieved_at`, so a copy restored from the archive loads when it equals the live one (session 374; session 384 drafts it). And `ferc_eqr_contracts`, 452 rows fewer here than live.
5. **"One alert policy"**, the draft in `docs/machines.md` (session 377).
6. **Smaller**: `restore_tables.py`'s note as a restored table's first header line (session 375); 2021's 4CP intervals from ERCOT by request (sessions 359 and 379).

## The other machines

- **The code machine** landed sessions 365 and 366 today (`task/365-366`, with the third machine's sessions 345 to 347, `/impact`) and wrote its night chain, `queue/next/014-night-20-october-code.md` (sessions 381 to 383). Sessions 367 to 371 wait on `wip/367-372-day` (its note, `docs/state/review_2026-10-20_day_code.md`, is on that branch), and `wip/367-map-land` is pushed.
- **The third machine's `wip/348-map`** is not on main: it brings `iso_queue_statistics` into coverage and the release package, and its own `sources.csv` row (public) for the one this chain wrote as internal.
- **This machine's next chain**: `queue/next/013-night-20-october-data.md`, sessions 384 to 386 (the green streak's remaining causes, the dataset prepared for the move under Ben's organization, the note), written by session 380 so that it does not idle.
