# ERCOT's four coincident peaks

One source table, `ercot_4cp_intervals`, written by `warehouse/connectors/ercot_4cp.py` (session 359, the chain of
20 October 2026). It answers the datacenter pack's fourth hidden item (section 6, item 4): a large load in ERCOT pays
transmission on its demand in the four coincident-peak intervals of June, July, August and September, and a load off
in them saves that charge.

## The table's shape (written before the table, for the code machine)

Shape: `series`. One row per year and summer month: the 15-minute interval ERCOT names as that month's coincident
peak. Key `(entity, variable, ts_utc)`.

| Column | What it holds |
|---|---|
| `entity` | `ercot:system` |
| `variable` | `cp4_load_mw`: ERCOT's load in the month's coincident-peak interval, as ERCOT publishes it |
| `ts_utc` | the interval's start in UTC (ERCOT names an interval by its end, in Central prevailing time; the table converts and keeps ERCOT's own words in `x_interval_local`) |
| `value`, `unit` | the load, `MW` |
| `freq` | `PT15M` |
| `geo`, `market`, `node` | `US-TX`, `ercot_4cp`, `ERCOT` |
| `source`, `source_url`, `retrieved_at` | ERCOT's document the row was read from |
| `vintage` | ERCOT's publication date of that document, where ERCOT states one |
| `x_year` | the year, `YYYY` |
| `x_month` | the month, `YYYY-MM` (June to September) |
| `x_interval_local` | the interval as ERCOT prints it (its date and interval ending, Central) |
| `x_published` | the date ERCOT published the interval, `YYYY-MM-DD`, as the document states it, or empty where it states none |

Years from 2018 to the newest summer ERCOT has published. A month ERCOT has not published has no row.

## The rule a page must keep

**An interval is known only after its month.** ERCOT names a month's coincident peak once the month's settlement
data are in; a load cannot see the interval while it happens, only forecast it. A page that shows what a load saves by
being off in these intervals shows a saving known after the fact: what a load that guessed right every month saved,
not what a rule decided in advance would have saved.

## Where it comes from (session 359)

ERCOT's page "ERCOT Four Coincident Peak Calculations" (https://www.ercot.com/mktinfo/data_agg/4cp) points to data
product NP9-83-M (report type 13037) for the current years and keeps the earlier years as one zip under Key
Documents. NP9-83-M's list held four workbooks on 20 October 2026 (2022 to 2025, posted on 28 November 2022, 27
November 2023, 25 November 2024 and 24 November 2025); the zip holds 1996 to 2020. Each workbook is ERCOT's "Four
Coincident Peak Load Calculation (MW)": one row per load entity (each distribution service provider) with its load in
each month's coincident-peak interval, the interval named in the column's header ("June\n6/19/2025 17:00"), and a
Total row, ERCOT's coincident peak load. ERCOT's note: DC tie exports, block load transfer exports and wholesale
storage load are excluded. The 2019 workbook in the zip is ERCOT's revised one (four entities' figures changed in
PUC Docket 50333; the workbook's second sheet gives the details).

- **Held: 2018, 2019, 2020, 2022, 2023, 2024, 2025** (28 rows). **2021 is not held**: it is on neither the list
  (which keeps four years) nor the zip (which ends with 2020); it is not filled.
- **The summer of 2026 is not published yet**: ERCOT posts the year's calculation in late November (the protocols
  ask for it by 1 December). ERCOT publishes no separate document of each month's interval as the month ends on these
  pages; the monthly operational overviews give the month's peak hour, which is not the settlement interval and is not
  read.
- **The interval's time.** ERCOT prints a time without saying whether it starts or ends the interval. Its settlement
  and price reports name a 15-minute interval by its end, and this table reads the 4CP time the same way: `ts_utc` is
  15 minutes before the printed time, Central prevailing time converted to UTC; `x_interval_local` keeps ERCOT's time.
- **Requests: 8 of 20** (the page, the product page, the list, four workbooks, the zip), at 1.5 seconds apart.

The loads, MW (June, July, August, September): 2018 69,255, 73,539, 69,990, 64,693; 2019 68,370, 71,254, 75,006,
69,293; 2020 68,196, 74,392, 74,420, 64,945; 2022 76,803, 80,233, 78,669, 71,150; 2023 81,018, 83,033, 85,637, 84,540;
2024 79,750, 81,184, 85,358, 77,879; 2025 77,486, 81,908, 83,968, 80,076. The printed times run from 14:30
(1 September 2020) to 17:45 Central.

    python warehouse/connectors/ercot_4cp.py --pull      # the list, then any workbook or the zip not yet held (at most 20 requests)
    python warehouse/lock.py run --task 4cp -- <python> warehouse/connectors/ercot_4cp.py --write
