# Uzbekistan's electricity production by region, 2010 to 2024, its solar and wind production, 2015 to 2024, and its electricity consumption by subscribers by region, 2016 to 2025, a year (National Statistics Committee of the Republic of Uzbekistan, SIAT open data)

Energy Research Warehouse (ERW), method note written in session 2452 (chain 118) for a table first written on 24 October 2026 (session 2451 of chain 118, its report `archive/sessions/SESSION_2451_REPORT.md`).

Tables: `siat_uzbekistan_electricity_annual`

## Publisher and address

The National Statistics Committee of the Republic of Uzbekistan, its open data portal SIAT (`siat.stat.uz`), four indicator files in JSON, four requests:

- `https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_440.json`, indicator 1.02.02.0004, "Volume of electricity production"
- `https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_446.json`, 1.02.02.0006, "Volume of electricity produced by solar power plants"
- `https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_458.json`, 1.02.02.0007, "Volume of electricity produced by wind power farms"
- `https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2684.json`, 1.02.02.0019, "Volume of electricity consumption by subscribers"

Source id `siat:electricity`. Each file is a list of one indicator with two parts. `data` holds a row per area, keyed `Code` (a four-digit code of the classifier the files name "Departmental classifier Designation system for administrative-territorial entities of the Republic of Uzbekistan"; the header calls it SOATO, a name the files do not use), the area's name in four scripts (`Klassifikator`, `_ru`, `_en`, `_uzc`), and a key a year. 440 and 2684 have 15 rows (the republic, code 1700, and 14 areas: the Republic of Karakalpakstan, 12 regions and Tashkent city); 446 and 458 the republic only. The wind file has a key "2022.1" between "2016" and "2017", 0.0 like "2022". `metadata` holds the indicator's record: first publication (2022-06-28 for 440 and 446, 2022-06-29 for 458, 2023-03-02 for 2684), last modified date (2025-09-03 for 440, 446 and 458; 2026-09-02 for 2684), code, name, periodicity "Аnnual", unit "Million kWt hour", the classifier (440 and 2684), a link "Calculation methodology" to a page of `lib.stat.uz` (not read), the preparer ("National Statistics Committee of the Republic of Uzbekistan"), the department ("Department of Industry and Energy Statistics"; 446: "Department of industrial statistics"), a staff member's name, telephone and email (not copied here), "Primary source of information: Reports", a note, and "Calculation methodology (briefly)".

The notes, as written:

- 440: "2010-2022 annual final indicators, 2023 year preliminary data, Republic of Uzbekistan (including unallocated data by region)"
- 446 and 458: "2015-2022 annual final indicators, 2023 year preliminary data, information has been collected since 2015"
- 2684: "2016-2022 annual final indicators, 2023 year preliminary data, information has been collected since 2016, gross electricity consumption"

No note speaks of 2024, which all four files hold, or of 2025, which 2684 holds (point 2). "Calculation methodology (briefly)" is the same text in all four and concerns industrial production in general: it is "compiled by type of product" under the classifier O'zDSt 2914:2014 for sections B to E, from state statistical reporting of legal entities, quarterly sample observations of small enterprises and microfirms, quarterly sample surveys of individual entrepreneurs "according to data from the state tax service", and surveys of households and individual entrepreneurs. Nothing in the files defines "consumption by subscribers" or says what "gross" covers (point 3).

Indicator 440's page (`https://siat.stat.uz/data/440/?lang=en`, read 836; "Updated: 2025-09-03") shows the same table, the same metadata, a dataset record naming `"license": "https://creativecommons.org/licenses/by/4.0/"` and `"temporalCoverage": "2010/2024"`, and the lines "Manba: Oʻzbekiston Respublikasi Statistika agentligi" and "Litsenziya: CC BY 4.0". The pages of 446, 458 and 2684 were not requested (point 1).

Session 2451's probe (`runs/c118/s2451/probe.csv`) made 12 requests: stat.uz's robots file (12:44:53Z, read 834), siat.stat.uz's (12:45:13Z, read 835), indicator 440's page (12:45:22Z, read 836), api.siat.stat.uz's robots file (12:45:30Z, read 837), the four download pointers (`https://api.siat.stat.uz/sdmx/<id>/table/download/?download_format=json`, 12:45:38Z to 12:45:41Z, reads 838 to 841), each naming its file, an import copy, an update time and a staff member's address, and the four files (reads 842 to 845): 440 at 12:45:50Z (19,334 bytes, Last-Modified "Mon, 30 Mar 2026 12:52:48 GMT"), 446 at 12:45:52Z (12,566 bytes, "12:52:49 GMT"), 458 at 12:45:53Z (12,642 bytes, "12:52:50 GMT") and 2684 at 12:45:54Z (18,487 bytes, "Wed, 02 Sep 2026 09:39:59 GMT"). All are saved in `runs/license_reads/s2451/`, each with the probe log's SHA-256 (checked in this session). The write read the files offline ("raw file reused", run log).

Connector: `warehouse/connectors/siat_uzbekistan.py` (session 2451): `[--offline] [--out-dir DIR]`, four requests, 2 seconds apart when asked. An area is matched by its English name to a fixed map of 15 names, each with an ISO 3166-2 code; the entity is built from the file's `Code`. Only keys of four digits are years, so "2022.1" is not taken. Checks, each stopping the run: the indicator's code and unit are as expected; an area not in the map; a value that is not a number; the areas adding to more than the republic by more than 1 GWh. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is in the release's held list (`warehouse/redivis/release_v1.py`, among the tables marked "held: not yet on Redivis ... In v1 by its license once uploaded").

## Vintage and revision

One write, run `20261024T124726Z` ("This run wrote 395 rows: 395 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved files; the report records no separate trial. Each row's `source_url`, `retrieved_at` and `vintage` are its file's: `generation` 225 rows (retrieved 2026-10-24T12:45:50Z, `vintage` 2026-03-30T12:52:48Z), `generation_solar` 10 (12:45:52Z, 12:52:49Z), `generation_wind` 10 (12:45:53Z, 12:52:50Z), `consumption` 150 (12:45:54Z, 2026-09-02T09:39:59Z). The `vintage` is the server's Last-Modified, which matches each pointer's update time (30 March 2026, 17:52 at UTC+5, for the first three), not the record's "Last modified date" (2025-09-03).

By the notes, 2010 (or 2015, 2016) to 2022 are final and 2023 preliminary; 2024 and 2025 are not described. A later run asks the four addresses again and merges by (entity, variable, ts_utc), so a revised year replaces the old.

## Shape and variables

Series, 395 rows, 15 entities, `unit` MWh throughout (the files' "Million kWt hour", read as million kWh, times 1,000), `freq` P1Y, `market` blank, and a column `x_region_code` holding the file's code. `siat:UZ` (`geo` UZ, `node` "Republic of Uzbekistan", code 1700) and 14 areas `siat:UZ:<code>`:

| Code | Node (Klassifikator_en) | geo |
|---|---|---|
| 1735 | Republic of Karakalpakstan | UZ-QR |
| 1703 | Andijan region | UZ-AN |
| 1706 | Bukhara region | UZ-BU |
| 1708 | Jizzakh region | UZ-JI |
| 1710 | Kashkadarya region | UZ-QA |
| 1712 | Navoi region | UZ-NW |
| 1714 | Namangan region | UZ-NG |
| 1718 | Samarkand region | UZ-SA |
| 1722 | Surkhandarya region | UZ-SU |
| 1724 | Syrdarya region | UZ-SI |
| 1727 | Tashkent region | UZ-TO |
| 1730 | Fergana region | UZ-FA |
| 1733 | Khorezm region | UZ-XO |
| 1726 | Tashkent city | UZ-TK |

The ISO 3166-2 codes are the connector's; no file read gives them. They agree with ISO 3166-2:UZ as this note's writer knows it (UZ-QR for Qoraqalpog'iston, UZ-TK for Toshkent city and UZ-TO for the region, UZ-NW for Navoiy, UZ-XO for Xorazm, UZ-QA for Qashqadaryo, UZ-SI for Sirdaryo, UZ-SU for Surxondaryo); the ISO's own list was not read in this session. Each code and name pair is the same in 440 and 2684.

| Variable | Rows | The file |
|---|---|---|
| generation | 225 | 440, 15 entities, 2010 to 2024 (12 zeros: Jizzakh region in 2010 to 2015 and 2018 to 2022, Namangan region in 2018) |
| generation_solar | 10 | 446, the republic, 2015 to 2024 |
| generation_wind | 10 | 458, the republic, 2015 to 2024 (6 zeros: 2015 to 2018, 2020, 2022) |
| consumption | 150 | 2684, 15 entities, 2016 to 2025 |

The republic, million kWh as the files give them (`runs/c118/s2452/notes/uz.out`); the table holds each times 1,000 in MWh:

| Year | Production | Not allocated to an area | Solar | Wind | Consumption by subscribers | Consumption below production (%) |
|---|---|---|---|---|---|---|
| 2016 | 59,100.5 | 19.8 | 0.3 | 0.0 | 45,058.7 | 23.8 |
| 2017 | 60,820.1 | 34.1 | 0.7 | 0.0 | 46,746.4 | 23.1 |
| 2018 | 62,896.6 | 5.5 | 0.2 | 0.0 | 60,744.7 | 3.4 |
| 2019 | 63,531.6 | 31.7 | 0.1 | 15.5 | 54,174.7 | 14.7 |
| 2020 | 66,500.7 | 17.0 | 0.03 | 0.0 | 53,839.9 | 19.0 |
| 2021 | 71,364.6 | 0.4 | 49.0 | 1.2 | 56,268.8 | 21.2 |
| 2022 | 74,269.3 | 0.6 | 435.8 | 0.0 | 59,109.2 | 20.4 |
| 2023 | 78,005.4 | 0.6 | 622.4 | 7.2 | 62,836.3 | 19.4 |
| 2024 | 82,739.7 | 0.6 | 3,965.2 | 789.6 | 65,490.5 | 20.8 |
| 2025 | | | | | 63,746.0 | |

Production is 51,976.3 million kWh in 2010, with nothing unallocated in 2010 to 2012, 0.4 in 2013, 24.5 in 2014 and 18.6 in 2015. Solar is 0.003 million kWh (3 MWh) in 2015.

- **The areas' consumption adds exactly to the republic's** in every year 2016 to 2025; production's areas fall short by the unallocated part above, never exceed it.
- **Production by area moves with new plants:** Namangan region from 0.0 in 2018 to 456.1 in 2019 and 5,624.6 in 2020; Bukhara region from 7.4 in 2021 to 1,578.3 in 2022; Tashkent city from 480.6 in 2021 to 6,273.4 in 2024. The largest in 2024 are Tashkent region (20,003.2), Syrdarya region (17,532.8), Navoi region (10,847.1) and Kashkadarya region (10,099.9).
- **2018's consumption is out of line in nearly every area.** The republic's 60,744.7 against 46,746.4 in 2017 and 54,174.7 in 2019; against the mean of its two neighbours, 2018 is 2.46 times in Surkhandarya region (5,653.0 against 2,230.9 and 2,364.3), 1.51 in Andijan region, 1.47 in Samarkand region, between 1.00 and 1.32 in the ten others, and below 1 only in Navoi region (0.94). The file marks nothing (point 4).
- **Solar and wind arrive in 2024:** 3,965.2 and 789.6 million kWh, 4.8 and 1.0 percent of production.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year, 2010-01-01 to 2025-01-01. Every value is the year's energy. A null or empty value would have no row; the four files have none in the keys taken. Zeros are kept as published. Nothing is filled; the republic's figure is never derived from its areas.

## License

Header: "License: public, CC BY 4.0 (each indicator's page). Source: National Statistics Committee of the Republic of Uzbekistan, siat.stat.uz." Indicator 440's page (read 836) reads "Litsenziya: CC BY 4.0" and its dataset record names `https://creativecommons.org/licenses/by/4.0/`; its source line reads "Manba: Oʻzbekiston Respublikasi Statistika agentligi" (point 6). The JSON files carry no license field. Robots: stat.uz's file (read 834) disallows Joomla's system paths only; siat.stat.uz's and api.siat.stat.uz's (reads 835 and 837, the same 447 bytes) name GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Applebot-Extended and CCBot, each "Allow: /", then "User-agent: *", "Allow: /". `warehouse/metadata/license_verdicts.csv`: the committee (SIAT), read 836, verdict "may be public", the same if the ERW sells anything. `warehouse/metadata/license_reads.csv` records reads 834 to 845 (session 2451). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", if the ERW sells anything "may be public", ERW verdict public.

## Checks (session 2452)

The figures in this note were computed from the rows of `warehouse/output/siat_uzbekistan_electricity_annual.csv`, read past its 10 header lines (counted), and from the four saved files and the saved page, read only from their bytes with Python's `json` (script `runs/c118/s2452/notes/uz.py`, output `uz.out` beside it; the files' metadata was read in a scratch folder outside the repository so that no name or address is kept in it).

- 395 rows, 15 entities, 4 variables, 2010 to 2025, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; no blank value.
- **Against the files:** an independent read of every year key of the four files gives exactly the table's 395 keys and values, times 1,000 (0 missing, 0 extra, 0 differences); "2022.1" is the only key not taken.
- **Areas against the republic:** production's republic less its areas is 0 to 34.1 million kWh (by year above), never negative; consumption's is 0 in every year.
- Session 2451's cross-check (`runs/c118/s2451/cross.py`, `cross.out`): production against `owid_ember_electricity_annual`'s Uzbekistan demand in 2016, 2018, 2020, 2022, 2023 and 2024: 3.3, 0.2, -3.7, -4.0, -2.2 and -2.0 percent (2024: 82.74 against 84.43 TWh). Consumption by subscribers is 21.2 to 23.6 percent below Ember's demand in 2020, 2022, 2023 and 2024 (2024: 65.49 against 84.43 TWh; this note's arithmetic on `cross.out`, which prints no 2021).

## The session report against the table

Every figure of `SESSION_2451_REPORT.md` checked against the table, the files and `cross.out` holds (395 rows, 15 entities, the four indicators and their years, MWh from "Million kWt hour", the notes as carried, the unallocated part at most 34.1 GWh with 19.8 in 2016 and 0.6 in 2022 to 2024, "2022.1" with both 0.0, wind 789.6 million kWh in 2024, reads 834 to 845, the robots files, within 4.0 percent of Ember, 3.3 above in 2016 and 2.0 below in 2024, 82.74 against 84.43 TWh, consumption 15 to 24 percent below production except 2018 (14.7 to 23.8), 60.74 against 62.90, 46.75 and 54.17 TWh, 12 requests of 15, the files 13 to 19 KB), except:

- "Each indicator page reads \"Litsenziya: CC BY 4.0\"": only 440's page was read (point 1).

## Limits

- **Consumption by subscribers is not gross supply.** It lies about a fifth below production in most years; what it leaves out (losses, own use, or more) the files do not say.
- **2024 and 2025 are undescribed** by the notes, and 2023 is preliminary.
- **Unallocated production** sits in the republic's figure only (up to 34.1 million kWh), so the areas do not add to it in 2013 to 2024.
- **Solar and wind for the republic only;** no other kind of plant, no capacity.

## What it does not hold

- Production by other kinds of plant, imports, exports, losses, capacity, any month, and SIAT's other energy indicators.

## Points for the session to act on

1. **Only one indicator page was read for the license.** The header reads "License: public, CC BY 4.0 (each indicator's page)", the docstring "(each indicator page: \"Litsenziya: CC BY 4.0\")", and the report "Each indicator page reads \"Litsenziya: CC BY 4.0\" ... (read 836)". The probe requested indicator 440's page only; the pages of 446, 458 and 2684 were not read, and the JSON files carry no license field. Either the three pages are read (three requests) or the header says the license was read on indicator 440's page.
2. **The notes stop at 2023; the files go further.** Header line 3 carries the notes ("2023 year preliminary data") without comment. All four files hold 2024 and the consumption file 2025, and no note describes those years, though the records were last modified on 2025-09-03 and 2026-09-02. The header could say that 2024 (and 2025 for consumption) carry no status in the files and are best read as preliminary.
3. **"Gross electricity consumption" is SIAT's word; the figures are not gross supply.** Header line 2 gives `consumption` as "gross electricity consumption by subscribers", and the docstring "gross electricity consumption". The indicator is "consumption by subscribers"; it lies 19.0 to 23.8 percent below production in 2016, 2017 and 2020 to 2024 (14.7 in 2019, 3.4 in 2018) and 21.2 to 23.6 percent below Ember's demand in 2020, 2022, 2023 and 2024, so it is not production plus imports less exports. No file defines it, and the methodology link was not read. The header could say that it is electricity consumed by subscribers, about a fifth below production, and that the files do not say what "gross" includes.
4. **2018's consumption is out of line, and the header does not say so.** The report notes it (60.74 against 46.75 and 54.17 TWh); the table's header does not. Thirteen of the 14 areas are above the mean of 2017 and 2019, Surkhandarya region 2.46 times. The header could flag 2018 as printed by SIAT and unexplained.
5. **The docstring's unallocated examples leave out the largest.** It reads "(production: 19.8 GWh in 2016, 0.6 GWh in 2022 to 2024)". The part is 0 in 2010 to 2012, 0.4 in 2013, 24.5 in 2014, 18.6 in 2015, 19.8 in 2016, 34.1 in 2017, 5.5 in 2018, 31.7 in 2019, 17.0 in 2020, 0.4 in 2021 and 0.6 in 2022 to 2024 (million kWh); the header gives the largest (34.1). The docstring could give the range or the largest.
6. **The page's source line names the Statistics Agency.** Indicator 440's page, under which the CC BY 4.0 license is stated, reads "Manba: Oʻzbekiston Respublikasi Statistika agentligi" (Source: the Statistics Agency of the Republic of Uzbekistan), while its metadata names the "National Statistics Committee of the Republic of Uzbekistan" as preparer; the header and `sources.csv` cite only the committee. For the attribution CC BY asks, the header could give the source as the page states it.

Compared besides, with no contradiction found: the header's and docstring's counts, years, the factor of 1,000, the four indicators, codes and names, "the republic only" for solar and wind, "Zeros are kept as published", "wind is 0.0 in most years to 2022" (6 of 8), the "2022.1" key, the regions as parts of the republic, the area names and codes, `retrieved_at` and `vintage` against the probe log, the robots files as described, and every row against the files.

Acted on in session 2452: the docstring and header now say that only indicator 440's page was read for the license and that the files carry none; name the page's source line (the Statistics Agency); quote the consumption indicator's own name and say that it is undefined and well below production; flag 2018's consumption; say that the files' notes stop at 2023; and give the largest unallocated parts. Session 2451's report is corrected on the license pages. The table was written again offline: the same rows.
