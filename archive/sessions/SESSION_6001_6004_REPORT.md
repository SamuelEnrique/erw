# Sessions 6001 to 6004 report: the states held at cost, the cross-checks (chain 270, samueloldlaptop)

14 November 2026, about 08:45 to 09:05 UTC. Branch `wip/6000-forecast`. Model spend under the owner's key: USD 0 (no model call by any tool). Six read-only subagents (sent by session 6000) returned their rows in their messages; one wrote a temporary text extract to the session's scratchpad (outside the repository), said so.

## What the readers found and what was encoded

| State | Before | Now | Source (spot-checked by this chain) |
|---|---|---|---|
| Washington gas | at cost | Trend I column 7.5, 21 years: 0.925 at age 1 to 0.153 at age 33, then 15 percent | DOR 2026 guidelines, index "Steam & Gas fired (fixed equipment) 7.5" (yes, the embedded workbook) |
| Washington geothermal | at cost | at cost (no class names it) | the same guidelines |
| California wind | at cost | AH 581 Table 4 (2026), 17-year column, 96 to 1 percent, last held | LTA 2017/020 (R2, 17 years; yes), AH 581 tables (yes) |
| California solar, gas, geothermal | at cost | at cost (no Board life assigned); a Board-assessed plant said | Rule 905, SAM 2016, AH 504 |
| South Carolina | at cost | at cost; 12-37-930's path and its unassigned class in the hover | 12-37-930 class 6(a) (yes), PT-300 Schedule E (yes) |
| West Virginia solar, gas, geothermal | at cost | at cost; 110CSR1M's unit value in the hover | Rule 110CSR1M (2026) |
| Kentucky wind | a note | 15 cents per 100, state only, at cost (manufacturing machinery) | Form 61A200(P) classification (yes, by word position), KRS 136.120 (yes) |
| Kentucky solar | at cost | at cost; the unit value's reason in the hover | KRS 136.160, 62A500 |
| New Mexico | at cost | Unregulated Electric tables: solar 20, wind 25, geothermal and combined cycle gas 28 years, 20 percent floor | TRD 2021 tables (yes, by word position), 3.6.5.36(B)(2) NMAC (yes), Pub 946 |
| Tennessee wind | at cost | one third of installed cost, every year | 67-5-601(e) as AG Op. 13-19 quotes it (yes), Op. 13-28 |
| Tennessee gas, geothermal | at cost | at cost (no Comptroller table; State Board capacity factor not found) | 2026 EL return, Op. 13-28 |
| Texas solar | at cost | Tax Code 23.26 (10 years at most, 20 percent floor) by Harris CAD's 2026 Solar/Ind 10-year schedule | 96-1569's quotation (yes), HCAD guide (yes, by word position) |
| Texas wind, gas, geothermal | at cost | at cost (F2/L2 industrial, no published schedule) | 96-313, 96-304, district plans |

- Spot-checks: 12 documents across 49 state rows (about one in four), every figure matching. Montana (session 6000) confirmed besides.
- Tests: `site/scripts/test-forecast.test.mjs` sessions 6000 to 6004, each state's hand-worked years from its document; node 50 of 50; the three Python test files naming the changed files 21 passed.

## The cross-checks (session 6004)

- Six studies added (`site/scripts/forecast-crosscheck.mjs`, `docs/reviews/forecast-crosscheck-2026-11-14.json`; the 13 November file kept): North Carolina wind (NREL, Southeast), Livingston County wind (Illinois, Midwest), Corona wind (New Mexico, Southwest), LSU's Louisiana combined cycle (Southeast), MSU's Michigan gas fleet (Midwest), NREL's JEDI geothermal example (Colorado, West). Four spot-checked.
- Ratios (model over published, construction jobs): NC 1.47, IL 0.58, NM on-site 0.62, LA 2.63, MI 0.18, geothermal 1.22. Each row's reason in the method note's new table.
- Still none readable: solar in the Plains and the Southwest; gas in the Northeast, the Plains and the Southwest; geothermal outside the West. The found and unusable studies are listed with reasons.

## Decisions made without you

- Washington's column 7.5 factors applied to constant dollars, as D applied column RG (they hold a price trend).
- California wind: Table 4's R3 17-year column stands in for the Board's R2 curve at 17 years (no R2 table is published); the last factor (1 percent) held after age 27; the hover says so.
- Tennessee wind's one third held in every year, as D held solar's 12.5 percent (ruling 19's default).
- New Mexico gas: the model's plant is EIA's combined cycle 2x2x1, IRS class 49.13 (28 years), so the Department's Table 28; the 2021 tables are the newest found (their formula, 100 - 80 x (age - 0.5) / life, checked against every printed value).
- Texas solar: Harris CAD's schedule as the statewide default (the only district schedule naming solar, inside 23.26's bounds); other districts may differ, said in the hover.
- Kentucky wind: added to the solar machinery rule on the Department's own classification.
- Livingston's cost taken as 2021 dollars (the report's year); the geothermal guide's example included and labelled as JEDI's own.
- Faults 13 and 21: left (ruling 12's default); D's other rulings' defaults already applied.

## For Samuel's ruling (default in brackets)

21. California solar, gas and geothermal: [held at cost] or AH 581 Table 4 at a life of 20, 25 or 30 years.
22. Washington geothermal: [held at cost] or the steam and gas fired column 7.5.
23. South Carolina: [held at cost] or 12-37-930's 11 percent a year (class 6(a)) to its 10 percent floor for property on Schedule E.
24. West Virginia solar, gas and geothermal: answered by session 6005 (the Tax Division's NAICS list assigns 2211 to table 9, 30 years: applied). Left: whether a merchant plant is assessed centrally [the county table].
25. Kentucky: [held at cost] or the 62A500 Class VI factors as a proxy for the unit value.
26. Texas wind, gas and geothermal: [held at cost] or Harris CAD's 20-year industrial column.
27. Texas solar: [Harris CAD's 10-year schedule] or a straight line over 10 years to 20 percent.
28. New Mexico solar: the federal investment tax credit the rule deducts from cost [not modeled, as every federal credit].
29. The JEDI geothermal example in the cross-check [kept, labelled as not independent] or left out.

## Next

- P1's close-out note (portable laptop) not on main at 09:03 UTC (chain 269 runs on `wip/5500-closeout`): the five tools' faults wait. The W46 Roundup does not exist yet.
- Row 12 moved to this head.

## Sessions 6005 and 6006 (about 09:05 to 09:20 UTC): three more readers, West Virginia, Killingly, the records

- Three read-only readers: West Texas wind districts, West Virginia's NAICS list and California's lives; gas studies for the Northeast, Plains and Southwest; solar studies for the Plains and Southwest.
- **West Virginia** (session 6005): the Tax Division's letter of 11 June 2026 to county assessors (as the Cabell County Assessor publishes it, with the NAICS list the Division's own copy omits; the host has no robots file, checked by this chain before its read) assigns 2211, electric power generation, to percent good table 9 (30 years). Read again by this chain by word position: 98, 97, 95 ... 21, 21, 20. Applied to solar, gas and geothermal; wind keeps its salvage valuation. The reader fetched that host before reading its robots file: said here, and this chain's own read came after the check.
- **Killingly Energy Center** (session 6006): PA Consulting's 2016 study for the Connecticut Siting Council (Docket 470), read again by this chain (the robots file disallows only an unrelated media path): construction jobs 1.05, output 0.98, operations jobs 0.97. The Northeast's gas row.
- **Not found**: Texas wind or gas district schedules (Mitchell CAD's report: a unit method by income, no schedule); a California life for solar or gas; solar studies in the Plains and the Southwest; gas studies in the Plains and the Southwest. Each listed in the method note with its reason.
- **Records**: the method note's section 4 table rows for the eight states changed (generated from the parameter files, `runs/s6000/table_rows.py`, in session 4296's form); section 9's region table; the review pack's cross-checks, its question 2 (Texas) and its question 12 (the states held at cost).
- Node 51 of 51; the three Python files 21 passed.

## Session 6007 (about 09:20 to 09:35 UTC): the last study gaps

- One more reader: gas in the Plains and the Southwest, geothermal with a cost. No gas study usable (Bison and Toronto applications, Evergy's plants: no multipliers or no readable study). Two county geothermal studies added, both read again by this chain (neither host has a robots file): Lyon County, Nevada (DRP 2019, 75 MW, USD 3,000 per kW: on-site construction 1.61, operations 2.30) and Black Rock, Imperial County, California (2024, 77 MW net, the middle of USD 557 to 882 million: the applicant's 471 construction job-years 2.28, operations 0.81).
- The cross-check now holds 22 studies; the region table in the method note's section 9.
- Queue file 271's unfinished steps written early (`d406eae0d`).
- A background watch for P1's close-out note runs (two-minute checks); step 5 starts when it lands.
- Node 51 of 51.
- 09:45 UTC: the background watch was stopped by Claude Code because the machine ran critically low on memory (MemFree 1.2 GB); not restarted, as the harness asks. P1's note exists on `wip/5500-closeout` (`fcadf7cf9`) but has not landed on main: step 5 not started.
