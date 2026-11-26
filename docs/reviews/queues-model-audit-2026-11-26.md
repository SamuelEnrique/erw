# The interconnection queue: the model audited as a hostile expert would

Session 10213, 26 November 2026, chain 710 (part D), the old laptop. Read as a developer's interconnection lead, who would choose where to file with this page and wants to find it wrong, and as an AI lab's siting team, who would read it for how much generation is coming and how long it takes. In the form of `docs/reviews/tracker-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/queues-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-queues-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- Not repeated: the page's read of 16 November (`docs/reviews/queues-read-2026-11-16.md`: ERCOT's hybrids labelled never withdrawn, ISO-NE's undated waits, no load in the file, the operators' own lists) and the two rulings of 17 November (`ruling-impact-queues-2026-11-17.md`, `ruling-alternatives-queues-2026-11-17.md`: a second, recent wait beside the headline; storage reconciled to Berkeley Lab's "approximately 749 GW"). They are cited where they bear.

## In short

- **The arithmetic is right.** An independent restatement written from the method note with the standard library alone (`restate_queues.py`, no pandas, no import of the builder or the replication) gives every value of all 76 views of the page's file (17,246 values) and the file's counts from Berkeley Lab's 38,201 rows. Of the 315 numbers the default view prints under a key, 312 equal it to the digit, as do 77 of its 78 hovers and the fold's four counts; the other three are one MW high because each MW sum is rounded twice, to a tenth in the builder and to a whole MW on the page (finding 6). The places page's 931 owner values and 25 states agree.
- **"Both parts" of a hybrid is true in one grid (finding 1).** The page says a solar-with-storage request's capacity is both parts together. Berkeley Lab's file gives a hybrid's second part its own MW in CAISO (730 of 733) and for some of the West's (360 of 1,862), and in no other grid (0 of 2,462). So CAISO's hybrids count both parts where ERCOT's count one figure, side by side in the "every grid" table. With each hybrid at its largest part, CAISO's active MW fall 32.1 percent (190,717 to 129,435). Fixed in words; the figure is for Samuel's ruling. It also gives a sized lead on the storage gap left open on 16 November: 1,507 active requests have a battery part the file sizes at nothing.
- **The default view's solar-with-storage share is unmarked (finding 2).** The builder marks the United States' solar-with-storage shares as counting ERCOT's 66 requests that the file never labels withdrawn. The page drew only ERCOT's mark, so the default table prints 62.62 percent withdrawn with no hover. Without ERCOT's it is 66.08. Fixed in words.
- **Smaller, all words.** "Recent years are mostly still open" is false in the default view: 29 to 49 percent of each year from 2021 to 2024 is open, and only 2025 is mostly open (finding 3). "The most entered in 2025" names the year of most MW still active; the most MW entered in 2023 and the most requests in 2022 (finding 4). Each grid's newest dates differ (no CAISO request after April 2023, NYISO's operation dates end in 2023 and MISO's in 2024), and 53 requests withdrawn in January 2026 count as withdrawn "at the end of 2025" (finding 5).
- **Checked and right:** survivors only, a median, said; the rise of the waits line is not the file's start; no fuel counted twice; ISO-NE's undated built requests; no held operator table reaches the page (the file is Berkeley Lab's, CC BY 4.0); the past window's choice is said and measured.
- **What an interconnection lead's own number would hold:** capacity weighted by each grid and technology's own past success, 209,653 of 1,864,963 MW (11.2 percent); the share of a cohort built within five years of its request, 9.22 percent; time to withdrawal, a median of 1.63 years; the queue by study phase (22.8 percent of active MW has an executed agreement). None of these is on the page.
- **Five branches fix words and move no figure (1, 3, 4, 5, 6); two show a figure for ruling (2, 7).** One data request (MISO's and NYISO's own queues against the file's missing operation dates). Nothing needs the key.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/queues/page.tsx` | The page `/queues`: the choice of grid (ten) and technology (eight); the summary sentence; four headline numbers (active capacity, reached operation, withdrawn, request to operation); active MW by year entered; the outcome of each year entered with its fold of counts; median years by operation year; the technology table of the grid; the "every grid" table of the technology; the fold "What the file does not hold"; how it is computed; the decisions; the source line |
| `site/lib/queues.ts` | Pure: the choices from the address, `viewOf`, `yearsOf`, `outcome` (the one division, a bar's height), `peakActive`, `noneWithdrawn`, `withdrawnOf`, `onYears`, number formats (`whole`: Math.round; `two`: two decimals) |
| `site/data/queues.json` | The page's file: the 76 views of `interconnection_queue_summary` (`years`, `on`, `whole`), the counts, the past window, the floors, and the builder's `not_comparable` marks. Built 17 November 2026 07:52 UTC from the input retrieved 2 October 2026 |
| `site/lib/decisions.ts`, `QUEUES_DECISIONS` | The nine decisions at the foot, word for word in the method note |
| `warehouse/derived/queue_summary.py` | The builder: technology from `type_clean`, status from the ERW status, MW = `capacity_mw` (negative as zero), year entered, years to operation (`(on_date - q_date)/365.25`, built and in order), the views, the floors, `not_comparable`, the snapshot |
| `warehouse/connectors/lbnl_queues.py`, `docs/methods/lbnl_interconnection_queue.md` | Berkeley Lab and GridTracker's Queued Up, 2026 edition: one row per request through the end of 2025, `capacity_mw = mw_1 + mw_2 + mw_3` |
| `site/app/queues/places/page.tsx`, `Decisions.tsx`, `site/data/queue_places.json`, `warehouse/derived/queue_places.py`, `docs/methods/queue_places.md` | `/queues/places`: the 49 queue owners of Berkeley Lab's West and Southeast and the 25 states with people outside the seven grids; capacity summed as filed |
| `docs/methods/interconnection_queue_summary.md` ("the method note") | The table's note: rules, rows, the replication (17,254 of 17,254), the cross-check, the decisions, what the reader meets, ERCOT's hybrids, what waits |
| `docs/methods/{caiso,ercot,isone,miso,nyiso,spp}_interconnection_queue.md`, `iso_queue_snapshot_summary.md`, `nyiso_load_queue.md` | The operators' own queue tables. `/queues` does not read them; its lead names them, as `/explore/interconnection` and `/map?tab=queues` count them: "another source, read on another day" |
| `docs/methods/generator_pipeline_by_grid.md` | EIA-860M's planned generators. No queue page reads it (only `tests/test_session2951.py`); listed because the brief named it |
| `site/scripts/queues-page.mjs`, `test-queues-read.mjs`, `check-queues.mjs` | The page drawn to HTML with its own code; the read's test (29 checks); the built site's check |
| `replication/queues/` | `replicate.py` (pandas, by the note), `replicate.do`. Not run here: the restatement above is independent of it |
| Read from the main copy, never written | `warehouse/output/lbnl_interconnection_queue.csv` (38,201 rows, retrieved 2 October 2026) |

## How every number here was computed

- **The default view:** `/queues` (all regions, all technologies), drawn with the page's own function (`site/scripts/queues-page.mjs`) on `site/data/queues.json` of origin/main (`draw_main_us_all.txt`).
- **The restatement:** `restate_queues.py` reads Berkeley Lab's rows with `csv` and `statistics`, applies the method note's rules, and compares with every value of the page's file and with every keyed number, hover and count of the drawing. `rounding.py` checks the three gaps with exact decimals.
- **One rule at a time and the claims:** `measures_queues.py`, `measures2_queues.py`, `measures3_queues.py` (expected capacity, from the page's file), `measures4_queues.py` (study phase).
- Copies of every script and printout: `docs/reviews/queues-model-audit-2026-11-26/` (written to run from `runs/c10213/` of a worktree).

## The arithmetic re-done

| Figure (default view) | The page | Restated | Gap |
|---|---|---|---|
| Active at the end of 2025 | 8,513 requests, 1,864,963 MW | the same | 0 |
| Suspended, not counted | 668 requests, 137,204 MW | the same | 0 |
| Past requests, 2000 to 2020 | 22,344; reached operation 18.78 percent (12.83 by MW of 3,590,750); withdrawn 70.89 (75.21 by MW); still open 10.33 | the same | 0 |
| Request to operation | 3.58 years, median, over 3,098 of 4,789 built | the same | 0 |
| The year of most MW still active | 2025 | 2025 (451,093.9 MW) | 0 |
| Active MW by year entered, 26 bars | 177 (2000) to 451,094 (2025) | 25 of 26 the same; 2005: 1,289 against 1,288 | 1 MW (finding 6) |
| The outcome of each year, 26 hovers | 2000: 304 requests, 81, 221, 2 ... 2025: 2,319, 13, 474, 1,832 | the same | 0 |
| Every year entered, 30 rows of 7 counts | 1995 to 2025 | 208 of 210 the same; MW entered 2016 213,253 against 213,252, 2022 681,953 against 681,952 | 1 MW (finding 6) |
| Median by operation year, 26 points | 0.69 (2000) to 5.44 (2025) | the same | 0 |
| The technology table, 7 rows | Solar 396,668, 2,742, 13.35, 73.95, 4.59 ... Everything else 137,905, 581, 32.78, 62.10, 2.26 | the same | 0 |
| The every-grid table, 10 rows | All regions 1,864,963 ... ERCOT 408,108, 1,796, 29.56, 51.19, 3.70 ... Southeast 143,820, 957, 15.83, 75.77, 3.79 | the same | 0 |
| The fold's counts | 4,789 built, 3,098 dated; 665 with no year, 10 of unknown status | the same | 0 |

- **The page's file:** 17,246 values of the 76 views (by year entered, by operation year, the whole) equal the restatement within the file's own rounding (a tenth of a MW, a hundredth of a percent or year); the counts equal; the status read from `q_status` equals the table's status on 38,201 of 38,201 rows; the nine regions add to the 38,201 of the United States and the seven technologies' active MW to its 1,864,963.3.
- **Rounded twice.** The three gaps are exact sums of 1,288.45, 213,252.46 and 681,952.47 MW: the builder writes 1,288.5 and the page prints 1,289. 22 of the 889 region-by-year MW sums lie where this can happen.
- **The places page:** 931 owner values (entries and MW by status, active MW by type and by year) and the 25 states restated; four sums differ in the tenth from float addition (TEP's withdrawn, exact 23,268.45, the file 23,268.4), none in the whole MW printed. The page opens on BPA and PacifiCorp, the two largest by active MW, as decision 3 says.
- **What a visitor sees:** the page is in review; drawn with the site's code, no em dash.

## One rule changed at a time

The base is the default view: 8,513 active requests and 1,864,963 MW; of 22,344 past requests, 18.78 percent built and 70.89 withdrawn; a median of 3.58 years.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Past requests entered 2000 to 2020 (five years' lag) | 2000 to 2018 / 2000 to 2015 / 2010 to 2020 | built 21.50 / 24.02 / 16.42 percent; withdrawn 72.30 / 73.62 / 69.87; still open 6.20 / 2.36 / 13.71 | yes (decision 6); its reason misworded (finding 3) |
| A share of every past request, open ones included | of the resolved ones only (built over built plus withdrawn) | 18.78 to 20.94 percent | the open share is printed beside |
| A hybrid's every part summed | each request at its largest part | 1,864,963 to 1,749,315 MW (-6.2 percent); CAISO -32.1, the West -12.1, every other grid 0; solar with storage 503,794 to 407,012 (-19.2) | the words say "both parts" for every grid (finding 1) |
| Suspended apart from active | counted active | 9,181 requests, 2,002,167 MW (+7.4 percent) | yes, the headline's note |
| A negative capacity as zero | as filed | -336.7 MW over 16 rows; the places page sums them as filed (finding 6) | yes (decision 4), on `/queues` |
| The status as the file has it | as at 31 December 2025 (January 2026 withdrawals active) | up to 8,566 requests and 1,878,238 MW (+0.7 percent) | no (finding 5) |
| A median of the built | a mean | 3.58 to 3.85 years (quartiles 1.96 and 5.19) | "median" is said |
| Every operation year | 2016 to 2025 | 3.58 to 4.29 years | the ruling of 17 November (2023 to 2025) is waiting; not repeated |
| A share from 20 past requests, a median from 5 dated | 50 / 5; 20 / 10; 50 / 20 | views with a share 73 to 65 of 76; with a median 56 to 51, or 43 | yes (decision 7) |
| Each sum rounded to a tenth, then to a whole MW | rounded once | 3 of the 315 keyed numbers one MW lower | no (finding 6) |
| Shares by request | by MW | built 18.78 against 12.83; withdrawn 70.89 against 75.21 | both are printed |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Active against withdrawn against in service | the sentence, the headline, the decisions | Berkeley Lab's four statuses, suspended apart, unknown counted as entered only | **Right**; "at the end of 2025": the statuses run to 16 January 2026 (finding 5) |
| Nameplate against summer capacity | the chart note: "what it asked to connect" | `capacity_mw`, the MW each part requests as filed: neither a built plant's nameplate nor a summer rating | **Right as stated** |
| A project with several fuels counted twice | the technology table, decision 3 | Each request once, by `type_clean`; every other hybrid in "Everything else"; the seven groups add to the whole | **Right** |
| A project in several phases or requests | the fold: "a developer may file at several points for one plant, and each request counts" | Each request counts | **Right as stated**. Sized: 565 active requests (112,964 MW, 6.1 percent) share an owner, a point of interconnection, a type and a MW with another request; 55 (4,734 MW) share a project name and a point. Candidates, not established duplicates |
| Storage hybrids: "both parts" | the chart note, the technology note, decision 4 | `mw_1 + mw_2 + mw_3` as the file gives them; the second part has MW in CAISO and part of the West only | **Finding 1** |
| Queue dates | every chart by year entered | `q_year`, the year of `q_date` on every row | **Right**. Many dates are a cluster window's: 590 of CAISO's requests since 2020 share 17 April 2023, 377 and 302 of MISO's 14 and 15 September 2022, 290 of SPP's 1 March 2025, so a wait counts from the window's day |
| "Time in queue": median against mean, survivors only | the headline, the waits chart | The median, over built requests with both dates, of days over 365.25 | **Right as stated**: "the ones with both dates", "Only requests that were built are here: it is not the wait of a request made today". The mean is 3.85 |
| The waits line rising from 0.69 to 5.44 years | the chart by operation year | One median a year from five dated requests | **Right**, checked against the file's start (its oldest request is of November 1995): only 2000 and 2001 cannot show a wait above 5.1 and 6.1 years, and in 2002 to 2009 only 2 to 13 percent of waits were above five years. NYISO's and MISO's later years are empty for another reason (finding 5) |
| Completion rates and how withdrawn requests enter | the headline, the decisions | Built, withdrawn and open over every past request with a known status; a withdrawn request with no withdrawal date counts by its status | **Right as stated**; its reason "recent years mostly still open" and "most outcomes known" are not (finding 3) |
| Each ISO's queue report and its date | the lead, decision 1 | One compiled file of the end of 2025 | Each grid's newest dates differ (finding 5); the operators' own lists named as another source (**right**) |
| A held grid (ISO-NE, MISO, NYISO) reaching a figure | the whole page | The page reads `site/data/queues.json` only, built from Berkeley Lab's file (CC BY 4.0, "may be public", `license_tables.csv`). MISO's pause concerns MISO's own servers | **Right**: no row of an operator's held table reaches `/queues` or `/queues/places`. Their figures for those grids are Berkeley Lab's |
| Staleness, the as-of date | the source line | "retrieved 2026-10-02, summarized 2026-11-17"; the file's Last-Modified 7 May 2026 | **Right**. A newer edition would replace every figure (decision 1) |
| ISO-NE: "carry no operation date" | the hover, the fold, decision 8 | 228 of 228 built ISO-NE requests have no `on_date` | **Right** |
| The United States' solar with storage | the default view's technology table | The file marks it (`not_comparable`); the page drew only ERCOT's mark | **Finding 2** |
| "The most entered in 2025" | the headline's note | `peakActive`: the year of most MW still active | **Finding 4** |
| "From Berkeley Lab and GridTracker's record of every request" | the lead | Every row of the file | Loose: the fold says operators keep finished and withdrawn requests for different lengths of time. The Southeast's entries of 2000 to 2009 are 15.6 percent of its past window, against 22 to 39 percent elsewhere. Not a branch |
| The places page: owners by active MW, BPA and the next first, 25 states all named | `/queues/places` | As stated | **Right**; one negative capacity summed as filed (finding 6) |

## What an interconnection lead's or a siting team's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| Capacity weighted by its chance of being built (each grid and technology's own past share of MW built, 2000 to 2020) | 209,653 of 1,864,963 MW (11.2 percent), or 1,267 of 8,513 requests; by grid ERCOT 18.8 percent, the Southeast 12.7, MISO 10.6, CAISO 9.8, the West 8.0, PJM 7.6, SPP 7.1, NYISO 5.7, ISO-NE 4.6 | `measures3.out`, the page's file |
| The capacity a point of interconnection allows, not the parts' sum | -115,648 MW (-6.2 percent) with each hybrid at its largest part, all of it CAISO's and the West's | finding 1 |
| The chance that a request made today is built in time | of the 22,344 requests of 2000 to 2020: 5.16 percent built within 3 years, 9.22 within 5, 12.70 within 10 (dated ones only, so a floor) | `measures.out` |
| How long a failure takes | withdrawn: a median of 1.63 years from request (mean 2.15; 15,367 dated) | the same |
| How long the queue already is | active requests have waited a median of 2.98 years; 3,312 (39.3 percent) longer than the built ones' median of 3.58 | the same |
| Where each request stands | active MW by Berkeley Lab's study phase: an executed agreement 22.8 percent (424,493 MW), facility study 20.9, in progress 17.6, cluster study 10.0, system impact 8.9, no phase 10.1; time to an agreement, a median of 2.24 years (4,718 dated) | `measures4.out`; the file holds `ia_phase` and `ia_date`, the page neither |
| The operators' queues after 2025 | not here: CAISO's, ERCOT's and SPP's newer lists are on `/explore/interconnection`; the others' are held | the page's lead |
| Network upgrade costs, the developer, withdrawal penalties | in no edition of the file | the fold |
| The storage in hybrids where the file gives it no MW | 1,507 active requests with a battery part of no MW (326.2 GW of capacity, the other part's): a likely part of the 196 GW gap to Berkeley Lab's summary, not an established one | `measures2.out` |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | "Both parts" of a hybrid: the file gives the second part MW in CAISO and part of the West only | CAISO's active MW 32.1 percent above a like-for-like count; the "every grid" table sets unlike figures side by side | words; the figure for ruling | `wip/audit-queues-1` (`0bd098f97`); `wip/audit-queues-2` (`7b976dd81`) |
| 2 | Low | The United States' solar-with-storage share, marked by the builder, is drawn unmarked in the default view | 62.62 percent withdrawn, 66.08 without ERCOT's | words | `wip/audit-queues-3` (`94ac1371e`) |
| 3 | Low | "Recent years are mostly still open" and "most outcomes known" | 2021 to 2024: 29 to 49 percent open; ERCOT's batteries' past requests 58.67 percent open | words | `wip/audit-queues-4` (`5ce00f1d3`) |
| 4 | Low | "The most entered in 2025" names the year of most MW still active | most MW entered in 2023, most requests in 2022; 54 of 76 views differ; "in 1 requests" in 155 bar hovers | words | `wip/audit-queues-5` (`7365f7af9`) |
| 5 | Low | One date for every grid: each grid's newest dates differ, and January 2026 withdrawals count | NYISO's waits end in 2023, MISO's in 2024; up to 53 requests and 13,275 MW (+0.7 percent) | words | `wip/audit-queues-6` (`cb38ed586`) |
| 6 | Very low | MW rounded twice; the places page sums a negative capacity | 3 of 315 keyed numbers one MW high; TVA's withdrawn MW 218,498 against 218,573 | figures, for ruling | `wip/audit-queues-7` (`368d61ec7`) |

## 1. "Both parts" of a hybrid is true in one grid (Medium)

- **Where.** `site/app/queues/page.tsx`, the active chart's note ("for solar with storage, both parts") and the technology table's note ("its capacity is both parts together"); decision 4 ("all parts of a hybrid together"); the method note.
- **Why it is wrong.** The builder sums `capacity_mw`, which is `mw_1 + mw_2 + mw_3`. Of the requests with a second part (`type_2`), the file gives that part its own MW for 730 of CAISO's 733 and 360 of the West's 1,862, and for none of the 2,462 in ERCOT, ISO-NE, MISO, NYISO, PJM, SPP and the Southeast (an ERCOT row: Solar 201.04 MW, Battery with no MW, capacity 201.04; a CAISO row: Solar 500, Battery 267, capacity 767). So CAISO's 194 active solar-with-storage requests carry 120,243 MW, both parts, and ERCOT's 524 carry 112,068, one figure. With each hybrid at its largest part, CAISO's active MW would be 129,435, not 190,717 (-32.1 percent), and the West's 394,235, not 448,601; every other grid's are the same either way. A developer comparing CAISO with ERCOT in the "every grid" table compares two counting rules.
- **The storage gap.** The method note's cross-check sets the file's 552.7 GW of battery parts beside Berkeley Lab's "approximately 749 GW" and leaves 196 GW unexplained. 1,507 active requests have a battery part that the file sizes at nothing (539 in ERCOT, 451 in the West, 206 in MISO, 146 in PJM), 326.2 GW of capacity in all, the other part's. That is a likely part of the gap, not an established one; it is now in the note.
- **The test.** `tests/test_audit_queues_1.py` on `wip/audit-queues-1`: in Berkeley Lab's rows, CAISO's second parts carry MW and seven regions' never do (passes on main, skipped where the rows are not held); the page's figures do not move (passes); the words test fails on main.
- **The fix on the branch, words only.** Both notes say a capacity is the sum of the parts the file gives MW for, which is both parts in CAISO and for some of the West's requests and one figure elsewhere, so the grids' hybrid MW are not alike. Decision 4 and its line in the method note say the same; the note gains the counts and the storage lead.
- **For Samuel's ruling.** Default "left as it is". The other choice, each request at its largest part everywhere (`wip/audit-queues-2`, a test only): CAISO 190,717 to 129,435 MW, the West 448,601 to 394,235, the United States 1,864,963 to 1,749,315 (-6.2 percent), solar with storage 503,794 to 407,012 (-19.2 percent).

## 2. The default view's solar-with-storage share is unmarked (Low)

- **Where.** `site/app/queues/page.tsx`, `Withdrawn`; `site/data/queues.json`, `not_comparable`; the method note, "ERCOT's solar with storage is not comparable".
- **Why it is wrong.** Session 7052 had the builder mark two views: ERCOT's solar with storage, and the United States', whose share withdrawn counts ERCOT's 66 past requests, none labelled withdrawn, "so its withdrawn share reads lower than a count would". The note says the site's copy carries both marks, and it does. The page drew only its own rule (`noneWithdrawn`), which catches ERCOT alone, so the default view's technology table, the United States' solar-with-storage headline and the every-grid table print 62.62 percent with no word. Without ERCOT's requests the share is 66.08 percent (1,194 past requests).
- **The test.** `tests/test_audit_queues_3.py` on `wip/audit-queues-3`: the file carries the mark and the figure (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Where a view is not already marked by `noneWithdrawn`, its share withdrawn carries the builder's mark as its hover ("The United States' solar-with-storage shares count ERCOT's 66 past requests, none of them withdrawn by the file's labels, so its withdrawn share reads lower than a count would."), and the note says so with the 66.08. No figure moves.

## 3. Recent years are not mostly open (Low)

- **Where.** `site/app/queues/page.tsx`, the outcome chart's note ("old enough (five years or more) for most outcomes to be known. Recent years are mostly still open"); decision 6 ("recent years, still mostly open"); the method note, "Past requests".
- **Why it is wrong.** In the default view the share still open of each year entered is 28.6 percent (2021), 44.1 (2022), 36.8 (2023), 49.3 (2024) and 79.0 (2025): only 2025 is mostly open, and most of the rest of 2021 to 2024 is withdrawn. Over the 76 views, 81 of 273 view-years of 2021 to 2024 are mostly open. And "most outcomes known" for 2000 to 2020 fails in two views without a label problem: 58.67 percent of ERCOT's standalone batteries' past requests and 60.00 percent of SPP's solar with storage are still open (ERCOT's solar with storage, 84.85, is finding 2's labels). The window's purpose holds; its stated reason does not.
- **The test.** `tests/test_audit_queues_4.py` on `wip/audit-queues-4`: the open shares from the file (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note reads that past requests are five years old or more, "so in most views most of their outcomes are known (the headline's "still active or suspended" says how many are not)", and that recent years "still hold many requests whose outcome is not known (in most views fewer than half of each year 2021 to 2024, and most of 2025)". Decision 6 and the method note read "many of whose requests are still open". No figure moves.

## 4. The headline names a year it does not say (Low)

- **Where.** `site/app/queues/page.tsx`, the headline "Active capacity", its note "The most entered in {year}."; `peakActive` in `site/lib/queues.ts`; the active chart's bar hovers.
- **Why it is wrong.** `peakActive` returns the year of most MW still active. "The most entered in 2025" reads as the year in which most was entered. In the default view the most MW entered in 2023 (861,011) and the most requests in 2022 (3,435); 2025 is the year of most still active (451,094 MW). In 54 of the 76 views the year of most MW still active is not both the year of most MW entered and of most requests entered. The bar hovers also say "in 1 requests" for 155 years of the views; the read of 16 November fixed the headline's plural, not the hover's.
- **The test.** `tests/test_audit_queues_5.py` on `wip/audit-queues-5`: the three years from the file (passes on main); the words test fails on main.
- **The fix on the branch, words only.** "More of it entered in 2025 than in any other year (by the MW still active; the year in which the most MW or the most requests entered can be another)." A bar of one request says "1 request". No figure moves.

## 5. One date for every grid (Low)

- **Where.** `site/app/queues/page.tsx`: the sentence and the legend ("At the end of 2025", "Active at the end of 2025"), the year table's note ("by their status at the end of 2025"), the waits chart; the fold "What the file does not hold"; the method note.
- **Why it is wrong.** The edition is of the end of 2025, but each grid's newest dates in it differ. The newest request date is 19 to 24 December 2025 in ERCOT, MISO, SPP, the West and the Southeast, 26 September 2025 in NYISO, 1 July 2025 in PJM, 14 January 2025 in ISO-NE (one request of 2025) and 17 April 2023 in CAISO (none of 2024 or 2025). The newest operation date is 31 December 2023 in NYISO and 19 December 2024 in MISO (NYISO's operation dates in 2021, 2022 and 2023 number 4, 9 and 5), so the waits chart has no 2024 or 2025 point for them, which a reader takes for "fewer than five built". And the statuses run past the year's end: 53 requests (13,275 MW; 33 of MISO's, 11 of PJM's) carry a withdrawal date of 2 to 16 January 2026 and count as withdrawn, not active.
- **The test.** `tests/test_audit_queues_6.py` on `wip/audit-queues-6`: the dates and the 53 from Berkeley Lab's rows (passes on main, skipped where the rows are not held); the words test fails on main.
- **The fix on the branch, words only.** A line of the fold, "One date for every grid", says each grid's newest dates differ, names CAISO's, ISO-NE's, NYISO's and MISO's, says a later year has no point for NYISO and MISO because the file dates none, and says the 53 January withdrawals count as withdrawn. The method note gives every grid's dates. The figure "as at 31 December 2025" (up to 8,566 requests, 1,878,238 MW, +0.7 percent) is measured, not made: for Samuel's ruling, default "left as it is", no branch.
- **Data request.** Whether MISO's and NYISO's own queues record requests in service in 2024 and 2025 that the file does not date (their tables are held, "license needed" since 21 October 2026 in `warehouse/metadata/license_status.csv`, so this machine did not read them).

## 6. Two small figures (Very low)

- **Rounded twice.** The builder writes each MW sum to a tenth (`round(x, 1)`) and the page rounds that to a whole MW (`Math.round`). Where an exact sum lies from .45 to .49 the page prints one MW high: 3 of the default view's 315 keyed numbers (2005's MW still active 1,289 against 1,288.45; 2016's MW entered 213,253 against 213,252.46; 2022's 681,953 against 681,952.47), and 22 of the 889 region-by-year MW sums could be.
- **Two pages, two rules.** `/queues` counts a negative capacity as zero (decision 4); `/queues/places` sums it as filed, so TVA's one withdrawn entry of -75 MW makes its withdrawn MW 218,498 where `/queues`' rule gives 218,573.
- **The test.** `tests/test_audit_queues_7.py` on `wip/audit-queues-7`, a test only (passes on main, skipped where the rows are not held).
- **For Samuel's ruling.** Default "left as it is". The other choice: the builder writes two decimals (or the page rounds the exact sum), and the places builder counts a negative capacity as zero: three default-view cells one MW lower; TVA's withdrawn MW 75 higher.

## The words branches drawn and read

Each branch's page was drawn to HTML with the site's own code (`node --import ./scripts/battery-awards-page-register.mjs scripts/queues-page.mjs <grid> <tech> <out>`, the read's own drawing of session 7545) and the new words read in the drawn text. No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-queues-1` | the active chart's note and the technology table's note (`us|all`, `caiso|solar_battery`); decision 4 | pass: "A request's capacity is what it asked to connect, the sum of the parts the file gives MW for: a hybrid's second part has its own MW in CAISO and for some of the West's requests, and in no other grid, where a solar-with-storage request carries one figure." and "... so CAISO's solar-with-storage MW count both parts where ERCOT's, PJM's and the rest count one figure: the grids' MW of hybrids are not alike." |
| `wip/audit-queues-3` | the solar-with-storage share withdrawn: the default view's technology table, `us|solar_battery`'s headline and every-grid row | pass: the hover on 62.62; ERCOT's own hover unchanged on 0.00 |
| `wip/audit-queues-4` | the outcome chart's note; decision 6 | pass |
| `wip/audit-queues-5` | the headline's note; the 2002 bar's hover | pass: "More of it entered in 2025 than in any other year ..."; "Entered 2002: 5 MW still active, in 1 request" |
| `wip/audit-queues-6` | the fold (`nyiso|all`) | pass: "One date for every grid. ..." |
| the five merged (a local trial, not pushed) | the default view | pass: every new sentence drawn once; the restatement on the merged drawing gives the same 312 of 315 (no figure moved) |

- The five words branches merge together onto origin/main of 26 November (`6441330f5`) with no conflict. Their tests with every test file that reads the changed files (`test_session241a`, `462`, `463`, `5001`, `5003`, `7018_board_done` to `7018_supply_done`, `7018_queues_done`, `7402_trackers`, `7405_trackers`, `95`, `105`, `9601_back_button`, `7052_queue_marks`, `7518_interconnection_read`) pass on the merge: 134 passed, 14 skipped, 199 subtests; `site/scripts/test-queues-read.mjs` 29 of 29. Each words test fails on origin/main; each behaviour test passes there.

## The decisions block, line by line

1. One yearly file, through 2025: **right**; each grid's newest dates differ (finding 5).
2. A request once, under its region; the US as every request: **right** (the nine regions add to 38,201).
3. Seven technology groups from `type_clean`, hybrids apart: **right**.
4. MW the sum of the parts as filed: **right as computed**; "all parts of a hybrid together" holds where the file gives each part MW (finding 1).
5. Berkeley Lab's four statuses, unknown counted as entered: **right**.
6. Shares over 2000 to 2020: **right**; its reason, "still mostly open", is not (finding 3).
7. Floors of 20 and 5: **right**.
8. Years to operation, dated and in order; ISO-NE none: **right** (48 reversed left out; 228 of ISO-NE's undated).
9. What the queues record, nothing inferred: **right**.

## Not covered, or left open

- **The operators' own tables** (`/explore/interconnection`, `/map?tab=queues`) are another tool; only the lead's sentence on them was read.
- **`site/app/cost-of-power/model.ts`** reads the same file for "how soon": covered by the cost audit's scope, not here.
- **The published replication** (`replication/queues/replicate.py`) was not run; the restatement above is independent of it and agrees with the file it checks.
- **The layout in a browser**: drawn to HTML only; no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-queues-1` (`0bd098f97`), `-3` (`94ac1371e`), `-4` (`5ce00f1d3`), `-5` (`7365f7af9`), `-6` (`cb38ed586`). They merge together cleanly onto origin/main of 26 November; each was drawn and read (pass). No figure moves.
- **For Samuel's ruling, default "left as it is":**
  - Finding 1, `wip/audit-queues-2` (`7b976dd81`), not for landing: each hybrid at its largest part; CAISO's active MW 190,717 to 129,435 (-32.1 percent), the United States' 1,864,963 to 1,749,315 (-6.2 percent).
  - Finding 6, `wip/audit-queues-7` (`368d61ec7`), not for landing: MW rounded once (three default-view cells one MW lower) and a negative capacity as zero on the places page (TVA's withdrawn MW +75).
  - Finding 5, no branch: statuses as at 31 December 2025, up to 8,566 active requests and 1,878,238 MW (+0.7 percent).
- **Data request:** for MISO and NYISO, count the requests their own queue tables (`miso_interconnection_queue`, `nyiso_interconnection_queue`) record as in service with a date in 2024 or 2025, against Berkeley Lab's file, which dates no MISO request in service after 19 December 2024 and no NYISO one after 31 December 2023; a count by year, no rows copied.
- **Needs the key:** nothing.
