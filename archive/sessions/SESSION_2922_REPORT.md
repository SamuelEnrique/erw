# Session 2922 report: ERCOT's four coincident peaks of summer 2026

6 November 2026, about 05:31 to 05:33 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: www.ercot.com, 1 request of the 10 allowed (`runs/s2922/probe.csv`). Robots was read by session 2919 at 05:21 UTC: `/mktinfo/` and `/files/` are allowed, `/misapp` and `/misdownload` are not.

## Read these first

- **Not posted where this reader may look.** ERCOT's 4CP page (`/mktinfo/data_agg/4cp`, fetched today) links two things:
  - the data product NP9-83-M (`/mp/data-products/data-product-details?id=NP9-83-M`), whose file list and downloads are served from `/misapp/servlets/IceDocListJsonWS?reportTypeId=13037` and `/misdownload/`, both disallowed;
  - the 1996 to 2020 zip under `/files/docs/`.
  - No 2026 workbook is linked on an allowed path.
- **The siting gaps row "ERCOT | Transmission and 4CP | the four peaks of summer 2026" waits.** ERCOT's protocols ask for the calculation by 1 December 2026. `ercot_4cp_intervals` holds 2018 to 2025 (not 2021).
- **Its connector reads the list at `/misapp`.** Since the robots rule of chain 147, the connector's `--pull` cannot be run here. A posting of 2026 under `/files/docs/` (as the history zip is) would be readable. Session 2935 of chain 155 looks again.

## Decisions made without you

- **The product page not asked:** its list loads from `/misapp`.

## For Samuel's ruling

- None new (the `/misapp` ruling of chain 147's note, item 1, covers this).
