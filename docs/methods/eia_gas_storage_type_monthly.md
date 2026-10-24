# U.S. underground natural gas storage by type, a month from December 1973: base gas, working gas, total, injections, withdrawals and net withdrawals, in all fields and, from 1994, in salt caverns and other fields (EIA, Natural Gas Monthly)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2283 of chain 104, its report `archive/sessions/SESSION_2283_REPORT.md`).

Tables: `eia_gas_storage_type_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Monthly, underground natural gas storage by storage type, through EIA's API v2, route `natural-gas/stor/type` (the route's metadata, `runs/c104/s2283/meta.json`, names its parent "EIA natural gas survey data" and gives monthly and annual frequencies, 1973-01 to 2026-07). The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/stor/type/`; the requests ask `data/?frequency=monthly&data[]=value` with the eighteen processes as facets, from 1973-01, in pages of 5,000 records sorted by period and series, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:natural-gas/stor/type`.

Eighteen processes, one area (NUS, the U.S.), unit "MMCF" on every record: SAB, SAO, SAT, SAI, SAW, SAN (all fields: base gas, working gas, total, injections, withdrawals, net withdrawals), SSB to SSN (salt) and SNB to SNN (non-salt). Session 2283's sample (`runs/c104/s2283/sample.json`, a page of 2025 asked without facets) held 216 records, these eighteen processes twelve times each, all for NUS. The two data pages are in `warehouse/raw/eia_gas_storage_type/20261024T051719Z/`. No page of EIA's was saved under `runs/license_reads/` for this table; EIA's verdict is read 1.

Connector: `warehouse/connectors/eia_gas_storage_type.py` (session 2283): `[--from 1973-01] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process, unit or area not in its map, or a key given twice, stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

The two pages were fetched by session 2283's trial (run `20261024T051719Z`) at 2026-10-24T05:17:23Z and 05:17:27Z (the raw manifest). The table was written at run `20261024T051823Z` from those pages ("0 requests of 10"): "File holds 8367 rows, one snapshot; the previous file held 0 rows." `retrieved_at` is the time EIA served each row's page (05:17:23Z on 4,817 rows, 05:17:27Z on 3,550), the fix chain 101's session 2247 made, inherited from the template; `vintage` is blank.

EIA's pages carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 8,367 rows, 18 entities `eia_gas_storage_type:<series>` (EIA's series id, N5010US2 to N5560US2), one variable each, `unit` MMcf, `freq` P1M, `geo` US, `market` blank, `node` EIA's series description. Every value is a whole number of MMcf.

| Variable | Rows | First | Last | Mean | Lowest (month) | Highest (month) | July 2026 |
|---|---|---|---|---|---|---|---|
| all_base_gas | 614 | 1973-12 | 2026-07 | 4,118,998.3 | 2,864,000 (1973-12) | 4,504,919 (2026-07) | 4,504,919 |
| all_working_gas | 614 | 1973-12 | 2026-07 | 2,454,844.5 | 730,055 (2003-03) | 4,012,723 (2016-10) | 3,137,146 |
| all_total | 614 | 1973-12 | 2026-07 | 6,573,841.2 | 4,446,000 (1977-02) | 8,432,410 (2025-10) | 7,642,065 |
| all_injections | 611 | 1975-09 | 2026-07 | 241,425.6 | 15,000 (1976-01) | 578,952 (2025-05) | 342,068 |
| all_withdrawals | 611 | 1975-09 | 2026-07 | 238,115.6 | 2,000 (1977-09) | 1,104,195 (2025-01) | 199,860 |
| all_net_withdrawals | 611 | 1975-09 | 2026-07 | -3,313.2 | -497,260 (2025-05) | 1,007,992 (2025-01) | -142,207 |
| salt_base_gas | 391 | 1994-01 | 2026-07 | 129,794.5 | 37,195 (1994-01) | 220,105 (2025-08) | 213,067 |
| salt_working_gas | 391 | 1994-01 | 2026-07 | 184,476.2 | 36,864 (1994-02) | 402,434 (2016-11) | 295,973 |
| salt_total | 391 | 1994-01 | 2026-07 | 314,270.7 | 74,817 (1994-02) | 600,226 (2025-11) | 509,039 |
| salt_injections | 391 | 1994-01 | 2026-07 | 43,162.7 | 9,236 (1994-08) | 125,845 (2025-03) | 51,060 |
| salt_withdrawals | 391 | 1994-01 | 2026-07 | 42,140.7 | 4,874 (1994-05) | 199,900 (2025-01) | 94,617 |
| salt_net_withdrawals | 391 | 1994-01 | 2026-07 | -1,022.0 | -88,749 (2016-10) | 145,564 (2025-01) | 43,556 |
| non_salt_base_gas | 391 | 1994-01 | 2026-07 | 4,217,603.6 | 4,117,268 (2006-03) | 4,351,366 (1995-06) | 4,291,852 |
| non_salt_working_gas | 391 | 1994-01 | 2026-07 | 2,314,586.0 | 672,715 (2003-03) | 3,629,636 (2016-10) | 2,841,173 |
| non_salt_total | 391 | 1994-01 | 2026-07 | 6,532,187.0 | 4,919,981 (2001-03) | 7,865,973 (2025-10) | 7,133,025 |
| non_salt_injections | 391 | 1994-01 | 2026-07 | 230,273.8 | 16,781 (2010-02) | 490,186 (2001-05) | 291,007 |
| non_salt_withdrawals | 391 | 1994-01 | 2026-07 | 228,325.4 | 15,030 (1994-09) | 904,295 (2025-01) | 105,244 |
| non_salt_net_withdrawals | 391 | 1994-01 | 2026-07 | -1,948.4 | -463,858 (2001-05) | 862,428 (2025-01) | -185,764 |

MMcf; means rounded to one decimal.

- **Stocks and flows.** Base and working gas and the total are stocks at the month's end (the header); injections, withdrawals and net withdrawals are the month's flows. Net withdrawals are withdrawals less injections: negative in 363 months of all fields (a net injection), 230 of salt and 231 of non-salt.
- **Rounding.** EIA's earliest figures are rounded to the bcf (2,864,000 MMcf in December 1973; 15,000 and 2,000 MMcf in 1976 and 1977), so the parts and totals of some months differ by up to 1,072 MMcf (the cross-check below).
- **The split by type** begins in January 1994: 391 months for each of the twelve salt and non-salt series, none missing. Salt's share of working gas, a year's mean of its months: 3.6 percent in 1995, 4.5 in 2005, 10.2 in 2015, 10.3 in 2025.

## Placing values in time, and what is filled

`ts_utc` is the first day of EIA's `period` (YYYY-MM) at 00:00:00Z, a label for the month; for a stock it stands for the month's end. EIA's pages hold 8,550 records (its `total` on both pages: 5,000 and 3,550); 183 have no number (value null): the all-fields stocks (SAB, SAO, SAT, 29 each) and flows (SAI, SAW, SAN, 32 each), in 1973 (69), 1974 (66) and 1975 (48). Those have no row; nothing is filled. So the stocks begin in December 1973 and then lack 18 months, January to September 1974, November 1974 and January to August 1975 (only October and December 1974 have rows); the flows begin in September 1975. From September 1975 every month to July 2026 has a row in each all-fields series, and from January 1994 in each salt and non-salt series.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/eia_gas_storage_type_monthly.csv`, read past its 10 header lines (counted), and from the saved pages, read only (scripts `runs/c104/s2289/eia.py` and `eia_ext.py`, outputs `eia_storage_type.out`, `storage_type_ext.out` and `storage_type_gaps.out` beside them).

- 8,367 rows, months 1973-12 to 2026-07, "8,550 records of EIA's, 8,367 rows", as header line 3 states; 18 series, one variable each; no (entity, variable, ts_utc) twice; no blank value; unit MMcf throughout; each row's `node` is the page's series description; no series all zero or constant.
- **Against the pages:** EIA's `total` is 8,550 on both pages; the 8,367 records with a number and the table's keys and values are the same, with 0 differences; the 183 without one are those listed above.
- **The trial against the table:** `runs/c104/s2283/trial/eia_gas_storage_type_monthly.csv` has the same rows past its header, byte for byte, `retrieved_at` included; the headers differ only in the run's name, its log and "2 requests of 10" against "0 requests of 10".
- Session 2283's cross-check (`runs/c104/s2283/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/storage_type_cross.out`): identical to the saved `cross.out`, which was run on the trial. Salt plus non-salt against all fields over 391 months: largest gaps 1 (base gas), 107 (working gas), 996 (total), 279 (injections), 1,072 (withdrawals) and 1,072 MMcf (net withdrawals); base plus working against total 1,000 (all, 614 months), 1 (salt), 1,000 (non-salt); withdrawals less injections against net 1,000 (all, 611 months), 1 and 1; the U.S. working gas against `eia_gas_storage_state_monthly`'s U.S. total over 307 months: largest gap 0 MMcf; salt's share 3.6, 4.5, 10.2 and 10.3 percent (1995, 2005, 2015, 2025).

## Where the description and the data disagree

1. **"A month from 1973" begins in December 1973, with a gap after it.** The docstring describes the table as "the U.S., a month from 1973", and the route's metadata starts at 1973-01. EIA gives no number for January to November 1973, so the first row is December 1973; the stocks then lack 18 of the 20 months from January 1974 to August 1975 and the flows begin in September 1975. Header line 3's "Months 1973-12 to 2026-07" and "A blank has no row" are right; a reader expecting every month from the first should not.
2. **The reads' numbers in the report's file list.** The report's text gives CAMMESA's robots requests as reads 477 and 478; its file list says "`warehouse/metadata/license_reads.csv` (446, 447)". Since the merge of chain 102 (commit ef284545) they are 477 and 478. They concern CAMMESA, not this table.

Compared besides, with no contradiction found: the header's and docstring's counts, span, series, processes, area, unit, the stocks and flows, "salt plus non-salt is all fields" (within EIA's rounding), "Each row carries the time EIA served its page" and "nothing is filled" against the rows and the pages.

Not acted on: this note changes no file but itself.

Acted on in session 2289: the connector's docstring now says the series start in December 1973 with gaps in 1974 and 1975 where EIA gives none. The rows are unchanged.

## The session report against the table

Every figure of `SESSION_2283_REPORT.md` checked against the table, the saved pages and the rerun cross-check holds (December 1973 to July 2026, 8,367 rows, 18 series, MMcf, base gas, working gas, total, injections, withdrawals and net withdrawals for all fields, salt and non-salt, each row carrying the time EIA served its page, 391 months with the split, the largest gap 1,072 MMcf, the U.S. working gas equal to `eia_gas_storage_state_monthly`'s in all 307 months, salt's share 3.6 percent in 1995 and 10.3 in 2025, the route's metadata 1973-01 to 2026-07, 4 requests to EIA, the write reusing the trial's two pages), except:

- Files: "`license_reads.csv` (446, 447)": renumbered 477 and 478 at the merge (disagreement 2).

## What it does not hold

- Storage by region or state (`eia_gas_storage_state_monthly`), the weekly report (`eia_gas_storage_weekly`), storage capacity (`eia_gas_storage_capacity_monthly`), the number of fields, the route's annual figures, the split by type before 1994, months before December 1973 and after July 2026, and LNG storage (`eia_lng_storage_annual`).
