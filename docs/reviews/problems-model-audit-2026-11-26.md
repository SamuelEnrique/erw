# The problem sets and the bill explainer: the learning pages audited as a hostile expert would

Session 10229, chain 710 part D, 26 November 2026, the old laptop. Platform tool 28, the problem set builder for educators (`/learn/problems` and its sets), and `/learn/bill`, the bill explainer (both in review, in no menu). Read as an economics professor checking each keyed answer before assigning it, and as a utility rate analyst checking the bill, each looking for the answer or line that is wrong. In the form of `docs/reviews/states-model-audit-2026-11-26.md`. The faults reads of 16 November (`docs/reviews/problem-sets-faults-2026-11-16.md`, `bill-faults-2026-11-16.md`) and the ruling papers of 17 November are not repeated.

- Nothing changed on main but this file, its evidence folder (`docs/reviews/problems-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-problems-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a keyed answer carries a test only and is not for landing.

## In short

- **The arithmetic is right.** An independent restatement (standard library, written from each question's words, the decisions block and the files' fields, not from `site/lib/problems.ts` or `site/lib/problemsets/`) gives all 142 figures the 39 answers of the five sets (worked examples included) of the whole country print, to the digit and in the order printed, and every one of the 503 keyed figures the five pages carry equals a restated figure. The five default bills (PG&E 229.63, SCE 224.76, SDG&E 332.91, Oncor 95.27, CenterPoint 95.28 USD) restate to the cent from the tariff passages, PG&E's both from its unbundled lines and from its total rates; the two bill questions (26.91 USD, 11.72 percent; 23.70 USD, 24.88 percent) restate from `cost_of_power_monthly`.
- **The two bill questions do not say which price their key uses (finding 1, Medium).** "How many dollars are wholesale energy" is keyed to the latest complete month's load-weighted real-time price of one hub, on the metered kWh, against the bill before taxes; none of that is in the question. At the month's simple mean the answers are 26.55 USD and 11.56 percent (PG&E), at the same price with 5 percent losses 28.25 and 12.30. Fixed in words.
- **"Most of a home's bill pays for wires, programs and fixed charges, not the power itself" is false for the default Oncor bill (finding 2, Medium).** The retailer's energy charge is 54.42 of 95.27 USD (57.12 percent); the wires 40.85 (42.88). The sentence holds only if "the power itself" is the wholesale energy at the hub (24.88 percent). Fixed in words.
- **Who trades with whom asks its ratios backwards (finding 3, Medium).** "How many times its 2019 flow was its 2025 flow?" is keyed to 2025 over 2019 (1.66); read in order, as ruling 7a's other questions are written, it is 0.60. The same in two more questions (1.04 against 0.96). Fixed in words.
- **The student is told to read numbers the key does not use (finding 4, Low).** The map's legend prints one decimal: from it the sun's ratio is 4.31 and the wind's gap 0.60, keyed 4.36 and 0.62; the answer's own printed figures give 4.37. In 3 of the 40 derived figures the printed inputs give another last digit, and no page says the key uses the unrounded figures. And the set's page says every answer is computed from the warehouse's tables when the page is built; the five sets read committed files that move only when rebuilt (finding 5). Fixed in words.
- **Two sentences the files contradict (finding 6, Low):** in Elliott's peak hour Tennessee's coal ran 116 MW above its baseline, while imports carried 40.4 percent of the extra demand; "how much did its demand grow" is average demand, asked beside the peak. Fixed in words.
- **A winter bill set against a summer month's price (finding 7, Low, a figure).** The California defaults are winter tariffs; their wholesale price is September 2026's. At the mean of the winter months held, PG&E's wholesale share is 8.07 percent, not 11.72. For Samuel's ruling, default "left as it is".
- **Right as stated:** every sign and window the questions name; the gap over the hours both reported; the tariff lines against the passages (PG&E's sixteen lines sum to its total rates exactly; Oncor's seven riders; taxes and local fees said to be left out); the Texas default energy charge as derived; no held grid's own rows reach a figure (MISO appears once, as EIA's partner name in the Tennessee Valley Authority's own reports).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/learn/problems/page.tsx` | The index: the ten sets, each with its grids, tables, skills, its CSV and the newest edition; the decisions of every set |
| `site/app/learn/problems/[slug]/page.tsx` | A set's page: what a student can do after it, the note for teachers, the worked example (open), the questions with "Show answer" (answer, one-line computation, worked solution, why it matters), each figure keyed (`Num`, its source on hover); the set's decisions |
| `site/app/learn/problems/[slug]/[edition]/`, `teacher/`, `data.csv` | The dated edition (students' and teacher's copies) and the set's figures as CSV; no edition holds the five sets of the whole country |
| `site/app/learn/problems/Decisions.tsx` | The 21 decisions, each with its default and source |
| `site/lib/problems.ts` | The five live sets (A to E) on the live set (Supabase) and committed files; `SETS`, `problemSet`; `calc` (ratio, difference, percent of two keyed figures) |
| `site/lib/problemsets/common.ts`, `who-trades-with-whom.ts`, `storm-across-the-country.ts`, `under-the-ground-and-in-the-wind.ts`, `where-energy-goes.ts`, `your-own-balancing-authority.ts` | The five sets of the whole country: every figure a `pf|` key into a committed page file (`site/lib/pagefile.ts`) |
| `site/lib/problemkit.ts` | The guide (what a student can do, the order easiest first), each figure's source as its hover, the CSV |
| `site/lib/format.ts` `shown` | How every figure prints: a whole number with separators, else two decimals |
| Page files read | `site/data/regions/trade/ten.json` (built 2026-11-21 01:13 UTC), `regions/trade_matrix.json`, `regions/events/elliott_2022.json`, `uri_2021.json`, `resources/manifest.json`, `industry.json`, `regions/authority/tva.json`, `erco.json`, `ciso.json` |
| `site/app/learn/bill/page.tsx`, `BillCalc.tsx`, `Decisions.tsx` | The bill explainer: five default cards (total, wholesale dollars and share), the calculator, ten terms, the 14 decisions |
| `site/lib/bill.ts`, `site/data/bill_rules.json` (version 2026-11-16.1) | The bills' arithmetic, and every rate with its tariff passage and effective date (PG&E E-TOU-C and SCE TOU-D as effective 1 June 2026; SDG&E TOU-DR1 of 1 August 2026; Oncor and CenterPoint as read 30 September and 1 October 2026) |
| `docs/methods/problem_sets.md`, `docs/methods/bill.md` | The method notes |
| `replication/problem_sets/` (`replicate.py`, `replicate_country.py`, `live_reads.json`, `page_figures.json`), `replication/bill/` | The replications and the live reads kept on 16 November 2026 |
| Table read here | `cost_of_power_monthly` (the main copy's `warehouse/output/`, built 3 October 2026; its September 2026 rows equal the live set's kept by `replication/bill/source_rows.csv`) |

## How every number here was computed

- **The pages as drawn:** `draw_problems.mjs` builds the five sets of the whole country with `site/lib/problems.ts` and draws each set's page (`app/learn/problems/[slug]/page.tsx`) with the site's own components, every request refused, keeping each question's parts, each keyed figure (key, value, unit, the printed string) and the visible text; it draws `/learn/bill` the same way (its wholesale reads refused, so the cards say the price is not held) and keeps the five default bills line by line from `lib/bill.ts`. The five live sets were drawn from the reads kept on 16 November 2026 with the site's own replay (`site/scripts/problem-sets-figures.mjs replay`).
- **The restatement:** `restate.py`, standard library. For each of the 39 questions it forms every figure the answer prints, in the order printed and as printed (half away from zero on the exact value, as the page's `toLocaleString` does), and checks that each appears in the drawn answer in order; that every keyed figure of the question (answer, line, steps) equals a restated figure; and, for each derived figure, what a student gets from the printed inputs. Then the five bills from the tariff passages, and the two bill questions from the table.
- **The measures:** `peek.py` and `peek2.py` on the page files and the table.
- Copies of every script and printout: `docs/reviews/problems-model-audit-2026-11-26/` (written to run from `runs/c10229/` of a worktree).

## The arithmetic re-done

| Set | Questions (with the worked example) | Answer figures | Equal to the restatement, in order | Keyed figures on the page | Each equal to a restated figure |
|---|---|---|---|---|---|
| Who trades with whom | 8 | 29 | 29 | 111 | 111 |
| A storm across the country | 8 | 37 | 37 | 120 | 120 |
| What is under the ground and in the wind | 7 | 22 | 22 | 79 | 79 |
| Where energy goes | 8 | 25 | 25 | 89 | 89 |
| Your own balancing authority | 8 | 29 | 29 | 104 | 104 |
| **All five** | **39** | **142** | **142** | **503** | **503** |

| Bill (600 kWh, the defaults) | The page | Restated | How |
|---|---|---|---|
| PG&E E-TOU-C, winter, 20 percent at peak, territory T, Income Tier 3, 30 days | 229.63 USD | 229.63 by the sixteen unbundled lines; 229.63 by the total rates (Sheet 2) | baseline 225 kWh (7.5 a day x 30); generation line 69.45, PCIA -6.07; Base Services Charge 23.80 |
| SCE TOU-D 4-9 PM, winter, Region 9 | 224.76 | 224.76 | baseline 360 kWh (12.0 x 30) at -0.10099 |
| SDG&E TOU-DR1, winter | 332.91 | 332.91 | no baseline credit (allowance 0) |
| Oncor | 95.27 | 95.27 | energy 54.42 (0.0907 x 600); delivery 40.85 (4.06 fixed, 0.061322 a kWh) |
| CenterPoint | 95.28 | 95.28 | energy 51.18; delivery 44.10 |
| B3, PG&E's wholesale energy and share | 26.91 USD of 229.63: 11.72 % | 26.91; 11.72 | 600 kWh x 44.8469 USD/MWh (NP15, September 2026) / 1,000 |
| B4, Oncor's | 23.70 USD of 95.27: 24.88 % | 23.70; 24.88 | 600 x 39.5037 (ERCOT's hub average, September 2026) / 1,000 |
| The Texas default energy charge | 0.0907 USD a kWh | 0.0907113, as the file's arithmetic says | 158.8 / 1,000 - 0.061322 - 4.06 / 600 |

| A sample of the answers, as printed | The page | Restated |
|---|---|---|
| Tennessee's net imports, October 2026 (t1) | 574,900 MWh; the Midwest 1,650,259 | equal; the four neighbours sum to the file's total |
| The Mid-Atlantic and Tennessee, 2019, the year of the largest gap (t4) | 2,437,201 against -6,612,970 MWh; apart 9,050,171; the file's gap 9,034,597 | equal; 2019 the largest gap of the eight whole years |
| Tennessee's peak in Elliott (s1) | 2022-12-24 01:00 UTC, 33,225 MW against 19,830: 1.68 times | equal (position 116 of 267 hours) |
| Texas's peak in Uri (s2) | 2021-02-15 01:00 UTC, 69,215 MW, 28,754 above the baseline | equal |
| The sun's legend (rx) | 1.58 to 6.91 kWh/m2/day: 4.36 times | equal (1.584, Alaska south of 60 degrees north; 6.912, Hawaii) |
| Industry, July 2026 (i1) | 2,713.60 TBtu in all, end use 2,239.91, apart 473.70; losses 473.70 | equal |
| The Tennessee Valley Authority (bx, b5, b7) | 44,697.40 MW, nuclear 19.77 %; MISO net 99.66 % of gross; growth 7.15 % against ERCOT's 27.22 % | equal |

## One rule changed at a time

| Rule | The key | Changed to | Measured worth |
|---|---|---|---|
| B3 and B4's price | the month's load-weighted real-time price | the month's simple mean | PG&E 26.91 to 26.55 USD (11.72 to 11.56 percent); Oncor 23.70 to 23.03 (24.88 to 24.18) |
| B3 and B4's energy | metered kWh | with 5 percent losses (EIA's figure, the bill's decision `wholesale-energy`) | PG&E 28.25 USD, 12.30 percent; Oncor 24.89, 26.12 |
| B3's month, for a winter bill | September 2026 (the latest complete month) | the mean of the winter months held, October 2025 to May 2026 (8 months, whole or not) | PG&E's NP15 44.85 to 30.91 USD/MWh: 26.91 to 18.54 USD, 11.72 to 8.07 percent |
| B3's bill, for a September price | the winter bill (229.63) | PG&E's summer bill at the same defaults (262.33) | 11.72 to 10.26 percent |
| The ratio's order (t2, t5) | later over earlier, Tennessee over the Midwest | read in the order the question is written | t5 1.66 and 1.67 become 0.60 and 0.60; t2 1.04 becomes 0.96 |
| What the student divides (rx, r1, r3, i1) | the files' unrounded figures | the figures the student is shown | rx 4.36 becomes 4.31 from the map's legend, 4.37 from the answer's own figures; r1 0.62 becomes 0.60 from the legend; r3 1.75 becomes 1.74; i1 473.70 becomes 473.69 |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "How many dollars are wholesale energy, and what share of the bill is that?" | B3, B4 (`prices-and-your-bill`) | the latest complete month's `rt_load_weighted` of the bill's hub (NP15; ERCOT's hub average), metered kWh, the bill before taxes | **Finding 1**: none of the four choices is in the question; the step names the month only |
| "Most of a home's bill pays for wires, programs and fixed charges, not the power itself" | B3, B4 "why it matters" | none: words | **Finding 2** for Oncor |
| "How many times the Southeast's report was Tennessee's?", "how many times its 2019 flow was its 2025 flow?" | tx, t2, t5 | Tennessee over the other side; the later year over the earlier | **Finding 3**; ruling 7a's order is "A was how many times B?", as s6, i2, i7 and b6 ask |
| "The sum of the four" | t1, the third step | typed; the question counts the neighbours from the file | Right today (four); **finding 3** words it from the file |
| "The legend ... prints one decimal" and the answer's two | rx, r1 | the answer divides the list's three-decimal values | **Finding 4** |
| "Every answer is computed from the warehouse's tables when the page is built, so the numbers move as the data updates" | every set's page | the five sets of the whole country read committed page files; they move when the data machine rebuilds a file (decision `page-file`) | **Finding 5** |
| Rounding the student is told | every page | no word; every figure two decimals or whole | **Finding 4** |
| "The extra demand of a storm hour falls to the plants that can be turned up, such as gas, coal and hydro" | s3 "why" | gas +5,374 MW and hydro +2,509 over the baseline hour; coal +116 (2,061 MW under its own window high); imports +5,415 of the extra 13,395 | **Finding 6** |
| "How much did its demand grow from 2019 to 2025" | b7 | the newest whole year's average demand against 2019's (`docs/methods/authority_facts.md`) | **Finding 6**: asked beside the peak, the measure is not named |
| A winter bill and its wholesale month | the cards, B3 | the latest complete month whatever the season | **Finding 7** |
| Units | all | MWh, MW, TBtu, MWe, dry metric tons a year, kWh/m2/day, each named on its figure; "ratio" printed as the capacity factor's unit | **Right** (the capacity factor's "0.31 ratio" reads oddly; the step says multiply by 100 for a percent) |
| The data's window and as-of date | every question | the month or year named in each question (October 2026; 2019 and 2025; July 2026; November 2025 to October 2026; EIA-860M of 2026-09); the storms' windows and baselines from the files | **Right**; the trade file's month is the newest that had ended at its `built` stamp, as the decision says |
| Signs | t1 to t7, s5, s7, b5 | ten.json above zero an import to Tennessee; the matrix's A report from A to B, B's turned to the same direction (`docs/methods/interchange_pairs.md`) | **Right** in every step |
| "A gap over the hours both reported" | t3, t4 | Tennessee 744 hours, the Mid-Atlantic 743, both 743: -224,071 against the file's -222,699 | **Right**, and the words follow the figures by rule |
| "The ended month ... reported for the smallest share of the hours" | t7 | July 2018, Tennessee's own report with the Midwest 407 of 744 hours, while its three other ties hold 743 | **Right**: a real part-month, not the file's start |
| "Mexico's side: 0 hours" | t6 | hours_b 0 | **Right** |
| The three authorities' months | b2, b6 | November 2025 to October 2026 in all three files | **Right** |
| "A few industries ... use most of manufacturing's energy" | i3 "why" | the first four of 21 hold 69.7 percent of the 21 industries' sum (15,740 TBtu) | **Right**; the ranking is the order of the United States totals |
| End use and losses | i1 | total less end use equals the file's losses to the second decimal | **Right** |
| Held grids reaching a figure | all | EIA-930, EIA-860M, EIA's surveys, NREL's and USGS's layers; MISO only as EIA's partner name in b5 | **Right** |
| A bill's tariff components against a real tariff | the cards, the calculator | fixed charges (PG&E's Base Services Charge by income tier; Oncor's customer and metering charges), energy and delivery per kWh, riders (Oncor's TCRF, EECRF, DCRF, NDC, RCE, MG, IS), credits; taxes and local fees left out | **Right as stated**: PG&E's 16 unbundled lines sum to the total rates of Sheet 2 to the hundred-thousandth of a dollar in each period; the page says "taxes and local fees are not included". Not sized here: the taxes (data request 1) |
| The tariffs' year | the cards, the decisions | each line's effective date; rates as read 30 September and 1 October 2026; nominal dollars | **Right as stated** |
| The Texas default energy charge | the cards, decision `texas-energy` | EIA's July 2026 Texas residential average less Oncor's delivery at 600 kWh | **Right** as derived (0.0907113); EIA's average is every Texas utility and retailer, said |
| Worded as a cause | the "why" lines | words | Finding 2 and finding 6; the others read as general statements the figures do not contradict |

## What an economics professor or a rate analyst would add

| Item | Size | From |
|---|---|---|
| A rounding rule for students: say that the key uses the files' unrounded figures, or key from the printed figures | 3 of 40 derived figures differ in the last digit | the restatement |
| The bill after taxes and local fees, so the share is of what the home pays | not sized here | data request 1 |
| The retailer's energy charge split into wholesale energy, losses, ancillary services, ERCOT's fees and margin, for the Texas cards | the gap is 54.42 less 23.70 = 30.72 USD at the defaults | the files; finding 2 |
| The wholesale price of the bill's own season | PG&E 11.72 to 8.07 percent | finding 7 |
| The Texas homes against their own load zone (North, Houston), not the hub average | not sized: the table holds the hubs only (the bill's decision `wholesale-zone`) | already said on the page |

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Medium | B3 and B4 do not state the price, the month rule, the kWh basis or that the bill is before taxes | simple mean: PG&E 26.55 USD, 11.56 percent; with losses 28.25, 12.30 | `wip/audit-problems-1` | words, for landing |
| 2 | Medium | "Most of a home's bill pays for wires ... not the power itself": false for the default Oncor bill | energy charge 54.42 of 95.27 USD, 57.12 percent | `wip/audit-problems-2` | words, for landing |
| 3 | Medium | Who trades with whom asks "how many times A was B" for B over A | t5 0.60 read in order against 1.66 keyed; t2 0.96 against 1.04 | `wip/audit-problems-3` | words, for landing |
| 4 | Low | The legend and the printed figures are not what the key divides; no page says so | rx 4.31 (legend) and 4.37 (printed) against 4.36; r1 0.60 against 0.62; 3 of 40 derived figures | `wip/audit-problems-4` | words, for landing |
| 5 | Low | "Computed from the warehouse's tables when the page is built" on the five sets that read committed files | 5 sets, 39 questions | `wip/audit-problems-4` | words, for landing |
| 6 | Low | Coal named among the plants turned up in Elliott's peak; "demand grow" is average demand | coal +116 MW, imports +5,415 of +13,395 | `wip/audit-problems-5` | words, for landing |
| 7 | Low | A winter bill valued at a summer month's price | PG&E 11.72 to 8.07 percent | `wip/audit-problems-6` | figure, the owner's |

- Three Medium, four Low. Finding 7 would move a keyed answer if fixed: its test is on its own branch, not for landing.
