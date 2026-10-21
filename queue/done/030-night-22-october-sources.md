# Chain of the night of 21 to 22 October 2026: sessions 548 to 554, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 547, the last session of `queue/done/029-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 548 to 554 were free in every queue file and branch when this was written. Each route below answered EIA's metadata call on 21 October (session 547).

Each source session follows chain 029's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/029-night-22-october-sources.md` hold, word for word, with its lessons. Read `docs/state/note_2026-10-23_late_sources_data.md` and sessions 530 and 543 to 546's reports first.

## Session 548: nuclear outages by reactor, 2015 on

Long end 1:30. Pulls: EIA's API v2, route `nuclear-outages/generator-nuclear-outages`, daily, at most 100 requests.

- Each reactor's capacity, outage and outage share, as `eia_nuclear_outages_generator_daily`, in `eia_nuclear_outages_facility.py`'s form: two windows, read until a short page, no day missing.
- Probe the row count first. If 2015 on is beyond the ceiling, take as many whole years from the newest back as fit, and leave the rest to 549.
- Cross-check: the reactors summed by plant against `eia_nuclear_outages_facility_daily`.

## Session 549: nuclear outages by reactor, the earlier years

Long end 1:30. Pulls: at most 100 requests. The years 548 left, written with 548's in one snapshot. Cross-check as 548.

## Session 550: interstate natural gas movements

Long end 1:30. Pulls: EIA's API v2, route `natural-gas/move/ist`, annual, at most 20 requests.

- Each state's receipts from and deliveries to its neighbours, and its international flows, as `eia_gas_interstate_annual` (MMcf).
- Probe the processes first. A movement between two states must name both, in the entity or the node.
- Cross-check: each state's net receipts against its consumption less its production (sessions 518 and 528), as an order of magnitude.

## Session 551: crude oil proved reserves by state

Long end 1:00. Pulls: EIA's API v2, route `petroleum/crd/pres`, annual, at most 10 requests.

- Proved reserves, and their changes if EIA gives them, by state and area, as `eia_crude_reserves_annual` in `kbbl`: EIA's million barrels times 1,000.
- Cross-check: the areas sum to the U.S.

## Session 552: natural gas proved reserves by state

Long end 1:00. Pulls: EIA's API v2, route `natural-gas/enr/dry`, annual, at most 10 requests.

- Dry natural gas proved reserves by state, as `eia_gas_reserves_annual`, in `bcf`.
- Cross-check: the areas sum to the U.S.

## Session 553: coal receipts' prices at power plants

Long end 1:30. Pulls: EIA's API v2, route `coal/shipments/receipts`, annual, at most 30 requests.

- The average delivered price of coal by plant state, mine state and mine type, as `eia_coal_receipts_price_annual`, in `USD/short_ton`.
- Quantities in short tons and heat content in MMBtu per ton wait for units the vocabulary does not hold.
- Cross-check: against `eia_power_plant_fuel_costs`' coal cost per short ton by state.

## Session 554: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-24_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (555 on: check `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
