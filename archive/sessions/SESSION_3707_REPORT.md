# Session 3707 report: the three decision tools' cross-check tables

Energy Research Warehouse (ERW). Chain 208, session 8 of 20, portable laptop, 6 November 2026, about 22:33 to 22:47 UTC, while session 3706's gate ran its suite. Branch `wip/3701-sellable`, commit `954d993ad`.

- **`docs/methods/crosschecks/battery.md`, `generator.md`, `datacenter.md`**: each headline figure of the replication packages (22, 13 and 14) named, with a published figure, the source, the gap and a one-sentence reason, or said to have none.
- **Sources:** the notes' own "Cross-checks" rows (Lazard, the ATB, Modo Energy, E3, ERCOT's awards, EIA), plus two new ones:
  - ERCOT's market monitor's *2025 State of the Market Report* (read in session 3708's three requests): the fleet's revenue fell 37 percent in 2025; solar's capacity factor was 23.8 percent; the North zone's load-weighted prices for 2021 to 2025;
  - EIA's Texas industrial retail prices, from the ERW's table.
- **The largest gaps:**
  - battery, 2024: +92.68 USD per kW against Modo's fleet average; 2025: +58.04 against its nowcast;
  - datacenter: -34.62 USD per MWh against Texas industrial retail over November 2025 to July 2026; 2021: -70.91 against the North zone's load-weighted average (Uri's hours);
  - generator: coverage 0.67 against the ATB's 1.275.
- **No counterpart:** 14 of the battery's 22, 9 of the generator's 13 and 13 of the datacenter's 14 have no published counterpart, each named.
- **Test:** `tests/test_session3707.py` (7 tests, OK). Every field of the three `page_figures.json` is named in its file; every row is whole; the eGRID conversions are right; no dash.

## Decisions made without you

- Berkeley Lab's figures for ERCOT solar's market value were not read: the ruling on Berkeley Lab's terms is open (session 253).
- The battery's fall from 2024 to 2025 (-40.8 percent against the monitor's -37) is "not explained". The split of ours (ancillary -64.6 percent, energy -8.5) does not by itself explain it.

## For Samuel's ruling

- Should Berkeley Lab's public data files be read for ERCOT (solar's market value, LevelTen's ERCOT indices)? They would give the generator's price received, capture rate and breakeven PPA a counterpart. This is session 253's open question.
