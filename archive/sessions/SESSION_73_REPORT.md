# Session 73 report: California's generation series, and what depends on it

Energy Research Warehouse (ERW), session 73, second of the overnight chain, on the portable laptop, 2026-10-03 from about 09:30 to 10:20 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). One approved pull, under its ceiling; no model call, no force push. Branch `wip/073-caiso-break` on GitHub (it holds session 72's branch too).

**A figure on a live page is affected: `/network`.** CAISO's sphere colour and the panel's carbon number come from EIA's California series. So does the panel's import share by "demand less net generation", which session 68 already shows as a range. Nothing on the home page, `/storage`, the battery tab or the seller tab depends on the break. Tonight's rule (nothing live changes) means `/network` is not labelled yet: the edit is in "To finish".

## To finish

```bash
# 1. After session 72's branch has merged (its "To finish", step 1), merge this one
git checkout wip/073-caiso-break
git fetch origin
git merge origin/main
git push origin wip/073-caiso-break:task/073-caiso-break

# 2. The label on the live /network page (not added tonight). In site/app/network/page.tsx, add the import
#      import { CaisoBreakNote } from "@/components/CaisoBreakNote";
#    and, directly above its <SourceLine ... /> element, the line
#      <CaisoBreakNote className="mt-6 mb-0" />
#    then build, run check-routes and the network browser test, commit, and push through a task/ branch.
```

## In plain words

**What broke, and when.** EIA-930's California generation changed in one hour: the hour starting 2025-12-16 08:00 UTC, midnight Pacific.

- A geothermal series appears for the first time (about 17.5 GWh a day).
- Natural gas falls from a daily mean of 251.7 GWh (2025-06-02 to 2025-12-15) to 118.3 (2025-12-16 to 2026-09-29).
- Total net generation falls from 554.1 to 454.3 GWh a day, and is still the sum of the fuels.
- Demand (656.1 to 646.0) and interchange did not step. So EIA's own balance for California, which closed within 4.7 GWh a day before, is 80.7 GWh a day short after (about 12 percent of demand).

**The likely cause, and how sure.** It is a reporting change, not a change in the grid: one hour, in the fuel categories, with demand and interchange unmoved. I am sure of that. And it is probably not California's alone: ERCOT's "unknown energy storage" series ends the day before (2025-12-15). That suggests EIA changed its fuel categories.

**The finding that turned the question around.** CAISO's own supply by fuel (pulled tonight) shows that **after the break, EIA's gas and geothermal equal CAISO's own to within 1 percent**:

| GWh a day | EIA before | CAISO before | EIA after | CAISO after |
|---|---|---|---|---|
| Natural gas | 251.7 | 178.3 | 118.3 | 119.1 |
| Geothermal | none | 17.8 | 17.4 | 17.6 |

So the series did not lose gas below CAISO's figure. **Before the break, EIA's "gas" was about 73 GWh a day above CAISO's own:** about 18 of that was geothermal not yet separated, and about 55 matches nothing in CAISO's fuel mix. After the break that ~55 is gone from EIA's generation but not from EIA's demand, which is why the balance broke.

What these data cannot settle: what that generation is. It could be resources CAISO's own fuel mix does not show, or a definition of demand that changed less than generation did. I say no more than that. EIA states no change in the workbook's notes; its known-issues page answered HTTP 403 and was not read.

**Affected pages, live first.**

- **Live:** `/network`: CAISO's sphere colour and carbon number, and the panel's import share by demand less net generation.
- **In review:** `/emissions`, `/grid`, `/grid/caiso`, `/mix`, `/cost-of-power` (its cost against carbon chart), session 62's AI gigawatts draft, the problem sets that use California's carbon intensity, and `/ask`.
- **Labelled tonight:** the six review pages, with one plain sentence and a link to the method note (`/data/methods/eia930_caiso_break`).
- **Not affected:** the home page tiles, `/storage`, the battery tab, the network's two historical stories (Uri 2021, June 2025), curtailment, the CAISO battery cycle (CAISO's own data), and every figure before 2025-12-16.

**The recommended correction (not applied; Samuel rules).** For California from 2025-12-16, use CAISO's own supply by fuel source (`caiso_fuel_supply`, now held hourly from 2025-06-01) for generation, the generation mix and the generation side of the carbon figures. Keep EIA-930 for interchange, and before the break. Say where the series join, on every page that crosses it. What that would change is in the audit below.

**The pull against its ceiling:** `caiso_fuel_supply`, CAISO Today's Outlook supply by fuel source, Pacific days 2025-06-01 to 2026-10-02, **151,320 rows of the 300,000 ceiling**, USD 0, public.

## Part A: what changed, with evidence

### A1. From the tables held

The ERW's EIA-930 tables in `warehouse/output` hold only the last weeks by fuel (`eia930_all_generation`, from 2026-08-26). The history by fuel was read from the per-balancing-authority workbooks the emissions connector saved (`warehouse/raw/eia930_emissions/`, EIA's "Published Hourly Data" sheet, every hour since 2015-07-01): no request.

- `warehouse/analysis/eia930_break.py` writes daily sums for the seven ISOs (`runs/session73/<ba>_daily.csv`, not in git).
- `warehouse/analysis/eia930_break_numbers.py` computes every number in this report from them.

CAISO, monthly means of complete UTC days, GWh a day (EIA-930):

| Month | Demand | Net generation | Natural gas | Geothermal | Hydro | Solar | Wind | Nuclear | Net imports |
|---|---|---|---|---|---|---|---|---|---|
| 2025-01 | 573.1 | 456.3 | 226.6 | none | 43.6 | 93.9 | 40.4 | 54.5 | 119.7 |
| 2025-06 | 645.1 | 578.1 | 196.3 | none | 65.0 | 191.0 | 75.2 | 54.6 | 70.2 |
| 2025-11 | 558.0 | 437.9 | 237.3 | none | 41.0 | 83.9 | 30.7 | 48.1 | 115.2 |
| 2025-12 | 597.8 | 387.4 | 170.2 | 17.3 | 54.0 | 74.6 | 30.4 | 52.2 | 174.6 |
| 2026-01 | 584.3 | 350.0 | 108.2 | 18.0 | 66.4 | 89.5 | 19.6 | 54.0 | 163.8 |
| 2026-04 | 563.8 | 388.4 | 55.1 | 16.1 | 52.8 | 141.2 | 75.0 | 54.6 | 94.0 |
| 2026-06 | 667.4 | 478.1 | 56.0 | 18.1 | 64.5 | 202.8 | 87.4 | 54.7 | 96.3 |
| 2026-08 | 818.3 | 658.4 | 274.0 | 18.2 | 62.8 | 188.2 | 67.6 | 54.0 | 66.8 |

(These first-pass monthly figures date each hour by its end; the dated figures elsewhere in this report date it by its start, which moves monthly means by a fraction of a percent.)

- **Which fuels fell, and on which day:** natural gas, from the hour starting 2025-12-16 08:00 UTC. The same hour geothermal appears: 16 hours of it on the UTC day 2025-12-16, all 24 from the 17th. Gas on the surrounding days: 204.9 GWh (12-14), 208.5 (12-15), 146.9 (12-16), 129.5 (12-17), 128.3 (12-18). Total net generation: 386.3, 409.2, 352.2, 352.6, 350.9 GWh.
- **Is the total still the sum of the fuels?** Yes, on every complete day from 2024 to today (the gap is 0.00 percent in every month).
- No other fuel steps at the break: hydro, solar and nuclear continue.

### A2. CAISO's own data (the approved pull)

`warehouse/connectors/caiso_fuel_supply.py` reads `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv` for each Pacific day: 5-minute MW for 13 sources, averaged to the hour.

- Complete days only; a day short of any interval is skipped and never filled. Four were skipped: 2025-11-02 and 2026-03-08 (clock changes the conversion could not place), 2026-08-21 (CAISO's file empty) and 2026-09-22 (287 of 288 intervals).
- **151,320 rows**, 485 days, 13 variables. Validator pass; in coverage (public, power, source); archived; in the Redivis draft (Redivis's count equals the file's; `erw_headers` 1,763 lines); `--check-license` ok. Not loaded into Supabase.
- The source allowed automated requests; nothing needed working around.

### A3. EIA against CAISO's own, by fuel

| GWh a day (UTC days) | EIA before | CAISO before | EIA after | CAISO after |
|---|---|---|---|---|
| Natural gas | 251.7 | 178.3 | 118.3 | 119.1 |
| Geothermal | none | 17.8 | 17.4 | 17.6 |
| Hydro (CAISO: large and small) | 56.6 | 56.7 | 59.1 | 59.4 |
| Nuclear | 49.0 | 49.1 | 53.5 | 53.8 |
| Solar | 149.4 | 172.2 | 150.6 | 172.7 |
| Wind | 51.7 | 56.7 | 60.5 | 76.6 |
| Batteries (CAISO; EIA reports none for CISO) | | -5.8 | | -6.9 |
| All generation (CAISO: imports excluded) | 554.1 | 534.2 | 454.3 | 501.3 |
| Net imports | 97.2 | 84.2 | 111.0 | 97.6 |
| EIA demand | 656.1 | | 646.0 | |
| EIA's balance residual | 4.7 | | 80.7 | |

Before: 2025-06-02 to 2025-12-15, 195 complete days. After: 2025-12-16 to 2026-09-29, 282.

What the evidence supports:

1. A reporting change effective 2025-12-16, after which EIA's California gas and geothermal are CAISO's own figures.
2. Before it, EIA's gas held about 55 GWh a day more than CAISO's gas and geothermal together.
3. After it, EIA's demand still includes that energy and EIA's generation does not.

Solar runs about 22 GWh a day below CAISO's own on both sides of the break. That is a standing difference (13 percent), not this break, but it matters to the seller tab (below). It is not a fuel moved into "imports": the imports gap (EIA about 13 GWh a day above CAISO's) is the same on both sides. It is not batteries: EIA reports no battery series for California, and CAISO's net battery figure is about -6 to -7 GWh a day.

### A4. The other six ISOs

The same checks, October 2024 to September 2026 (`runs/session73/residual_by_month.csv`):

| | Balance residual, share of demand, by month | Fuel categories appearing or ending |
|---|---|---|
| ERCOT | 0.0 every month | BAT and UES appear 2024-10-23; **UES ends 2025-12-15** |
| ISO-NE | 0.0 | PS, SNB, BAT appear 2024-11-07; COL ends 2026-03-25 |
| NYISO | 0.0 | NUC appears 2024-10-16 as its own series; OIL ends 2026-09-15 |
| MISO | -1.7 to -2.9 percent, steady | BAT appears 2025-01-15 |
| SPP | within 1 percent | BAT appears 2026-02-04; OIL ends 2026-06-02 |
| **PJM** | **-1.0 to -5.4 percent from May 2025**, moving month to month (-3.9 June, -5.4 August, back to 0 in October and November 2025, -3.5 by September 2026) | none |

No break of California's kind elsewhere. **PJM's unstable residual since May 2025 is flagged:** generation plus imports exceed its demand by up to 5 percent in some months. It is smaller than California's and not one step, and I did not investigate it.

## Part B: the audit

Every table, derived table and page that reads California's EIA-930 generation (or EIA's CO2, which EIA computes from it) for dates from 2025-12-16:

| Table | What reads California's series | Most affected figure | Rough size | Pages |
|---|---|---|---|---|
| `eia930_all_generation`, `eia930_generation_latest` (rolling, from 2026-08-26) | the mix by fuel | California's generation total | about 47 GWh a day (9 percent) below CAISO's own after the break; gas, geothermal, hydro and nuclear match it; solar about 13 percent and wind about 21 percent below | `/mix`, `/grid`, `/grid/caiso` (review); `/ask` |
| `eia930_all_emissions` | EIA's CO2 for California | CO2 generated | 104.3 kt a day before, 50.5 after: the comparison across the break is not like for like | through the carbon tables |
| `carbon_intensity_hourly`, `_daily`, `_monthly` | CO2 over EIA's generation or demand | intensity of generation | 188 kg/MWh before against 139 on CAISO's own generation (EIA's gas factor, 0.40 t/MWh); 110 against 101 after. EIA's figure ran about 49 high before the break and about 9 high after. Consumed intensity 201 before, 115 after | **`/network` (live: CAISO's sphere colour and carbon number)**, `/emissions`, `/grid/caiso` (review), problem sets, `/ask` |
| `cost_of_power_carbon` | California's consumed intensity by month | the cost against carbon chart's CAISO point | moves with consumed intensity: about 40 percent lower after the break | `/cost-of-power` (review) |
| `ba_supply_monthly` | the import share by demand less net generation | CAISO's "balance" import share | about 12 points high from the break (session 68: 26.87 percent against 16.49 by its ties, September 2025 to August 2026) | **`/network` (live: the panel's range; session 68 already says the balance overstates California's imports)** |
| `grid_network_nodes` | `carbon_intensity_hourly` | the sphere colour | as the carbon row | **`/network` (live)** |
| `ai_power_regions` (session 62's draft) | consumed intensity, a year's mean; the import share by EIA's balance | CAISO's carbon figure and import share | the year (September 2025 to August 2026) is 3.5 months before the break and 8.5 after. The carbon mean mixes two series. The import share reads about 8 to 10 points high (by the ties, about 16.5 percent) | the draft (review) |
| `merchant_revenue_monthly` | EIA's solar and wind per MW installed | CAISO solar and wind revenue | **no break**: EIA's solar is about 13 percent below CAISO's own on both sides. If CAISO's own is the better measure, the seller tab's CAISO solar revenue per MW is understated by about that much | `/cost-of-power/seller` (live): not labelled, since it is not this break; flagged |
| `battery_levels` (the game's CAISO days) | EIA's solar shape on 2026-04-27 and 2026-07-24 | the rooftop add-on's shape | no break in solar; the same standing 13 percent | the game (review, not merged) |
| `event_window_daily`, the network stories | California's generation in event windows | | none: every window is before 2025-12-16 | |
| `iso_curtailment_monthly`, `caiso_curtailment_daily`, `storage_daily_cycle` (CAISO rows) | | | none: CAISO's own data | |

## Part C: labels, not corrections

- **The method note:** `docs/methods/eia930_caiso_break.md`, served at `/data/methods/eia930_caiso_break` (in review, as every methods page but four).
- **The label:** `site/components/CaisoBreakNote.tsx`, one sentence: "EIA's generation series for California changed on 16 December 2025, and California figures after that date are under review: the method note."
- **Placed on** `/emissions`, `/grid`, `/grid/caiso` (only that grid page), `/mix`, `/cost-of-power` and the AI gigawatts draft, under each page's title. Checked in the built site: once on each, visible; not on `/grid/ercot`.
- **No table's values changed and no page switched source.**
- **`/network` is live and was not labelled tonight:** "To finish", step 2.

## Tests and checks

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 354 tests, OK (2 skipped), exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes`, both passes | exit 0 (14 live and 63 in review as a visitor, 0 failed) |
| Validator, coverage, `--check-license` (`caiso_fuel_supply`) | exit 0 each |

Package tests were not rerun: no package code changed since session 72's run.

## Errors and decisions

- **Decision: CAISO's data hourly, not 5-minute.** 5-minute rows would have been about 1.9 million, past the ceiling. The hourly mean is also the hour's MWh, which is what EIA-930 reports.
- **Decision: the comparison uses UTC days.** EIA-930 is hourly in UTC, and CAISO's hours were converted to UTC; complete days only on both sides.
- **Decision: not loaded into Supabase.** The prompt asked for history, validation, coverage and the Redivis draft; the load would also write a catalogue row that the live home page counts.
- **Error, mine:** the extractor first dated each EIA hour by its end (EIA's "UTC time" is the hour's end). Corrected and rerun; every figure here is on the corrected dates, except the first-pass monthly table in A1 as marked.
- **Error, mine:** the extractor first looked for every BA's workbook in one run folder (the connector saves them in different runs). Fixed to take each BA's newest workbook.
- **The data lock** was held 09:42 to about 09:49 UTC, for the pull, coverage, archive and upload.

## For Samuel

1. **Decide the correction for California from 2025-12-16:** CAISO's own supply by fuel (`caiso_fuel_supply`) for generation and the carbon tables' generation side, or keep EIA-930 labelled. The recommendation is CAISO's own.
2. **The live `/network`:** add the label ("To finish", step 2), and decide whether CAISO's sphere colour should keep reading EIA's intensity.
3. **The seller tab's CAISO solar** rests on EIA's solar, which runs about 13 percent below CAISO's own on both sides of the break. Not this break, but worth a ruling before the seller tab is shown to investors.
4. **PJM's balance residual** of 1 to 5 percent since May 2025 is unexplained.
5. **EIA's known-issues page** refused a plain request (HTTP 403). If someone can read it in a browser, it may state the December 2025 change.
