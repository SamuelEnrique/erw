# Session 2029 report: outages by county (Oak Ridge's EAGLE-I): the connector, no table yet

23 October 2026, from 18:25 UTC, on lab-desktop (the data machine), the second session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended, beside two other agents' chains on the same machine (chain 057, and chain 059, which another agent took from `queue/next` at 18:18 UTC, seven minutes after session 2028 pushed it). Model spend USD 0. Pulls: 9 requests of 15 (below).

## Read these first

- **No table written.** The trial downloaded the 2023 file (`eaglei_outages_2023.csv`, 1,199,752,423 bytes, saved in `warehouse/raw/eaglei_outages/`) and was stopped at about 18:33 UTC while reading it: Claude Code ended the background command because the machine was critically low on memory (16 GB, three agents running; 7.6 GB free a few minutes later). Claude Code's notice says not to start it again unasked, so the session did not, and the 2024 and 2025 files were not asked. The connector, its tests and the table's registration are on the branch; the commands to finish are below.
- **The source:** ORNL's EAGLE-I dataset for reuse, "The Environment for Analysis of Geo-Located Energy Information's Recorded Electricity Outages 2014-2025" (figshare, version 4 of 25 February 2026, doi 10.6084/m9.figshare.24237376, CC BY 4.0, by Brelsford, Tennille, Myers, Chinthavali and others): one CSV a year of every county's customers out at 15-minute intervals, as EAGLE-I read utilities' public outage maps, 78 MB for 2014 and 1.1 to 1.4 GB a year from 2018; beside them the modeled customers a county (`MCC.csv`), the state coverage history and a data quality index.
- **The table as built, when it runs:** `eaglei_county_outages_daily`, a series: a county's peak customers out a day (the largest of its 15-minute records), `entity eaglei:<FIPS>`, `unit count`, `freq P1D`, `geo` from the FIPS code's state, the day's record count in `x_records`. The 15-minute files are too large to hold whole, so the day's peak is held. A county and day with no record has no row (no record is not no outage: EAGLE-I's coverage is partial). The connector stops if the files' times are local: a clock-change day must hold 96 record times, as a UTC day does.
- **figshare.com's robots file answered HTTP 202 with an empty body** (a challenge page, not a robots file). The host was not asked again; the dataset's record came from `api.figshare.com` and the files from `ndownloader.figshare.com`, neither of which has a robots file. The download redirects to figshare's S3 bucket (`s3-eu-west-1.amazonaws.com/pfigshare-u-files/`), whose robots paths answer 403, so no path is disallowed there either. The redirect was read (a HEAD request) before the bucket's robots path was asked, as the chain's rule on a new host asks.
- **The raw manifest holds the redirect's signed address,** with figshare's public access key id and a 10-second expiry; `warehouse/raw/` is not in git, and nothing of it is in a committed file.

## The pulls

1. `figshare.com/robots.txt`: HTTP 202, empty. 2. `api.figshare.com/robots.txt`: 404. 3. The dataset's record, `api.figshare.com/v2/articles/24237376`. 4. `ndownloader.figshare.com/robots.txt`: 404. 5. A HEAD of the 2023 file's address, not followed: 302 to the S3 bucket. 6. `s3-eu-west-1.amazonaws.com/robots.txt`: 403. 7. The bucket's robots path: 403. 8 and 9. The 2023 file: ndownloader's redirect and the bucket's answer.

Reads 178 to 183 of `license_reads.csv` (the robots answers and the record, whose license field says CC BY 4.0). Session 2033's licenses round reads figshare's terms and gives EAGLE-I its verdict.

## To finish

With memory to spare (no other agent's large job running), in the main checkout, the data lock waited for:

```
cd /c/Users/Shared/Documents/erw
cp ../erw-c058/warehouse/connectors/eaglei_outages.py warehouse/connectors/
.venv/Scripts/python.exe warehouse/connectors/eaglei_outages.py --out-dir runs/c058/s2029/trial > runs/c058/s2029/trial.out 2>&1; echo "exit=$?"
rm -f warehouse/connectors/eaglei_outages.py
.venv/Scripts/python.exe runs/c058/s2029/cross.py runs/c058/s2029/trial/eaglei_county_outages_daily.csv warehouse/output/doe_oe417_events.csv
WT=../erw-c058 bash runs/c058/write_table.sh 2029 eaglei_county_outages_daily eaglei_outages.py --offline
WTN=erw-c058 bash runs/c045/finish_table.sh 2029 eaglei_county_outages_daily public
```

The trial asks for the 2024 and 2025 files (four requests, through the redirect), so it stays within the session's 15. The reader holds a year's file in memory (about 1.4 GB) and reads it a million rows at a time; a lower-memory reader would read the saved file from disk instead of through `fetch_raw`, and is a change for a session that can run it.

## Decisions made without you

- **Three years, 2023 to 2025,** the years of DOE-417's events that session 2028 holds with their own printed totals, rather than all twelve (about 13 GB).
- **The day's peak, not the 15-minute records.** The chain file allowed this when the file is too large to hold whole, and it is.
- **The killed trial was not started again** (Claude Code's instruction after a memory stop), and the chain went on to session 2030, whose files are small.
- **The registration (the sector rule and both holds) committed with the connector,** so the table is held when it is written; the release package's check passes without the table.

## For Samuel's ruling

- None new. Whether to run the EAGLE-I write (above) when the machine is quieter, or to have the code machine write a lower-memory reader first.

## Files

- New: `warehouse/connectors/eaglei_outages.py`, `tests/test_session2029.py` (5 tests), this report.
- Changed: `build_coverage.py` (the sector rule), `release_v1.py`, `live_set.yaml`, `license_reads.csv` (178 to 183), `docs/licenses.md`.
- On the data machine only: `runs/c058/s2029/` (the probe, the HEAD script, the cross-check script), `runs/license_reads/s2029/`, `warehouse/raw/eaglei_outages/` (the 2023 file).
