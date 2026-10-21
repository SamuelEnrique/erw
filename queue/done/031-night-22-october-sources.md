# Chain of the night of 21 to 22 October 2026: sessions 555 to 561, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 554, the last session of `queue/done/030-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 555 to 561 were free in every queue file and branch when this was written. Each route below answered EIA's metadata call on 21 October (session 554).

Each source session follows chain 030's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/030-night-22-october-sources.md` hold, word for word, with its lessons. Two are added from chain 030:

- **EIA can give one series under two ids with one value** (session 550): keep a row repeated with the same value once, count it, and stop on two values.
- **A record EIA repeats on every field it gives, with two values, has no key** (session 553): do not invent one or average it. Report it, and take a route of the same subject that is unique.

Read `docs/state/note_2026-10-24_sources_data.md` and sessions 548 to 553's reports first.

## Session 555: petroleum supply and disposition

Long end 1:30. Pulls: EIA's API v2, route `petroleum/sum/snd`, monthly, at most 30 requests.

- The U.S. and PADD supply and disposition of crude oil and the main products (field production, refinery output, imports, exports, stock change, product supplied), as `eia_petroleum_snd_monthly`, in `kbbl` or `kbbl/d` as EIA gives them.
- Probe the processes and products first, and take only units the vocabulary holds.
- Cross-check: the U.S. crude field production against `eia_crude_production_state_monthly` (session 527).

## Session 556: petroleum products supplied

Long end 1:00. Pulls: EIA's API v2, route `petroleum/cons/psup`, monthly, at most 20 requests.

- Product supplied by product, U.S. and PADD, as `eia_product_supplied_monthly` (`kbbl/d`).
- Cross-check: against session 555's product supplied, where both hold it.

## Session 557: natural gas supply and disposition

Long end 1:00. Pulls: EIA's API v2, route `natural-gas/sum/snd`, monthly, at most 20 requests.

- The U.S. and state supply and disposition of natural gas, as `eia_gas_snd_monthly` (`MMcf`).
- Cross-check: against sessions 518 and 528's consumption and production.

## Session 558: densified biomass (wood pellets)

Long end 1:30. Pulls: EIA's API v2, routes `densified-biomass/*` (sales and price by region, production, capacity, inventories), at most 20 requests.

- Each route's figures in units the vocabulary holds (prices in USD per short ton, capacity, counts). Quantities in short tons wait for the unit (a ruling already asked: sessions 490 and 519).
- One table a route the probe finds worth it, or one table with the route as a column. The session decides and says why.
- Cross-check: the regions sum to the U.S.

## Session 559: petroleum stocks by type

Long end 1:00. Pulls: EIA's API v2, route `petroleum/stoc/ts`, monthly, at most 20 requests.

- Stocks by type (refinery, tank farm and pipeline, bulk terminal, SPR) and product, U.S. and PADD, as `eia_petroleum_stocks_monthly` (`kbbl`).
- Cross-check: the month's end against `eia_petroleum_stocks_weekly`'s nearest week.

## Session 560: another public source

Long end 1:30. Pulls: at most 20 requests.

- A source the ERW does not hold, chosen by the session from EIA's routes (the route list from `https://api.eia.gov/v2/`, with its key) or another U.S. federal publisher whose robots file and terms allow it.
- Say why it was chosen, and follow the same form.

## Session 561: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-24_night_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (562 on: check `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
