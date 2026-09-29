Session 8 of the Energy Research Warehouse (ERW). Read CLAUDE.md, docs/datastandard.md, docs/coverage.md, docs/platform-tools.md, .claude/skills/erw-add-connector/SKILL.md and SESSION_7_REPORT.md first. Same non-negotiables: real data only, fail loudly, no em dashes, never delete existing files, commit after each task, do not push, do not stop to ask questions. Keys from .env and repository secrets; never print or commit one.

Human rulings on session 7's open questions: no equities connector until a Tiingo key exists (skip); the human will request permissions from ISO-NE, MISO, PJM, CARB, RGGI, EIA and ICE separately; rig counts are deferred, no manual files yet; IMF PortWatch chokepoint transits are wanted now and registered internal until terms are confirmed.

TASK 1. Run the full daily sequence end to end (PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh), fix anything that fails, and record row counts before and after. Commit.

TASK 2. The entities shape, first tables.
New connector warehouse/connectors/eia860.py. From the latest EIA-860M monthly generator inventory (the public xlsx on eia.gov, no key needed) build entities tables: eia860m_operating_generators (every operating generator: plant id, generator id, plant name, utility, state, county, lat, lon, technology and prime mover, energy source, nameplate MW, net summer MW, operating year, balancing authority, entity_type generator, status operating), eia860m_planned_generators (planned units with planned operation date, status per EIA's code), and eia860m_retired_generators (retired in the current and prior year, with retirement date). Keep EIA's own codes and add a readable technology label. Store the monthly vintage in every row. Add to run_daily.sh on a monthly cadence (run when the vintage on EIA's page changes). Extend the validator to enforce the entities shape (required columns, lat and lon ranges, MW numeric, status vocabulary) and record it in docs/datastandard.md.

TASK 3. Interconnection queues.
New connector warehouse/connectors/iso_queues.py using gridstatus's interconnection queue methods for ERCOT, CAISO, NYISO, MISO, SPP and ISO-NE (PJM too if the key exists). Entities table per ISO, <iso>_interconnection_queue: queue id, project name, county, state, POI or zone, fuel or technology, capacity MW, status, queue date, proposed and actual in-service dates, withdrawn date where present. Keep each ISO's own status vocabulary and add a harmonized status column (active, withdrawn, completed, suspended). Same completeness and provenance rules. Add to run_daily.sh weekly.

TASK 4. ERCOT history for the signature explorer.
Extend the ERCOT connector to add HB_HUBAVG to the hub list going forward, and backfill real-time and day-ahead hub prices from 2015-01-01 to the start of the current window from the NP6-785-ER yearly archives and the corresponding day-ahead archives, into the existing ERCOT tables through the merge writer. Confirm 35,040 quarter-hour intervals per hub per non-leap year (35,136 in leap years) and note any DST handling. This is the data behind the thesis peak-premium chart; the human's known values for HB_HUBAVG full-year 2015 versus 2025 are median 20.49 versus 25.68 and 99.9th percentile 583.96 versus 311.80 USD/MWh; compute the same and report whether they match, and if they do not, explain the difference rather than adjusting anything.

TASK 5. Remaining free monthly series.
From docs/price-sources.md, add as series tables under existing connectors: EIA retail electricity prices by state and sector (electricity/retail-sales, cents/kWh converted to USD/MWh with the conversion stated in the header), EIA first purchase prices (Mars, North Dakota), EIA imports by country, EIA PADD-to-PADD crude pipeline flows, and IMF PortWatch daily transits for the Strait of Hormuz, Suez and Panama (internal). Follow the file's routes and licenses.

TASK 6. Validate, coverage, package.
Every table passes; coverage regenerated with entities shape and sector; erw.fetch, filter and cite handle entities tables; tests cover every new table. Update docs/platform-tools.md status for tools 2, 3, 4, 5 and 7.

TASK 7. Report.
SESSION_8_REPORT.md in the usual format, including the ERCOT 2015 versus 2025 comparison and the row counts by shape (series, entities, events). Final commit.