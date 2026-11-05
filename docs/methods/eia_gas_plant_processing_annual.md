# Natural gas plant processing a year, 1967 to 2024: gas processed, extraction loss and liquids extracted, for the U.S., the states, the federal offshore and EIA's pairs of producing and processing areas (EIA, Natural Gas Annual)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2287 of chain 104, its report `archive/sessions/SESSION_2287_REPORT.md`).

Tables: `eia_gas_plant_processing_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Annual, natural gas plant processing, through EIA's API v2, route `natural-gas/prod/pp` (the route's metadata, `runs/c104/s2287/meta.json`, names its parent "EIA natural gas survey data" and gives monthly and annual frequencies, 1973-01 to 2026-07; the annual records begin in 1967). The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/prod/pp/`; the access line is `https://api.eia.gov/v2/natural-gas/prod/pp/data/?frequency=annual&data[]=value&facets[process][]=YGP&facets[process][]=VG9&facets[process][]=YGT&start=1967`, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:natural-gas/prod/pp`.

Three processes, as the pages name them: YGP "Natural Gas Processed" and VG9 "Extraction Loss" (product EPG0 "Natural Gas", unit "MMCF"), and YGT "Total Liquids Extracted - State of Origin" (product EPL0 "Natural Gas Liquids and Liquid Refinery Gases", unit "MBBL"). 94 area codes: NUS (the U.S.), 26 states (S<state>), the federal offshore Gulf (R3FM, "Gulf of America" in EIA's descriptions), and pairs of a producing area and a processing area (S<state>-S<state>, R3FM-S<state>, R5F-SCA, and EIA's onshore and offshore parts of five states, such as RTXO-STX "Texas Onshore ... in Texas"); every pair and R area has `area-name` "NA" on the pages but one record (RTXO-SLA, "USA-LA"). Session 2287's sample (`runs/c104/s2287/sample.json`, 2023 and 2024 asked without facets) held 531 records: these three processes, 177 each, over 89 areas. The two data pages are in `warehouse/raw/eia_gas_plant_processing/20261024T052500Z/`. No page of EIA's was saved under `runs/license_reads/` for this table; EIA's verdict is read 1.

Connector: `warehouse/connectors/eia_gas_plant_processing.py` (session 2287): `[--from 1967] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. An area code not of EIA's forms (NUS, S<state>, an R area, or either followed by -S<state>), a process or unit not in its map, or a key given twice stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

The two pages were fetched by session 2287's trial (run `20261024T052500Z`) at 2026-10-24T05:25:04Z and 05:25:08Z (the raw manifest). The table was written at run `20261024T052602Z` from them ("0 requests of 10"): "File holds 5829 rows, one snapshot; the previous file held 0 rows." `retrieved_at` is the time EIA served each row's page (05:25:04Z on 4,993 rows, 05:25:08Z on 836); `vintage` is blank.

EIA's pages carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 5,829 rows, 276 entities `eia_gas_plant_processing:<series>` (EIA's series id; two Idaho series, SID-SID and SID-Z00 of YGP, share one description, so 275 distinct `node` values), `freq` P1Y, `market` blank, `node` EIA's series description. Every value is a whole number.

| Variable | Process | Unit | Rows | Entities | Years | Zeros |
|---|---|---|---|---|---|---|
| gas_processed | YGP | MMcf | 2,075 | 92 | 1967 to 2024 | 111 |
| extraction_loss | VG9 | MMcf | 2,030 | 92 | 1967 to 2025 | 76 |
| liquids_extracted | YGT | kbbl | 1,724 | 92 | 1983 to 2024 | 39 |

The entities by area: the U.S. 3 (geo US), the 26 states 78 (geo US-<state>), pairs of two states 129 (geo the first state's: 57 within one state, such as SKS-SKS, and 72 across two), the federal offshore 18 (R3FM, R3FM-S<state> and R5F-SCA; geo US), and the onshore and offshore parts of Alabama, Alaska, California, Louisiana and Texas 48 (RTXO-STX and the like; geo US). In a pair the first area is where the gas was produced and the second where it was processed: SWY-SCO is "Wyoming Natural Gas Processed in Colorado".

The U.S. (MMcf, but liquids in kbbl):

| Series | First year | 1970 | 1990 | 2010 | 2024 | Lowest (year) | Highest (year) |
|---|---|---|---|---|---|---|---|
| gas processed (NA1180_NUS_2) | 1967: 15,641,633 | 18,509,309 | 14,610,303 | 16,267,757 | 27,088,079 | 12,794,932 (1988) | 27,088,079 (2024) |
| extraction loss (N9060US2) | 1967: 784,534 | 906,413 | 784,118 | 1,066,366 | 3,658,962 | 761,944 (1982) | 3,941,527 (2025) |
| liquids extracted (NA1720_NUS_1) | 1983: 569,968 | | 573,054 | 749,095 | 2,563,303 | 569,913 (1989) | 2,563,303 (2024) |

- **Levels overlap.** The U.S., a state and its pairs, and the federal offshore are levels of one another (the header: "a sum takes one level"). The 26 states' own totals are 0.925 to 1.000 of the U.S. for gas processed and 0.930 to 1.000 for extraction loss; adding the federal offshore Gulf (R3FM, given from 2012 for gas processed and 2007 for extraction loss) brings them to 1.000 in every year it is given (session 2289, from the pages).
- **Extraction loss** is the gas volume removed as liquids; EIA's descriptions of the U.S. and state series call it "Natural Gas Plant Liquids Production (Million Cubic Feet)", the page's process name "Extraction Loss".
- **A series of zeros.** RTXSF-STX ("Texas Offshore ... Extracted in Texas") has 8 rows of extraction loss, 2017 to 2024, all 0; its gas processed and liquids extracted are 0 in 8 of 9 rows. 46 series have at least one zero.
- **Single rows.** Nine series hold one value only (RTXO-SLA, RTXSF-SLA for 2015; RALO-SFL for 2024; and their three measures).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z (EIA's `period`, YYYY), a label for the calendar year. EIA's pages hold 5,836 records (its `total` on both pages: 5,000 and 836); 7 have no number (value null): RTXSF-STX's three measures in 2014, its extraction loss in 2015, and RALSF-SAK's three measures in 2015. Those have no row; nothing is filled.

Years missing inside a series's span are records EIA does not give at all, not blanks: 1979 and 1980 in 22 series (the U.S. gas processed and 21 states' gas processed), and 131 years in all over 43 series, most of them pairs that appear and disappear. Liquids extracted begin in 1983; the only 2025 row is the U.S. extraction loss (N9060US2), whose 59 years 1967 to 2025 are complete.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/eia_gas_plant_processing_annual.csv`, read past its 10 header lines (counted), and from the saved pages, read only (scripts `runs/c104/s2289/eia.py`, `eia_ext.py` and `plant2.py`, outputs `eia_plant.out`, `plant_ext.out` and `plant2.out` beside them).

- 5,829 rows, years 1967 to 2025, "5,836 records of EIA's, 5,829 rows", as header line 3 states; 276 series; no (entity, variable, ts_utc) twice; no blank value; units MMcf (gas processed, extraction loss) and kbbl (liquids extracted), as the header names them; geo US on 69 series and US-<state> on 207; each row's `node` the page's series description.
- **Against the pages:** EIA's `total` is 5,836 on both pages; the 5,829 records with a number and the table's keys and values are the same, with 0 differences; the 7 without one are those listed above.
- **The trial against the table:** `runs/c104/s2287/trial/eia_gas_plant_processing_annual.csv` has the same rows past its header, byte for byte, `retrieved_at` included; the headers differ only in the run's name, its log and "2 requests of 10" against "0 requests of 10".
- Session 2287's cross-check (`runs/c104/s2287/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/plant_cross.out`): identical to the saved `cross.out`, which was run on the trial. The U.S. series: gas processed 56 rows, extraction loss 59, liquids extracted 42, with the 1970, 1990, 2010 and 2024 values above; the states' single totals against the U.S.: gas processed 56 years, 0.925 to 1.000 (2024 0.980); extraction loss 58 years, 0.930 to 1.000 (2024 0.979). It found no supply and disposition table holding N9060US2; `eia_gas_balance_annual` holds none of the three U.S. series (session 2289, no match for their ids or for "processed", "extraction" or "plant liquids").

## Where the description and the data disagree

1. **Not every R area is federal offshore.** The docstring gives "geo US for the U.S. and EIA's federal offshore areas". 18 series are federal offshore (R3FM, R5F); 48 are EIA's onshore and offshore parts of Alabama, Alaska, California, Louisiana and Texas (RAKO, RALO, RALSF, RCAO, RCASF, RLAO, RLASF, RTXO, RTXSF, paired with a state), whose descriptions name the state ("Texas Onshore Natural Gas Processed in Texas") but whose geo is US. Texas' own processing by pair is therefore under geo US, not US-TX (the state total NA1180_STX_2 is US-TX).
2. **A pair's first state is where the gas came from.** The docstring describes a pair as "EIA's processing and origin areas: geo is the first state's", and the report as "a processing state and an origin state". EIA's descriptions put the producing state first and the processing state second ("Wyoming Natural Gas Processed in Colorado" for SWY-SCO), so a pair's geo is the producing state, not the processing one.
3. **Years missing are not blanks.** Header line 3 says "A blank has no row; nothing is filled". That covers the 7 null records; the 131 years missing inside 43 series's spans, among them the U.S. gas processed in 1979 and 1980, are years EIA gives no record for. A reader summing the states over 1967 to 2024 finds two years absent.

Compared besides, with no contradiction found: the header's and docstring's counts, years, processes, units, "a sum takes one level", the area forms the connector accepts (every area on the pages is of them), "Each row carries the time EIA served its page" and the one 2025 row against the rows and the pages.

Not acted on: this note changes no file but itself.

Acted on in session 2289: the geo now follows EIA's codes. A state's onshore or state offshore part (R<state>O, R<state>SF) takes the state's geo. The federal offshore (R3FM, R5F) stays US. A pair's geo is its first, producing area's, and the docstring now says the second is where the liquids were extracted. The table was written again offline (the same rows, geo corrected). The years EIA does not give are recorded.

## The session report against the table

Every figure of `SESSION_2287_REPORT.md` checked against the table, the saved pages and the rerun cross-check holds (1967 to 2024 with one 2025 row, the U.S. extraction loss, 5,829 rows, 276 series, MMcf and kbbl, the U.S., the states, EIA's offshore areas and pairs, each row carrying the time EIA served its page, the states' totals 0.925 to 1.000 of the U.S. for gas processed over 56 years and 0.980 in 2024, 0.930 to 1.000 for extraction loss and 0.979 in 2024, "the rest is EIA's offshore areas" (the states and R3FM come to 1.000), 18.5 trillion cubic feet in 1970, 14.6 in 1990 and 27.1 in 2024, liquids 573 million barrels in 1990 and 2,563 in 2024, none of these series in `eia_gas_balance_annual`, 4 requests of 20, the write reusing the trial's two pages), except:

- "EIA's pairs of a processing state and an origin state. A pair's geo is its first state.": the first state is the origin, so geo is the producing state (disagreement 2).
- "For the U.S., the states, EIA's offshore areas, and EIA's pairs": 48 series are the onshore and offshore parts of five states, with geo US (disagreement 1).

## What it does not hold

- The months the route offers from 1973, the number of plants and their capacity, the liquids by kind (ethane, propane and the rest), the years and pairs EIA gives no record for, and anything after 2024 but the U.S. extraction loss of 2025.
