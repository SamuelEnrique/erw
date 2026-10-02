# Session 62 report: where the next gigawatts for AI can come from

Energy Research Warehouse (ERW), session 62, second of the overnight run, on the portable laptop (role data), 2026-10-02 09:15 to about 10:10 UTC. **Wall time about 55 minutes. Model spend: USD 0.00** (the cap was USD 2; no model call was needed). No force push. Nothing released on Redivis.

## In plain words

**The draft.** A first flagship report is drafted, internal only: "Where the next gigawatts for AI can come from".
- **Where:** `/reports/draft/ai-gigawatts?token=<INTERNAL_COSTS_TOKEN>`. Without the token it answers 404; it is not in the navigation, not indexed, not published.
- **What it measures:** the seven ISO regions, the same way over the same year (September 2025 to August 2026), for one flat 1 GW load:
  - what it would pay for energy;
  - how much CO2 it would carry;
  - how stressed the grid is;
  - how fast new supply connects;
  - how much the region leans on its neighbors.
- **Size:** 3,014 words.
- **Checks:** every one of its 240 numbers is a row of the new table `ai_power_regions` (or a ratio or difference of two), shown with its check key. check-values matched all 165 distinct values to Supabase.

**The pulls.** Two approved pulls feed it, both under their ceilings:
- Berkeley Lab's Queued Up 2026 data file: 38,201 rows of 100,000;
- EIA-930 daily interchange for every balancing-authority pair from 2019: 945,130 rows of 3,000,000.

## The five findings the draft leads with

1. **Energy cost differs by a factor of 2.48.**
   - A flat 1 GW would have paid USD 249.06 million a year at real-time hub prices in CAISO (SP15), the cheapest region, against USD 616.43 million in ISO-NE, the dearest.
   - That is USD 367.37 million more, for wholesale energy alone.
2. **Carbon differs more than cost (3.05 times).**
   - The same gigawatt would carry 1,250,886 tonnes of CO2 a year in CAISO and 3,817,811 in MISO.
   - CAISO is both the cheapest and the cleanest, and also the last of six to connect new supply.
3. **New supply connects fastest in ERCOT.**
   - Requests that came online in 2018 to 2025 took a median 3.79 years in ERCOT, against 7.79 in CAISO.
   - ERCOT completed 30.27 percent of its 2000 to 2019 requests; CAISO 12.98 percent.
4. **The queues are not the bottleneck in size.**
   - ERCOT held 408,002 MW of active requests at the end of 2025, and MISO 350,125 MW.
   - What matters is how little gets built, and how long it takes.
5. **Some regions lean on their neighbors.**
   - CAISO imported a net 27.02 percent of its demand over the year (EIA's own balance), and was a net importer on every complete day.
   - PJM exported, at -3.00 percent.

The prose computes these comparisons from the table at render time: which region is cheapest, cleanest or fastest. It stays true if the table is rebuilt.

## The table: `ai_power_regions`

Derived, public, 187 rows: one row per region and measure, in Supabase's live set and the Redivis draft. Key measures:

| Region | Flat real-time price, USD/MWh | A flat 1 GW, USD a year | kg CO2/MWh | Hours at or above USD 200 | Active queue, MW (end 2025) | Median years to operation | Completion, percent | Net imports, percent |
|---|---|---|---|---|---|---|---|---|
| CAISO | 28.43 | 249,062,342 | 142.80 | 19 | 190,717 | 7.79 | 12.98 | 27.02 |
| ERCOT | 31.52 | 276,135,276 | 303.37 | 57 | 408,002 | 3.79 | 30.27 | 0.09 |
| ISO-NE | 70.37 | 616,431,496 | 235.38 | 408 | 14,623 | not held | 29.48 | 4.92 |
| MISO | 47.19 | 413,371,403 | 435.82 | 195 | 350,125 | 4.21 | 20.17 | -0.03 |
| NYISO (the NYC zone) | 68.61 | 601,033,917 | 262.83 | 391 | 27,119 | 5.03 | 22.66 | 11.40 |
| PJM | not held | not held | 333.41 | not held | 130,611 | 4.89 | 23.93 | -3.00 |
| SPP | 30.63 | 268,289,073 | 411.06 | 160 | 151,152 | 4.81 | 17.04 | -1.11 |

The table also holds, per region:
- the day-ahead price;
- the CO2 of a flat 1 GW;
- hours at or above USD 1,000, and the highest hour;
- CAISO's emergency days (39);
- the largest studied event's effect on demand, and which event;
- the ISO's own active queue (September 2026);
- the pair-sum import measures (pair-sum share, days a net importer, the ten peak days);
- the counts behind each measure.

**PJM.** Its prices are licensed for internal use and not held, so it has no cost or price-stress measure and none is estimated. ISO-NE has no median time to connect, because Berkeley Lab gives no online dates for its completed requests.

## The pulls, against their ceilings

| Pull | Ceiling | Rows | Notes |
|---|---|---|---|
| Berkeley Lab, Queued Up 2026 edition data file | 100,000 | **38,201** requests (8,513 active) | License **CC BY 4.0** (attribute Lawrence Berkeley National Laboratory and GridTracker), quoted in the header. emp.lbl.gov answers automated requests with HTTP 403, which I did not work around; the same file is published on eta-publications.lbl.gov. One download, saved under `warehouse/raw/lbnl_queues/`; a rerun reads it. Table `lbnl_interconnection_queue` (entities, history, kept out of the live set) |
| EIA-930 interchange, every pair, 2019 to today | 3,000,000 | **945,130** pair-days | Hourly would have been about 23 million rows, over the ceiling, so the daily route was used: EIA's Eastern day for every pair, 390 directed pairs, 2019-01-01 to 2026-09-30, 282 pages. It is resumable by month checkpoint, and three helper processes filled checkpoints in parallel (`eia930_daily_interchange_fill.py`). Table `eia930_daily_interchange` (history, not in the live set). Public domain |

Both tables, and `ai_power_regions`, pass the validator and are in the Redivis draft.

## Decisions and what the data showed along the way

- **Imports: EIA's balance is the headline.** EIA's daily interchange is missing for 47 to 53 days of the year in six regions, and 156 in SPP. A few pair-days are impossible: SWPP-MISO reported 2,159,056 MWh on 2026-07-21, more than SPP's whole daily demand. So:
  - The headline import share is EIA's own balance, demand less net generation over the year's complete hours.
  - The pair sums give the per-day measures, on complete days only, with pair-days further than ten median absolute deviations from the pair's median screened out (9 in SPP).
  - CAISO's pair sums (16.64 percent) do not close with its balance (27.02 percent). The draft says so and shows both.
- **Carbon is the daily mean.** The monthly carbon table keeps only complete months (4 to 12 of the year, by region), so the carbon measure is the mean of the year's daily intensity over the days held (233 for SPP, 353 to 365 elsewhere).
- **A new unit, `year`, for the time to connect** (data standard Decision 36).
- **Every number in the prose is keyed.** I removed two unkeyed figures from my own first draft ("roughly fifty days", "more than 2 TWh") and one unsupported claim. Two sentences that assumed a ranking are now computed: in this year's data the cheapest region is also the cleanest.

## What the draft cannot say (its own section)

- Permitting, local approval, land, water and a utility's large-load connection are out of scope.
- Cost is wholesale energy at a hub. Capacity, transmission, distribution, ancillary services, taxes and hedges are not in it.
- One year: averages, not the margin.
- Queues and connection times are for generators, not loads.
- Regions are large.
- PJM's prices are not held.

## For Samuel

Nothing is required. The draft is ready for review at the token URL above. It is not published and should not be until you decide.

## Notes

- **The data lock** was held for the session and released at the end. Before the Supabase and Redivis writes, the sync was run (`--refresh`); it fetched but did not merge while files were uncommitted, then the merge was done before pushing.
- **Two new files:**
  - `docs/reports/ai_gigawatts_methods.md`, the methods appendix;
  - `warehouse/derived/ai_power_regions.py`, the builder. Rebuild with `python warehouse/derived/ai_power_regions.py` under the lock.
