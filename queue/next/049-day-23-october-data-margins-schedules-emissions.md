# Chain of the day of 23 October 2026: sessions 895 to 908, data machine (lab-desktop), unattended: reserve margins for every grid, EIA-860's and EIA-923's other schedules, power plants' emissions, offshore wind leases, an ERCOT node's county

machine: data

Written by session 881, the first session of `queue/done/048-night-23-october-data-utility-files-products.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). Sessions 895 to 908 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 894 of chain 048 updates this file if its results change what it should hold. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked alone and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/c045/write_table.sh`, `runs/c045/finish_table.sh` (or `finish_replace.sh`), `runs/c046/write_derived_pair.sh`, `runs/c047/write_pair.sh`, `runs/s622/resolve_ours_plus.py`, `runs/c046/take_theirs.py`, `runs/c047/replace_tables.py`, `runs/c045/keep_newest_row.py` and `runs/c045/method_cells.sh` on the data machine, each given the chain's worktree (`WT=`, `WTN=`);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/048-night-23-october-data-utility-files-products.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**: no session asks either path until the owner rules.
- **EIA's robots file disallows `/archive/`**: a file there is read only from a zip already saved.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own** (one row a publisher, `test_session205`).
- **A table that a page reads is never rewritten to add rows from another file**: a new file of the same form is a table of its own (session 853).
- **A request cap on the Redivis uploader stops between tables, never inside one** (session 880).
- **Session 895 begins by writing `queue/next/050-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 909), commits it alone and pushes it to main before any other work; session 908 updates it.

Read first: chain 048's note (`docs/state/note_2026-10-28_data.md`, written by session 894), sessions 881 to 894's reports, `docs/state/note_2026-10-27_data.md`, `docs/reviews/siting-gaps.md`.

## Session 895: reserve margins for every grid (EIA's Electric Power Annual, NERC assessment areas)

Long end 1:30. Pulls: EIA, at most 10 requests. The siting gaps' "Reserve margins: open" (session 731): the Electric Power Annual's tables of noncoincident peak demand, net internal demand, capacity resources and capacity margin by NERC assessment area, summer and winter, actual and projected, a series table; cross-check: ERCOT's area against `ercot_cdr_reserve_margins` for the same years (the two define the margin differently; say how).

## Session 896: EIA-860's environmental and multifuel schedules

Long end 1:30. Pulls: none (`eia8602025.zip` under `warehouse/raw/eia860_plants/`, saved by session 873). The schedules chain 048's session 885 did not take: the environmental associations and equipment (`6_1_EnviroAssoc`, `6_2_EnviroEquip`: each generator's boilers, scrubbers, stacks and controls) and the multifuel generators (`3_5_Multifuel`), each as a table of its own; cross-check against `eia860m_operating_generators` by plant and generator.

## Session 897: each plant's monthly generation and fuel (EIA-923)

Long end 1:30. Pulls: EIA, at most 4 requests (none if the zip behind `eia923_plant_fuel_annual` is saved). Schedules 3 and 4's monthly columns, by plant, prime mover and fuel, from 2020, a series table of its own beside `eia923_plant_fuel_annual`; cross-check: the months summed against the annual table.

## Session 898: power plants' emissions by unit (EPA's Clean Air Markets)

Long end 1:30. Pulls: at most 20 requests. EPA's CAMPD bulk files (annual, then monthly if the ceiling allows) of each unit's SO2, NOx, CO2 and heat input; robots and terms first (EPA's host and its API's); a key from api.data.gov only if the bulk files need none, else the session stops and says so. Cross-check: the units summed by state against `eia_power_co2_state_annual`.

## Session 899: the natural gas pipeline projects (EIA)

Long end 1:30. Pulls: EIA, at most 6 requests. EIA's natural gas pipeline projects tracker (each project's capacity, miles, cost, states, status and dates), an events table; cross-check: the projects in service by year against `eia_gas_interstate_annual`'s capacity changes where they overlap.

## Session 900: offshore wind leases (BOEM)

Long end 1:30. Pulls: at most 15 requests. BOEM's renewable energy lease list (lease, lessee, area, state, date, status), an entities table, robots and terms first; cross-check: the leases named against the offshore wind projects in `eia860m_planned_generators`.

## Session 901: an ERCOT node's county and zone (a derived table)

Long end 1:30. Pulls: none. The siting gaps' "A node's zone, hub, wires utility and county" (session 733): `ercot_cdr_units` (session 872) and `eia860_plants_annual` (session 873, with each plant's wires owner) joined to the resource nodes of `node_basis_daily` by unit code where they match, the match rule and its misses counted, in `warehouse/derived/` with a method note; no guessed match is written.

## Session 902: the licenses' fourth round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 048 did not reach, EPA's and BOEM's first if sessions 898 and 900 found no terms page.

## Sessions 903 and 904: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 905: method notes for this chain's tables

Long end 1:00. Pulls: none.

## Session 906: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 100 requests. This chain's public tables, uploaded with the true replace and the proof, in whole tables under the cap; any table chain 048 left out; `--reconcile`; the release note extended. Nothing released.

## Session 907: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As chain 043's session 682: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 908: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-29_data.md`, in session 683's form.
2. `queue/next/050-*.md` (written by session 895) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
