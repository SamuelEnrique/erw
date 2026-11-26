# The curtailment tracker: its figures audited as a hostile expert would

Session 10210, chain 710 part D, 26 November 2026, the old laptop. Read as a renewables developer's analyst and an ISO market monitor who want to find it wrong. Platform tool 22 (`docs/platform-tools.md`): `/curtailment` and its view `/curtailment/where-when`.

- Nothing changed on main but this file and its evidence folder (`docs/reviews/curtailment-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked.
- Work in progress: the sections below are filled as the session goes.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/curtailment/page.tsx` | The page. Chooser of seven grids (CAISO, SPP, ERCOT, ISO-NE, NYISO open; MISO and PJM named only), California's period (a year or a month of the five-minute record) and a battery of 2, 4 or 8 hours. With no address it opens on CAISO, the newest year the profile holds (2026, ten months), a 4-hour battery. The summary sentence, the headline rows, "By day" and "By month" (the two live reads), California by hour, by reason and against the batteries, "Where free energy is", "What it is worth", "What each grid's number is", every month's share, the decisions block |
| `site/app/curtailment/Sections.tsx` | "Where free energy is" (`free_energy.json`), "What it is worth" (`worth.json`), Texas by the hour (`ercot.json`) |
| `site/app/curtailment/Charts.tsx` | The charts' wrappers (the site's SVG chart set) |
| `site/app/curtailment/where-when/page.tsx`, `Decisions.tsx` | "Where and when power is spare": a place's hour of the day against month (CAISO's curtailment, SPP's months, the hubs' hours below zero), the trend by whole year, the places ranked, eight decisions |
| `site/lib/curtailment.ts` | The chooser, addresses, a year's share from its months (`yearShare`), the newest and highest month, the number formats |
| `site/lib/curtailmentv2.ts` | California's profile read: hour-of-day arrays, the peak hour, whether a reason is published, the battery months |
| `site/lib/freeenergy.ts` | `FACE` (one line a grid: whose number it is), the share rule, the free-energy ranking and heat map, the flat load, the battery ceiling |
| `site/lib/wherewhen.ts` | The where-when view's cells, a cell's share of hours below zero, the newest whole year |
| `site/lib/decisions.ts` `CURTAILMENT_DECISIONS` | The page's eleven decisions, word for word the note's |
| `site/data/curtailment_profile.json` | California by month and year from CAISO's record (five-minute to 2025, the Daily Renewable Report by the hour from 2026): MWh by fuel, reason, category and Pacific clock hour, and the battery overlay. Built 2026-11-16, months 2019-01 to 2026-10 |
| `site/data/curtailment/shares.json` | Every month's share of available output (CAISO 150 months, SPP 98), with the output source of each month. Built 2026-11-17 |
| `site/data/curtailment/worth.json` | The value of curtailed energy at the hubs' prices, the flat load, the battery rule and the fleet (CAISO; ERCOT's estimate over its hours). Built 2026-11-17 |
| `site/data/curtailment/free_energy.json` | Hours under USD 5 and below zero by hub and zone, the twelve months to October 2026 and October alone, ERCOT, CAISO, NYISO, ISO-NE, SPP. Built 2026-11-16 |
| `site/data/curtailment/ercot.json`, `zone_shapes.json`, `where_when.json` | Texas's hours and days (the ERW's estimate); the boundaries found (none); the where-when view's file (built 2026-11-20) |
| Live reads | `iso_curtailment_monthly` (one entity, every row) and the grid's daily table (`caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`) since 100 days back |
| Builders | `warehouse/connectors/curtailment.py`, `caiso_curtailment_intervals.py`, `ercot_wind_solar_history.py`; `warehouse/derived/iso_curtailment_monthly.py`, `curtailment_profile.py`, `curtailment_shares.py`, `curtailment_worth.py`, `free_energy.py`, `ercot_estimate_page.py`, `where_when.py` |
| Notes | `docs/methods/curtailment.md` (the method, its decisions and cross-checks), `caiso_curtailment_intervals.md`, `caiso_curtailment_daily.md`, `spp_curtailment_daily.md`, `where_when.md`; `replication/curtailment/` (profile and Texas 11,515 of 11,515 on 16 November; free energy; not worth, not SPP's shares) |
| Earlier reads | `docs/reviews/curtailment-faults-2026-11-16.md`, `curtailment-read-2026-11-16.md`, the ruling files of 17 November; not repeated here |

## The default view re-done, to the digit

The live set holds newer days than this machine. Every figure below is the page's figure on the page's committed files and, for the two live reads, on the main copy's tables as this machine holds them (read only; the daily table to 4 November 2026, the monthly table to September 2026), with "now" set to 26 November 2026 12:00 UTC.

- **The page's own code.** `draw.mjs` draws `/curtailment` (and seven other addresses) to HTML with the site's own components, the two live reads answered from `fixture.json` (rows of the main copy's tables), every other request refused. Every figure the page marks (`data-n`) is collected (`main_default_n.json`).
- **The restatement.** `restate.py` (standard library, none of the site's code), written from the method note and the page's words, computes every figure from the same files.
- **Result: 141 of 141 figures of the default view agree to the digit** (`compare.out`), and so do the thirteen months of the monthly table and the totals over the 78 days the daily table gives (solar 374,254.63 MWh, wind 51,376.40).

| Figure (CAISO, 2026, 4-hour battery) | Page | Restated |
|---|---|---|
| Solar curtailed, wind curtailed | 4,944,663 MWh; 353,207 | the same |
| Days | "304 of 304 days, 10 months" | 304 days held of the 304 in the ten months; the calendar year has 365 |
| For local congestion, system-wide oversupply | 4,301,964; 995,905 MWh | the same |
| The hour with the most | 15:00 (602,149 solar, 39,639 wind) | the same; 14:00 holds 635,266 against 641,788, 1.0 percent less |
| Share of available output, 2026 | 6.52 percent | 6.52 (ten months' curtailed over curtailed plus output) |
| The highest month; the newest | 15.81 (April 2026); 2.73 (October 2026); 150 months | the same |
| Curtailed while the batteries charged, October 2026 | 91.54 percent (182,465 MWh, 31 days, 1,668,564 MWh charged) | the same |
| Hours under USD 5, SP15, twelve months | 1,375 (1,109 below zero) | the same; the heat map's cells add to it |
| Cheapest against dearest place | 4.18 (ZP26 28.98, NP15 33.16); October 5.02 | the same |
| Curtailed energy at SP15 real-time prices, 2026 | USD -29.0 million, -5.48 per MWh, 5,297,870 MWh | the same |
| In hours below zero; under USD 5 | 79.97; 84.23 percent | the same |
| A flat load in those hours; in all hours | 26.96; 28.32 USD per MWh, 5,876 hours | the same |
| A 4-hour battery could have taken in | 1,210 MWh per MW, 99.48 percent of one full charge a day over 304 days | the same |
| A 4-hour fleet against what the fleet charged in the curtailed hours | 4,245,847 of 15,638,274 MWh, 27.15 percent | the same |

### What it is worth, restated from the tables (never replicated before)

`worth_check.py` (standard library, written from the note's "What it is worth") rebuilds the value, the flat load and the battery rule from `caiso_curtailment_intervals` and the hubs' prices, one year at a time. **86 of 88 hub, market and month cells of 2025 and 2026 agree with `worth.json`** (value to USD 1, per MWh and shares to 0.01, MWh to 0.1, hours exactly); the two that differ are October 2026 at the two hubs in real time, where this machine's price table holds 720 of the month's 744 hours (`worth_compare.out`). The battery rule per MW agrees in every month.
