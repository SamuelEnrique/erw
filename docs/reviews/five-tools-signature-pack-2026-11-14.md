# The five tools: a signature pack for Samuel (14 November 2026)

Energy Research Warehouse (ERW). Written by session 5502 of chain 269 (`queue/done/269-night-14-november-portable-p1-closeout.md`), window P1 of the portable laptop, for one sitting: read, run and sign all five. Roadmap item 2's done line asks each tool for "a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, and a decisions block". Everything but the signatures is built; this pack is what you need to give them, or to say why not.

- **What a signature is.** You fill the three lines of the note's "Sign-off" block (`Signed off by`, `Date`, `Items ... ruled, and how`) and commit it, or say it in a prompt and a session writes your words there. A session never signs.
- **What you sign accepts** the rules the block lists, at the defaults of the decisions table. It does not freeze the figures: they move with the data every day.
- **The expected values below** are what each tool's Python mirror printed on 14 November 2026 at about 09:20 UTC, on main at `85e5b2eeb` (the files of `replication/<tool>/` and `site/public/`, none changed by this chain). The do-file prints the same lines; the tolerance is half the last digit the page shows.
- **Before you run Stata.** A checkout of main at `85e5b2eeb` or later. Each do-file is run from its own folder (it reads `assumptions.csv` there and the public CSV by a relative path). The files use `import delimited` with `varnames`, `rowrange` and `stringcols(_all)`, and no package. Keep a log of each (the commands below open one), so a session can set your printed lines beside the mirror's: that closes the last open step of every chain since 233 ("a do-file run in Stata").
- **Order of the sitting.** Battery, generator, datacenter (one model family), then Automated Analysis and the Grid. Then the rulings at the end.

---

## 1. What a battery earns (`/cost-of-power/battery`)

**You sign:** `docs/methods/battery_earns_algorithm.md`, section "Sign-off". It accepts the model of section 3 (each local day from empty, at most one full cycle, foresight within the day, a price taker, reserves never called, energy at the hub, the required durations of section 3.3), the assumptions of section 6, the 90 percent month, scenarios A and B (section 11.1), the decisions of section 12 (the page's foot) and your rulings of 11, 12, 15 and 19 October 2026. It leaves open the differences of section 10.

**Key assumptions** (`replication/battery/assumptions.json`; the page's decisions block):

| Assumption | Default | Source |
|---|---|---|
| Capital cost, 4 hours | USD 1,110 per kW | Lazard, *Levelized Cost of Energy+*, June 2025, its 100 MW / 400 MWh storage case, the midpoint of 620 to 1,600 |
| Fixed O&M, 4 hours | USD 22 per kW a year | the same, the midpoint of USD 3.0 to 8.0 per kWh a year |
| Financing | 20 percent debt at 8 percent over 20 years; NPV to equity at a 12 percent hurdle | Lazard's storage structure (page 19); your ruling of 12 October 2026 |
| Degradation | 2.6 percent a year, a cut to revenue | Lazard's storage cases (the ATB holds no rate: its battery is augmented inside fixed O&M) |
| The dispatch | one cycle a day from empty, 86 percent round trip, perfect foresight within the day (the day-ahead schedule the other choice), reserves paid and never called, at the hub | the model of session 67; Lazard's low end for the round trip. An upper bound, said on the page |

**Cross-checks** (`docs/methods/crosschecks/battery.md`, 22 headline figures; the note's own table, 25 rows):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| 2024, USD 147.68 per kW | ERCOT's fleet average, USD 55 | Modo Energy, ERCOT annual report 2024 (19 March 2025) | +92.68 | one price-taking 4-hour battery with foresight and uncalled reserves at the hub, against a fleet of mostly shorter batteries at their nodes |
| 2024, USD 147.68 per kW | a modeled 2-hour battery at ERCOT North, about USD 127 | E3, *2024 ERCOT Market Update*, December 2024 | +20.68 | the closest method; duration and hub explain the rest |
| 2025, USD 87.44 per kW | the fleet's nowcast, USD 29.4 | Modo Energy, 3 February 2026 | +58.04 | the same reasons; ours over theirs 3.0, near 2024's 2.7 |
| The fall from 2024 to 2025, -40.8 percent | "-37%" per kW of storage capacity | Potomac Economics, 2025 State of the Market Report for ERCOT, June 2026 | -3.8 points | the mix of streams: the same falls by stream, ours more in reserves |
| Ancillary services, January to July 2026: USD 2.25 per kW a month | the fleet's day-ahead awards, USD 0.40 | ERCOT's awards, `ercot_storage_dam_awards_monthly` | 5.66 times | the model sells reserves as if the market had no limit; printed on the page |
| Debt coverage 2.63 | the ATB's lender coverage 2.0 | ATB 2025, financial cases | +0.63 | a required coverage against what twelve months gave on 20 percent debt |
| Breakeven toll, USD 4.19 per kW-month | Lazard's LCOS, USD 12.08 to 26.67 per kW-month | Lazard, June 2025, LCOS v10.0 | -7.89 to -22.48 | the toll pays debt and O&M only; Lazard's cost pays charging, augmentation, taxes and a return on equity |
| CAISO 2025, day-ahead, USD 85.59 per kW | the market monitor's model, USD 77.3 | CAISO DMM, 2025 annual report, Table 1.8 | +8.29 | hub against nodes, four reserves against regulation, 0.86 against 0.85 |

Fourteen of the 22 headline figures have no published counterpart (the page's own arithmetic or counts).

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\battery"
log using "battery_stata_2026-11-14.log", text replace
do replicate.do
log close
```

**Expected:** the file ends with "the page shows, for the months of the public file:" and these lines, each difference inside its tolerance:

- last twelve months, all streams, USD per kW: 81.40 (mirror 81.4022)
- share from ancillary services, percent: 33
- annual debt payments, USD: 2,261,119
- debt coverage, last twelve months, times: 2.63 (2.6271)
- scenario A, NPV at the hurdle rate, USD per kW: -697.80; USD for 100 MW: -69,779,883
- scenario A, IRR, percent a year: -8.8 (-8.8091)
- scenario A, breakeven toll, USD per kW-month: 4.19 (4.1887)
- scenario A, merchant tail, years: 0
- months held of the 36: 36; a bad month: December 2024 (Stata prints the month as 2024m12), USD 475,477 for 100 MW
- calendar 2024: energy 62.70, ancillary 84.98 USD per kW; 2025: 57.39 and 30.05

The mirror (`python replication/battery/replicate.py`): **22 of 22 inside the tolerance.**

---

## 2. What a generator earns (`/cost-of-power/seller`)

**You sign:** `docs/methods/generator_earns_algorithm.md`, section "Sign-off". It accepts the fleet's shape for solar and wind; the battery's day from empty with one cycle and its 86 percent round trip (an upper bound); the peaker's run rule; the 90 percent month (95 for the capture price); the hub chosen pricing everything; Lazard's midpoints as the cost defaults and its financing as the debt; the 12 percent hurdle; the decisions of section 13. It leaves open the items of section 10 marked "Open".

**Key assumptions** (`replication/generator/assumptions.json`):

| Assumption | Default | Source |
|---|---|---|
| The plant | ERCOT's whole solar fleet by the hour (EIA-930), scaled to 100 MW, paid the hub average `HB_HUBAVG` in real time; nothing curtailed; no capacity or ancillary payment | the model of `merchant_revenue.py` (built 4 October 2026) |
| Capital cost, fixed O&M, life (solar) | USD 1,375 per kW; USD 12.50 per kW a year; 35 years | Lazard, *Levelized Cost of Energy+*, June 2025, the midpoints of 1,150 to 1,600 and 11 to 14 |
| Financing | 60 percent debt at 8 percent over the life; NPV to equity at 12 percent | Lazard's LCOE financing; the hurdle by your ruling of 12 October 2026 |
| Degradation (solar) | 0.7 percent a year, a cut to revenue | NREL ATB 2025, utility-scale PV; your ruling 7a of 18 October 2026 |
| Months counted | a month at 90 percent of its hours (95 for the capture price) | the model's rule; edge case 6 of the note |

**Cross-checks** (`docs/methods/crosschecks/generator.md`, 13 headline figures; the note's table, 34 rows):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| Price received, USD 23.27 per MWh | ERCOT solar's captured price, USD 21, 2025 | Potomac Economics, 2025 State of the Market Report for ERCOT | +2.27 | the fleet at the hub over October 2025 to September 2026, against each plant's node over 2025 |
| Debt coverage 0.67 | the ATB's lender coverage for PV, 1.275 | ATB 2025, financial cases | -0.605 | a merchant plant's twelve months do not pay a lender's coverage on 60 percent debt; the contract price below would |
| Energy sold, 2,580 MWh per MW (29.5 percent) | Lazard's ERCOT solar, 24 percent; the monitor's 23.8 percent | Lazard June 2025; Potomac 2025 | +5.5 and +5.7 points | the fleet's own output over EIA-860M's nameplate, against an assumed plant and a year with 6 percent curtailed |
| Contract price for 1.25 times coverage, USD 39.14 | Lazard's solar LCOE, USD 38 to 78 | Lazard June 2025, LCOE v18.0 | inside the range, at its low end | the contract pays debt and O&M only |
| Breakeven PPA price, USD 58.36 | the same, USD 38 to 78 | the same | inside the range | the PPA pays a 12 percent return as Lazard's cost does |
| Gas peaker, 2025, USD 50.42 per kW | a combustion turbine's net revenue, USD 52.59 | Potomac 2025 | -2.17 | energy alone at the hub under the page's run rule, against energy and services at nodal prices |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\generator"
log using "generator_stata_2026-11-14.log", text replace
do replicate.do
log close
```

**Expected:**

- revenue, last twelve months, USD per kW: 59.85; long-run averages: 102.24 (2023 to 2025) and 130.80 (every full year held)
- hours used for the capture price: 8736; price received 23.27; flat average 32.17; capture rate 72
- annual debt payments, USD: 7,078,769; debt coverage: 0.67 (0.6689)
- energy sold: 2,580 MWh per MW; contract price at 1.25 times: 39.14
- NPV at the hurdle rate: -76.66 USD million for 100 MW; breakeven PPA price: 58.36
- the worst month: 2024-02, USD 139,298.97 for 100 MW

The mirror: **13 of 13 inside the tolerance.**

---

## 3. What a datacenter pays (`/cost-of-power`)

**You sign:** `docs/methods/datacenter_pays_algorithm.md`, section "Sign-off". It accepts the 95 percent month; twelve counted months in a row; the bad month as the top tenth of 36 by nearest rank; standard time with no daylight saving shift; the flexible rule's 30 prior days and its yearly budget; the two transmission figures for a flat load over 8,760 hours; the two stated defaults; the decisions of section 12 (the page's foot). It leaves open the sixteen items of section 10.

**Key assumptions** (`replication/datacenter/assumptions.json`; the page's scenario fields):

| Assumption | Default | Source |
|---|---|---|
| The load | flat, 100 MW, at `LZ_NORTH`, buying every hour at the real-time price with no hedge | the page's default |
| What is counted | market energy alone: no delivery, transmission, capacity or ancillary charge (Texas's delivery charges in their own table, never added) | the page's rule, said under the figure |
| Power per GPU | 1.3 kW | NVIDIA DGX H100 datasheet: 8 GPUs, 10.2 kW maximum system power |
| Facility overhead ratio (PUE) | 1.56 | Uptime Institute, Global Data Center Survey 2024 |
| Present value | 20 years at 9.6 percent, prices unchanged | Lazard's WACC (0.6 x 8 + 0.4 x 12); no cited term or forecast is held, so the plain defaults |

**Cross-checks** (`docs/methods/crosschecks/datacenter.md`, 14 headline figures; the note's table, 8 rows):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| Market energy, a flat load, nine months held by both: USD 32.40 per MWh | Texas industrial customers, USD 67.02 | EIA, *Electric Power Monthly*, Table 5.6.A | -34.62 | wholesale energy at one zone against what industrial customers paid for everything |
| Carbon, the last twelve months: 301.82 kg CO2 per MWh | eGRID2023, ERCT: 332.87 | EPA, eGRID2023 summary tables | -31.05 | another year (2023) and method; EIA-930's own 2023 figure is 342.96, so most of the gap is ERCOT's fall since |
| 2021, a flat load at the North zone: USD 150.61 per MWh | the zone's load-weighted average, USD 221.52 | Potomac 2025 | -70.91 | Uri's highest prices fell in the hours of highest load; ours is the flat mean |
| 2022 to 2025, the same zone | 77.30, 78.01, 30.42, 35.34 | Potomac 2025 | -14.37, -29.32, -4.01, -2.68 | the same weighting |

Eleven of the 14 headline figures have no counterpart held.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\datacenter"
log using "datacenter_stata_2026-11-14.log", text replace
do replicate.do
log close
```

**Expected:**

- the last twelve months: 2025-11 to 2026-10; market energy, a flat load: 34.07 USD per MWh (34.0714)
- cost for 100 MW: USD 29,846,522; power per GPU-hour: 0.0691; GPUs that 100 MW powers: 49,310
- bought day-ahead, the same twelve months: 35.70
- a bad month: 2026-08, 37.88 USD per MWh
- hours at or above USD 1,000: 4; a flat 100 MW load paid USD 446,175 in them
- carbon at the monthly average: 301.82 kg per MWh, 264,395 tonnes a year; the hourly window: 10,151 hours, 309.54 kg per MWh (the public file's window; the live page's window moves daily)

The mirror: **14 of 14 inside the tolerance.**

---

## 4. Automated Analysis (`/research`)

**You sign:** `docs/methods/automated_analysis.md`, section "Sign-off". It accepts the templates and the engine; the rule since session 119 for the week's most notable real change; the decisions of the section "Decisions" at their defaults; the final form as the section "Final form" lists it, with findings published only after your approval. It leaves open what `automated_analysis_findings.md` leaves open in its own block; `automated_analysis_scanner.md` is covered through "Final form".

**Key assumptions** (`replication/analysis/assumptions.json`, 35 rows):

| Assumption | Default | Source |
|---|---|---|
| The week's chart | a real measure's change (not a level), ranked among its own last 104 weekly or 36 monthly changes, at least 8 of them, its period new and ended within 100 days; the highest score chosen | `warehouse/analysis/run.py` (session 119); the note, "The rule since session 119" |
| The scanner's spike | a daily mean at 2 times the 99th percentile of the prior 3 years' daily means, with at least 730 points | `warehouse/config/scanner.yaml`; `automated_analysis_scanner.md` |
| The cards' statistics | regressions with robust errors scaled by n / (n - k), as Stata's `vce(robust)`; the impact study's Newey-West lags floor(4 (n / 100) ^ (2 / 9)) | the cards' own code |
| The license hold | a callout naming ISO-NE, MISO or NYISO reads "license needed" | `site/data/license_status.json`, since 21 October 2026 |
| Publishing | a deeper finding only after you approve it at `/internal/findings`, its Stata run first; nothing posted to LinkedIn | your rulings of 12 October 2026, night |

**Cross-checks** (`docs/methods/crosschecks/automated_analysis.md`):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| ERCOT's battery fleet, end of 2025: 13,909 MW | "exceeded 17 GW" | Potomac 2025 | at least -3,091 MW | what each counts: ERCOT's capacity approved to operate against EIA-860M's operating inventory; Modo's count agrees with EIA's |
| ERCOT's solar added in 2025: 7,816 MW (EIA-860M) | "6.2 GW of solar entered commercial operation in 2025" | Potomac 2025, pages 13 and 15 | +1,616 MW | two inventories: EIA's operating plants against ERCOT's commercial operation dates |
| ERCOT West's negative hours, 2025: 638, the most of the hubs | "the West zone experienced the highest number of intervals with negative prices ... of any load zone" | Potomac 2025, chapter I.C | the same order: West first | the monitor states the rank, not the hours |
| A 1 GW load's all-in: USD 41.04 to 46.83 per MWh | Texas industrial retail price | EIA, *Electric Power Monthly* | -25.98 and -20.19 | the retail price holds distribution and retail costs |

The queue card (75 percent of requested capacity withdrawn, 2000 to 2020) is set beside your own thesis, not a publisher's figure; the file says so.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\analysis"
log using "analysis_stata_2026-11-14.log", text replace
do replicate.do
log close
```

**Expected:** a list of every card's figures (card, field, the page's text, the replication, the difference, the status), then "inside the tolerance: 62" and "outside the tolerance: 0". The mirror computes 66 (all inside); the do-file leaves the week's chart's 4 to `replicate.py` (its file is JSON), and says so in each row's status. Also 10 "license needed" and 2 "not in the download" (the siting card's months to connect).

---

## 5. The Grid (`/grid`: network, energy mix and Ask on one page)

**You sign:** `docs/methods/grid_network.md`, section "Sign-off". It accepts EIA-930's interchange as the network's one source, with the pair rule; the newest complete hour and the two-day lag said under the chart; EIA-930's net generation as the gravity shape's one source, CAISO's break said and not substituted; the square-root pull; your rulings of 18 October 2026 that the page's decisions block carries (1a, 2c, 3c, 4b, 6a). It leaves open what the section "Cross-checks" lists as not compared, and the "Checked against" line the page does not carry (ruling G1 below).

**Key assumptions** (`replication/grid/assumptions.json`, 25 rows):

| Assumption | Default | Source |
|---|---|---|
| The network's source | EIA-930's hourly interchange, each pair once, the flow the first balancing authority in code order reports | `warehouse/derived/grid_network.py` |
| The hour shown | the newest hour every reporting pair holds; a pair quiet for 48 hours set aside; its age said twice | `site/lib/networkV3.ts`, `gridKeys.ts`; your ruling 3c |
| The gravity shape | EIA-930's net generation for every circle (CAISO not substituted); the pull sign(share) x sqrt(abs(share) / 0.25), full at a quarter of generation | your rulings 1a and 2c of 18 October 2026 |
| Carbon intensity | EIA's CO2 emissions generated over net generation, energy-weighted over whole UTC days | `warehouse/derived/carbon_intensity.py`; `docs/methods/emissions.md` |
| The opening grid and the panel | the Lower 48; the Ask panel answers from public tables only, a held grid's tables refused by name | your ruling 4b; `warehouse/chat/tools.py` |

**Cross-checks** (`docs/methods/crosschecks/grid.md`; the note's table, 11 rows):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| Net generation 2025, EIA-930 summed: ERCOT 485.2, CAISO 185.4, PJM 873.8 TWh | Form EIA-923's plant rows by balancing authority: 541.8, 203.1, 878.1 | EIA-923, 2025 final file | -10.45, -8.72, -0.48 percent | metered by the authority against each plant's own generation, self-use among it |
| The Lower 48, 2025: 4,280.5 TWh | 4,494.7 TWh | the same | -4.76 percent | the sum of the reasons above |
| Carbon, 2023, kg CO2 per MWh: the Lower 48 348.57, ERCOT 342.96, ISO-NE 231.85 | eGRID2023: US, ERCT, NEWE | EPA, eGRID2023 | +0.57, +10.09, -12.76 | the generation EIA-930 leaves out (7.5 percent in ERCOT, 6.5 in ISO-NE) at its implied rate |
| Net imports by ties, the hour of 12 October 2026 03:00 UTC: ERCOT 128, ISO-NE 156, NYISO 2,120 MW | EIA-930's demand less net generation: 128, 156, 2,111 | EIA-930 | 0, 0, +9 MW | the three grids whose ties close EIA's balance |
| One tie, MISO to SPP, 15 February 2021: 95,060 MWh | SPP's report of the same tie: 95,390 | EIA-930 | -330 MWh (0.3 percent) | two operators' reports of one flow; the pair rule reads one |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\grid"
log using "grid_stata_2026-11-14.log", text replace
do replicate.do
log close
```

`replicate.do` runs `replicate_ask.do` at its end. It reads `snapshot_hour.csv` (committed) and, for the carbon months, the warehouse's tables as CSV in `../../warehouse/output` (set `global tables` at its top to another folder if yours are elsewhere).

**Expected:** the network's lines (`net|lag|2026-11-03T23:00:00Z|2026-11-05T23:09:35Z = 48`, `net|topexport|... = 2634 (SRP)`), then the comparison: "met: 85" and "not met: 0" (every network and gravity figure: 9 net exports, 12 net imports, 7 tie counts, 7 largest flows, 48 ties, the lag, the largest net exporter). On a checkout without the carbon tables the 21 carbon figures read "not held in the tables given". `replicate_ask.do` then prints each stored answer's query beside the page's value; those whose tables are not given read as not held, and the 22 of ISO-NE, MISO and NYISO "license needed".

The mirror: **85 of 85 computed figures met**, 22 license needed, 81 not held in this laptop's tables (the carbon months and the Ask answers: window A's data request row 3 rewrites them where the tables are).

---

## The rulings waiting (each with its default; the default stands until you rule)

From chain 243's note (`docs/state/note_2026-11-13_portable_p1_c243.md`), with what this chain built on each default:

1. **The generator's six pinned tests** (data request row 2): may a session change them so `GENERATOR=1` runs daily? Default: no; the page ends September 2026.
2. **The price years build on the data machine's daily run** (data request row 4). Default: window A builds and loads it by hand. This chain wrote the ready script (`scripts/price_years_rebuild.py`, data request row 5).
3. **The five signatures.** Default: unsigned. This pack.
4. **The do-files in Stata.** Default: never run. The commands above.
5. **Research's final form.** Default: final as the note describes. Built on the default (session 5503): the note's "Final form" now says final, on this default.
6. **The words for a negative coverage** (battery row 11). Default: as written: "did not earn its fixed O&M, so nothing was left for its debt (coverage -0.14 times)." (CAISO, 8 hours, the day-ahead schedule). Held by a test (session 5503).
7. **Building on this laptop while three windows run.** Default: P1 builds only with 2 GB free (your words of 14 November), else reads production.
8. **Chain 233's battery rows 4, 5 and 8, and the queue mark.** Defaults stand.

New in this pack:

- **G1. The Grid page's "Checked against" line.** The three economics pages end with "The default case hour by hour: CSV, Stata do-file, Python mirror ... Checked against: N published figures ... Each comparison". No view of `/grid` links the Grid's replication or its cross-checks; the default view links `generation_mix_hourly` only, the Network tab `grid_network`. Default: no line (a change of the page's words, which the note leaves to you). If you say yes, one line in the economics pages' form under the decisions block: "The network's hour: CSV, Stata do-file, Python mirror. Method note. Checked against: 11 published figures (EIA-923, eGRID, EIA-930). Each comparison."
