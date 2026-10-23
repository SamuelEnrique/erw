# The billion-dollar disasters, an event (NOAA NCEI's U.S. Billion-Dollar Weather and Climate Disasters)

Energy Research Warehouse (ERW), method note written in session 2079 (chain 067) for a table first written on 23 October 2026 (session 2073).

Tables: `noaa_ncei_billion_disasters`

## Publisher and address

NOAA's National Centers for Environmental Information (NCEI), U.S. Billion-Dollar Weather and Climate Disasters (`https://www.ncei.noaa.gov/access/billions/`, DOI 10.25921/stkw-7w73), a product NCEI retired in 2025. The page is drawn by script; the events file its application downloads is read directly: `https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv`. Source id `noaa:billion_dollar_disasters`. Connector: `warehouse/connectors/noaa_billion_disasters.py` (session 2073).

## Vintage and revision

Events beginning 10 April 1980 to 9 October 2024 (`event_date`), the last ending 31 December 2024 (`x_end_date`). The file was retrieved 2026-10-23T20:19:06Z; the table was written by run `20261023T203619Z` (session 2079 wrote it again, its rows unchanged, so the header says NCEI gave no last-modified time instead of ending blank) (23 October 2026) from the saved file (`--offline`, session 2073's report). The header's "last modified" is blank: no last-modified time was recorded for the file.

The table is a snapshot, written whole each run. The file is reused from `warehouse/raw/noaa_billion_disasters/` once saved, as the retired record no longer changes.

## Shape and variables

Events, 403 rows, one a disaster: `event_id` `noaa_billion:<begin date>:<12 hex of the SHA-1 of the name>`, our own (NCEI gives none), stable while NCEI keeps the name; `event_date` the begin date; `event_type` NCEI's type in snake case, its words in `x_disaster`; `x_name` NCEI's name; `parties`, `entity_ids`, `mw`, `price`, `currency` and `status` empty in every row.

| Type | Events | CPI-adjusted, USD billion | Deaths |
|---|---|---|---|
| severe_storm | 203 | 514.0 | 2,145 |
| tropical_cyclone | 67 | 1,543.0 | 7,211 |
| flooding | 45 | 203.0 | 765 |
| drought | 32 | 367.8 | 4,658 |
| winter_storm | 24 | 104.4 | 1,463 |
| wildfire | 23 | 148.0 | 537 |
| freeze | 9 | 37.3 | 162 |

- Cost: `x_cost_cpi_adjusted_usd` sums to USD 2,917,606,500,000 and `x_cost_unadjusted_usd` to USD 2,060,097,700,000; NCEI's millions are written as dollars, every value a whole multiple of USD 100,000. Neither is blank, and no unadjusted cost exceeds its adjusted one; the 13 events of 2024 have the two equal (the adjustment runs to the record's last year). The largest is Hurricane Katrina (August 2005), USD 201.3 billion adjusted (125.0 billion unadjusted); the smallest adjusted, Mountain West Severe Weather (July 2018), USD 1.0638 billion.
- Deaths (`x_deaths`): 16,941 in all, none blank; Hurricane Maria (September 2017) has the most, 2,981.
- By the decade of the begin date: 1980s 33 events (USD 219.6 billion adjusted); 1990s 57 (335.1); 2000s 67 (621.9); 2010s 131 (994.4); 2020 to 2024 115 (746.5). 2023 and 2024 have 27 each.
- Three names are given twice, a different begin date each: Midwest Severe Weather (June 2017), Colorado Hail Storm (June 2018), North Central Hail Storms (May 2022). The date in the id keeps them apart.

## Reading the source

- The file's lines before its header must say the costs are "in millions of dollars"; the header must be `Name,Disaster,Begin Date,End Date,CPI-Adjusted Cost,Unadjusted Cost,Deaths`.
- A date not `YYYYMMDD`, a cost that is not a number, deaths not a whole number, or an event id given twice stops the run. A blank cost stays blank; nothing is filled. Values as published, whitespace collapsed.
- The file names no state an event touched; the product's maps did, and are not taken.
- Ceiling: one request. NCEI's robots file disallows `/data*`, `/orders*` and parts of `/access/crn/`; `/access/billions/` is not among them (read 198).

## License

`license_tables.csv` lists the table under NOAA NCEI. `license_verdicts.csv` records NOAA NCEI, read 9: "may be public", for public and for commercial use; its one restriction is on ISD's non-U.S. stations (WMO Resolution 40), and its note adds NCEI's privacy policy (read 182). The connector and the header call the data a U.S. Government work in the public domain and give the citation, NOAA NCEI U.S. Billion-Dollar Weather and Climate Disasters (2025), DOI 10.25921/stkw-7w73. `docs/licenses.md` gives the table "may be public", flagged public, agreeing; `sources.csv` names the source's license as public.

## Cross-checks (session 2079)

- The counts above were computed from the rows, read past the header lines; the seven types match the header's counts and sum to its 403, and the adjusted costs sum to its USD 2,917,606,500,000. No `event_id` is given twice, each recomputes from its begin date and name, and the rows are in (event_date, event_id) order. No event ends before it begins.
- Session 2073's check against `noaa_ncei_storm_events`, recomputed: the 29 tropical cyclones of 2015 to 2024 against the storm events of types hurricane, hurricane_typhoon, tropical_storm and storm_surge_tide whose local begin day falls from the cyclone's begin day less one to its end day plus two. 27 of 29 have such events (the report: 27); property and crop damage correlate with NCEI's unadjusted cost at 0.611 (the report: 0.611) and sum to 12.8 percent of it (the report: 13); Hurricane Ian (September 2022), 175 events with USD 15.40 billion against NCEI's USD 111.8 billion unadjusted (the report: the same). The two without events are Tropical Storm Imelda (2019) and Hurricane Fiona (2022). Read by the UTC begin day instead, 26 of 29 match (Typhoon Mawar, May 2023, also drops) and the correlation is 0.623.
- Hurricane Beryl (July 2024) has 10 such events; they record USD 9,000 of property damage and USD 5,000 of crops (`noaa_storm:1204150`, 1204077, 1204082); session 2073's report, which first said none, now says so.

## What it does not hold

- The states or places an event touched (the product's maps), and anything the page shows beyond the events file.
- Any event after 2024: the product was retired in 2025, and the record ends there.
- Damage by kind (insured, uninsured, crops): one total a cost basis.
