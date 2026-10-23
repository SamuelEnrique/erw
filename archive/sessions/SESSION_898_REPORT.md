# Session 898 report: EPA's unit emissions: stopped, the bulk files need a key

23 October 2026, from 06:34 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: 2 requests of 20.

## Read these first

- **No table written.** EPA's Clean Air Markets bulk files (each unit's SO2, NOx, CO2 and heat input) are listed by `https://api.epa.gov/easey/camd-services/bulk-files`, which answers HTTP 403 "API_KEY_MISSING: An API Key is required but was not provided. Get one at https://www.epa.gov/airmarkets/cam-api-portal." The data machine's `.env` holds no EPA or api.data.gov key. The queue file says that in this case the session stops and says so, without signing up; it did.
- **Read:** api.epa.gov has no robots file (HTTP 404); EPA's terms already have a verdict in the record ("may be public", read 55).
- **What the ERW holds of EPA's emissions meanwhile:** `epa_ghgrp_power_co2` (the greenhouse gas reporting program) and eGRID's plant tables; EIA's `eia930_all_emissions` and `eia_power_co2_state_annual`.

## Decisions made without you

- Not signed up for a key: registering an account for the ERW is the owner's.

## For Samuel's ruling

- A free CAM API key (https://www.epa.gov/airmarkets/cam-api-portal), set as `EPA_CAMD_API_KEY` in the data machine's `.env`, would let a later session take every unit's hourly-to-annual emissions with a few requests.

## Files

- New: this report. On the data machine only: `runs/c049/s898/`, `runs/license_reads/s898/`.
