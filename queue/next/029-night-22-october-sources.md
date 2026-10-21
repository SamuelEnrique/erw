# Chain of the night of 21 to 22 October 2026: sessions 530 and 543 to 547, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 529, the last session of `queue/done/028-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Session 530 was free, 531 to 542 are the old laptop's chain 024 (`queue/done/024-night-21-october-code.md`), and 543 to 547 were free in every queue file and branch when this was written. Each route below answered EIA's metadata call on 21 October (session 529).

Each source session follows chain 028's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check against a table the ERW holds;
- `runs/write_table.sh` and `runs/finish_table.sh` on the data machine; `runs/union_resolve.py` when two sessions' metadata meet; `runs/release_replace.py` for a table that gains rows;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/028-night-22-october-sources.md` hold, word for word, with its lessons. Three are added from chain 028:

- **An area code can hold two series** (Alaska and its North Slope): key on EIA's series stem where the area repeats (session 527).
- **EIA's aggregate rows ("Other States", R98) repeat their members**: name them in the header and leave them out of a sum (session 528).
- **A trial's own clean-up must not remove a file main tracks** (session 523): copy a connector in for a run only through `runs/write_table.sh`, or restore it with `git checkout` after.

Read `docs/state/note_2026-10-23_night_sources_data.md` and sessions 523 to 528's reports first.

## Session 530: CO2 emissions by state, sector and fuel

Long end 1:30. Pulls: EIA's API v2, route `co2-emissions/co2-emissions-aggregates`, annual 1970 to 2022, at most 20 requests.

- Each state's energy-related CO2 by sector and fuel, as `eia_co2_state_annual`, in `tCO2` (EIA's million metric tons times 1,000,000).
- Cross-check: the electric power sector's CO2 by state against `epa_ghgrp_power_co2` summed by state for 2010 to 2022 (an order of magnitude: GHGRP covers large plants only).

## Session 543: refinery utilization and inputs, weekly

Long end 1:30. Pulls: EIA's API v2, route `petroleum/pnp/wiup`, weekly, at most 20 requests.

- The U.S. and PADD refinery crude inputs, gross inputs, operable capacity and utilization, as `eia_refinery_weekly`. Units the vocabulary holds (`kbbl/d`, `ratio` for a percent divided by 100); any other unit waits for a ruling.
- Cross-check: the U.S. crude inputs against `eia_petroleum_supply_weekly` where it holds them.

## Session 544: each state's electricity source and disposition

Long end 1:30. Pulls: EIA's API v2, route `electricity/state-electricity-profiles/source-disposition`, annual 1990 to 2024, at most 20 requests.

- Each state's generation, imports, sales, losses and direct use, as `eia_state_source_disposition_annual` (MWh).
- Cross-check: the states' generation against `eia_state_generation_monthly` summed by year.

## Session 545: net metering by state

Long end 1:00. Pulls: EIA's API v2, route `electricity/state-electricity-profiles/net-metering`, annual 2013 to 2024, at most 10 requests.

- Each state's net-metered capacity and customers by technology and sector, as `eia_net_metering_state_annual` (MW, count).
- Cross-check: the 2024 total against `eia861m_utility_sales_monthly`'s behind-the-meter owners as an order of magnitude, or against EIA-861's net metering file if the ERW holds it.

## Session 546: SEDS' other series

Long end 1:30. Pulls: EIA's API v2, route `seds`, at most 20 requests.

- Add to `eia_seds_state_energy` (session 507) the series a reader of power and gas needs and that it lacks: each sector's electricity and natural gas consumption, and electricity's and natural gas's prices by sector. Probe the series ids first, and keep units the vocabulary holds.
- The table gains rows: replace its release row.
- Cross-check against `eia_gas_consumption_state_monthly` (session 518) and `eia861_utility_sales` by state and year.

## Session 547: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-23_late_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (548 on: check `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
