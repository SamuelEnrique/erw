# Session 850 report: ERCOT's settlement point mapping, refused by ERCOT's robots file

23 October 2026, from 01:35 UTC, on lab-desktop (the data machine), the first session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **ERCOT's robots file disallows `/misapp` and `/misdownload` for every agent**, the two paths of ERCOT's public report list and its downloads, where the Settlement Points List and Electrical Buses Mapping (report type 10008, NP4-160) is posted. Under the chain's rule (a robots file that disallows the path ends the source), `ercot_settlement_points` is not written. The file is the same as the copy session 322 saved on 19 October (`warehouse/raw/ercot_grid_notices/s322/robots.txt`), so the rule is not new.
- **My error: one request went to a disallowed path.** The probe listed the robots file and the report list in one batch, so the list (`/misapp/servlets/IceDocListJsonWS?reportTypeId=10008`, HTTP 200, four postings, the newest 21 October, "CIM_Oct_ML3_1_10272026_SP_List_and_EB_Mapping") was asked for before the robots file was read. Nothing was downloaded from `/misdownload`. From here every probe reads the robots file in a request of its own before listing any other path.
- **The ERW's standing ERCOT pulls use the same disallowed paths.** Twelve connectors reach `/misapp` or `/misdownload` (`ercot_rt_spp.py`, `ercot_dam_esr.py`, `ercot_sced_esr.py`, `ercot_dam_cleared.py`, `ercot_as_prices.py`, `ercot_rt_adders.py`, `ercot_4cp.py`, `ercot_wind_solar_forecast.py`, `ercot_wind_solar_history.py`, `ercot_zone_prices.py`, `iso_prices.py`, `curtailment.py`), some of them steps of the daily runs. The Virginia SCC was paused for a robots file that disallows its paths (`docs/methods/vascc_pause.md`); whether ERCOT's report pulls should be paused, or moved to ERCOT's public API (`api.ercot.com`, which needs a subscription key the ERW does not hold), is for Samuel. Nothing was paused or changed here.
- Chain 047 (`queue/next/047-night-23-october-data-utilities-plants.md`, sessions 867 to 879) was written and pushed to main first (`867f4e1c`, 01:36 UTC), as chain 045's rule asks; its session 872 (ERCOT's resource lists) is subject to the same robots question.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.ercot.com | 4 of 10 | two attempts that failed at the name lookup (nothing sent), then the robots file and the report list (the list in breach of the robots file, above) |

## Decisions made without you

- No other ERCOT path was tried for the mapping (no API key; the robots file ends the source).
- The standing pulls were not paused: a pause is a person's decision.

## For Samuel's ruling

- ERCOT's robots file disallows `/misapp` and `/misdownload`, which twelve ERW connectors use (some daily): pause them as the Virginia SCC was, read ERCOT's terms for its MIS separately, or obtain a key for ERCOT's public API.

## Files

- New: this report; `queue/next/047-night-23-october-data-utilities-plants.md` (on main). On the data machine only: `runs/c046/s850/` (the probe and its log), `runs/license_reads/s850/` (the robots file and the list).
