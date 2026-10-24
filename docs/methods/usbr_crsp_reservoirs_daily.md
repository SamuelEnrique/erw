# Flaming Gorge, Blue Mesa, Morrow Point and Crystal a day: pool elevation, storage, power release and total release, over each reservoir's period of record (Reclamation's hydrodata)

Energy Research Warehouse (ERW), method note written in session 2221 (chain 098, drafted by a helper beside session 2218) for a table first written on 24 October 2026 (session 2221 of chain 098; its report, `archive/sessions/SESSION_2221_REPORT.md`, was not yet written when this note was). Lake Powell and Lake Mead, from the same files, are `docs/methods/usbr_mead_powell_daily.md`.

Tables: `usbr_crsp_reservoirs_daily`

## Publisher and address

U.S. Bureau of Reclamation (USBR), Upper Colorado Basin Region, reservoir data (hydrodata). The source page in the header is Reclamation's site map, `https://www.usbr.gov/uc/water/hydrodata/reservoir_data/site_map.html`; the files are `https://www.usbr.gov/uc/water/hydrodata/reservoir_data/<site>/csv/<data type>.csv`, one CSV a reservoir and data type, "datetime,<name>", one line a day. Sites: 917 Flaming Gorge Reservoir (Utah), 913 Blue Mesa Reservoir, 914 Morrow Point Reservoir and 915 Crystal Reservoir (the Wayne N. Aspinall Unit on the Gunnison River, Colorado). Data types: 49 pool elevation, 17 storage, 39 power release, 42 total release. Source id `usbr:hydrodata_crsp_reservoirs`. Files saved under `warehouse/raw/usbr_crsp_reservoirs/` (session 2221's probe, `20261024T020838Z_probe`: sixteen answers of HTTP 200, 344,628 to 491,296 bytes).

Two pages read in session 2221 and saved in `runs/license_reads/s2221/`: 01, the site map, whose markers pair the tooltips FLAMING GORGE, BLUE MESA, MORROW POINT and CRYSTAL RESERVOIR with the dashboards `./917/`, `./913/`, `./914/` and `./915/`; 02, the Aspinall Unit page (`https://www.usbr.gov/uc/rm/crsp/aspinall/index.html`, "Last Updated: 8/19/21"), with each reservoir's full pool and capacity when full and the plants' nameplate table.

Connector: `warehouse/connectors/usbr_crsp_reservoirs.py` (session 2221): `[--offline] [--out-dir DIR]`, at most sixteen requests, each reused with `--offline`. A header not "datetime,<name>", a date not YYYY-MM-DD, a value that is not a number or a day given twice stops the run. Since session 2218's note on Lake Mead, `ended_days()` leaves out every row dated on or after the retrieval's local date (America/Denver) and counts it in the header. The files state no unit; the units are those of `usbr_mead_powell_daily`: `ft` (Decision 71), `acre-ft` (Decision 72), `ft3/s` (Decision 65). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

The table's header is run `20261024T021907Z`, written offline from the sixteen files retrieved at 2026-10-24T02:09:29Z and 02:09:30Z (`retrieved_at`: 133,920 and 196,373 rows): "This run wrote 330293 rows: 0 new, 330293 replacing earlier rows ...; 0 rows are kept from earlier runs", so it replaced, row for row, the write of `runs/c098/s2221/write.out`. `vintage` is each file's Last-Modified, sixteen values from 2026-10-23T22:06:25Z to 22:11:29Z.

Reclamation: "All data considered provisional and subject to revision" (header line 2). No row carries a provisional flag; every row is provisional. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but a day Reclamation later blanks writes no row, so the earlier value would be kept.

## Shape and variables

Series, 330,293 rows, four entities: `usbr_hydrodata:917` (90,881 rows, `geo` US-UT), `usbr_hydrodata:913` (85,390), `usbr_hydrodata:914` (81,540) and `usbr_hydrodata:915` (72,482), the last three `geo` US-CO; `node` the reservoir's name, `freq` P1D, `market` blank.

| Reservoir | Variable | Unit | Rows | First day | Last day | Lowest (day) | Highest (day) |
|---|---|---|---|---|---|---|---|
| Flaming Gorge | pool_elevation | ft | 21,145 | 1968-12-01 | 2026-10-22 | 5,966.88965 (1970-03-22) | 6,043.7998 (1983-07-13) |
| Flaming Gorge | storage | acre-ft | 23,336 | 1962-12-02 | 2026-10-22 | 200.000763 (1962-12-02) | 3,913,631 (1983-07-13) |
| Flaming Gorge | power_release | ft3/s | 23,033 | 1963-10-01 | 2026-10-22 | 0 (1994-11-02) | 5,051.75 (1975-07-25) |
| Flaming Gorge | total_release | ft3/s | 23,367 | 1962-11-01 | 2026-10-22 | 40.0000038 (1962-11-13) | 12,300 (1983-07-16) |
| Blue Mesa | pool_elevation | ft | 21,859 | 1965-11-30 | 2026-10-22 | 7,303.9 (1965-11-30) | 7,519.63965 (1970-07-08) |
| Blue Mesa | storage | acre-ft | 21,180 | 1966-01-31 | 2026-10-22 | 6,502 (1966-01-31) | 831,720.813 (1970-07-08) |
| Blue Mesa | power_release | ft3/s | 21,206 | 1968-10-01 | 2026-10-22 | 0 (1969-02-24) | 6,090.33333 (1970-06-27) |
| Blue Mesa | total_release | ft3/s | 21,145 | 1968-12-01 | 2026-10-22 | 0 (1969-02-24) | 12,485.375 (2017-05-25) |
| Morrow Point | pool_elevation | ft | 20,446 | 1968-03-31 | 2026-10-22 | 6,954 (1968-03-31) | 7,163.79 (1977-03-22) |
| Morrow Point | storage | acre-ft | 20,415 | 1970-12-01 | 2026-10-22 | 76,595.6719 (1973-10-31) | 120,132.031 (1977-03-22) |
| Morrow Point | power_release | ft3/s | 20,265 | 1970-10-31 | 2026-10-22 | -119.60493 (1990-11-01) | 6,183.43 (1985-06-19) |
| Morrow Point | total_release | ft3/s | 20,414 | 1970-12-02 | 2026-10-22 | -119.6 (1990-11-01) | 12,434.7917 (2017-05-25) |
| Crystal | pool_elevation | ft | 18,121 | 1977-03-13 | 2026-10-22 | 6,587.8 (1977-03-13) | 6,763.19 (2017-05-25) |
| Crystal | storage | acre-ft | 18,121 | 1977-03-13 | 2026-10-22 | 38 (1977-03-13) | 20,097 (2017-05-25) |
| Crystal | power_release | ft3/s | 18,120 | 1977-03-14 | 2026-10-22 | 0 (1980-10-21) | 3,413.20833 (1980-06-15) |
| Crystal | total_release | ft3/s | 18,120 | 1977-03-14 | 2026-10-22 | 35.29 (1977-03-16) | 13,150.2083 (2017-05-25) |

- **Not every series is daily from its first day.** Blue Mesa's elevation is a value a month (month ends) until 1966-12-31 and its storage until 1968-11-30 (383 and 1,000 days absent inside their spans); Morrow Point's elevation is a month-end value, with some months missing, until 1970-11-30 (944 days absent). Morrow Point's power release has a gap of 152 days ending 2003-06-01 (181 days absent in all). Every other series holds every day from its first to its last.
- **Zeros:** power release 17 days at Flaming Gorge, 825 at Blue Mesa, 330 at Morrow Point, 1,241 at Crystal; total release 679 at Blue Mesa, 27 at Morrow Point. **Negatives:** 49, all at Morrow Point (disagreement 2).
- **Above full pool:** against the Aspinall Unit page's full pools, Blue Mesa stood more than half a foot above 7,519 ft on 5 days (highest 7,519.64 ft, 1970-07-08), Morrow Point above 7,160 ft on 87 (7,163.79 ft, 1977-03-22), Crystal above 6,755 ft on 541 (6,763.19 ft, 2017-05-25). The page says Crystal's ungated spillway passes water "when the reservoir level exceeds full pool at elevation 6,755".
- Values keep Reclamation's digits; 34 release values carry floating-point tails of more than 8 decimals (Blue Mesa's power release 3.5533333000000002 on 2023-09-20).

On 2026-10-22: Flaming Gorge 6,005.38 ft and 2,441,796.7 acre-ft, releasing 2,165.03375 ft3/s; Blue Mesa 7,412.06 ft and 139,818.46 acre-ft; Morrow Point 7,150.22 ft and 109,246.04 acre-ft; Crystal 6,748.89 ft and 15,767.97 acre-ft, releasing 725.207083 ft3/s (719.082083 through the turbines).

## Placing values in time, and what is filled

`ts_utc` is the day at 00:00:00Z (Decision 11); Reclamation's day is the reservoir's local day (Mountain time). The files were retrieved at 20:09 on 23 October Mountain daylight time and last modified between 16:06 and 16:11 that day; every series ends on 2026-10-22, and `ended_days()` left out no row ("0 rows of a day not yet ended ... are left out", the header). The files do not say whether a day's elevation and storage are a reading at a fixed hour or the day's end, nor how a day's releases are averaged. A blank has no row; nothing is filled.

## License

Header: "License: public (U.S. Bureau of Reclamation, a work of the U.S. government; the Department of the Interior's notice). Cite: U.S. Bureau of Reclamation, reservoir data, provisional." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 173 (session 2005, Reclamation's disclaimer pointing to the Department's notice: "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission"), verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public. The site map and the Aspinall Unit page read in session 2221 were not yet in `warehouse/metadata/license_reads.csv` (its last read is 356) when this note was written.

## Checks (session 2218)

The figures in this note were computed from the rows of `warehouse/output/usbr_crsp_reservoirs_daily.csv`, read past its 10 header lines, and from the saved pages, read only (scripts `runs/c098/s2218/crsp.py` and `crsp2.py`, outputs beside them).

- 330,293 rows, `ts_utc` from 1962-11-01T00:00:00Z to 2026-10-22T00:00:00Z, as the header states; each series' first and last day as header line 3 lists them; no (entity, variable, ts_utc) twice; units ft (81,571 rows), acre-ft (83,052) and ft3/s (165,670), as the header names them.
- The trial's table (`runs/c098/s2221/trial/usbr_crsp_reservoirs_daily.csv`) has the same rows, byte for byte.
- Session 2221's cross-check (`runs/c098/s2221/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. Storage at full pool, the median over the days within half a foot of the page's full pool, against the page's capacity when full: Blue Mesa 824,289 against 940,800 acre-ft (185 days, ratio 0.876), Morrow Point 116,937 against 117,190 (224 days, 0.998), Crystal 17,490 against 26,000 (243 days, 0.673). Power release above total release by more than 0.5 ft3/s on 5,275 of 82,560 days with both. A year's total release, 2016 to 2025, rises down the Gunnison from Blue Mesa to Morrow Point to Crystal in every year (2025: 778, 814 and 856 thousand acre-feet).
- **The docstring against the saved pages.** The site ids 917, 913, 914 and 915 are the site map's for the four reservoirs. The nameplate figures, Blue Mesa 86.4 MW, Morrow Point 173.3 MW and Crystal 31.5 MW, are the Aspinall Unit page's table ("The current combined nameplate capacity of the generating units in each powerplant"); the page's fact boxes round them to 86, 173 and 32 megawatts. The full pools in the cross-check, 7,519, 7,160 and 6,755 ft, and the capacities 940,800, 117,190 and "about 26,000" acre-feet, are the page's. Data type 39 is "Power Release" in the list of files on Lake Powell's dashboard (`runs/license_reads/s2211/02_*`), as the docstring says. The page gives no figure for Flaming Gorge.

## Where the description and the data disagree

1. **Power release above total release.** The docstring: "Power release is the water through the turbines; total release adds the outlet works, spillway and bypass", so power release should never exceed total release. It does by more than 0.5 ft3/s on 5,275 of the 82,560 days with both: Flaming Gorge 5,015 (5,010 of them from 1969 to 2004, 5 in February and March 2026; median ratio 1.0237, the middle 90 percent 1.0031 to 1.0768, the largest difference 1,632.04 ft3/s), Morrow Point 232 (217 in the 1990s), Blue Mesa 24 (2016 and 2017, a median 100 ft3/s), Crystal 4 (2020 and 2025, a median 2.01 ft3/s). By any amount, 28,505 days, most of them within rounding. No day has a total release of zero with a power release above it. The files give no reason; a reader who needs a release takes total release, and power release as Reclamation's figure for the turbines, without assuming one bounds the other.
2. **Negative releases at Morrow Point.** 49 rows, 18 of power release and 31 of total release, from 1973-11-03 to 2001-12-16: 22 in 1973, 8 in 1977, 2 in 1988, 3 in 1989, 11 in 1990, 1 in 1992, 2 in 2001; the lowest -119.60493 (power) and -119.6 (total) ft3/s on 1990-11-01. A release out of a reservoir cannot be negative; the header and docstring say only "Values as published", and the files give no reason.
3. **Storage at full pool.** The docstring says the values "agree with the Aspinall Unit page's full pools (session 2221's cross-check)". The elevations do; storage agrees only at Morrow Point (0.998). At full pool Blue Mesa's storage is 0.876 of the page's capacity when full and Crystal's 0.673, and neither reservoir's storage ever reaches the page's figure (highest 831,720.813 and 20,097 acre-ft). The gap is steady over the decades (Blue Mesa's median at full pool 823,648 to 825,661 acre-ft in each decade from the 1970s to the 2010s; Crystal's 17,450 to 17,499), so it is a difference of definition, not of time; the files do not say what their storage counts, and the page's "total capacity" may count water the files leave out. A reader takes the table's storage as Reclamation's daily figure, not as a share of the page's capacity.
4. **Spans that are not daily.** Header line 3 gives each series a first and last day, with `freq` P1D; Blue Mesa's elevation and storage and Morrow Point's elevation begin as month-end values (to 1966-12-31, 1968-11-30 and 1970-11-30), and Morrow Point's power release lacks 152 days before 2003-06-01. "A blank has no row" covers them, but a reader counting days finds them short.

Acted on in session 2221: the connector's docstring now says what the cross-check found for storage (disagreement 3) and names disagreements 1, 2 and 4 as Reclamation's data as published, not changed. The table is not written again: its rows and header are unchanged by a docstring. The two pages session 2221 read are in the license record (reads 357 and 358 on the branch).

## The session report against the table

Session 2221's report was written after this note, from the same runs and with this note's findings; its figures are those below. The figures the session left in `runs/c098/s2221/` hold: the trial's and the write's 330,293 rows (`trial.out`, `write.out`) and every line of `cross.out`. `write.out` ends "metadata to the branch exit=1 ... done, fail=1": that step of the 02:14 write failed, and the table was written again at 02:19 (run `20261024T021907Z`, the same rows).

## What it does not hold

- Reclamation's other data types for these reservoirs (inflow, evaporation, spillway and bypass release, among the files Lake Powell's dashboard lists), Reclamation's other reservoirs (Lake Powell and Lake Mead are `usbr_mead_powell_daily`), readings within the day, and the plants' generation.
