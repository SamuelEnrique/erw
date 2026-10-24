# Session 2231 report: a second source of the session's own choosing (the Netherlands' electricity balance, CBS)

24 October 2026, from 02:48 UTC, on lab-desktop (the data machine), chain 099, unattended. Model spend USD 0. Pulls: 11 requests of 20 (10 by the probe and the zip; the trial and the write ran offline).

## Read these first

- **Three sources refused or barred the reader before the fourth was taken,** each recorded as a read:
  - **New Zealand's MBIE** (electricity statistics, quarterly): its robots file allows the page, but the page answered an Incapsula bot challenge, not the page. It is not asked again.
  - **Hydro-Quebec's open data portal:** its robots file disallows `/api/` and every download path for every reader but Googlebot. Nothing further was asked.
  - **EirGrid's System and Renewable Data reports:** robots allows them, but EirGrid's website disclaimer says its materials "may not be copied, modified, reproduced, republished, ... distributed or used for any public or commercial purposes except as expressly provided for on this website or expressly authorised in writing by EirGrid". No file was fetched. EirGrid goes to the licenses round as "needs written permission".
- **One already held:** FERC Form 714's planning area demand (`ferc714_area_demand_*`, through PUDL).
- **A new table, `cbs_netherlands_electricity_monthly`** (series, 8,880 rows, `power`):
  - Statistics Netherlands' table 84575NED, the Netherlands' electricity balance, a month from January 1976 to July 2026, across 30 measures:
    - gross and net production and their sources (nuclear, coal, oil products, natural gas, biomass, other fuels, hydro, onshore and offshore wind, solar, other);
    - imports and exports in total and with Belgium, Denmark, Germany, the United Kingdom and Norway;
    - distribution losses and net consumption.
  - In MWh (CBS's million kWh times 1,000), each measure under an English name in the connector's map of CBS's codes, CBS's Dutch name kept as the node, the period's status kept (7,951 definitive, 719 later provisional, 210 provisional).
  - CBS's description: complete monthly figures from 2015; from 1976 a month only the totals of production, imports and exports. The rows hold more than that from 1976 (own use, net production, losses, net consumption, imports from Belgium and Germany), found by session 2233.
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** CC BY 4.0, stated in the table's own properties (read 376) and CBS's catalog; source "CBS".
- **The robots files:** opendata.cbs.nl's disallows its OData paths, which the connector does not use; datasets.cbs.nl, where the table's download is, has no robots file.
- **Cross-checks:**
  - CBS's balance holds: net production plus imports less exports less losses equals net consumption within 1,000 MWh (CBS's rounding of a million kWh) in all 607 months it can be computed.
  - Against Eurostat (`eurostat_electricity_monthly`, the Netherlands), full years 2016 to 2025: imports and exports agree exactly from 2017, except 2018, where Eurostat lacks a month. Net production is within 2 percent (1.017 in 2017, 0.985 in 2018).
  - CBS's net consumption is 0.930 to 0.942 of Ember's Dutch demand.

## Requests (11 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.mbie.govt.nz/robots.txt | 200 |
| 2 | MBIE's electricity statistics page | 200, an Incapsula challenge (212 bytes) |
| 3 | donnees.hydroquebec.com/robots.txt | 200: /api/ and downloads disallowed |
| 4 | www.smartgriddashboard.com/robots.txt | 200: allows all |
| 5 | www.eirgrid.ie/robots.txt | 200 |
| 6 | EirGrid's data reports page | 200: three workbooks on cms.eirgrid.ie |
| 7 | EirGrid's disclaimer | 200: no copying without written authority |
| 8 | opendata.cbs.nl/robots.txt | 200: OData disallowed |
| 9 | datasets.cbs.nl/robots.txt | 404 |
| 10 | table 84575NED's properties | 200: CC BY 4.0 |
| 11 | datasets.cbs.nl/csv/CBS/nl/84575NED | 200, a zip of 144,901 bytes |

Reads recorded: 369 to 376.

## Decisions made without you

- **The Netherlands, after three refusals,** each respected and recorded.
- **English names for CBS's codes, from a fixed map;** an unmapped code stops the run.
- **The monthly periods only,** CBS's years and quarters left out.

## For Samuel's ruling

- EirGrid (Ireland's grid): its disclaimer bars copying without written authority. A letter would be needed for its System and Renewable Data reports.

## Files

- New: `warehouse/connectors/cbs_electricity.py`, `tests/test_session2231.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2231/`, `warehouse/raw/cbs_electricity/`, `warehouse/output/cbs_netherlands_electricity_monthly.csv`.
