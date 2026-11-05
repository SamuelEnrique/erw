# NYISO load scheduled in the day-ahead market, by hour, system-wide (P-30)

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table first written in session 136 (approved pull).

Tables: `nyiso_dam_cleared_energy`

## Publisher and address

New York Independent System Operator (NYISO), report P-30, Day-Ahead Market Daily Energy Report (`http://mis.nyiso.com/public/P-30list.htm`): a zip a month, `http://mis.nyiso.com/public/csv/damenergy/<YYYYMM>01DAM_energy_rep_csv.zip`, one CSV a day inside. Source id `nyiso:damenergy`. Raw files under `warehouse/raw/nyiso_dam_cleared/`.

Connector: `warehouse/connectors/nyiso_dam_cleared.py` (session 136), with the frame shared by the five cleared-energy connectors, `warehouse/connectors/dam_cleared.py`: by default the last 14 days, a zip a calendar month (this month and the last fresh, earlier months once), a ceiling of 5,000 rows read a run, and a run fails if the newest hour is more than 5 days old.

Schedule: weekly, on Saturdays (UTC), in the supply step of `warehouse/run_daily.sh` (`bash warehouse/refresh_supply.sh`, `SUPPLY=1` on any other day), which runs the five cleared-energy connectors under the 15-minute pull budget and `warehouse/health.py`; the daily run is `.github/workflows/daily-prices.yml`. A run asks nothing while NYISO is in `paused_sources.csv`.

## Vintage and revision

The header's last run is `20261010T150004Z`: "Rows read from the operator in this run: 1,025 ... Hours written by this run: 984, 2026-09-01T04:00:00Z to 2026-10-12T03:00:00Z", "96 new, 888 replacing ..., 8760 rows are kept from earlier runs"; then "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". `retrieved_at` runs from 2026-10-06T20:22:03Z to 2026-10-10T15:00:07Z (14 values, one per monthly zip); `vintage` is empty. The table merges, so it keeps months the operator's window no longer covers.

## Shape and variables

Series, 9,744 rows, one an hour: entity `nyiso:system`, variable `dam_cleared_energy`, value NYISO's column "Total Load Scheduled" (bid, bilateral and price-capped load together, as NYISO totals them), `unit` MW (over the hour), `freq` PT1H, `geo` US-NY, `market` nyiso_dam, `node` "Total Load Scheduled". Lowest 12,268.2 MW, highest 31,245.5, mean 17,711.10.

## Placing values in time, and what is filled

NYISO's "Date Hour" is the hour's start in Eastern time; the connector places it in America/New_York (`ambiguous="infer"`) and converts to UTC. The file's "Total" line is the day's sum and is not a row; the report's other columns are read and not written. An hour the operator does not give is not written; nothing is filled.

## License

The header: "License: public, with a caution (sessions 65 and 85). NYISO's legal notice grants no license and forbids republishing "any image or video on this website as a stand-alone file", which names images and video, not data (https://www.nyiso.com/legal-notice, read 6 October 2026). A person can rule otherwise." A person has since ruled: `docs/licenses.md` gives verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled". That ruling of 21 October 2026, which governs NYISO's tables (`docs/methods/nyiso_dam_zone_prices.md`), governs this table's standing whatever its header says.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/nyiso_dam_cleared_energy.csv`, read past its 12 header lines (scripts in `runs/c098/s2214/`).

- 9,744 rows, `ts_utc` from 2025-09-01T04:00:00Z to 2026-10-12T03:00:00Z, as the header states: every hour of the span (406 Eastern days: 404 of 24 hours, 2025-11-02 of 25, 2026-03-08 of 23); no hour twice.
- Against actual load (`nyiso_zone_load_hourly`, its 11 zones summed): over 9,706 hours the day-ahead scheduled load is a median 1.0291 of the load (10th percentile 0.9826, 90th 1.0926).

## Where the description and the data disagree

1. **The license line.** The header and docstring call the table public, with a caution, and leave a ruling to a person; the license record has ruled ("needs written permission", license needed from 2026-10-21), and the weekly supply step still runs the connector.

Recorded, not changed in session 2214: the license record (the ruling of 21 October 2026, license needed) governs the table's standing whatever its header says, as for NYISO's other tables; the release package holds the table whole ("license needed from 2026-10-21"), and whether the weekly step keeps pulling is the owner's (the license question of `docs/licenses.md`).

## What it does not hold

- Zones, offers, generation, imports, exports and virtual bids (read and not written), and real-time quantities.

## Found by chain 097's session 2180

Chain 097's session 2180 described this table on its own branch while chain 098's session 2214 wrote this note; at chain 097's merge (session 2189) this note is kept and the other's findings, read against the same connector, are added here as written:

- The header and `coverage.csv` say public; `license_verdicts.csv`, `license_status.csv` and `docs/licenses.md` say NYISO's permission is needed (license needed from 21 October 2026, ERW verdict unsettled). The connector keeps its weekly step in `warehouse/refresh_supply.sh`, while NYISO's note in `license_verdicts.csv` records that `nyiso_as_prices` gets no scheduled step until this license is answered (session 308).
- The docstring and `docs/methods/supply_and_trade.md` disagree on what Total Load Scheduled counts: the docstring lists the virtual bids among the columns "read and not written"; the method note says the total includes cleared virtual bids.
- Within a month's zip, `pull()` gathers the days' hours in one dictionary (`hours.update`): an hour given by two daily files keeps the later file's value without a word, and the run's check for a key given twice sees only what is left.
- The docstring is silent on cells that are not numbers; the code drops them without a count.
- The refresh is weekly, on Saturdays, but `run_status.csv` holds only the run of Saturday 10 October 2026 for this table, and no row of any connector dated 15, 16 or 17 October. The copy on the data machine ends on 11 October 2026 (Eastern).
