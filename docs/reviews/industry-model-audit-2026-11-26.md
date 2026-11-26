# Energy use by industry: the page audited as a hostile expert would

Session 10224, 26 November 2026, chain 710 (part D, in the form of part B), the old laptop. `/industry` ("Energy use by industry") read as three hostile readers would: an industrial energy buyer who wants to know what power costs a plant in a state; an economist of manufacturing energy use who knows the surveys' definitions; and a fund analyst who will quote one figure from the page. In the form of `docs/reviews/demand-model-audit-2026-11-26.md` and `docs/reviews/ai-energy-model-audit-2026-11-26.md`, whose findings are not repeated.

- Nothing changed on main but this file, its folder of evidence (`docs/reviews/industry-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-industry-<n>`. Words-only fixes (1 to 6, merged as `wip/audit-industry-words`) are for landing; branches 7 and 8 carry a test only and wait for the owner. Three data requests.
- **What kind of page this is.** It draws EIA's figures from one file and computes little: a year's twelve months summed, a share, three percent changes, two orders. So the arithmetic is small and right; the audit's weight is on what the page's words say the figures are.

## In short

- **The arithmetic is right.** An independent restatement from the page's own file (`site/data/industry.json`), written from the method note and the page's words, gives every figure the default view prints to the digit: 535 of 535 marked figures, the order of the 21 industries and of the 51 states, and the 8 labels and names the headlines and hovers carry. A second set of choices (the South, Paper against Primary Metals, 2019, electricity, Ohio against Pennsylvania, bulk chemicals) gives 586 of 586. The file's Monthly Energy Review months (5,144 values) and Form EIA-861M months (19,096 values) equal the main copy's two tables value for value.
- **The headline row sets two different things side by side without saying so (finding 1).** "Industrial sector" is the Monthly Energy Review's: manufacturing, agriculture, mining and construction, with feedstocks and the sector's share of electrical losses. "Largest manufacturing industry" is the 2022 survey's manufacturing fuel only. Manufacturing's 15,742 TBtu of fuel is 50.5 percent of the sector's 31,169 TBtu in 2022; Chemicals' 3,976 is 12.5 percent of the sector's 2025. Words, for landing.
- **"Net electricity" is not an industry's electricity use (finding 2).** It is electricity bought net of sales, plus the plants' renewables; restated from the survey's parts in 52 of 52 industries. What a plant makes from its own fuel (146,163,000 MWh of cogeneration) is counted as that fuel. Paper's net electricity is 51.6 percent of its net demand, Chemicals' 71.4. The states' "Electricity" is sales only; in the South plants make 22.1 percent of manufacturing's net demand. Words, for landing.
- **The states' "Average price" is not what a buyer pays for power, and not expenditures over the total beside it (finding 3).** It is EIA's all-fuel average over a smaller quantity: in 2024 expenditures over price are below the printed total in all 52 rows (21.8 to 93.5 percent of it). Texas: $9.11 printed, $6.34 on the total, $57.14 a MWh for electricity alone (from the same file, not on the page). Words, for landing.
- **Smaller, in words:** "not held, with EIA's reason on hover": the hover lists four codes and the file keeps none, and * (65 percent of coded cells) is an estimate under 0.5, not a withheld cell (finding 4). The decisions omit the outlook's opening industry and series and the opening region and year (finding 5). The MECS table note calls the sector's end use "total primary energy" (finding 6).
- **Two choices for Samuel, each a test on its branch, default "left as it is":** the only change figure is one month on a year before (July 2026: total -1.9 percent, petroleum -6.6) where twelve months on twelve say +0.4 and +0.8 (finding 7); no share is drawn in any census region, because one industry's total is withheld in each, though the survey prints each region's total (finding 8).
- **What an expert's own number would hold:** electricity's price by state in dollars a MWh (in the file, not shown: Louisiana $43.85, Texas $57.14, the nation $78.10, California $205.67); net demand rather than net electricity; energy including feedstocks by industry (data request 1); real dollars (no price index held, data request 3); the survey's sampling errors and earlier surveys (not held).
- **Right as stated:** the 2022 survey is labelled 2022 everywhere and never called current; nominal dollars are said in the decisions and every money hover; every table is EIA's and public in the license register; no held or operator row reaches a figure; the outlook's figures are named EIA's projections; "the twelve months summed" and the shares say what they are of.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/industry/page.tsx` | The page: the lead with two hints, the license line and the file's build date; three headlines (the sector's latest month, its latest whole year, the largest manufacturing industry); the monthly chart from a chosen year and the latest month beside the same month a year before; the 21 three-digit industries ranked by fuel in a census region with shares; two industries side by side (fuels, the components of electricity); the states ranked by a source in a year with price and expenditures; two states side by side (chart, table, sales chart); EIA's outlook (an industry, a series, two cases, every case in a table); the decisions, downloads and source line. `force-dynamic` for the forms |
| `site/app/industry/Decisions.tsx` | The eight decisions (`as-published`, `withheld`, `whole-year`, `first-two`, `ranking`, `cases`, `from-2015`, `nominal`), each with its default, source and session; the method note carries the same list (a test holds the two to one list) |
| `site/lib/industry.ts` | The file's shape (`readIndustry`), the labels of the fuels, regions and sources, and the page's few sums: `lastMonth`, `monthValue`, `yearSum` (twelve months or none), `lastWholeYear`, `rankedIndustries` (largest total first, a withheld total last), `industryChoices`, `shareOfSum` (none in a region with a withheld total), `rankedStates` (the nation left out), `statePoints`, `stateValue`, `statePrice`, `lastStateYear`, `changePct`, `salesYear`, the outlook's series and points, `tbtu` and `pct1` |
| `site/data/industry.json` | The page's file, built 2026-11-19 12:04 UTC: the Monthly Energy Review's eight industrial series 1973-01 to 2026-07; the 2022 survey's 81 industries in the nation and four regions (Tables 3.2, 11.1, 11.3); the State Energy Data System's 50 states, the District and the nation, 1990 to 2024; Form EIA-861M's sales to industry, 2001-01 to 2026-08, 62 areas; AEO2026's eleven industries in eleven cases, 2025 to 2050 |
| `warehouse/derived/industry_page.py` | Writes the file from six tables (`eia_sector_energy_consumption_monthly`, `eia_mecs_manufacturing`, `eia_seds_industrial_annual`, `eia_seds_state_energy`, `eia_retail_sales_monthly`, `eia_aeo_industrial`): no sum across sources, values rounded to 3 decimals (MWh to 1), the survey's note on its codes |
| `docs/methods/industry_page.md` ("the method note") | The file, the two new tables, what the file does not say, the build, the page, the replication and its two cross-checks, the decisions |
| `docs/methods/eia_mecs_manufacturing.md`, `eia_sector_energy_consumption_monthly.md`, `eia_seds_state_energy.md`, `eia_retail_sales_monthly.md` | The tables' notes: the survey's codes and counts (* 1,307, D 30, NA 324, Q 356), the parts of net demand, the cross-check of MECS against the Monthly Energy Review (finding 6) |
| `replication/industry/replicate.py` | Reads the page as served and computes every marked figure again from the file; 535 and 586 figures reproduced on 19 November. Not run here (it reads a served page) |
| `tests/test_session8012_industry.py`, `tests/test_session9871.py`, `tests/test_session8902_tour.py`, `site/scripts/test-reader-pages-render.mjs` | The page's tests: one file, in no menu, the decisions and the note one list, the sums under node, a withheld cell null; the page drawn and read for headings, tips and captions |

Of the six tables, this machine holds two (`eia_sector_energy_consumption_monthly`, `eia_retail_sales_monthly`, read only from the main copy); the survey, the State Energy Data System and the outlook are checked from the page file only.

## How every number here was computed

- **The page as a reader meets it:** `draw_industry.mjs` draws `app/industry/page.tsx` whole with the site's own loaders and the two stand-ins of `site/scripts/test-reader-pages-render.mjs` (no build, no server, every request refused), and writes the visible words, every marked figure (`data-fig`, `data-not-held`) and every hover.
- **The independent restatement:** `restate.py` (standard library), written from the method note's "The page" and the page's own words, not from `lib/industry.ts` or the replication: the newest month whose total is held, the same month a year before, the newest whole year, the 21 three-digit industries by their regional total, the shares of their sum, the newest SEDS year with the nation's total, the states by the chosen source, the two largest states, the changes since 2019, the twelve months of sales, the outlook's first year and every fifth; each written as the page's words say (TBtu whole from 100 and to one decimal below, percent to one decimal with its sign, dollars to the cent, billions and TWh to one decimal, MWh whole, half away from zero).
- **One rule at a time and each claim's size:** `measures.py` and `price_quantity.py` on the page file. The file against the held tables: `check_tables.py`, streamed.
- Copies of every script and its printout: `docs/reviews/industry-model-audit-2026-11-26/` (written to run from `runs/c10224/` of a worktree, the `.mjs` from `site/`).

## The arithmetic re-done

| Figure (the default view) | Drawn by the site's code | Restated | Gap |
|---|---|---|---|
| Industrial sector, latest month | 2,714 TBtu, July 2026 | TEICBUS of 2026-07 | 0 |
| Industrial sector, 2025 | 31,692 TBtu, "the twelve months summed" | 31,692.182 (and the held table's twelve months, the same) | 0 |
| Largest manufacturing industry, 2022 | 3,976 TBtu, Chemicals (NAICS 325) | the largest three-digit national total | 0 |
| The latest month beside a year before | 8 sources, 24 figures (e.g. total 2,714, 2,767, -1.9%; coal 62.7, 68.7, -8.7%) | the same | 0 (24 of 24) |
| Manufacturing industries ranked, United States | 21 rows: shares (25.3% to 0.0%), ten fuels each, 53 cells "not held" | the order by total, shares of the 21's sum (15,740 TBtu), the cells | 0 (231 of 231, order equal) |
| Two industries side by side | Chemicals against Petroleum and Coal Products: ten fuels, eight parts of electricity | the same | 0 (36 of 36) |
| States by industrial total consumption, 2024 | 51 rows: total, price, expenditures (Texas 8,113, $9.11, $51.5 bn) | the order by total; the same | 0 (153 of 153, order equal) |
| Two states side by side | Texas against Louisiana: seven sources, change since 2019 (+10.6%, -2.4%), price, expenditures, sales (176.1, 40.7 TWh) | the same | 0 (22 of 22) |
| EIA's outlook | Iron and steel, total energy use, 11 cases at 2025, 2030 to 2050 (66 figures) | the same | 0 (66 of 66) |
| Labels and hover names | "July 2026", "Industrial sector, 2025", "Chemicals (NAICS 325), United States", the two industries and states drawn first, "File built 2026-11-19", "outlook to 2050", the decision "Texas and Louisiana in 2024" | the same | 0 (8 of 8) |

- **535 of 535 marked figures equal** (`restate.out`), and 586 of 586 on the second set of choices (`restate_q2.out`; its one "MISSING" label is the restatement's own slip: the hover "The industries drawn first" names the default pair whatever is chosen, which is what it says).
- **The file against its tables:** the Monthly Energy Review's eight series, 5,144 values, and the sales to industry of 62 areas, 19,096 values, equal the main copy's tables (built 5 November and 12 November) value for value (`check_tables.out`). The sector's 2025 total moved from 31,691.322 TBtu (the table note's vintage of 27 September) to 31,692.182: EIA's revision, 0.003 percent.
- **The survey's own sums, restated from the file:** the 21 three-digit totals sum to 15,740 TBtu against all manufacturing's 15,742; the regions hold the survey's own all-manufacturing totals (Northeast 1,274, Midwest 4,213, South 8,306, West 1,948).

## One rule changed at a time

Each line changes one choice and keeps every other (`measures.out`).

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The largest industry by fuel consumption (Table 3.2) | by net demand for electricity (Table 11.1) | Chemicals stays first (210.1 TWh); Primary Metals second (104.4), Paper third (96.6); Petroleum and Coal Products falls from second to sixth (69.5) | the ranking's hover says fuel; the headline did not (finding 1) |
| the same | by electricity bought | Chemicals 164.1 TWh, Primary Metals 99.8, Food 79.6, Plastics 70.4, Nonmetallic Minerals 61.9, Paper sixth (54.4) | no |
| the same | fuel less "Other" (byproduct and other fuels) | Chemicals 3,278, Petroleum and Coal Products 1,420, Primary Metals 1,275; Paper falls from third to sixth (833) | no; the note's double counting is in the "not held" hover only |
| "Net electricity" (bought, net of sales) | net demand (all electricity used) | all manufacturing 783.7 TWh to 932.7 (+19.0 percent); Paper 49.8 to 96.6; Chemicals 150.1 to 210.1; Petroleum and Coal Products 46.9 to 69.5 | no (finding 2) |
| The states by EIA's total (with losses and feedstocks) | by end use (losses out), or the total less HGL | the top six do not move (Texas, Louisiana, California, Pennsylvania, Indiana, Ohio); Texas's HGL is 2,751 of its 8,113 TBtu (33.9 percent), its losses 759 | the ranking stands; what the total holds was not said (finding 1) |
| the same | by electricity sold | Texas 601.0 TBtu, Ohio 172.9, Pennsylvania 166.6, California 150.2, Illinois 145.7, Indiana 145.0; Louisiana is not in the six | the source is a choice on the page |
| The states' price: EIA's all-fuel average (TEICD) | expenditures over the total printed beside it | the nation $11.53 to $7.35; Texas $9.11 to $6.34; Louisiana $7.39 to $5.31; Hawaii $69.49 to $29.24 | no (finding 3) |
| the same | electricity alone, expenditures over sales at 3,412 Btu a kWh | Texas $57.14 a MWh, Louisiana $43.85, California $205.67, the nation $78.10 | no (finding 3; not shown) |
| The change: one month against the same month a year before | twelve months against the twelve before | total -1.9 to +0.4 percent; petroleum -6.6 to +0.8; natural gas +1.8 to +1.0; electricity sold -0.3 to +0.3; coal -8.7 to -6.0 | the caption says one month (finding 7, for ruling) |
| A share of the 21 industries' sum, none where one is withheld | a share of the survey's own regional total | the nation: Chemicals 25.26 percent either way; the four regions: no share drawn, against South Chemicals 32.8, West Petroleum and Coal Products 42.4, Midwest Chemicals 22.1, Northeast Paper 16.1 | the hover says none where a total is withheld (finding 8, for ruling) |
| A state's change since 2019 | since 2018, since 2021 | Texas +10.6 to +12.6 and +7.1; Louisiana -2.4 to -1.7 and -0.6 | the row names 2019 |

## Each claim against the code

| Claim, or question | Where | What the code and the file do | Verdict |
|---|---|---|---|
| Industry codes and their vintages | the ranked table ("NAICS 325" on hover), the choices | The survey's own codes (21 three-digit, 81 in all), as Table 3.2 prints them; no vintage of NAICS is named. The outlook's eleven industries are the AEO's own groupings (bulk chemicals, refining, metal-based durables), not NAICS, and the page never joins them to the survey's | Right as stated; the NAICS year the 2022 survey uses was not verified here (no web read) |
| Energy against electricity | the headlines, "Net electricity", the Electricity table | Electricity counts at 3,412 Btu a kWh in the survey's fuel and in the states' table, with no losses; the sector's total adds the losses (the chart's hint says so) | **Finding 1** (the headline row), **finding 2** |
| Purchased against self-generated | "Net electricity"; the states' "Electricity"; "Electricity sold to industry" | Net electricity = purchases + transfers in + renewable generation - sales offsite (52 of 52 within 1 TBtu); the states' electricity equals Form EIA-861M's sales at 3,412 Btu a kWh (the note's cross-check); neither holds what plants make from their own fuel | **Finding 2** |
| Prices paid by class against tariffs | "Average price (USD per MMBtu)" | EIA's all-fuel industrial average, per a smaller quantity than the total beside it | **Finding 3** |
| Survey years presented as current | the headline "2022", the section "ranked, 2022", every survey hover ("Figures are for 2022") | The survey is every four years; the next is fielded in 2027 (the table's note). The page never calls 2022 current; the code's comment "kept current" is about the monthly series | **Right** |
| Nominal against real dollars | the decision `nominal`, the price and expenditure hovers | Nominal, said in four places; nothing is set against an earlier year's dollars on the page; the year chooser offers 1990 prices in 1990 dollars, as said | **Right**; real dollars would need a price index (data request 3) |
| Shares of what total | "Share" | Of the 21 three-digit industries' sum in the region (said on hover); in the nation it equals the survey's all-manufacturing total within 2 TBtu | **Right**; in the regions none is drawn (**finding 8**, for ruling) |
| Held or internal rows reaching a figure | the license line | Six EIA tables, each public in `warehouse/metadata/license_tables.csv` through the source registry; no operator's held table | **Right** |
| The as-of date | the license line, the headlines, the table heads | "File built 2026-11-19"; the newest month (July 2026), the SEDS year (2024) and AEO2026 are in words; Form EIA-861M's newest month (August 2026) is only on the chart's axis | **Right**, the last a small gap (not a finding) |
| "Nothing is filled, scaled or estimated" | the decision `as-published` | No value filled; the units changed are stated (million kWh as MWh, MWh as TWh); the outlook's values are EIA's | **Right** |
| "A cell EIA withholds or does not estimate ... with EIA's reason on hover" | the decision `withheld`, the hover | The file keeps no code; * is EIA's estimate under 0.5 | **Finding 4** |
| "Each choice that moves what the page shows" | the decisions fold | The outlook opens on Iron and steel, total energy use; the industries on the United States; the states on the total in 2024: none of the three named | **Finding 5** |
| "EIA's own projections, not the ERW's" | the outlook's hover | The file marks no history year; the first year (2025) differs between cases (1,110 to 1,116 TBtu for iron and steel), so it is model output | **Right** |
| "AEO2026 names no Reference case" | the hint and `cases` | The file's eleven cases hold none named Reference | **Right** by the file |
| The twelve months summed | "Industrial sector, 2025" | The sum of the file's twelve months, written only when all twelve are held | **Right** |
| The sector's total is end use plus losses | the chart's hint | TEICBUS = TNICBUS + LOICBUS within 0.02 TBtu in 2022 and 2025 | **Right** |

## What an industrial buyer, an economist or a fund analyst would hold that this does not

| Item | Size | From |
|---|---|---|
| Electricity's price by state, a buyer's first number | 2024: Louisiana $43.85 a MWh, New Mexico $53.18, Oklahoma $54.13, Texas $57.14, Montana $58.98 the cheapest; Hawaii $336.07, California $205.67, Rhode Island $197.04 the dearest; the nation $78.10. In the page file (expenditures over sales), not drawn | `measures.py` |
| An industry's electricity use, not its net purchase | net demand: all manufacturing 932.7 TWh (16.2 percent made onsite); by region onsite generation is 22.1 percent in the South, 18.3 in the Northeast, 15.0 in the West, 6.3 in the Midwest | the file's Table 11.1 |
| Energy including feedstocks, by industry | not held: Table 1.2 (first use) was read for a check in session 2016 (all manufacturing 20,843 TBtu against 15,742 of fuel), not stored. Whether Chemicals or Petroleum and Coal Products is the larger user with feedstocks counted is data request 1 | `docs/methods/eia_mecs_manufacturing.md` |
| Real dollars | no price index is held on this machine (data request 3) | `warehouse/output` |
| Energy per dollar of output | not held: the AEO's shipments and intensity series are not taken (the method note), nor the survey's Table 6 | the method note |
| The survey's sampling error | not held (the table note: no relative standard errors); Q marks 356 cells whose error is above 50 percent | the table note |
| Change between surveys | not held (2022 only; 2018 not taken) | the table note |
| A trend, not one month | twelve months to July 2026 on the twelve before: +0.4 percent against the page's -1.9 for one month | `measures.py` (finding 7) |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Moderate | The headline row and the lead set the industrial sector (with agriculture, mining, construction, feedstocks and losses) beside the survey's manufacturing fuel, unsaid | 15,742 TBtu is 50.5 percent of the sector's 31,169 in 2022; a reader sums or compares two measures | words | `wip/audit-industry-1` (`85cfc94bb`) |
| 2 | Moderate | "Net electricity" and the states' "Electricity" are electricity bought, not used; the page never says so | Paper 51.6 percent of its net demand, Chemicals 71.4; the South makes 22.1 percent onsite | words | `wip/audit-industry-2` (`a0543e11a`) |
| 3 | Moderate | "Average price (USD per MMBtu)" is all fuels, per a smaller quantity than the total beside it; not a tariff | Texas $9.11 against $6.34 on the total and $57.14 a MWh for electricity | words | `wip/audit-industry-3` (`e92ae5c22`) |
| 4 | Low | "Not held ... with EIA's reason on hover": four codes, none kept; * is an estimate under 0.5 | 53 cells on the default view; * is 1,307 of 2,017 coded cells | words | `wip/audit-industry-4` (`7ee01bb01`) |
| 5 | Low | The decisions omit the outlook's opening industry and series, the opening region and the states' year and source | the fold's "each choice" is three short | words | `wip/audit-industry-5` (`ffa5ad277`) |
| 6 | Low | The MECS table note calls the sector's end use "total primary energy" | 26,076 is end use; the total is 31,169 | words (the note) | `wip/audit-industry-6` (`db39f9bae`) |
| 7 | Low | The only change figure is one month on a year before | total -1.9 against +0.4 on twelve months; petroleum -6.6 against +0.8 | for ruling | `wip/audit-industry-7` (`407dd8fb6`, test only) |
| 8 | Low | No share in any census region, one total being withheld in each | the South's Chemicals 32.8 percent of the survey's regional total, not drawn | for ruling | `wip/audit-industry-8` (`be0c93e05`, test only) |

The words branches 1 to 6 are merged as `wip/audit-industry-words` (`081214ad1`); 2 and 4 met in one place of the method note (the bullets of the ranked and the paired industries), resolved by keeping both changes.

### 1. The sector and the survey count different things (Moderate)

- **Where.** `site/app/industry/page.tsx`, the lead and the third headline ("Largest manufacturing industry, 2022", note "Chemicals (NAICS 325), United States").
- **Why it is wrong.** The first two headlines and the states' tables are the industrial sector of the Monthly Energy Review and the State Energy Data System: manufacturing, agriculture, mining and construction, counting energy used as a raw material and the sector's share of electrical system losses. The third headline and the industries' tables are the 2022 survey's Table 3.2: manufacturing alone, only the energy used as fuel, electricity at 3,412 Btu a kWh with no losses. The method note says the surveys measure different things; the page, where a reader sets 3,976 beside 31,692, does not. The page's title and lead say "energy use".
- **How much.** 2022: the sector 31,168.8 TBtu, its end use 26,075.8; the survey's manufacturing fuel 15,742 (50.5 and 60.4 percent). Chemicals' 3,976 is 12.5 percent of the sector's 2025. Texas's HGL, chiefly counted as feedstock in the sector, is 33.9 percent of its total. The order of the top six states does not move on end use or the total less HGL.
- **The test.** `tests/test_audit_industry_1.py`: manufacturing's fuel is between 45 and 55 percent of the sector's 2022 total; the sector's total is end use plus losses (passes on main); the words (fail on main).
- **The fix on the branch, words only.** A hint in the lead: "The industrial sector and the survey count different things", its hover: "The industrial sector of the Monthly Energy Review and the State Energy Data System is manufacturing, agriculture, mining and construction together, and its total counts energy used as a raw material (feedstocks) and the sector's share of the energy lost making and moving electricity. The 2022 survey counts manufacturing alone, and only the energy it uses as fuel, with its electricity at 3,412 Btu a kWh and no losses. An industry's figure is not a part of the sector's total." The headline: "Largest manufacturing industry by fuel, 2022", note "... United States: fuel consumption, feedstocks not counted". The note's "What the file does not say" gains the figures. No figure moves.

### 2. Electricity bought, not used (Moderate)

- **Where.** The ranked table's and the paired table's "Net electricity" (hover: "Net electricity, TBtu"); the states' source "Electricity" and every State Energy Data System hover; "Electricity sold to industry" and its chart.
- **Why it is wrong.** The survey's Table 3.2 "Net electricity" equals electricity bought and transferred in, plus generation from renewables other than wood and biomass, less sales and transfers offsite (restated from the file's Table 11.1 parts within 1 TBtu in all 52 industries with every part held). Electricity a plant makes from its own fuel is counted as that fuel; the industry's use is its net demand, which the page draws further down without a word joining the two. The states' "Electricity" equals Form EIA-861M's sales at 3,412 Btu a kWh (the note's own cross-check): no self-generation. An economist of manufacturing reads "Net electricity" as use; a buyer sizing a plant's load is short by the cogeneration.
- **How much.** All manufacturing 783.7 TWh of net electricity against 932.7 TWh of net demand; Paper 49.8 against 96.6 (51.6 percent), Petroleum and Coal Products 46.9 against 69.5 (67.4), Chemicals 150.1 against 210.1 (71.4). Onsite generation is 22.1 percent of net demand in the South.
- **The test.** `tests/test_audit_industry_2.py`: the restatement for 325, 324, 322, 311 and all manufacturing, Paper under 55 percent, the South over 20 percent (passes on main); the words (fail on main).
- **The fix on the branch, words only.** The "Net electricity" hover (ranked and paired tables): "Net electricity is the electricity bought and transferred in, plus what the plants made from renewables other than wood and other biomass, less what they sold or transferred offsite, at 3,412 Btu a kWh. Electricity a plant makes from its own fuel is not in it: that fuel is counted in its own column. An industry's electricity use is its net demand, in the Electricity table under Two industries side by side." The State Energy Data System's hovers add "Electricity is the electricity sold to industrial customers; electricity a plant makes for itself is not in it, and the fuel burned to make it is counted with the other fuels." Form EIA-861M's add "Sales only: electricity a plant makes for itself is not in it." The note's bullet says the same with the figures. No figure moves.

### 3. The average price (Moderate)

- **Where.** The states' table, "Average price (USD per MMBtu)" (hover "The industrial sector's total average price, nominal dollars"), and the paired states' row (hover: the source only).
- **Why it is wrong.** An industrial buyer reads a state's price as what a plant pays. This is EIA's average over all the sector's fuels, feedstocks among them, set beside a total it is not divided by: the expenditures over the price is a smaller quantity than the total in every row, so the expenditures are not the total times the price, and the figure is no fuel's price and no tariff.
- **How much.** 2024: expenditures over price is 21.8 to 93.5 percent of the printed total (the nation 63.8), below the total in 52 of 52 rows and below 99 percent of the end use in 48 (DC, Maryland, Rhode Island and Vermont at 99 to 100). Texas: $51.5 bn over $9.11 is 5,650 TBtu against a total of 8,113 ($6.34 on the total); its electricity alone $57.14 a MWh. Which energy EIA leaves out of the quantity is EIA's rule, not read here (no web read).
- **The test.** `tests/test_audit_industry_3.py`: the quantity below the total in all 52 rows and below 99 percent of end use in 48; Texas's three figures (passes on main); the words (fail on main).
- **The fix on the branch, words only.** One hover for the three price cells: "EIA's average price of the industrial sector's energy, all fuels together, nominal dollars: not a tariff, and not the price of electricity or of any one fuel. It is per million Btu of a smaller quantity than the total beside it (the electrical system losses are not in it, and in most states part of the rest is not either), so the expenditures are not the total times this price." The note gains a paragraph with the figures. No figure moves.

### 4. "Not held" and EIA's codes (Low)

- **Where.** The hover of every "not held" cell of the survey's tables (`WITHHELD`); the decision `withheld`; the note; the file's own note (`warehouse/derived/industry_page.py`).
- **Why it is wrong.** The page said "EIA withholds or does not estimate this cell" and the decision "with EIA's reason on hover". The file keeps no code (the table drops the cell), so the hover can only list the four; and * is EIA's estimate under 0.5 in the table's unit, neither withheld nor unestimated. By the table note's counts * is 1,307 of 2,017 coded cells (65 percent): most "not held" cells are under half a unit.
- **The test.** `tests/test_audit_industry_4.py`: the counts of the note, no code in the file (passes on main); the words (fail on main).
- **The fix on the branch, words only.** The hover: "EIA prints no figure for this cell. It marks such a cell * (an estimate under 0.5 in the table's unit), D (withheld to avoid disclosure), NA (not available) or Q (withheld, its relative standard error above 50 percent); the file does not keep which, so the cell has no figure here. Fuel consumption counts some byproduct fuels twice, as EIA's note to Table 3.2 says." The decision and the note say the hover gives all four; the file's note at its next build: "EIA prints no figure for some cells (codes * for an estimate under 0.5, D, NA, Q)". The page tests the hover by equality, not by its first words. No figure moves; a cell is still never drawn as zero.

### 5. The decisions name every opening choice (Low)

- **Where.** `site/app/industry/Decisions.tsx`, `cases` and `ranking`; the note's table.
- **Why it matters.** The fold says it holds "each choice that moves what the page shows". The outlook opens on Iron and steel's total energy use, the industries on the United States, the states on the total in 2024; the fold named none of the three (the cases and the first two states it names).
- **The test.** `tests/test_audit_industry_5.py`: the page's defaults (passes on main); the words (fail on main).
- **The fix on the branch, words only.** `cases`: "EIA's outlook opens on Iron and steel, its total energy use, and on two of its eleven cases ..."; `ranking`: "(the United States until another is chosen)", "(the total in the newest year until others are chosen)". The count of decisions stays eight.

### 6. The MECS note names end use as total (Low)

- **Where.** `docs/methods/eia_mecs_manufacturing.md`, the cross-check of session 2016.
- **Why it is wrong.** "first use 20,843 TBtu ... against total primary energy 26,076, 79.9 percent; fuel consumption 15,742, 60.4 percent": 26,076 is the sector's end use (TNICBUS, 2022, 26,075.8), the total with losses being 31,168.8.
- **The test.** `tests/test_audit_industry_6.py`: the 2022 sums (end use 26,076, total 31,169, natural gas 10,781, coal 987, electricity 3,482; passes on main); the note's words (fail on main).
- **The fix on the branch, words only (the note).** "against the sector's end-use energy 26,076 (TNICBUS, without electrical system losses; session 10224 corrected "total primary energy": the sector's total with its losses, TEICBUS, is 31,169), 79.9 percent; fuel consumption 15,742, 60.4 percent of end use and 50.5 percent of the total".

### 7. One month against twelve (Low, for ruling)

- **Where.** "The latest month beside the same month a year before" and its "Change" column, the page's only change figure for the sector.
- **Why it matters.** A fund analyst quotes "industrial energy use down 1.9 percent". One month of the Monthly Energy Review on the same month a year before carries the month's weather, its working days and EIA's newest estimates; the twelve months to July 2026 against the twelve before say +0.4 percent. The caption says one month, so nothing is false.
- **The test.** `tests/test_audit_industry_7.py` on `wip/audit-industry-7` (test only, passes on main; skips its exact figures once the file ends later than July 2026).
- **For Samuel's ruling.** Default "left as it is". The other choice: add twelve months on the twelve before beside the one month. Measured: total -1.9 and +0.4 percent; petroleum -6.6 and +0.8; natural gas +1.8 and +1.0; electricity sold -0.3 and +0.3; coal -8.7 and -6.0.

### 8. No share in the regions (Low, for ruling)

- **Where.** The ranked table's "Share" (`shareOfSum` returns none for every industry when one three-digit total is withheld in the region).
- **Why it matters.** A total is withheld in each census region (Northeast 314 and 316; Midwest 315; South 312, 316, 332 and 337; West 315 and 316), so a reader who chooses a region sees "not held" in every share. The survey prints each region's all-manufacturing total, which the file holds; on it the shares could be drawn, with the withheld industries' part (at most 422 TBtu in the South, 3 or fewer elsewhere) unassigned.
- **The test.** `tests/test_audit_industry_8.py` on `wip/audit-industry-8` (test only, passes on main).
- **For Samuel's ruling.** Default "left as it is". The other choice: in a region, the share of the survey's own regional total. Measured: 0 shares drawn in each region today; the South's Chemicals 32.8 percent, the West's Petroleum and Coal Products 42.4, the Midwest's Chemicals 22.1, the Northeast's Paper 16.1. In the nation nothing moves (25.26 percent either way).

## The words branches drawn and read

Each branch's page was drawn to HTML with the site's own code (`draw_industry.mjs`: `app/industry/page.tsx` whole, the decisions with it) and its new sentences read in the drawn words or hovers (`draw_b<n>.out`); the restatement run on each drawing gives 535 of 535 equal (`restate_b<n>.out`). No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-industry-1` | the lead's hint and its hover; the third headline | pass: "Largest manufacturing industry by fuel, 2022 3,976 TBtu Chemicals (NAICS 325), United States: fuel consumption, feedstocks not counted"; the hover ends "An industry's figure is not a part of the sector's total." |
| `wip/audit-industry-2` | the Net electricity hovers; the State Energy Data System and Form EIA-861M hovers | pass: the three sentences read in the hovers |
| `wip/audit-industry-3` | the 53 price hovers | pass: "... all fuels together, nominal dollars: not a tariff ..."; "... so the expenditures are not the total times this price." |
| `wip/audit-industry-4` | every not-held hover; the decisions fold | pass: "EIA prints no figure for this cell. It marks such a cell * (an estimate under 0.5 in the table's unit) ..." |
| `wip/audit-industry-5` | the decisions fold and its tips | pass: "EIA's outlook opens on Iron and steel, its total energy use, ..."; "Default: Iron and steel, total energy use; Case A ..." |
| `wip/audit-industry-6` | the table note (not drawn: a note) | read in the file |
| `wip/audit-industry-words` | every place above | pass: all ten sentences drawn (`draw_bw.out`), 535 of 535 figures equal (`restate_bw.out`), the site's `test-reader-pages-render.mjs` 74 of 74 (`/industry`: one h1, no level skipped, every tip its target, 7 tables captioned) |

- Tests: each branch's own test with `test_session8012_industry`, `test_session9871` and `test_session8902_tour` (the test files that read the page, its decisions or its note): 19, 19, 19, 19, 18 and 2 passed; on the merge 40 passed (`tw.out`). On origin/main the eleven words tests fail and the nineteen behaviour tests pass, those of branches 7 and 8 among them (`on_main.out`). No test reads `warehouse/derived/industry_page.py` or `docs/methods/eia_mecs_manufacturing.md` but the audit's own.

## The decisions block, line by line

1. `as-published`, EIA's figures, the page sums only twelve months and computes the shares and changes it names: **right**.
2. `withheld`: never zero, **right**; "EIA's reason on hover" and "does not estimate" (**finding 4**).
3. `whole-year`, twelve months or no figure: **right** (`yearSum`, `salesYear`).
4. `first-two`, Chemicals and Petroleum and Coal Products, Texas and Louisiana in 2024: **right** by the file.
5. `ranking`: **right**; the opening region and year unsaid (**finding 5**).
6. `cases`: **right**; the opening industry and series unsaid (**finding 5**).
7. `from-2015`: **right**.
8. `nominal`: **right**.

## Not covered, or left open

- **Four of the six tables are not on this machine.** The survey, the State Energy Data System and the outlook were checked from the page file only; the replication of 19 November set the file beside the page and its cross-checks set the Monthly Energy Review beside the State Energy Data System (0.12 percent apart in 2024).
- **EIA's definitions not read here.** The quantity behind the State Energy Data System's average price, the NAICS year of the 2022 survey, whether the newest months of Table 2.4 are estimates: each needs EIA's documentation (no web read). The page's new words claim only what the file shows.
- **The State Energy Data System's parts do not sum to its total** (the nation's six parts drawn exceed the total by 96 TBtu in 2024, Texas's by 6.9): the page never sums them; not a finding.
- **The Ask panel** was not run (it calls a model). The page in a browser: drawn to HTML; the browser read of 20 November covers widths and the keyboard.
- **An inline script ran inside a repository test.** `tests/test_session8012_industry.py` runs node with code on its command line (its own design since session 8012); it was run as one of the page's tests, unchanged.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-industry-words` (`081214ad1`), the merge of `wip/audit-industry-1` (`85cfc94bb`), `-2` (`a0543e11a`), `-3` (`e92ae5c22`), `-4` (`7ee01bb01`), `-5` (`ffa5ad277`) and `-6` (`db39f9bae`). Files: `site/app/industry/page.tsx`, `site/app/industry/Decisions.tsx`, `docs/methods/industry_page.md`, `docs/methods/eia_mecs_manufacturing.md`, `warehouse/derived/industry_page.py` (the file's note, at the data machine's next build), six test files. Drawn and read: pass. The page's 535 figures do not move.
- **For Samuel's ruling, default "left as it is":**
  - Finding 7, `wip/audit-industry-7` (`407dd8fb6`), not for landing: add twelve months on the twelve before beside the one-month change; total -1.9 and +0.4 percent, petroleum -6.6 and +0.8.
  - Finding 8, `wip/audit-industry-8` (`be0c93e05`), not for landing: in a census region, draw each share on the survey's own regional total; today no share in any region, then e.g. the South's Chemicals 32.8 percent.
- **Data requests (the data machine, files only):**
  1. The 2022 survey's Table 1.2 (first use of energy for all purposes, fuel and nonfuel), if session 2016's saved copy is under `warehouse/raw/` (it was read for the check, not stored as a table): each three-digit industry's first use and nonfuel use in the nation and each region. To say whether Chemicals or Petroleum and Coal Products is the larger user with feedstocks counted, and how much of each industry the page's fuel figure leaves out (finding 1).
  2. From the State Energy Data System's saved documentation or its series list, if held: what the industrial total average price (TEICD) is divided by, to name in the hover what is left out of its quantity (finding 3; the page now says only "a smaller quantity", which the file shows).
  3. Whether any table on the data machine holds a price index (the GDP implicit price deflator or the consumer price index), to restate the states' prices and expenditures in one year's dollars; none is in this machine's `warehouse/output`.
- **Needs the key:** nothing.
