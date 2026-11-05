# Session 2516 report: Norway's hydropower reservoirs a week, 1995 to 2026 (NVE's reservoir statistics), the third own choice, public

24 October 2026, about 17:57 to 18:01 UTC for the reads and the connector; the table written under the data lock at 18:22 UTC. On lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2516.out`). Model spend USD 0. Pulls: 8 requests of 20 (7 by the probe, 1 by a fetch).

## Read these first

- **First try not reachable:** UNdata's Energy Statistics Database. data.un.org has no robots file (read 923), and its old download handler now answers HTTP 404 (one fetch).
- **Why NVE:** Norway's hydropower reservoirs are the main store of the Nordic power system's energy; the ERW held Statnett's production and consumption, not the reservoirs.
- **The Norwegian Water Resources and Energy Directorate (NVE):**
  - biapi.nve.no and api.nve.no have no robots file (reads 924, 928); www.nve.no asks a crawl delay of 20 seconds, kept (read 926);
  - its reservoir statistics page (read 927) links the API's documentation (read 929);
  - the API (read 925) gave 14,931 weekly records, 1995 to 2026, for the country, its five price areas and its three water regions. The probe's answer was saved for the connector, so the data were asked once.
- **A new table, `nve_norway_reservoirs_weekly`** (series, 44,793 rows, 9 entities, `power`): the filling share (pct), the stored energy and the capacity (MWh, from TWh), a week, at the date NVE gives the week (its last day: a stock at that date). Written by run `20261024T182250Z`, validated (0 errors, 0 warnings), archived, held from the live set; public, so in the release package and the next draft.
- **Public.** NVE's API documentation (read 929): "Data som ligger på api.nve.no er lisensiert under Norsk lisens for offentlige data (NLOD) som er kompatibel med CC Navngivelse 3.0 Norge (CC BY 3.0)." Verdict: may be public, sold or not; the header names NVE.

## Cross-checks

- The five price areas' capacities and the three regions' each sum to the country's (87.44 TWh in the week to 18 October 2026).
- The country's filling share on 18 October 2026: 69.3 percent (NO2, the south-west, 52.9; NO4, the north, 90.3).

## Requests (8 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | data.un.org/robots.txt | the site's page: no robots file |
| 2 | UNdata's old download handler (a fetch) | 404 |
| 3 | biapi.nve.no/robots.txt | 404 |
| 4 | the reservoir statistics API | 200: 14,931 records |
| 5 | www.nve.no/robots.txt | 200: a crawl delay of 20 seconds |
| 6 | the reservoir statistics page (20 seconds after) | 200 |
| 7 | api.nve.no/robots.txt | 404 |
| 8 | the API's documentation | 200: NLOD |

Reads recorded: 923 to 929 (on this branch). Test 205's bound was raised by 40 again. Web searches for NVE's licence reached no publisher's host.

## Decisions made without you

- **NVE's reservoirs as the third own choice; public** under NLOD.
- **`ts_utc` the date NVE gives** (the week's last day), the reservoir level being a stock at that date.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/nve_norway_reservoirs.py`, `tests/test_session2516.py`, this report.
- Changed: the registration; the metadata files; `docs/redivis/release-v1/`; the license record (reads 923 to 929, one verdict); `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c122/s2516/`, `warehouse/raw/nve_reservoirs/`, `warehouse/output/nve_norway_reservoirs_weekly.csv`.
