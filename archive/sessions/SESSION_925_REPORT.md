# Session 925 report: the reactor fleet (NRC)

23 October 2026, from 09:51 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: 6 requests of 15 (the NRC's robots file, asked alone and read first; the List of Power Reactor Units; the NRC Data page; the operating and decommissioning reactors datasets; the connector's list).

## Read these first

- **One table written, validated, archived, in coverage (sectors power and uranium, public), in the release package, both holds:** `nrc_power_reactors`, 130 reactor units, an entities table beside `nrc_reactor_status`:
  - the 95 operating units of the NRC's list as read today (docket, license, reactor type, place, owner and operator, NRC region), with the NRC operating reactors dataset's parent company, licensee, containment and steam supply types, architect-engineer and constructor, construction permit, operating license, commercial operation, renewed and subsequent renewed licenses, license expiry, licensed thermal power and capacity (95,869 MWe for the 93 units it holds);
  - the 35 units in decommissioning, from the NRC's decommissioning dataset (status `retired`, with their shutdown, license termination, decommissioning method and estimated closure).
- **The datasets are older than the list:** their "Year of Update" is 2022 (last modified September 2025). Palisades and Vogtle 4 are on the list but not in the operating dataset, so their dataset columns are empty; a license the dataset shows expiring in the 2020s may have been renewed since (7 units). The header names the datasets' year and the two units.
- **The cross-checks:**
  - **Every operating unit is a unit of `nrc_reactor_status`'s last day (22 October 2026):** 95 and 95, matched by name, four of them spelled apart (Harris 1 and Shearon Harris 1, LaSalle and La Salle 1 and 2, River Bend Station 1 and River Bend 1).
  - **Capacity against EIA-860M's nuclear generators:** 95,869 MWe for 93 units in the NRC dataset of 2022, against 98,423 MW of net summer capacity (103,698 nameplate) for EIA-860M's 96 generators today; the dataset, of 2022, holds neither Vogtle 4 nor Palisades.
- Two date cells of the dataset hold "Application Withdrawn": kept as given and counted in the header.

## Decisions made without you

- **The list for who and where, the datasets for the dates and power,** each column named by its source and the datasets' year carried in `x_dataset_year`.
- **The datasets' derived columns not taken** (reactor age, time and share of license remaining, all as of 2022) **nor their capacity factors** (headed "Percent", given as fractions; EIA's tables hold the generation).
- **`entity_type` `generator`** for a reactor unit, as `ercot_node_places` uses it for a resource.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nrc_reactors.py`, `tests/test_session925.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s925/`, `runs/license_reads/s925/`, `runs/s925*`, `warehouse/raw/nrc_reactors/`.
