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
