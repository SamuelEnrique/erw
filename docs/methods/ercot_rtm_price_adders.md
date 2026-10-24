# ERCOT's real-time reserve price adders by the hour, from 1 June 2014 (NP6-792-ER)

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written in session 244 (its oldest rows retrieved on 13 October 2026). The method of session 244 is `docs/methods/ercot_rt_price_adders.md`, which the header names; this note describes the table as it stands.

Tables: `ercot_rtm_price_adders`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves", report NP6-792-ER, report type 13231: `https://www.ercot.com/mp/data-products/data-product-details?id=NP6-792-ER`. The list of documents is `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13231`; each document is a zip holding one Excel workbook, a sheet a month and a row a SCED interval, at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. Source id `ercot:NP6-792-ER` (in `sources.csv`, license public, first seen 2026-10-13, last 2026-10-18).

Connector: `warehouse/connectors/ercot_rt_adders.py` (session 244). A run asks for the list, then reads only the documents whose address the table does not yet hold (and the last sheet of the document before, for the first hour of a year); `--full` reads every document again, `--offline` the raw files only. Raw files stay in `warehouse/raw/ercot_rt_adders/`, 3 seconds between requests; a run asks nothing while ERCOT is in `paused_sources.csv`. Ceiling 1,000,000 rows, checked on the rows a run writes.

Schedule: the data machine's daily run, `warehouse/run_data_machine.sh` section 1d, soft step `dm_ercot_rt_adders`, then `dm_rt_adders_stores` when the table moved. `warehouse/run_data_machine_tables.sh` loads it into the live set from that machine (it is in `LIVE_ONLY` and `WEEKLY_LIVE`). The GitHub runner does not run it: the yearly workbooks are on the data machine. Reader named in `license_tables.csv`: `scarcity_hours_by_grid`.

## Vintage and revision

Fourteen documents, each row carrying its document's address, its retrieval time and ERCOT's publication time as `vintage`:

| DocID | `vintage` (ERCOT's publication) | `retrieved_at` | Rows (Central local year) |
|---|---|---|---|
| 468554538 | 2015-01-02T16:00:28Z | 2026-10-13T06:34:15Z | 20,536 (2014) |
| 505964801 | 2016-01-07T21:44:38Z | 2026-10-13T06:34:23Z | 44,148 (2015) |
| 644817014 | 2019-01-17T20:19:27Z | 2026-10-13T06:34:36Z | 52,668 (2016) |
| 644817015 | 2019-01-17T20:19:27Z | 2026-10-13T06:34:32Z | 52,548 (2017) |
| 643552126 | 2019-01-08T15:53:35Z | 2026-10-13T06:34:28Z | 52,530 (2018) |
| 694452063 | 2020-01-02T18:30:02Z | 2026-10-13T06:34:41Z | 52,530 (2019) |
| 751366904 | 2021-01-01T15:26:33Z | 2026-10-13T06:34:45Z | 52,698 (2020) |
| 814938847 | 2022-01-01T15:26:31Z | 2026-10-13T06:34:49Z | 52,512 (2021) |
| 899479048 | 2023-03-02T20:04:14Z | 2026-10-13T06:34:54Z | 52,548 (2022) |
| 969827183 | 2024-01-01T15:09:09Z | 2026-10-13T06:34:57Z | 52,554 (2023) |
| 1065495488 | 2025-01-01T15:09:34Z | 2026-10-13T06:35:03Z | 52,686 (2024) |
| 1169113636 | 2025-12-08T17:21:55Z | 2026-10-13T06:35:07Z | 48,648 (2025, the ORDC adders to 4 December) |
| 1180319793 | 2026-01-08T23:58:14Z | 2026-10-13T06:35:10Z | 1,294 (2025, RTRDPA from 5 December) |
| 1287934701 | 2026-10-18T15:14:32Z | 2026-10-18T17:13:12Z | 13,910 (2026) |

The 2015 rows all come from the whole-year document (505964801); the half-year 2015 document is not read, as the docstring says. ERCOT republishes the current year's workbook weekly under a new DocID, so a run that finds one rereads it and replaces that year's rows: the last run in the header, `20261018T171307Z`, "wrote 13910 rows: 336 new, 13574 replacing earlier rows with the same (entity, variable, ts_utc); 587900 rows are kept from earlier runs."

## Shape and variables

Series, 601,810 rows. `entity` ercot:system, `unit` USD/MWh, `freq` PT1H, `geo` US-TX, `market` ercot_rtm, `node` the adder as ERCOT names its column (equal to the variable's stem in every row). No cell is empty.

| `variable` | `node` | Rows | First `ts_utc` (Central) | Last `ts_utc` (Central) | Highest, USD/MWh (hour) | Mean |
|---|---|---|---|---|---|---|
| rtorpa_mean, rtorpa_max | RTORPA | 100,878 each | 2014-06-01T06:00:00Z (01:00 CDT) | 2025-12-05T05:00:00Z (23:00 CST, 4 December) | mean 4,160.4039, max 7,200.7061 (2021-02-16T14:00:00Z) | 2.0971, 4.5442 |
| rtoffpa_mean, rtoffpa_max | RTOFFPA | 100,878 each | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z | mean 2,325.5415, max 3,600.353 (2021-02-16T14:00:00Z) | 1.2852, 2.5362 |
| rtordpa_mean, rtordpa_max | RTORDPA | 91,547 each | 2015-06-25T06:00:00Z (01:00 CDT) | 2025-12-05T05:00:00Z | mean 8,986.6426, max 8,993.6045 (2021-02-18T22:00:00Z) | 6.7005, 8.7771 |
| rtrdpa_mean, rtrdpa_max | RTRDPA | 7,602 each | 2025-12-05T07:00:00Z (01:00 CST) | 2026-10-18T03:00:00Z (22:00 CDT, 17 October) | mean 156.9873, max 319.01 (2026-01-28T13:00:00Z) | 0.3352, 0.8890 |

The lowest value of every variable is 0.0. Hours with a mean above zero: RTORPA 17,667, RTOFFPA 10,010, RTORDPA 8,914, RTRDPA 1,515.

## Placing values in time

- ERCOT stamps each SCED interval in Central time to the second, with a repeated-hour flag; the flag `Y` marks the second pass through the autumn's repeated hour, and the first pass is read as daylight time. Stamps are converted to UTC.
- A value holds from its stamp to the next stamp, for at most 15 minutes. `<adder>_mean` weights each value by the seconds it held within the UTC hour; `<adder>_max` is the largest value that held in the hour. `ts_utc` is the start of the hour.
- Every stamp bounds the value before it, whatever document it comes from: the last ORDC value of 4 December 2025 holds to the first stamp of the new form.

## What is and is not filled

- An hour is written only when all 3,600 of its seconds are covered by a value; an empty cell covers nothing. An hour with a longer silence is left out and named as a gap in the run log and the header.
- The first and the last hour of each adder's span are left out by the same rule when not covered.
- Nothing is filled or carried past 15 minutes.

## License

Header: "License: public. ERCOT terms of use, item 5: raw data in public portions of the website may be used, reproduced, and redistributed in compilations, charts, and analyses." `license_verdicts.csv` records ERCOT, read 2: "may be public", for public and for commercial use. `docs/licenses.md` lists `ercot_rtm_price_adders` under ERCOT: "may be public", flag public, ERW verdict public.

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/ercot_rtm_price_adders.csv`, read past its 11 header lines.

- 601,810 rows, `ts_utc` from 2014-06-01T06:00:00Z to 2026-10-18T03:00:00Z, as the header's "File holds" line states. 1 entity, 8 variables, 14 source addresses, 13 distinct `vintage` values (two documents share 2019-01-17T20:19:27Z).
- No (entity, variable, ts_utc) is given twice. Each adder's `_mean` and `_max` hold the same hours.
- Consistency: in every hour of every adder the mean is at most the max (0 exceptions); no value is negative.
- Hours missing inside each adder's own span (first to last hour written): RTORPA and RTOFFPA 42 of 100,920 (the same hours for both, from 2014-11-22T16:00:00Z to 2025-08-14T15:00:00Z; by UTC year 2014: 2, 2015: 3, 2016: 6, 2017: 2, 2018: 5, 2019: 5, 2020: 1, 2021: 8, 2022: 2, 2023: 1, 2024: 3, 2025: 4); RTORDPA 37 of 91,584 (those of the ORDC adders from 2016 on, and 2025-10-07T05:00:00Z and 2025-10-08T13:00:00Z, hours RTORPA holds); RTRDPA 3 of 7,605 (2026-03-19T15:00:00Z, 2026-05-12T15:00:00Z, 2026-06-04T20:00:00Z, as the header names).
- The handover: 2025-12-05T05:00:00Z (23:00 CST on 4 December) is the last hour of RTORPA, RTOFFPA and RTORDPA, all three 0.0; 2025-12-05T07:00:00Z is the first of RTRDPA; 2025-12-05T06:00:00Z (00:00 to 01:00 CST on 5 December) holds no adder.

## Where the description and the data disagree

1. **The header names 3 gaps; the table has 124.** Header line 4: "3 hours are left out of this run for a longer silence", the three RTRDPA hours of 2026. The file also lacks 42 hours inside the spans of RTORPA and RTOFFPA and 37 inside RTORDPA's (listed in the checks above). The code writes into the header only the gaps of the documents the run read, and a run that reads only the current year replaces the header, so the earlier gaps are named nowhere in the file.
2. **"From 5 December 2025" and "1 June 2014".** The docstring and header give RTRDPA from 5 December 2025 and RTORPA and RTOFFPA from 1 June 2014. The first hours written are 01:00 CST on 5 December 2025 (2025-12-05T07:00:00Z) and 01:00 CDT on 1 June 2014 (2014-06-01T06:00:00Z): the hour from local midnight is absent in both, so no adder at all covers 00:00 to 01:00 CST on 5 December 2025. The docstring's rule ("The first hour of the record and the last one (still open) are left out by the same rule") accounts for both first hours. What neither the docstring nor the header says is that one hour between the two forms has no adder: the code's comment that the last ORDC value "holds to the first stamp of the next form" completes the hour ending at local midnight, not the one after it.

Acted on in session 2124: the docstring now says RTRDPA's first hour begins at 01:00 CST on 5 December 2025. The header's count of gap hours is written by each run for its own window and is left as it is; the 124 hours are recorded here.

## What it does not hold

- The reserves columns of ERCOT's workbooks (only the adders are read), and any SCED interval value.
- The system lambda, real-time prices (`ercot_rtm_node_prices`, `ercot_all_hub_prices_history`) or ancillary service prices (`ercot_as_prices`).
