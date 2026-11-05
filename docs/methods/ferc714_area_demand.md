# FERC Form 714 hourly demand by planning area, and its respondents

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `ferc714_area_demand_2006`, `ferc714_area_demand_2007`, `ferc714_area_demand_2008`, `ferc714_area_demand_2009`, `ferc714_area_demand_2010`, `ferc714_area_demand_2011`, `ferc714_area_demand_2012`, `ferc714_area_demand_2013`, `ferc714_area_demand_2014`, `ferc714_area_demand_2015`, `ferc714_area_demand_2016`, `ferc714_area_demand_2017`, `ferc714_area_demand_2018`, `ferc714_area_demand_2019`, `ferc714_area_demand_2020`, `ferc714_area_demand_2021`, `ferc714_area_demand_2022`, `ferc714_area_demand_2023`, `ferc714_area_demand_2024`, `ferc714_area_demand_2025`, `ferc714_respondents`

Connectors: `warehouse/connectors/ferc714_demand.py` (session 484, the yearly demand tables) and `warehouse/connectors/ferc714_respondents.py` (session 514, the respondents).

## Publisher and report

The original is the Federal Energy Regulatory Commission (FERC), Form 714 Annual Electric Balancing Authority Area and Planning Area Report, Part III Schedule 2a (each planning area's hourly demand, filed once a year). FERC's own pages answer automated requests with HTTP 403 (Cloudflare, session 484), so the ERW takes FERC's filings as Catalyst Cooperative's Public Utility Data Liberation project (PUDL) publishes them, in its stable release on a public AWS bucket:

- demand: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__hourly_planning_area_demand.parquet` (source code `pudl:core_ferc714__hourly_planning_area_demand`);
- respondents: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__respondent_id.parquet` (source code `pudl:core_ferc714__respondent_id`).

PUDL's page for the source: `https://docs.catalyst.coop/pudl/en/stable/data_sources/ferc714.html`.

## Vintage and revision rule

- The demand connector reads the whole parquet file and writes one table a year. By default it writes 2023 to the latest whole year in the file; `--from` and `--to` choose the years. The years 2006 to 2025 are held. A "whole" year is one with more than 100,000 rows in the file.
- `vintage` is the file's Last-Modified time: 2026-10-14T17:41:46Z for both files. The tables were retrieved on 21 October 2026.
- Every table is written with `ip.write_snapshot`: a run replaces the whole table for that year. A later PUDL release replaces what was held.
- Ceiling: two requests a run (the two files). A file already in `warehouse/raw/ferc714_demand/` is reused. The respondents connector reuses the file the demand connector saved and asks for it (one request) only when it is not there.

## Shape and columns: `ferc714_area_demand_<year>`

Series shape: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`.

- `entity`: `ferc714:<respondent_id_ferc714>`, PUDL's respondent id, which links FERC's CSV ids (to 2020) and XBRL ids (from 2021). Example: `ferc714:1`, PowerSouth Energy Cooperative.
- `variable`: `demand` only, unit `MW`: the planning area's demand over the hour, as filed (PUDL's `demand_mwh`; an hour's MWh is its mean MW).
- `ts_utc`: the hour's start. PUDL's `datetime_utc` marks the hour's end, so the connector takes one hour off.
- `freq` `PT1H`; `geo` `US`; `market` empty; `node` the respondent's name from PUDL's respondent table.

Respondents a year, from the headers: 175 in 2006, 177 in 2007, 159 in 2008, 154 in 2009, 128 in 2010, 126 in 2011, 122 in 2012 and 2013, 121 in 2014, 101 in 2015, 99 in 2016, 100 in 2017, 98 in 2018, 97 in 2019, 95 in 2020, 99 in 2021, 91 in 2022, and 89 in 2023, 2024 and 2025.

## Shape and columns: `ferc714_respondents`

Entities shape, 219 rows, each with an EIA code. `entity_id` `ferc714:<PUDL's respondent id>` (the entity of the demand tables); `entity_type` `utility`; `name` the respondent's name as filed; `geo` `US`; `lat`, `lon`, `capacity_mw`, `status`, `status_date` and `operator` empty. After the standard columns: `respondent_id_ferc714` (PUDL's id), `respondent_id_ferc714_csv` (FERC's id in its CSV years, to 2020), `respondent_id_ferc714_xbrl` (FERC's id in the XBRL years, 2021 on), `eia_code` (the respondent's EIA utility code). A blank stays blank.

## License

ERW verdict: internal, for all 21 tables (licenses.md: the publisher's terms not settled, needs written permission by default). Header: "License: internal (PUDL's data CC-BY-4.0: cite Catalyst Cooperative, PUDL; FERC's filings a U.S. government work; FERC's own terms page unread, HTTP 403: a person rules on public)." The respondents' header says the same: internal until a person rules.

## Cross-check

None in the connector. Its docstring records a one-time check of the hour stamp: ERCOT's own system load for 2025 against respondent 58 (8,759 hours). With the hour shifted one hour earlier, the mean difference is 1,184 MW on a mean of 55,734 MW; as PUDL stamps it, 2,717 MW; one hour later, 4,176 MW. The connector stops when a respondent's hour is given twice; the respondents connector stops when an id is missing or given twice.

## What it does not hold

- No imputed hour. PUDL's `out_ferc714__hourly_planning_area_demand` fills missing and anomalous hours by imputation; the ERW does not use it. A respondent's missing hour is absent.
- Some respondents hold only part of a year. Hours a respondent, from the headers: 2006 from 8,751 to 8,756 (respondent 1's first hour is 2006-01-01T05:00:00Z); 2016 8,784 for every respondent; 2020 from 8,760 to 8,784; 2023 from 8,759 to 8,760; 2024 from 8,760 to 8,784; 2025 from 28 to 8,760; 2013 from 5, 2022 from 6, and every other year from 4 hours, up to a full year.
- Values are as filed, negatives included (an area can export more than it serves); nothing is corrected.
- No forecast demand, no other Form 714 schedule, and no year before 2006.
