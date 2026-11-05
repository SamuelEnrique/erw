# EIA state electricity profiles: each state's net summer capacity by producer type and energy source, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_state_capacity_annual`

Connector: `warehouse/connectors/eia_state_capacity.py` (session 526).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, net summer capacity, read through EIA's API v2, route `electricity/state-electricity-profiles/capability`.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/capability/data/?frequency=annual&data[]=capability&start=1990`, in pages of 5,000 sorted by year, state, producer type and energy source. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 20 requests a run, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_state_capacity/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 20).

## Vintage and revision rule

Years 1990 to 2024: 56,719 records of EIA's, every one with a value. The start year is fixed at 1990 in the code; the API returns every later year it holds. The table is written by `write_snapshot`: each run replaces the whole table. The connector checks that the records read equal EIA's count, and stops if they do not.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_state_capacity:<state>:<producertypeid>:<energysourceid>`, EIA's codes. The 50 states, DC and US (52 areas).
  - Producer types: EU (electric utilities), IPP (independent power producers), TOT (both).
  - Energy sources: ALL; a fuel (COL, NG, PET, NUC, HYC, HPS pumped storage, WND, SOL, GEO, WOO, OBM, OOG, OT, BAT); or a part of one (NGCC, NGGT, NGIC, NGST, NGOTH within NG; PETGT, PETIC, PETST, PETOTH within PET; SOLPV, SOLTH within SOL).
- `variable` `net_summer_capacity`, unit MW (EIA's megawatts; any other unit stops the run).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` EIA's descriptions of state, producer type and source.

A sum over sources takes one level only (fuels or their parts) and leaves ALL and TOT out. A record with no state, producer type or source stops the run, and so does a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 526's report, an order of magnitude only: each state's 2024 net summer capacity (both producer types, all sources) against `eia860m_operating_generators`' nameplate summed by state. 51 areas, a median ratio of 0.895 (middle half 0.854 to 0.917); the U.S. 1,230,416 MW against 1,417,946 MW. Net summer capacity runs below nameplate, and the fleet has grown since 2024.

## What it does not hold

- The parts of a fuel before 2008: NGCC, NGGT and the other prime-mover parts of natural gas, petroleum and solar begin in 2008. BAT (batteries) begins in 2010.
- Any producer type other than EIA's three codes EU, IPP and TOT.
- Nameplate capacity, plants or generators: the figure is EIA's state net summer capacity.
- A blank has no row; nothing is filled.
