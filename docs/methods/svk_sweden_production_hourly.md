# Svenska kraftnät's settled production for all of Sweden, an hour by production type, 1 January 2020 to 18 March 2025 (Mimer)

Energy Research Warehouse (ERW), method note written in session 2353 (chain 105) for a table first written on 24 October 2026 (session 2351, `archive/sessions/SESSION_2351_REPORT.md`, "Sweden's production an hour by type (Svenska kraftnät's Mimer), a second source of the session's own choosing"; commit `6c98467a`). Statistics Sweden's monthly balance is `scb_sweden_electricity_monthly` (`docs/methods/scb_sweden_electricity_monthly.md`); Eurostat's monthly net production, the table this one is checked against, is `eurostat_electricity_monthly`. The table is closed history: Mimer's production statistics stop in March 2025, and the days after go to eSett (below).

Tables: `svk_sweden_production_hourly`

## Publisher and address

Svenska kraftnät, Sweden's transmission system operator, Mimer, Produktionsstatistik, `https://mimer.svk.se/ProductionConsumption/ProductionIndex`. Six GET downloads, one a production type, area SN0 (Hela Sverige), `https://mimer.svk.se/ProductionConsumption/DownloadText?PeriodFrom=01%2F01%2F2020%2000%3A00%3A00&PeriodTo=03%2F18%2F2025%2000%3A00%3A00&ConstraintAreaId=SN0&ProductionSortId=<type>`, the type `KK` (Kärnkraftproduktion), `OK` (Övrig värmekraftproduktion), `OP` (Uppmätt ospecificerad produktion), `SE` (Solenergiproduktion), `VA` (Vattenkraftproduktion) or `VI` (Vindkraftproduktion). Each answer is `text/csv`, UTF-8 with a byte order mark, semicolons, decimal commas: the line `Period;Avräknad (kWh);Publiceringstidpunkt;`, 45,696 hour lines and one `Summa` line. Source id `svk:mimer_production_statistics`; `sources.csv`: publisher Svenska kraftnat, report "Mimer, Produktionsstatistik (production statistics), all of Sweden", document list `https://mimer.svk.se/`, license internal, first and last seen 2026-10-24.

The six files, 1,974,722 to 2,155,894 bytes, HTTP 200, no `Last-Modified`, were fetched from 06:45:09Z to 06:46:04Z on 24 October 2026 by session 2351's probe (`runs/c105/s2351/probe.py`, rows 4 to 9 of `probe.csv`). They are saved in `warehouse/raw/svk_sweden/20261024T064433Z_probe/`, and the same bytes in `runs/license_reads/s2351/`. The run that wrote the table, `20261024T065055Z`, read them offline ("raw file reused", `warehouse/output/logs/svk_sweden_20261024T065055Z.log`); its raw folder holds only the data lock's check, and `20261024T065015Z` (the trial) an empty manifest.

Connector: `warehouse/connectors/svk_sweden.py` (session 2351), `--offline` and `--out-dir`. It asks `iso_prices.paused` and `iso_prices.paused_host("mimer.svk.se")` first; neither names Svenska kraftnät. It stops if a file's first line is not the one above, if a figure is blank, if a file has no `Summa` line or its rows do not sum to it (to 1 kWh), if an hour comes twice, or if a day has other than 24 hours. Values are kWh divided by 1,000, rounded to 6 decimals; `ts_utc` is the label less one hour. The file is a snapshot. Ceiling: six requests.

Schedule: none, and none is needed while Mimer's statistics stay closed. No run script, workflow or step of `warehouse/scheduled.py` names the connector.

`run_status.csv`: no row (the run wrote `runs/status/svk_sweden.json`, run `20261024T065055Z`, "ok", "274176 rows"; disagreement 6). `archive_manifest.csv`: 274,176 rows, run `20261024T065110Z-local`, data hash `5f62b27c...`, which equals the hash of the file on this machine. `redivis_uploads.csv`: no row. Live set: in `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded, not in the live catalogue). Readers: none; `build_coverage.py` gives it the sector `power`, and `tests/test_session2351.py` tests the parse (3 tests).

## Vintage and revision

One retrieval of each file, so one `retrieved_at` a variable (06:45:09Z for nuclear to 06:46:04Z for wind). `vintage` is blank in every row. Mimer prints a publication time for every hour, `Publiceringstidpunkt`, which the table keeps as printed in `x_published` (`YYYY-MM-DD HH:MM`; its clock is not stated; disagreement 5).

What the publication times show, with each lag measured from the hour's end on the labels' clock (Swedish normal time):

- **3,677 distinct times,** from 2020-01-02 05:01 to 2025-03-30 12:00. No hour was published before it ended.
- **Most hours were published more than a week after the hour:** 186,993 of 274,176 (68.2 percent); 34,958 (12.8 percent) more than 31 days after, and 1,610 more than 90 days after. The lag: 10th percentile 0.75 days, median 10.83, 90th percentile 38.79, longest 119.12.
- **By type:** nuclear is fast (median 0.67 days, longest 12.54; 174 hours over a week); solar is never published within a week (shortest 7.42 days, median 12.83). In between: hydro (median 11.96 days; 44,084 hours over a week), wind (11.54; 44,414; longest 119.12), other thermal (8.88; 27,978) and unspecified measured (7.75; 24,647).
- **One time an hour.** The files carry one publication time for each hour, presumably the newest; an earlier publication of the same hour is not in them.
- **Batches over months already published.** Several times cover long stretches of hours already weeks or months old:
  - 2023-03-10 03:01 carries 6,331 hours of hydro, nuclear, other thermal and wind, from 2022-11-30T23:00Z to 2023-03-09T22:00Z;
  - 2023-06-03 04:02 carries 3,706 hours, 2023-02-28T23:00Z to 2023-06-02T22:00Z;
  - 2022-09-28 04:00 carries 2,526 hours of nuclear and wind, 2022-05-31T23:00Z to 2022-09-27T22:00Z.
  
  Nuclear's hours are usually published within a day (median 0.67 days), so those of June to September 2022 were most likely published a second time, months on: a revision, or the same figures published again; the files cannot say which.
- **In 2020,** from January to July, two thirds of each month's hours (four of the six types) carry one time, 17 to 48 days after the month's end (for example 2020-02-18 19:01 for 2,976 hours of January 2020).
- **Mixed times within a day.** A type's 24 hours often carry more than one time: nuclear on 51 of the 1,904 days, the other types on 436 (hydro) to 895 days (unspecified measured).

So Mimer's settled figures were revised or republished after first publication, and the table holds the version Mimer served on 24 October 2026. A later change to an hour of 2020 to 2025 would not reach the table without a new pull.

## Shape and variables

Series, 274,176 rows, 14 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_published`), 10 header lines. One entity, `svk:sweden`; unit MWh; `freq` PT1H; `geo` SE; `market`, `node` and `vintage` blank; `source_url` the type's download. Six variables of 45,696 hours each, 2019-12-31T23:00:00Z to 2025-03-18T22:00:00Z.

| Variable | Mimer's type | Mean | Median | Lowest (hour) | Highest (hour) | All hours, TWh |
|---|---|---|---|---|---|---|
| `generation_nuclear` | KK, Kärnkraftproduktion | 5,594.6 | 5,642.6 | 2,100.7 (2024-08-21T18:00:00Z) | 7,785.5 (2020-01-28T13:00:00Z) | 255.650 |
| `generation_hydro` | VA, Vattenkraftproduktion | 7,927.7 | 8,058.4 | 1,823.1 (2023-07-16T12:00:00Z) | 13,006.3 (2025-01-22T11:00:00Z) | 362.263 |
| `generation_wind` | VI, Vindkraftproduktion | 3,803.0 | 3,299.6 | 42.2 (2020-05-21T06:00:00Z) | 12,911.2 (2024-01-31T17:00:00Z) | 173.781 |
| `generation_other_thermal` | OK, Övrig värmekraftproduktion | 782.4 | 720.1 | 0 (2024-04-11T23:00:00Z, the one zero hour) | 2,257.8 (2021-12-06T10:00:00Z) | 35.751 |
| `generation_solar` | SE, Solenergiproduktion | 146.2 | 2.6 | 0.089 (2020-12-05T02:00:00Z) | 2,470.5 (2024-06-04T11:00:00Z) | 6.679 |
| `generation_unspecified_measured` | OP, Uppmätt ospecificerad produktion | 20.4 | 13.1 | 0.142 (2022-07-18T19:00:00Z) | 207.7 (2021-12-21T09:00:00Z) | 0.932 |

MWh an hour. No value is blank or negative; only one is zero. Solar is never zero, not even at night: its lowest hour is 0.089 MWh.

By UTC year, TWh (the first hour, 2019-12-31T23:00Z, falls in 2019; 2025 is to 18 March):

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| Nuclear | 47.397 | 51.443 | 50.061 | 46.687 | 48.404 | 11.650 |
| Hydro | 72.074 | 73.606 | 69.580 | 65.840 | 64.390 | 16.768 |
| Wind | 27.583 | 27.471 | 33.060 | 34.335 | 40.824 | 10.503 |
| Other thermal | 5.943 | 7.996 | 7.956 | 6.755 | 5.395 | 1.705 |
| Solar | 0.458 | 0.640 | 1.103 | 1.852 | 2.463 | 0.164 |
| Unspecified measured | 0.219 | 0.307 | 0.187 | 0.066 | 0.125 | 0.029 |

## Placing values in time, and what is filled

Mimer labels each hour `YYYY-MM-DD HH:MM`, 00:00 to 23:00. Each file holds 1,904 days, 2020-01-01 to 2025-03-18, each with all 24 labels, and no label twice. The ten clock-change days in the span (the last Sundays of March and October, 2020 to 2024) have 24 hours in all six files. So the labels run on a fixed offset, not on Sweden's clock with summer time, which would give those days 23 and 25 hours. No saved page states the offset; the saved Mimer pages contain none of UTC, CET, normaltid, vintertid, sommartid or tidszon.

The sun fixes the offset. With the labels read as hour starts and each hour taken at its middle, the weighted centre of mean solar output in June is 12:03 on the label clock. The mean output of the hours labelled 11:00 and 12:00 is nearly equal (938 and 935 MWh), with 10:00 and 13:00 at 886 and 885 MWh. Solar noon in mid June, in Swedish normal time (UTC+1), is about 12:08 at Malmö (13.0 E), 12:00 at 15 E and 11:48 at Stockholm (18.1 E). So the labels are hour starts in UTC+1:

- **Hour ends in UTC+1** would put the centre at 11:03, an hour before solar noon;
- **Hour starts in UTC** would put it at 13:03 Swedish normal time;
- **Hour ends in UTC** give the same instants as hour starts in UTC+1, and the same `ts_utc`.

The centre moves through the year as solar noon does with the equation of time. By month (label clock, hours) it is latest in February (12.39 to 12.47) and earliest in October and November (11.83 to 11.90 in October, 11.50 to 11.98 in November), with June 12.02 to 12.12. Over the 14 days either side of each of the ten clock changes it moves by -0.53 to +0.19 hours, never by the hour that labels following summer time would add or remove.

`ts_utc` is the label less one hour, the hour's start in UTC: the first is 2019-12-31T23:00:00Z (00:00 on 1 January 2020 in Sweden), the last 2025-03-18T22:00:00Z. Nothing is filled, and nothing needed to be.

The last day. Mimer's production page (saved by session 2351 at 06:44:52Z) says: "Produktionsstatistik för dygn 2025-03-18 och framåt rapporteras till eSett och publiceras på: Production | eSett Open Data. Historisk data innan 2025-03-18 kommer finnas kvar på Mimer". In English: the days from 2025-03-18 on are reported to eSett, and history before 2025-03-18 stays on Mimer. Yet each file holds 18 March 2025 whole: 24 hours of each type, published from 2025-03-19 05:00 (nuclear) to 2025-03-30 12:00 (solar). The page's own default listing, 192 hours of wind from 2025-03-11 00:00 to 2025-03-18 23:00, ends on that day too, and its 192 values and publication times equal the wind file's. The connector asked for no day after 18 March 2025 (disagreement 4).

## License

Header line 9: "License: internal until the licenses' round reads Svenska kraftnat's terms. Source: Svenska kraftnat." `coverage.csv` and `sources.csv`: internal. `license_tables.csv`: Svenska kraftnat, "the source registry". `docs/licenses.md`, the table's row: Svenska kraftnat, "not settled (needs written permission by default)", not read: Svenska kraftnat, flag internal, "not settled", if the ERW sells anything "may be public" (disagreement 7), ERW verdict internal; and in its list, "not read: Svenska kraftnat". No row in `license_verdicts.csv`, `license_reads.csv`, `license_status.csv` or `paused_sources.csv`.

The pages session 2351 read, saved in `runs/license_reads/s2351/`:

- `https://mimer.svk.se/robots.txt`: HTTP 404, the server's "404 - File or directory not found" page.
- Mimer's home page and its production page: HTTP 200.
- `https://www.svk.se/robots.txt`: HTTP 200. It disallows only `/siteassets/aktorsportalen/tekniska-riktlinjer/arkivet/`, `/sok/`, `/sok*?`, `/en/search/` and `/en/search*?`.
- www.svk.se's home page and "Om webbplatsen": HTTP 200. "Om webbplatsen" ("Här hittar du information om hur webbplatsen fungerar och även vår grafiska manual") links to personal data, cookies, accessibility and a site map.

None of these pages states terms of reuse. Once tags and scripts are removed, their text holds no licens, upphovsrätt, Creative Commons, CC0, öppna data, vidareutnyttjande, terms or copyright. The only "villkor" is in a menu item on grid connection ("Avtal och villkor vid anslutning").

## Checks (session 2353)

The figures in this note were computed by `runs/c105/s2353/check_svk_sweden_production_hourly.py` (output `check_svk_sweden_production_hourly.out` beside it). It streams the rows of `warehouse/output/svk_sweden_production_hourly.csv` in the main checkout, read past its 10 header lines (counted, never parsed as comments), and also reads Mimer's six raw files and `eurostat_electricity_monthly` (entity `eurostat_elec:SE`). No request was made.

- **The table:** 274,176 rows, 2019-12-31T23:00:00Z to 2025-03-18T22:00:00Z, as header line 1 states; no (entity, variable, ts_utc) twice; rows in key order; `coverage.csv` agrees (274,176 rows, the same range, validator pass, last run 2026-10-24T06:50:55Z).
- **The six `Summa` lines:** each file has exactly one, and its rows sum to it exactly (a difference of 0.000000 kWh):

| Type | Summa (kWh) |
|---|---|
| KK | 255,649,606,966.882 |
| OK | 35,751,485,301.628 |
| OP | 931,525,258.359 |
| SE | 6,678,835,620.652 |
| VA | 362,263,135,281.457 |
| VI | 173,780,907,805.112 |

- **The raw files:** no blank figure, no negative, one zero (OK), no hour twice, 1,904 days of 24 hours in each.
- **Against the raw files:** in each variable, every `ts_utc` is its label less one hour, every value is the file's kWh divided by 1,000 (none differs), and every `x_published` is the file's publication time (none differs).
- **Against Eurostat's net production for Sweden** (`eurostat_electricity_monthly`, MWh, Eurostat's GWh times 1,000; nuclear N9000, hydro RA100, wind RA300, solar RA400, combustible fuels CF for other thermal, TOTAL for all; Mimer's unspecified measured has no counterpart and is counted only in all), by UTC year:

| Type | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Nuclear | 1.0029 | 1.0000 | 1.0000 | 1.0021 | 0.9951 |
| Hydro | **1.0121** | 1.0000 | 0.9999 | 1.0016 | 1.0015 |
| Wind | 0.9998 | 0.9996 | 0.9996 | 1.0029 | 1.0023 |
| Solar | (Eurostat 0) | 0.5695 | 0.5617 | 0.5979 | 0.5941 |
| Other thermal | 0.4697 | 0.5218 | 0.5206 | 0.5009 | 0.4586 |
| All types | 0.9682 | 0.9555 | 0.9528 | 0.9533 | 0.9530 |

  The table's sum over Eurostat's. Nuclear, hydro and wind are within 0.5 percent in every year but hydro's 2020, 1.21 percent over (72.074 against 71.215 TWh; by month 1.2 to 1.6 percent over in January to March 2020 and 2.4 to 2.6 percent over in October to December 2020). By month, from 2020-01 to 2025-02 (62 months), nuclear's median is 1.0014 (10th percentile 0.9996, 90th 1.0031), except August 2024, 0.9251 (3,996 against 4,320 GWh, the month of nuclear's lowest hour); hydro's median is 1.0010 and wind's 1.0011, wind never off by more than 0.6 percent. Eurostat gives Sweden's solar as 0 in every month of 2020 (and of 2019), so 2020 has no ratio; from 2021 solar is 56.2 to 59.8 percent of Eurostat's, other thermal 45.9 to 52.2 percent, all types 95.3 to 96.8 percent.

## Where the description and the data disagree

1. **"Within 0.5 percent each year from 2020 to 2024".** The docstring ("Nuclear, hydro and wind equal Eurostat's net production for Sweden to 0.5 percent each year from 2020 to 2024 (exactly in 2021 and 2022)"), header line 3 ("within 0.5 percent a year") and `SESSION_2351_REPORT.md` ("agree within 0.5 percent every year from 2020 to 2024, and exactly in 2021 and 2022"). Hydro in 2020 is 1.21 percent over Eurostat's, and up to 2.6 percent in a month; "exactly" is within 0.04 percent (wind 2021 and 2022). Suggested: "within 0.5 percent each year from 2020 to 2024 except hydro in 2020 (1.2 percent over); within 0.05 percent in 2021 and 2022".
2. **"In UTC labels it would fall at 13:00".** The docstring ("Sweden's solar noon falls (about 11:50 normal time; in UTC labels it would fall at 13:00)") and the report. Read as written, Sweden's solar noon in UTC is about 10:48 to 11:08; 13:00 is about solar noon in summer time (UTC+2). The point the sentence makes holds only in another wording: read as UTC, the labels would put the centre of June's output at about 13:00 Swedish normal time, an hour after solar noon. Suggested: "read as hour starts in UTC, the labels would put the centre of June's output at about 13:00 normal time, an hour after solar noon".
3. **"Centred on the 12:00 label".** Header line 3 ("June's solar output centred on the 12:00 label"), the docstring and the report ("symmetric about the 12:00 label"). The centre is at 12:03 on the label clock: the start of the hour labelled 12:00, between it and the hour labelled 11:00, which hold nearly the same output (935 and 938 MWh). Centred on the hour labelled 12:00 would be 12:30. Suggested: "June's solar output centred at 12:00 normal time, between the hours labelled 11:00 and 12:00".
4. **"Mimer's production statistics end with 18 March 2025".** The docstring quotes only half of Mimer's sentence ("for dygn 2025-03-18 och framat rapporteras till eSett") and reads it as Mimer ending with 18 March. The page's whole sentence gives 18 March to eSett and keeps on Mimer only the history "innan 2025-03-18" (before it). Yet Mimer's files hold 18 March whole, and its page's listing ends there, so 18 March is on Mimer and, by the page, on eSett too. The connector asked for no later day, so the table's end is the request's, as well as Mimer's. Suggested: quote both halves, and say "Mimer still serves 18 March 2025 (its page's listing ends there); the page gives that day and later to eSett Open Data, so compare 18 March with eSett before joining the two".
5. **`vintage` blank though the publication time is known.** `docs/datastandard.md` (rule 5: "v0 tables keep the value the connector retrieved and record the publication time in `vintage`"; `vintage`, "When the source published the document the value came from", ISO 8601 UTC). Every row's publication time is in `x_published`; `vintage` is blank because the time's clock is not stated, which neither the header nor the docstring says. Suggested: say so in the header ("vintage blank: Mimer's publication time is in x_published as printed, its clock not stated"), or fill `vintage` once the clock is known.
6. **No record of the run.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap". It holds no row of this table: the run wrote only `runs/status/svk_sweden.json`. Suggested: record the run with `run_status.py record`.
7. **"May be public" if the ERW sells anything.** `docs/licenses.md`, the table's row, gives "may be public" in the column "If the ERW sells anything" for a publisher whose terms no one has read ("not settled", "not read: Svenska kraftnat"). Suggested: "not settled" there too.
8. **"Retrieved: 20261024T065055Z ... by warehouse/connectors/svk_sweden.py".** Header line 4 names the run that wrote the file as the retrieval; that run made no request (its raw folder holds only the lock check). The files were fetched from 06:45:09Z to 06:46:04Z by session 2351's probe script, as the line's second half and `retrieved_at` say. Suggested: "Written: 20261024T065055Z (UTC), offline, by warehouse/connectors/svk_sweden.py, from the six files fetched from 06:45:09Z to 06:46:04Z by session 2351's probe (runs/c105/s2351/probe.py)".

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2351_REPORT.md`:

- "274,176 figures": holds.
- "Six production types, hourly, all of Sweden, 1 January 2020 (Swedish time) to 18 March 2025": holds.
- "Unit: MWh, Mimer's settled kWh divided by 1,000": holds, no value differs.
- "Every file's rows sum to its 'Summa' line; 24 hours every day; no hour twice; no blank figure": each holds, the sums exactly.
- "Every day has 24 hours, the clock-change days included": holds, the ten days in the span.
- "June's mean solar output is symmetric about the 12:00 label": about 12:00 on the label clock, not about the hour labelled 12:00 (disagreement 3).
- "In UTC labels it would fall at 13:00": see disagreement 2.
- "Nuclear, hydro and wind agree within 0.5 percent every year from 2020 to 2024, and exactly in 2021 and 2022": not for hydro in 2020 (disagreement 1).
- "Solar is about 58 percent of Eurostat's, and other thermal about 50 percent": holds, 56.2 to 59.8 and 45.9 to 52.2 percent.
- "All types together come to 95 to 97 percent": holds, 95.3 to 96.8.
- "The page says the days from 2025-03-18 on are reported to eSett": holds, but the files hold that day too (disagreement 4).
- "The test is tests/test_session2351.py (3 tests)": holds.

## What it does not hold

- Sweden's four bidding areas (Mimer's Elområde 1 to 4 and "Elområde 2 DK"), which the page offers and the connector does not ask for; consumption (Mimer's Förbrukningsstatistik); imports and exports; reserves (FCR, aFRR, mFRR).
- Hours before 1 January 2020 (Swedish time), which were not asked for; hours after 18 March 2025, which are eSett's (eSett Open Data covers Sweden, Finland, Norway and Denmark; no ERW table holds it yet).
- Production not settled hourly at the grid. Solar is about 58 percent and other thermal about 50 percent of Eurostat's. The docstring's reason, "production behind the meter and on industrial sites is not in it", is the session's reading and is not shown by the files.
- Mimer's earlier publications of an hour it published again: only the newest time and figure are in the files (`x_published`; `vintage` blank).
