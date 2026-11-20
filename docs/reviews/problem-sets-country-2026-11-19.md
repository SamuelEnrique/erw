# Problem sets of the whole country (chain 507, part C, session 8901), 19 November 2026

Branch `wip/8901-problem-sets`, from origin/main at `24110a0d1`. Four new problem sets after the five, every figure a
`pf|` key into a committed page file (`site/lib/pagefile.ts`), recomputed by `site/scripts/check-values.mjs`. Nothing was
built, deployed or published; no model and no website was asked anything. Method: `docs/methods/problem_sets.md`, section
"The whole country (chain 507, session 8901)".

## The four sets

The answers below are as the page files give them today (the page rounds as shown; each figure carries its key).

### Who trades with whom: `https://erw-flame.vercel.app/learn/problems/who-trades-with-whom`

Files: `site/data/regions/trade/ten.json`, `site/data/regions/trade_matrix.json`. Order on the page: t1, t6, t2, t7, t5, t3, t4.

| Id | Question, in one line | Answer as the file gives it |
|---|---|---|
| tx (example) | October 2026: Tennessee's and the Southeast's reports of their flow, and their ratio | -81,343 and -81,468 MWh; 1.00 times; same sign, Tennessee sent power to the Southeast |
| t1 | October 2026: Tennessee's net imports in all and from each neighbour; the largest | in all 574,900 MWh; Carolinas -94,603, Mid-Atlantic -899,413, Midwest 1,650,259, Southeast -81,343 MWh; the most from the Midwest |
| t2 | October 2026: Tennessee's and the Midwest's reports of one flow, and their ratio | 1,650,259 and 1,583,612 MWh; 1.04 times; the file's gap 66,647 MWh |
| t3 | October 2026: the Mid-Atlantic flow, the difference of the reports against the file's gap | -899,413 and -675,342 MWh; difference -224,071, gap -222,699 MWh (744, 743 and 743 hours) |
| t4 | The Mid-Atlantic and Tennessee in 2019, the year their reports differ most: which way each said the power ran | Mid-Atlantic 2,437,201 MWh to Tennessee; Tennessee -6,612,970 MWh (it sent power to the Mid-Atlantic); apart 9,050,171, file's gap 9,034,597 MWh |
| t5 | Midwest to Tennessee, 2025 over 2019, by each side's report | 1.66 times by Tennessee's, 1.67 times by the Midwest's |
| t6 | California to Mexico, 2025: California's report and the hours of each side | 971,140 MWh over 8,712 hours; Mexico's side 0 hours, so no gap |
| t7 | The ended month with the smallest share of hours Tennessee reported for the Midwest | July 2018: 407 of 744 hours, 54.70 percent; that month's import 410,651 MWh |

### A storm across the country: `https://erw-flame.vercel.app/learn/problems/storm-across-the-country`

Files: `site/data/regions/events/elliott_2022.json`, `site/data/regions/events/uri_2021.json`. Order: s1, s2, s3, s5, s4, s6, s7.

| Id | Question, in one line | Answer as the file gives it |
|---|---|---|
| sx (example) | Elliott: the Carolinas' highest hour against the baseline | 2022-12-24 11:00 UTC: 44,630 against 26,915 MW, 1.66 times |
| s1 | Elliott: Tennessee's highest hour against the baseline | 2022-12-24 01:00 UTC: 33,225 against 19,830 MW, 1.68 times |
| s2 | Uri: Texas's highest hour, MW above the baseline | 2021-02-15 01:00 UTC: 69,215 against 40,461 MW, 28,754 MW above |
| s3 | What ran in Tennessee at that hour; the gas share; gas against the baseline | gas 10,727, coal 2,423, nuclear 8,593, hydro 5,497 MW; gas 39.23 percent of 27,342 MW; 2.00 times the baseline's 5,353 MW |
| s4 | Texas at its Uri peak: wind and gas against the baseline | wind 8,087 against 10,408 MW (-2,321 MW); gas 43,798 against 16,616 MW (2.64 times) |
| s5 | Tennessee's net imports at its peak and the flow from each neighbour | 5,807 against 392 MW; Carolinas 57, Mid-Atlantic 2,561, Midwest 4,827, Southeast -52 MW; the most from the Midwest |
| s6 | Texas's imports at its Uri peak against Tennessee's at its Elliott peak | 1,194 MW against 5,807 MW; Tennessee's 4.86 times Texas's |
| s7 | Central to Texas at the Texas peak: the two sides' reports | Central 820 MW, Texas 812 MW, apart by 8 MW |

### What is under the ground and in the wind: `https://erw-flame.vercel.app/learn/problems/under-the-ground-and-in-the-wind`

File: `site/data/resources/manifest.json` (it names no warehouse table). Order: r2, r1, r3, r6, r4, r5.

| Id | Question, in one line | Answer as the file gives it |
|---|---|---|
| rx (example) | Global horizontal irradiance: the legend's lowest and highest, and their ratio | 2.81 and 6.50 kWh/m2/day; 2.32 times |
| r1 | Wind speed at 100 m: the legend's top against the source's own highest cell | 13.58 against 14.20 m/s; 0.62 m/s lower (a map cell is a mean) |
| r2 | The tops of the global horizontal and direct normal legends | 6.50 and 9 kWh/m2/day; 1.38 times |
| r3 | Wind capacity factor: the mean and the highest | 0.31 and 0.54 (ratios); 1.75 times |
| r4 | Hydrothermal sites: the count, the sum of estimated MWe, the largest and its share | 253 sites; 9,060.80 MWe; 2,209.90 MWe, 24.39 percent |
| r5 | Non-powered dams: capacity, yearly energy, and hours of full output | 3,939.27 MW; 15,244,926.85 MWh a year; 3,869.99 hours |
| r6 | Biomass: the national total, crop residue and its share | 315,802,780.06 and 173,997,321.42 dry metric tons a year; 55.10 percent |

### Where energy goes: `https://erw-flame.vercel.app/learn/problems/where-energy-goes`

File: `site/data/industry.json`. Order: i1, i2, i3, i6, i4, i7, i5.

| Id | Question, in one line | Answer as the file gives it |
|---|---|---|
| ix (example) | Chemicals, 2022: total fuel, natural gas and its share | 3,976 and 2,585 TBtu; 65.02 percent |
| i1 | July 2026: the industrial total, end use, their difference, against the losses | 2,713.60 and 2,239.91 TBtu; 473.70 TBtu, the losses 473.70 TBtu |
| i2 | July 2026 against July 2025 | 2,713.60 and 2,766.80 TBtu; 0.98 times |
| i3 | The two largest industries of 2022 and their ratio | Chemicals 3,976, Petroleum and Coal Products 3,543 TBtu; 1.12 times |
| i4 | Petroleum and Coal Products: "other" fuels and their share | 2,123 of 3,543 TBtu; 59.92 percent |
| i5 | Chemicals: on-site generation as a share of net electricity demand | 60,426,000 of 210,095,000 MWh; 28.76 percent |
| i6 | Chemicals: the South's share of the United States' fuel | 2,725 of 3,976 TBtu; 68.54 percent |
| i7 | 2024: Texas's industrial energy against Louisiana's | 8,113.46 and 2,997.21 TBtu; 2.71 times |

The fifth set, a reader's own balancing authority, was not written: its files (`site/data/regions/authority/`) are not on
main. No set was found unusable.

## What changed beside the four modules

- `site/lib/pagefile.ts` (new): the `pf|` key and its pure resolver; `site/scripts/check-values.mjs`: a `pf|` case beside
  `calc|`, and the four addresses in its list of pages (no floor yet).
- `site/lib/problemkit.ts`: `addGuide`, `notePageFile`, `pageFilesOf`; `keyWords`, `tableOfKey` and `tablesOfKey` know
  `pf|`; the instructors' hover names the page files. The five's guide is unchanged.
- `site/lib/problems.ts`: the four after the five in `SETS` and `problemSet`; nothing of the five moved.
- Pages, additive: the set page names a question's page files (and drops the empty "Tables:" words only where a question
  reads no table); the index names each set's page files; the index and the set page link a dated edition only when it
  holds the set; the edition and teacher pages list addresses only for sets their edition holds (for the five, the same
  ten as before). Five new decisions (`page-file`, `trade-month`, `storm-hour`, `layer-by-id`, `industry-pick`) in
  `Decisions.tsx` and the note's table.
- `site/scripts/build-problem-edition.mjs`: a `pf|` figure becomes a row of its own with its page file as source.
- The teacher's copy: the existing teacher page draws a set from a dated edition, and no edition holds the four (the
  edition of 15 October 2026 predates them; a new one is built from the live set by the data machine). The live set page
  draws every worked solution and "why it matters" for the four, checked by drawing it to HTML.

## Tests run (no site build, no full suite: this machine is short of memory)

| Test | Result |
|---|---|
| `site/scripts/test-pagefile.mjs` (resolver; check-values end to end on `regions/trade/car.json`) | 6 of 6, exit 0 |
| `site/scripts/test-problem-sets-country.mjs` | exit 0: 4 sets, 27 questions and 4 examples, 399 keyed figures recomputed from their files, 399 found on the drawn pages |
| `site/scripts/test-problem-sets-render.mjs` | exit 0: 9 sets, 20 choices, the note's list equal |
| `site/scripts/test-problemkit.mjs` | 12 of 12, exit 0 |
| `site/scripts/test-check-values-slow.mjs` | 5 of 5, exit 0 |
| `replicate_country.py --compare` (the site's figures from `problem-sets-country-figures.mjs`) | 31 questions, 113 answer figures, 0 differ, exit 0 |
| TypeScript, the 14 changed or new files only (`tsconfig.c507b.json`, not committed) | exit 2: one error, in `app/network/Network.tsx` (untouched; no declaration file for `three` in the junctioned node_modules); none in the files of this session |
| `tests/test_session8901_problem_sets_country.py` | 7 passed, exit 0 |
| `tests/test_session7534_problem_sets.py` | 8 passed, exit 0, after its pin moved (below) |
| `tests/test_session5171.py` | 9 passed, exit 0, after its pin moved (below) |
| `tests/test_session44.py`, `149_checks`, `288`, `3650`, `369`, `4051`, `408`, `55` | 3, 4, 11, 1, 14, 2, 7, 11 passed; each exit 0 |
| `tests/test_session293.py`, `465` | 9 passed; 9 passed and 1 skipped; exit 0 |
| Tests that read `check-values.mjs`'s cases or pages: `178`, `235`, `236`, `237`, `239`, `264`, `265`, `300`, `315`, `329`, `332`, `347`, `402`, `405`, `406`, `409`, `430`, `466`, `467`, `468`, `471`, `500`, `505`, `54`, `579`, `58`, `581`, `584`, `700`, `7201_large_load_on_site`, `90`, `2244_deals`, `2245_deals` | all passed (some with skips for missing node pieces), each exit 0 |
| `tests/test_session1880.py` | exit 1: 1 failed of 15, its node test `test-attention-view.mjs` on the attention week file ("the build's Monday is 2026-11-02"), a date-bound check of a page this session did not touch. On a clean worktree of `24110a0d1` (no node_modules) that test skips, so the failure is not confirmed there; nothing of this session reaches `lib/attention.ts` or its data |
| `replicate_country.do` | not run: Stata is not installed on this machine; its rules are checked as text by the test |

Pins moved, each with its reason beside it: `tests/test_session5171.py` lists `lib/pagefile.ts` among the files that read
the disk, with its name guard; `tests/test_session7534_problem_sets.py` compares the replay's five sets with the kept
figures and holds the four new ones to be drawn whole, and counts 20 choices on the index, not 15.

## Commits

`4f1d99ea2` the key; `cc64e8d2c`, `52ee20293`, `973861ad4`, `124e8e554` the four sets; `c5e656efa` the registration, pages,
decisions and node tests; `a89d11c28` the two pins; `a3ae78561` the replication and the note; and this report's commit.

## What a browser must check (after a build on a machine that can hold one)

| Address | What to look at | What should be seen |
|---|---|---|
| `/learn/problems` | The list of sets | Nine sets, the four new last; each new one with "Page files: site/data/..." and "no dated edition holds this set yet"; the five unchanged, each with its edition and teacher's copy links |
| `/learn/problems/who-trades-with-whom` | The worked example and question 1 | October 2026; 574,900 MWh in all; every figure's hover names `site/data/regions/trade/ten.json`; "Page file: site/data/regions/trade/ten.json" under each question |
| `/learn/problems/who-trades-with-whom` | Question 7 (the hours) | July 2018, 407 of 744 hours, 54.70 % |
| `/learn/problems/storm-across-the-country` | Questions 1 and 2 | 2022-12-24 01:00 UTC, 33,225 MW against 19,830 MW; 2021-02-15 01:00 UTC, 69,215 MW against 40,461 MW; compare with the events pages' "Highest hour" for Tennessee and Texas |
| `/events/elliott-2022#whole-country` | Tennessee's row | Highest hour 33,225 MW at 2022-12-24 01:00 UTC; Baseline that hour 19,830 |
| `/learn/problems/under-the-ground-and-in-the-wind` | Each question's sources line | "Page file: site/data/resources/manifest.json" and no empty "Tables:" words |
| `/map?tab=resources` | The legends of Wind speed at 100 m, GHI and DNI | 13.58 m/s, 6.50 and 9 kWh/m2/day at the top, as the set says |
| `/learn/problems/where-energy-goes` | Questions 1 and 2 | July 2026, 2,713.60 TBtu; July 2025, 2,766.80 TBtu |
| Each new set's page | The decisions fold at the foot | `page-file` and the set's own choice, each with its default and source on hover |
| Each new set's `data.csv` (internal view) | The CSV download | One row a figure, its `pf|` key, its tables (none for the resource set) and its source words |
| `/learn/problems/<new slug>/2026-10-15` | The address of an edition | Not found, as for any address no edition holds |
| Each new set at 390 px | The worked example and an open answer | No sideways scroll; the long `pf|` hover words wrap in the tip |
