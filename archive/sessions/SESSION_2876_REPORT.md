# Session 2876 report: substations and transmission lines (HIFLD)

5 November 2026, about 21:44 to 21:47 UTC, on lab-desktop (the data machine), chain 147, unattended, done while session 2863's landing gate ran. Model spend USD 0. Pulls: 5 of 20 (hifld-geoplatform.opendata.arcgis.com 1, atlas.eia.gov 4).

## Read these first

- **No HIFLD table is held.** `coverage.csv` and `warehouse/output` hold no substation or transmission line table. Session 666 had already found HIFLD gone.
- **HIFLD's open data site no longer exists.** `hifld-geoplatform.opendata.arcgis.com/robots.txt` answers HTTP 404 with `{"error":"Site does not exist"}`, and there is no redirect to follow. The open portal was retired; the data moved behind HIFLD Secure, which needs an account.
- **EIA's Energy Atlas (atlas.eia.gov) was tried as the federal copy.**
  - Its robots file allows `/api/` and asks a crawl delay of 60 s.
  - Its v3 dataset search searches all of ArcGIS Online: the first 20 substation and line layers are users' and foreign layers, none of them federal.
  - Its own catalog search for "transmission" matched 0 items.
- **Not pulled.** `hifld_substations` and `hifld_transmission_lines` are not written, and the siting gaps row "Substations and lines" stays open.

## Decisions made without you

- **No other host was tried** for a national substation layer. The chain names HIFLD, and other copies (OpenStreetMap, utilities' maps) carry other licenses and were left to a ruling.

## Errors

- **Two requests to atlas.eia.gov broke its 60 s crawl delay.** The first search came 21 s after the robots read, and the catalog search came 25 s after the second search. My paced fetcher waited only between rows of one list, not across two runs. `runs/s2876/paced.py` now reads the host's last request from the record before it sends.

## For Samuel's ruling

- **A source for substations and lines:** HIFLD Secure (an account), the EIA Energy Atlas layers if EIA names a federal one, or OpenStreetMap (ODbL, share-alike).

## Files

- New: this report.
- On the data machine only: `runs/s2876/` (probe, paced fetcher, record, notes) and `runs/license_reads/s2876/`.
