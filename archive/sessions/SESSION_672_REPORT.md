# Session 672 report: reserve margins (not pulled) and each grid's peak against its capacity

22 October 2026, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **First half, NERC's reserve margins: not pulled.** NERC's terms page loads its text by script and could not be read (session 666); the chain's rule makes that a refusal.
- **Second half: `grid_peak_vs_capacity` is written (56 rows)**: each ISO's 2025 peak hour (`eia930_demand_growth`) against the net summer capacity of the generators EIA-860M places in its balancing authority. Peak to capacity: CAISO 0.49, ERCOT 0.51, SPP 0.56, MISO 0.62, ISO-NE 0.73, NYISO 0.74, PJM 0.76. Validated, archived, in coverage (derived; sectors power and capacity), method `docs/methods/grid_peak_vs_capacity.md`.
- **No state is mapped to a grid:** EIA-860M names each generator's balancing authority, so the capacity is summed by it, and the states each grid shares with another are named (`x_split_states`).
- **Not a reserve margin:** solar, wind and storage count at their summer ratings; the note says so beside every figure.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.nerc.com | 0 of 5 | not asked: its terms could not be read |

## Decisions made without you

- Capacity by EIA-860M's balancing authority field in place of the chain's state mapping: exact where a mapping would split states by guess. The states that split are still named.
- `capacity_mw` counts the generators in the 2026-08 list that began operating by the end of 2025; one retired since is not in the list, which the note says.

## For Samuel's ruling

- NERC's terms, read in a browser, before the LTRA's reserve margins are pulled.

## Files

- New: `warehouse/derived/grid_peak_vs_capacity.py`, `docs/methods/grid_peak_vs_capacity.md`, this report. Changed: the metadata and release files as in session 667; `tests/test_session671.py` holds its test.
