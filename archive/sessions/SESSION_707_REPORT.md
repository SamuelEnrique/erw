# Session 707 report: carbon on the All grids tab

22 October 2026, from 09:32 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-707` on `wip/707-allgrids` (cut from `wip/706-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 707. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Each row shows its eGRID subregion's CO2 rate**: the plants' CO2 over their net generation, kg per MWh, with lb under it. The source is eGRID2023 (`egrid_power_plants`, rebuilt from the archive, through the new `site/data/siting/carbon.json`).
  - ERCOT ERCT 332.9 kg (733.9 lb).
  - CAISO CAMX 194.3 kg (428.5 lb).
  - NYISO: NYUP for zones A to G (242.1 lb), NYCW for H to J (864.5), NYLI for K (1,180.7).
  - ISO-NE NEWE (539.3 lb); SPP SPNO and SPSO; MISO's hubs their state's subregion; PJM the plants eGRID places in PJM (716.9 lb).
- **The first sum was wrong, and was mended before anything was committed**: plants whose CO2 cell is blank (wind, solar, hydro, nuclear) had been dropped with their generation, giving NYUP 890 lb. eGRID sums every plant's generation and the CO2 reported, and now so does the tab (242.1). `tests/test_session707.py` recomputes three subregions from the plant table and pins them.
- **A profile that runs in some hours** (the electrolyzer, flexible compute) shows the grid's hourly intensity weighted by the load over the hours it runs, with the annual rate under it. This is `carbon_intensity_hourly`, `intensity_demand`, the measure "Your load" uses, and it needs 90 percent of the hours covered.
  - Electrolyzer: ERCOT 265.1 kg, CAISO 94.9, NYISO 250.5.
  - MISO and PJM: annual only (no price, so no hours run).
- **Keys**: `allgrids|carbon|<row>`, `allgrids|carbonlb|<row>`, `allgrids|carbonh|<row>|<profile key>`.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view): the Carbon column, ERCOT 332.87 kg, 733.86 lb.
2. Choose Electrolyzer, and under "Sort and filter" sort by carbon, smallest first: CAISO's hubs come first (about 95 kg over its hours), with "annual 194.32" under each.
3. Screenshots: `docs/brand/review-707/` (712's build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session707` and 700 to 706 | 0 | OK, 1 skip |
| built and checked on 712's branch | 0 | see 712's report |
| the replication (712), the electrolyzer's hourly carbon at three rows from the live set | 0 | equal, once the tab's file was rebuilt from the newer copy of the hourly table (712's report) |

## The landing

With sessions 706 to 712 in one push.

## Decisions made without you

1. **Each row's subregion by geography** (`subregionOf`): New York's zones H and I with the city (Westchester); MISO's hubs by their states; PJM by eGRID's ISO/RTO field, because it spans several subregions.
2. **The annual figure is generation-based (eGRID), the hourly one consumption-based (EIA-930)**: each tip says which. They differ: NYCW's in-city plants are 392 kg, while NYISO's consumption is 251 over the electrolyzer's hours.
3. **eGRID's own published subregion rates were not compared** (no web request). The three pinned figures are the file's own.

## For Samuel's ruling

- Whether the annual column should be consumption-based too (EIA-930's monthly intensity, as "Your load" draws it), so both figures are of one measure.

## Files

- Changed: `site/lib/siting.ts` (`subregionOf`, `areaRate`, `hourlyCarbon`, `carbonCell`; `profileTwelve` keeps its weights), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`CarbonTd`), `site/scripts/siting-files.mjs`, `warehouse/derived/siting_page.py` (`carbon.json`).
- New: `site/data/siting/carbon.json`, `tests/test_session707.py`, this report.
