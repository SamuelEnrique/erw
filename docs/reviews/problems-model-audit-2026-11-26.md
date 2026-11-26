# The problem sets and the bill explainer: the learning pages audited as a hostile expert would

Session 10229, chain 710 part D, 26 November 2026, the old laptop. Platform tool 28, the problem set builder for educators (`/learn/problems` and its sets), and `/learn/bill`, the bill explainer (both in review, in no menu). Read as an economics professor checking each keyed answer before assigning it, and as a utility rate analyst checking the bill, each looking for the answer or line that is wrong. In the form of `docs/reviews/states-model-audit-2026-11-26.md`. The faults reads of 16 November (`docs/reviews/problem-sets-faults-2026-11-16.md`, `bill-faults-2026-11-16.md`) and the ruling papers of 17 November are not repeated.

- Nothing changed on main but this file, its evidence folder (`docs/reviews/problems-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-problems-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a keyed answer carries a test only and is not for landing.

## In short

- **The arithmetic is right.** An independent restatement (standard library, written from each question's words, the decisions block and the files' fields, not from `site/lib/problems.ts` or `site/lib/problemsets/`) gives all 142 figures that the 39 answers of the five sets of the whole country print (worked examples included), to the digit and in the order printed, and every one of the 503 keyed figures the five pages carry equals a restated figure. The five default bills (PG&E 229.63, SCE 224.76, SDG&E 332.91, Oncor 95.27, CenterPoint 95.28 USD) restate to the cent from the tariff passages, PG&E's both from its unbundled lines and from its total rates; the two bill questions (26.91 USD, 11.72 percent; 23.70 USD, 24.88 percent) restate from `cost_of_power_monthly`.
- **The two bill questions do not say which price their key uses (finding 1, Medium).** "How many dollars are wholesale energy" is keyed to the latest complete month's load-weighted real-time price of one hub, on the metered kWh, against the bill before taxes; none of that is in the question. At the month's simple mean the answers are 26.55 USD and 11.56 percent (PG&E), at the same price with 5 percent losses 28.25 and 12.30. Fixed in words.
- **"Most of a home's bill pays for wires, programs and fixed charges, not the power itself" is false for the default Oncor bill (finding 2, Medium).** The retailer's energy charge is 54.42 of 95.27 USD (57.12 percent); the wires 40.85 (42.88). The sentence holds only if "the power itself" is the wholesale energy at the hub (24.88 percent). Fixed in words.
- **Who trades with whom words its ratios so they read backwards (finding 3, Medium).** "How many times its 2019 flow was its 2025 flow?" is keyed to 2025 over 2019 (1.66); read in statement order, the order ruling 7a has the other sets ask in, it is 0.60. The same form in two more questions (1.04 against 0.96). Fixed in words.
- **The student is told to read numbers the key does not use (finding 4, Low).** The map's legend prints one decimal: from it the sun's ratio is 4.31 and the wind's gap 0.60, keyed 4.36 and 0.62; the answer's own printed figures give 4.37. In 3 of the 40 derived figures the printed inputs give another last digit, and no page says the key uses the unrounded figures. And the set's page says every answer is computed from the warehouse's tables when the page is built; the five sets read committed files that move only when rebuilt (finding 5). Fixed in words.
- **Two sentences the files contradict (finding 6, Low):** in Elliott's peak hour Tennessee's coal ran 116 MW above its baseline, while imports carried 40.4 percent of the extra demand; "how much did its demand grow" is average demand, asked beside the peak. Fixed in words.
- **A winter bill set against a summer month's price (finding 7, Low, a figure).** The California defaults are winter tariffs; their wholesale price is September 2026's. At the mean of the winter months held, PG&E's wholesale share is 8.08 percent, not 11.72. For Samuel's ruling, default "left as it is".
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
| B3's month, for a winter bill | September 2026 (the latest complete month) | the mean of the winter months held, October 2025 to May 2026 (8 months, whole or not) | PG&E's NP15 44.85 to 30.91 USD/MWh: 26.91 to 18.54 USD, 11.72 to 8.08 percent |
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
| The wholesale price of the bill's own season | PG&E 11.72 to 8.08 percent | finding 7 |
| The Texas homes against their own load zone (North, Houston), not the hub average | not sized: the table holds the hubs only (the bill's decision `wholesale-zone`) | already said on the page |

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Medium | B3 and B4 do not state the price, the month rule, the kWh basis or that the bill is before taxes | simple mean: PG&E 26.55 USD, 11.56 percent; with losses 28.25, 12.30 | `wip/audit-problems-1` | words, for landing |
| 2 | Medium | "Most of a home's bill pays for wires ... not the power itself": false for the default Oncor bill | energy charge 54.42 of 95.27 USD, 57.12 percent | `wip/audit-problems-2` | words, for landing |
| 3 | Medium | Who trades with whom asks "how many times B was A?" for A over B, which reads in statement order as B over A | t5 0.60 read in order against 1.66 keyed; t2 0.96 against 1.04 | `wip/audit-problems-3` | words, for landing |
| 4 | Low | The legend and the printed figures are not what the key divides; no page says so | rx 4.31 (legend) and 4.37 (printed) against 4.36; r1 0.60 against 0.62; 3 of 40 derived figures | `wip/audit-problems-4` | words, for landing |
| 5 | Low | "Computed from the warehouse's tables when the page is built" on the five sets that read committed files | 5 sets, 39 questions | `wip/audit-problems-4` | words, for landing |
| 6 | Low | Coal named among the plants turned up in Elliott's peak; "demand grow" is average demand | coal +116 MW, imports +5,415 of +13,395 | `wip/audit-problems-5` | words, for landing |
| 7 | Low | A winter bill valued at a summer month's price | PG&E 11.72 to 8.08 percent | `wip/audit-problems-6` | figure, the owner's |

- Three Medium, four Low. Finding 7 would move a keyed answer if fixed: its test is on its own branch, not for landing.

### 1. The bill questions do not name their price (Medium)

- **Where.** `site/lib/problems.ts`, set B, `billQ` (questions 3 and 4 of "Prices and your bill", asked second and third on the page).
- **Why it matters.** "On the default PG&E (California) bill of /learn/bill (600 kWh), how many dollars are wholesale energy, and what share of the bill is that?" A professor marking a student's answer needs the price the key uses, and four choices sit behind it: the hub (CAISO's NP15 zone for PG&E, ERCOT's hub average for Oncor), the weighting (load-weighted, not the plain mean), the month (the latest complete one, September 2026 on the kept reads), and the energy (the metered kWh, no losses), set against the bill without taxes and local fees. The worked solution names the month only; the decisions fold (`bill`) names the hubs. At the month's simple mean PG&E's answer is 26.55 USD and 11.56 percent (key 26.91 and 11.72), Oncor's 23.03 and 24.18 (23.70 and 24.88); with the losses the bill's own decision mentions (about 5 percent), 28.25 and 12.30, 24.89 and 26.12.
- **The test.** `tests/test_audit_problems_1.py` on `wip/audit-problems-1`: the simple mean gives another answer, from the live rows kept in `replication/bill/source_rows.csv` (passes on main); the words (fail on main).
- **The fix on the branch, words only.** The question adds "taxes and local fees are not on it" and "Value the kWh on the meter, with no losses added, at the load-weighted real-time price of the CAISO NP15 (the ERCOT hub average) in the latest complete month, 2026-09." The kept page figures (`replication/problem_sets/page_figures.json`) carry the new words so the replay comparison holds; the method note gains the line. No figure moves.

### 2. "Not the power itself" (Medium)

- **Where.** The same two questions' "why it matters".
- **Why it is wrong.** The default Oncor bill is 54.42 USD of energy charge (the retailer's price for the power, 0.0907 a kWh) and 40.85 of Oncor's delivery: the power is 57.12 percent of the bill (CenterPoint's 53.72). The sentence is true for PG&E (its generation line, less the PCIA, is 63.38 USD, 27.60 percent) and true of the wholesale energy at the hub, which is what the question computes; but it says "the power itself". A rate analyst reads the retailer's energy charge as the power: it carries the wholesale energy (23.70 USD) and also the losses, the grid's reserves and services, ERCOT's fees, the retailer's hedging and margin (30.72 USD together at the defaults).
- **The test.** `tests/test_audit_problems_2.py` on `wip/audit-problems-2`: both Texas defaults' energy charge above half the bill, the wholesale energy below (pass on main); the words (fail on main).
- **The fix on the branch, words only.** "The wholesale energy is the smaller part of a home's bill. The rest pays for the wires, programs and fixed charges, and for what the power costs the utility or the retailer above the wholesale price (its contracts and hedges, the grid's reserves, the energy lost on the wires, its margin): in Texas the retailer's energy charge alone is more than half the default bill. How much differs by state."

### 3. Ratios worded to read backwards (Medium)

- **Where.** `site/lib/problemsets/who-trades-with-whom.ts`: the worked example (tx), questions t2 and t5.
- **Why it matters.** Ruling 7a of 14 October 2026 has a ratio asked in the order a student reads, "ERCOT's peak was how many times CAISO's?", and the other four sets follow it (s6 "Tennessee's net imports were how many times Texas's?", i2, i7, b6). This set asks "how many times the Midwest's report was Tennessee's?" and "by Tennessee's own report, how many times its 2019 flow was its 2025 flow?", keyed to Tennessee over the Midwest and 2025 over 2019. Read as a statement, the student divides the other way: 0.60 and 0.60 for t5 (keyed 1.66 and 1.67), 0.96 for t2 (1.04); the worked example is 1.00 either way. Grammatically the form can be read as the key does (as "how many times the baseline was it?" can); a professor would still not assign a question whose two readings give 0.60 and 1.66.
- **The test.** `tests/test_audit_problems_3.py` on `wip/audit-problems-3`: the two readings differ, from the files (pass on main); the words (fail on main).
- **The fix on the branch, words only.** "Tennessee's report was how many times the Southeast's?", "... the Midwest's?", "its 2025 flow was how many times its 2019 flow?". The typed "the sum of the four" (t1, true today) reads "the sum of the neighbours' figures above". No figure moves (111 of 111 drawn equal). The dated editions of 20 and 21 November keep the old words: they are frozen.

### 4. What the student reads is not what the key divides (Low)

- **Where.** `site/lib/problemsets/under-the-ground-and-in-the-wind.ts`, the worked example (rx) and r1, which send the student to the map's legend; every set's page.
- **Why it matters.** The map's legend prints one decimal when its range is 5 or more (`site/lib/resources.ts`, `tickLabel`): the sun from 1.6 to 6.9, the wind's top 13.6. The key divides the list's values (1.584 and 6.912; 13.582): 4.36 and 0.62, where the legend gives 4.31 and 0.60. The answer prints 1.58 and 6.91, which divide to 4.37. More widely, 3 of the 40 derived figures of the five sets give another last digit from the printed inputs (rx 4.37 against 4.36, r3 0.54 / 0.31 = 1.74 against 1.75, i1 2,713.60 - 2,239.91 = 473.69 against 473.70), and no page says the key uses the unrounded figures.
- **The test.** `tests/test_audit_problems_4.py` on `wip/audit-problems-4`: the three readings of the sun and the two of the wind from the list (pass on main); the words (fail on main).
- **The fix on the branch, words only.** rx's first step adds "The answer divides the list's own values, which hold more decimals than the legend prints, so a ratio of the legend's rounded ends can differ in its last digit."; r1's "The legend prints it to one decimal; the answer subtracts the list's own value, ..."; every set's page "Each answer is computed from the unrounded figures and printed as a whole number or to two decimals, so a student who works from the printed figures, or from a legend that prints fewer decimals, can differ in the last digit."; the method note's paragraph "Rounding".

### 5. "Computed from the warehouse's tables when the page is built" (Low)

- **Where.** `site/app/learn/problems/[slug]/page.tsx`, the line under every set's title.
- **Why it is wrong.** The five sets of the whole country read committed page files (decision `page-file`: "The figures move when the data machine rebuilds a file, not each hour"); the line says the opposite on their pages. And the method note still says no dated edition holds them; the editions of 20 and 21 November 2026 do, and each set's page links the newest.
- **The fix on `wip/audit-problems-4`, words only.** A set with page files reads "Every answer is computed from committed page files built from the warehouse's tables, so the numbers move when the data machine rebuilds a file."; the five live sets keep their line. The method note says the editions hold the sets. `tests/test_session8901_problem_sets_country.py` still expects no edition to hold them and fails on origin/main (below); it is not changed here.

### 6. Two sentences the files contradict (Low)

- **Storm, question 3's "why".** "The extra demand of a storm hour falls to the plants that can be turned up, such as gas, coal and hydro." At Tennessee's highest hour of Elliott (2022-12-24 01:00 UTC) demand was 13,395 MW above the baseline hour; natural gas rose 5,374 MW, hydro 2,509, net imports 5,415 (40.4 percent), coal 116, and coal ran 2,061 MW under its own highest hour of the window. Fixed: "... falls to the plants that can be turned up and to the neighbours: in this hour natural gas and hydro rose most above the baseline and imports carried much of the rest (the question on the flows into Tennessee), while coal ran little above its baseline hour and far below its own highest hour of the window." (The page numbers the questions in the guide's order, so the flows are question 4 on the page; the sentence names the question by what it asks.)
- **Authority, question 7.** "How much did its demand grow from 2019 to 2025" comes right after "its highest demand"; the figure is the newest whole year's average demand against 2019's (`docs/methods/authority_facts.md`). Fixed: "its average demand", and the step names it.
- `tests/test_audit_problems_5.py` on `wip/audit-problems-5`: the hour's figures from the file (pass on main); the words (fail on main). No figure moves.

### 7. A winter bill at a summer month's price (Low; a figure)

- **Where.** `/learn/bill`'s California cards and bar, and question 3 of "Prices and your bill": the default season is winter (Samuel's ruling of 14 October 2026), the wholesale month the latest complete one, September 2026, the last month of PG&E's summer.
- **How much.** PG&E 26.91 USD of 229.63, 11.72 percent. At the mean of NP15's eight winter months held (October 2025 to May 2026, 30.91 USD/MWh; six of them miss an hour or more), 18.54 USD, 8.08 percent. September's price against PG&E's summer bill at the same defaults (262.33 USD): 10.26 percent. Oncor's tariff has no season; SCE and SDG&E are set against SP15 the same way.
- **The test.** `tests/test_audit_problems_6.py` on `wip/audit-problems-6` (passes on main). Not for landing.
- **For Samuel's ruling, default "left as it is":** value a seasonal bill at its own season's months (or name the season beside the month); PG&E's share 11.72 to 8.08 percent.

## The decisions blocks, line by line

The problem sets' 21 decisions (`site/app/learn/problems/Decisions.tsx`), the ones of the five sets read here and the bill's:

1. `page-file`: **right**; the set's page line said otherwise (**finding 5**).
2. `trade-month`: **right** (October 2026, the newest month ended at the `built` stamp 2026-11-21; years whole on both sides; 2019 the largest gap).
3. `storm-hour`: **right** (the first highest hour; Elliott's baseline the same weekday 364 and 728 days earlier, Uri's the same calendar days of 2019 and 2020, as printed).
4. `layer-by-id`: **right**; the legend's ends over every part, as the map draws them; what the student reads from it, **finding 4**.
5. `industry-pick`: **right** (July 2026 and July 2025; Chemicals and Petroleum and Coal Products, the order of the United States totals; 2024).
6. `authority-pick`: **right** (Browns Ferry, 2034 coal 1,900 MW, 2027 natural gas 1,830.6 MW, MISO by gross exchange; the three files' months equal).
7. `bill` (sets B): **right as stated**, but the question does not say it (**finding 1**); its "winter" against September's price, **finding 7**.

The bill's 14 decisions (`site/app/learn/bill/Decisions.tsx`): `kwh`, `peak-share`, `super-share`, `weekdays`, `season`, `baseline`, `income-tier`, `days`, `climate-credit`, `texas-energy` (0.0907113 as derived), `wholesale-zone`, `wholesale-month` and `wholesale-energy` restate as stated; `left-out` says taxes and local fees are not included, and the cards' share is of that bill (finding 1 puts it in the question). `season` with `wholesale-month`: **finding 7**.

## The branches

Each from `origin/main` (`f904d2427`), pushed. Tests run on each: its own test and every test file that reads a changed file (`tests/test_session44.py`, `149_checks`, `288`, `293`, `369`, `3650`, `408`, `4051`, `5171`, `55`, `7534_problem_sets`, `8901_problem_sets_country`, `9601_resource_set_legend`). Each words test fails on main and passes on its branch; each file test passes on both. Two tests fail on origin/main as on every branch, with the same lines (below).

| Branch | Head | Kind | Files changed | Test | Drawn and read |
|---|---|---|---|---|---|
| `wip/audit-problems-1` | `e81079e68` | words, for landing | `site/lib/problems.ts`, `replication/problem_sets/page_figures.json`, `docs/methods/problem_sets.md` | `tests/test_audit_problems_1.py` | pass (set B drawn from the kept reads: both questions, the answers 26.91 of 229.63 and 23.70 of 95.27 unchanged) |
| `wip/audit-problems-2` | `95eb87907` | words, for landing | `site/lib/problems.ts` | `tests/test_audit_problems_2.py` | pass (both "why it matters", the old sentence gone) |
| `wip/audit-problems-3` | `3e1d0a97b` | words, for landing | `site/lib/problemsets/who-trades-with-whom.ts` | `tests/test_audit_problems_3.py` | pass (the three questions and the step; 111 of 111 figures equal) |
| `wip/audit-problems-4` | `d2bbd7019` | words, for landing | `site/lib/problemsets/under-the-ground-and-in-the-wind.ts`, `site/app/learn/problems/[slug]/page.tsx`, `docs/methods/problem_sets.md` | `tests/test_audit_problems_4.py` | pass (the two steps; the line on a page-file set and on set B) |
| `wip/audit-problems-5` | `f13ad4022` | words, for landing | `site/lib/problemsets/storm-across-the-country.ts`, `your-own-balancing-authority.ts` | `tests/test_audit_problems_5.py` | pass (the "why" and the question and step) |
| `wip/audit-problems-6` | `9cb641f64` | figure, not for landing | test only | `tests/test_audit_problems_6.py` | not drawn (no words) |
| `wip/audit-problems-words` | `67e2ae39a` | the five words branches merged onto origin/main | all of the above | all five with the thirteen: 111 passed, the two failing as on origin/main | pass: the five sets of the whole country and set B drawn, every new sentence found, no old one left, 503 of 503 figures and both bill answers unchanged, no em dash |

The five words branches touch different lines and merge without a conflict.

## Data requests (rows for the data machine)

1. **The taxes and local fees on the two default bills.** On a PG&E bill in San Francisco (territory T) and an Oncor bill in Dallas, each tax and fee the utility or the city adds, with its rate and its source (for PG&E: the state's Energy Commission surcharge per kWh and San Francisco's utility users' tax; for Oncor: any city sales tax on residential electricity and the gross receipts and Public Utility Commission assessments, if the retailer itemizes them): to state each default bill and its wholesale share with them. Not read here (no web read); the page says taxes and local fees are not included.

## Problems found outside this audit

- **Two tests fail on origin/main** (`f904d2427`), on this machine, before any change: `tests/test_session7534_problem_sets.py::test_the_kept_figures_are_the_pages` (the replay builds set E's network questions on the committed `site/data/grid_network.json`, rebuilt since the kept reads: its hour is 2026-11-23 23:00 UTC against the kept 2026-11-15 04:00) and `tests/test_session8901_problem_sets_country.py::test_each_figure_is_pinned_to_its_file_and_drawn` (it expects no dated edition to hold the sets of the whole country; the editions of 20 and 21 November hold them, so the pages link one). Not changed here: a row for window A.

## What was checked and found right

- Every window and as-of date a question names, from the files' own stamps.
- Every sign: Tennessee's file above zero an import; the matrix's A report from A to B, B's turned; the storm pairs into Tennessee; the partner's net import.
- The gap over the hours both reported (t3: 744, 743, 743), the part-month (t7: Tennessee's own report with the Midwest, 407 of 744 hours, its other three ties 743), the one-sided border (t6: 0 hours from Mexico).
- The bills: PG&E's sixteen lines equal its total rates in each period (peak 0.39757, off-peak 0.36757, the baseline credit -0.0814 as the CIA's two rates' difference); the Base Services Charge's four parts sum to 0.79343; the Texas default energy charge as its arithmetic line says.
- Units on every figure; the TVA blank with its reason; MISO only as EIA's partner name.

## Not covered, or left open

- The five live sets (A to E) were not restated here: they read the live set, which this machine does not ask; the replication of 16 November (146 of 146) stands, and the bill questions B3 and B4 were restated from the table.
- The dated editions were not read; the editions of 20 and 21 November carry the old words of findings 3 and 6 (frozen by design).
- The calculator's other cases (summer, other usage) were not restated; the replication of 17 November did.
- No browser, no width of 390 px: the words branches were drawn with the site's own code and read.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-problems-1` (`e81079e68`), `-2` (`95eb87907`), `-3` (`3e1d0a97b`), `-4` (`d2bbd7019`), `-5` (`f13ad4022`), or all five merged as `wip/audit-problems-words` (`67e2ae39a`). Each drawn and read: pass.
- **For Samuel's ruling, default "left as it is":** finding 7 (`wip/audit-problems-6`): value a seasonal California bill at its own season's wholesale months; PG&E's share 11.72 to 8.08 percent (26.91 to 18.54 USD).
- **Data requests:** the one above.
