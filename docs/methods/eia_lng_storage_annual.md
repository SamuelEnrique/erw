# LNG peak-shaving storage a year, 1969 and 1980 to 2024: additions to and withdrawals from LNG storage, the U.S. and the states (EIA, Natural Gas Annual)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2292 of chain 104, its report `archive/sessions/SESSION_2292_REPORT.md`).

Tables: `eia_lng_storage_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Annual, liquefied natural gas additions to and withdrawals from storage, through EIA's API v2, route `natural-gas/stor/lng` (the route's metadata, `runs/c104/s2292/meta.json`, names its parent "EIA natural gas survey data" and gives an annual frequency only, 1969 to 2024). The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/stor/lng/`; the access line is `https://api.eia.gov/v2/natural-gas/stor/lng/data/?frequency=annual&data[]=value&facets[process][]=SLI&facets[process][]=SLW&start=1969`, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:natural-gas/stor/lng`.

Two processes are taken, as the page names them: SLI "LNG Storage Additions" and SLW "LNG Storage Withdrawals", unit "MMCF" on every record, for NUS (the U.S.) and the states (S<state>). A third, SAL "LNG Storage Net Withdrawals", is not taken (below). Session 2292's sample (`runs/c104/s2292/sample.json`, 2023 and 2024 asked without facets) held 243 records: SLW 84, SAL 81, SLI 78, over 42 areas. Two data pages are in `warehouse/raw/eia_lng_storage/`: the first trial's (run `20261024T052915Z`, with SAL, 4,613 records) and the second's (run `20261024T053157Z`, without it, 3,078 records), from which the table was written. No page of EIA's was saved under `runs/license_reads/` for this table; EIA's verdict is read 1.

Connector: `warehouse/connectors/eia_lng_storage.py` (session 2292): `[--from 1969] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. An area code other than NUS or S<state>, a process or unit not in its map, or a key given twice stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

The page was fetched by session 2292's second trial (run `20261024T053157Z`) at 2026-10-24T05:32:01Z (the raw manifest). The table was written at run `20261024T053214Z` from it ("0 requests of 10"): "File holds 3074 rows, one snapshot; the previous file held 0 rows." `retrieved_at` is 2026-10-24T05:32:01Z in every row, the time EIA served the page; `vintage` is blank.

EIA's page carries no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 3,074 rows, 81 entities `eia_lng_storage:<series>` (EIA's series id), `unit` MMcf, `freq` P1Y, `market` blank, `node` EIA's series description; `geo` US for the U.S., US-<state> for 41 states. Every value is a whole number of MMcf.

| Variable | Rows | Entities | Years | Mean | Highest | Zeros |
|---|---|---|---|---|---|---|
| additions | 1,502 | 39 (the U.S. and 38 states) | 1969, 1980 to 2024 | 3,038.3 | 121,928 | 211 |
| withdrawals | 1,572 | 42 (the U.S. and 41 states) | 1980 to 2024 | 2,827.2 | 127,627 | 247 |

The U.S.: additions 2,581 MMcf in 1969, 52,780 in 1980, 36,869 in 2000, 49,805 in 2023 and 44,470 in 2024, highest 121,928 in 1983; withdrawals 62,431 in 1980, 51,513 in 2000, 34,286 in 2020, 41,033 in 2023 and 45,435 in 2024, lowest 24,468 in 1987, highest 127,627 in 1983.

- **The states.** The largest by mean withdrawals 2015 to 2024 are North Carolina (6,116 MMcf a year), Massachusetts (6,013), Pennsylvania (5,572) and Tennessee (4,408); in 2024 Washington (8,094) leads. New England (Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island) draws 20.7 percent of the states' withdrawals over 1980 to 2024 and 17.2 percent over 2015 to 2024, more than any one state.
- **Levels overlap.** The U.S. and the states are levels of one another (the header: "a sum takes one level"); the states come within 4 MMcf of the U.S. for additions in all 46 years and within 3 MMcf for withdrawals in all 45.
- **Placeholders.** Oklahoma's withdrawals (6 rows, 2019 to 2024) and Florida's (one row, 2023) are 0 in every row; Alaska's additions are 0 in 36 of 42 rows. Wyoming's withdrawals have one row (2023).
- **EIA's net series, not taken.** On the first trial's page SAL equals additions less withdrawals, the reverse of its name, in 1,314 of 1,430 area-years where all three are given; in 109, every area's 2003, 2004, 2005 and 2006 (29 areas), it equals withdrawals less additions; 7 are neither, among them Tennessee's 1998 (-1,746,367 MMcf beside additions of 1,816 and withdrawals of 3,562) and Louisiana's 2019 (-1,532 beside additions and withdrawals of 0). The docstring tells a reader to take withdrawals less additions.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z (EIA's `period`, YYYY), a label for the calendar year. EIA's page holds 3,078 records (its `total`); 4 have no number (value null): Texas's additions in 2013, Illinois's in 2022, and Florida's and Wyoming's withdrawals in 2024. Those have no row; nothing is filled.

The years held are 1969 and 1980 to 2024 (46 years): EIA gives no record for 1970 to 1979, and 1969 holds two rows only, Alaska's additions and the U.S.'s, both 2,581 MMcf. Withdrawals begin in 1980. Within a series, Alaska's additions lack 1970 to 1983, the U.S.'s 1970 to 1979, Illinois's 2022 and Texas's 2013 (26 years in four series).

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/eia_lng_storage_annual.csv`, read past its 10 header lines (counted), and from the saved pages, read only (scripts `runs/c104/s2289/eia.py`, `eia_ext.py` and `lng_net.py`, outputs `eia_lng.out`, `lng_ext.out`, `lng_net.out` and `lng_ne.out` beside them).

- 3,074 rows, years 1969 to 2024, "3,078 records of EIA's, 3,074 rows", as header line 3 states; 81 series; no (entity, variable, ts_utc) twice; no blank value; unit MMcf throughout; geo US on two series and US-<state> on 79; each row's `node` the page's series description.
- **Against the page:** EIA's `total` is 3,078; the 3,074 records with a number and the table's keys and values are the same, with 0 differences; the 4 without one are those listed above.
- **The trial against the table:** `runs/c104/s2292/trial/eia_lng_storage_annual.csv` (the second trial) has the same rows past its header, byte for byte, `retrieved_at` included; the headers differ only in the run's name, its log and "1 requests of 10" against "0 requests of 10".
- Session 2292's cross-check (`runs/c104/s2292/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/lng_cross.out`): identical to the saved `cross2.out`, which was run on the second trial; it differs from `cross.out`, run on the first trial with the net series, whose lines on the net series the script no longer prints. The states against the U.S.: additions 46 years and withdrawals 45, a ratio of 1.000 to 1.000 at three decimals; U.S. withdrawals 62,431 MMcf (1980), 51,513 (2000), 34,286 (2020), 45,435 (2024). `cross.out`'s net-series lines (1,430 area-years, the largest gap 1,744,621 MMcf for Tennessee in 1998, 116 above 1) agree with session 2289's reading of the first page (116 = 109 reversed and 7 neither).

## Where the description and the data disagree

1. **The header's title names net withdrawals.** Header line 1 reads "LNG storage additions, withdrawals and net withdrawals (peak-shaving tanks)"; the table holds additions and withdrawals only, and header line 2 itself says "EIA's net series not taken".
2. **"A year from 1969" skips the 1970s.** The docstring and header give years 1969 to 2024; EIA gives no record for 1970 to 1979, and 1969 holds only Alaska's additions and the U.S.'s (the same 2,581 MMcf). A reader expecting a continuous series from 1969 finds it begins in earnest in 1980.
3. **The net series's reversed sign is four whole years, not a few cases.** The docstring says SAL is additions less withdrawals "in most years, the opposite in some (the U.S. in 2003 and 2006)", and the report adds Georgia in 2006. On the page the reversal holds for every area in 2003, 2004, 2005 and 2006 (109 area-years, 29 areas). It bears only on a series the table leaves out.
4. **The states do not sum to the U.S. exactly.** The report says "The states sum to the U.S. exactly"; they differ by up to 4 MMcf (additions) and 3 MMcf (withdrawals), which the cross-check's ratio, printed to three decimals, shows as 1.000.

Compared besides, with no contradiction found: the header's and docstring's counts, processes, areas, unit, "a sum takes one level", "Each row carries the time EIA served its page" and "nothing is filled" against the rows and the page.

Not acted on: this note changes no file but itself.

Acted on in session 2289: header line 1 no longer names net withdrawals and says the table has no rows for 1970 to 1979; the table was written again offline. Session 2289's report corrects session 2292's "exactly" (the states differ from the U.S. by up to 4 MMcf), its net-sign cases (every area, 2003 to 2006) and its request count.

## The session report against the table

Every figure of `SESSION_2292_REPORT.md` checked against the table, the saved pages and the rerun cross-check holds (1969 to 2024, 3,074 rows, 81 series, additions and withdrawals in MMcf for the U.S. and the states, each row carrying the time EIA served its page, EIA's net series not taken, 2023 U.S. 49,805 less 41,033 equal to its net 8,772, the net series reversed for the U.S. in 2003 and 2006 and for Georgia in 2006, Tennessee's 1998 at -1,746,367 MMcf, additions over 46 years and withdrawals over 45, U.S. withdrawals 62,431 MMcf in 1980, 51,513 in 2000, 34,286 in 2020 and 45,435 in 2024, the route annual only from 1969 to 2024, New England's share of withdrawals the largest of any region named), except:

- "The states sum to the U.S. exactly": within 4 MMcf, not exactly (disagreement 4).
- "In some years it has the opposite sign: the U.S. in 2003 and 2006, Georgia in 2006": every area in 2003 to 2006 (disagreement 3).
- "Pulls: EIA's API, 4 requests of 20": the pulls the report lists are five (the route's metadata, the refused monthly sample, the annual page of 2023 and 2024, and the trial's page twice); `sample.py` as saved makes the metadata and annual requests only, so the refused request is not on record.
- "1969 to 2024": 1970 to 1979 have no rows (disagreement 2).

## What it does not hold

- EIA's net withdrawals (left out, above), LNG in storage at the year's end, the tanks' capacity, months (the route has none), 1970 to 1979, years after 2024, and the export and import terminals (`eia_lng_exports_monthly` and the ERW's other LNG tables).
