# Chain of the night of 21 to 22 October 2026: sessions 570 to 576, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 561, the last session of `queue/done/031-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 570 to 576 were free in every queue file and branch when this was written. It was first pushed as 032 with sessions 562 to 568, and renumbered at once: the code machine's `queue/next/032-night-22-october-code-563.md` and its `wip/562-land-023` hold 562 and 563, and 564 to 569 are left for it. The routes below are in EIA's route lists read on 21 October (sessions 519, 558 and 560).

Each source session follows chain 031's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/031-night-22-october-sources.md` hold, word for word, with its lessons. Two are added from chain 031:

- **An edit to a file with Windows line endings must match them** (session 555): convert the text searched for as well as the text written.
- **When EIA's API answers 502s, take another session's route and come back** (sessions 556 and 557). Never fill a page that did not come.

Read `docs/state/note_2026-10-24_night_sources_data.md` and sessions 555 to 560's reports first.

## Session 570: advanced meters by state

Long end 1:00. Pulls: EIA's API v2, route `electricity/state-electricity-profiles/meters`, annual, at most 10 requests.

- Advanced (AMI) and automated (AMR) meters by state and sector, as `eia_meters_state_annual` (`count`).
- Cross-check: the sectors and states sum to their totals; the residential meters against `eia861_utility_sales`' residential customers by state, as a share.

## Session 571: power plants' CO2 by state and fuel

Long end 1:00. Pulls: EIA's API v2, route `electricity/state-electricity-profiles/emissions-by-state-by-fuel`, annual, at most 10 requests.

- CO2 by state, fuel and producer type, as `eia_power_co2_state_annual` (`tCO2`). EIA's SO2 and NOx in metric tons wait for a unit (put the unit's addition under "For Samuel's ruling").
- Cross-check: against `eia_co2_state_annual`'s electric power sector (session 530).

## Session 572: coal prices by rank

Long end 1:00. Pulls: EIA's API v2, route `coal/price-by-rank`, annual, at most 10 requests.

- The average sales price of coal by state and rank (bituminous, subbituminous, lignite, anthracite), as `eia_coal_price_rank_annual` (`USD/short_ton`).
- Cross-check: against `eia_coal_prices_annual` (session 519).

## Session 573: coal exports' and imports' prices

Long end 1:00. Pulls: EIA's API v2, route `coal/exports-imports-quantity-price`, at most 20 requests.

- The price of coal exports and imports by country and rank, as `eia_coal_trade_price` (`USD/short_ton`). Quantities wait for the tonnage unit.
- Cross-check: the exports' price against `eia_coal_prices_annual`'s U.S. open market price, as an order of magnitude.

## Session 574: petroleum supply and disposition, the other products

Long end 1:30. Pulls: at most 30 requests.

- Add to `eia_petroleum_snd_monthly` (session 555) the products it left out, from 2015 on, within the ceiling (split by product into two runs if needed, written together as one snapshot).
- The table gains rows: replace its release row.
- Cross-check: the products against EP00, the total.

## Session 575: wood pellets' feedstock costs

Long end 1:00. Pulls: EIA's API v2, route `densified-biomass/feedstocks-and-cost`, at most 10 requests.

- The cost of feedstocks by type, in `USD/short_ton` (quantities wait for the unit), added to `eia_wood_pellets_monthly` (session 558) as another route, or as its own table if the shape differs.
- Cross-check: the cost against the pellets' domestic price.

## Session 576: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-25_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (577 on: check `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
