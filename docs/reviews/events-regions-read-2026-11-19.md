# The events pages' "whole country" views, read as their reader (started 19 November 2026)

Energy Research Warehouse (ERW). Chain 503, part E (session 8440, the old laptop). The form is part B of chain 304: five real cases a named reader would bring, each taken start to finish on the page; every gap a numbered row; every fault fixed at its cause with a test. Then the done line for the new views: the method note, the replication, a cross-check against a published figure, the decisions.

## The reader and the five cases

The reader: **a resource adequacy analyst at a utility in the Southeast**, preparing a note on how much help neighbors gave in recent storms and heat. Real places, real dates:

1. **Winter Storm Elliott, Tennessee, 23 and 24 December 2022** (`/events/elliott-2022#whole-country`): what Tennessee's demand, generation by source and net imports did against the baseline, and which neighbors sent it power.
2. **Winter Storm Elliott, the Carolinas beside Tennessee** (`/events/elliott-2022?region=car&b=ten#whole-country`): the same for the Carolinas, the two side by side, and the pair between them.
3. **Winter Storm Uri, Texas beside the Central region, 14 to 19 February 2021** (`/events/uri-2021?region=tex&b=cent#whole-country`): what crossed Texas's ties and what the Central region (the Southwest Power Pool's ground) sent or took.
4. **The September 2022 heat wave, California beside the Northwest** (`/events/caiso-heat-2022?region=cal&b=nw#whole-country`): California's net imports through 6 September against the baseline, and what the Northwest and the Southwest each sent.
5. **The January 2025 cold, the Mid-Atlantic beside the Southeast** (`/events/cold-2025?region=mida&b=se#whole-country`): each region's highest hour against the baseline at that hour, and the change in gas and coal generation.

For each case the questions are the same: can the reader get the answer without leaving the page, without a figure that contradicts another page, and without a word they would not know?

## State on 19 November 2026, on the real files (session 8470)

The data machine's page files landed on origin/main in commit af1962719 (built 19 November 2026, 12:04 UTC). Every part below was done on them.

| Part | State |
|---|---|
| The five cases read on the page | done: each page drawn whole with the site's own code (`drawPage` of `site/scripts/events-pages.mjs`, the warehouse's two tables from the main copy, the real page files), section "The five cases on the real files" below. Every case is answered on the page. Gaps 5 to 18 below; every fault fixed at its cause with a test (`site/scripts/test-events-regions.mjs`, 94 of 94). |
| The method note | done: `docs/methods/events.md`, "The whole country", with the count on the real files and the cross-check (session 8470). |
| The replication | done on the real files: `replication/events/replicate_regions.py`, **2,434 of 2,434** figures over the nine events (Uri 265, COVID-19 265, August 2020 heat 251, September 2022 heat 272, Elliott 272, 2023 ERCOT heat 272, January 2025 cold 272, June 2025 heat 283, January 2026 cold 282). No difference. |
| The Stata do-file for the five headline figures | written (`replication/events/replicate_regions.do`, rows from `replicate_regions.py --write-rows`, 68,042 rows). Stata is not installed on this machine, so it was not run. Its five steps were applied literally in Python to the same rows: every expected value in the do-file's header comes out to the last digit written, and each agrees with the figure the page draws. |
| The cross-check against a published figure | done for two of the five cases, section "The cross-check" below. Winter Storm Elliott (Tennessee) and the January 2025 cold (the Mid-Atlantic) have no public figure read: TVA's server refused the robots file (HTTP 403), `www.ferc.gov` and `www.nerc.com` refused on 19 November and were not asked, PJM's terms page was not found at either address on record, so no PJM page was read. |
| The decisions | confirmed: each choice of the section is a hover with its default and its source: the baseline (the file's own words and offsets; source the event's window in `docs/methods/events.md`), the 5 percent of "Reached" (default and "no publisher's threshold" on the index's hover), the regions drawn first (each page's reason; Elliott's from FERC and NERC as the page quotes them), the switch from hours to days (21 days: its default and source added in session 8470, gap 16). The page's own decisions block is not changed (the pin holds it). |

## State on 19 November 2026, before the files (session 8440)

| Part | State |
|---|---|
| The five cases read on the page | waits for the files: `site/data/regions/events/<event>.json` are not on origin/main (the data machine's chain 501, step B7). Nothing was waited on; the parts below that need no file are done. |
| The method note | done: `docs/methods/events.md`, "The whole country" (session 8410), with the replication's lines (session 8440). |
| The replication | written and tested on the fixture: `replication/events/replicate_regions.py`, 203 of 203; it runs on the site as it stands and says no file is there. The count on the real files waits for them. |
| The Stata do-file for the five headline figures | waits for the files: its expected values are real figures and none can be written before a file exists. |
| The cross-check against a published figure | waits for the files. What it will set beside the page: the federal inquiry's account of Winter Storm Elliott for the Tennessee Valley Authority and Duke (already linked on the page), ERCOT's and the Southwest Power Pool's own accounts of February 2021, CAISO's report on September 2022, and EIA's own regional totals on its Hourly Electric Grid Monitor. Each host's robots file and terms are read first; `www.ferc.gov` and `www.nerc.com` refused the reader on 19 November and are not asked again. |
| The decisions | on the page as hovers inside the section (each with its default and source): the baseline, the 5 percent of "reached", the regions drawn first, the 21 days that switch the charts to days. The page's own decisions block is not changed (the pin holds it). |

## Gaps found before any file (from the section as drawn on the fixture)

| # | Where | The gap | What was done |
|---:|---|---|---|
| 1 | "A region hour by hour", the charts | Hours are in UTC, as the file writes them; the reader's storm is in local time. The contract gives each region's time zone only in `index.json`. | Left as it is, said on the hover "How a figure here is formed". When `index.json` is on the site: draw the charts in the region's own time and name the zone under them (one change in `site/app/events/WholeCountry.tsx`, with a test). |
| 2 | "Each region across the event", the highest hour | The baseline beside it is the baseline at that same hour, not the baseline days' own highest hour, which is what the page's older sections use. A reader setting the two side by side sees two different percents for nearly the same ground. | Said on the head's hover. For Samuel's ruling in session 8410's report (the default: the file's hourly baseline). |
| 4 | The whole section, an accessibility read | The section drawn from the fixture was read with axe-core (WCAG 2.0 to 2.2, A and AA) in this machine's headless browser, as a file with no stylesheet (the site's CSS exists only in a build), so colour contrast was left out. 24 rules passed, the form's two lists and the three tables' heads among them. One rule broke, on 26 links: the size of a touch target (24 px, or enough room around it), on the region names in the two tables. Without the stylesheet a table row is one line of text high, so this says nothing yet about the built page, whose cells carry padding. | Not a fault that can be judged here. Row 417 of `docs/state/browser_reads_wanted.md`: on a build, at 390 px, the region names in the tables are each at least 24 px tall or stand 24 px apart. |
| 3 | The pair table | The file gives one flow a pair (the first side's report where held, else the second's); the two sides' reports and their gap are in the trade files, not in the event file. A reader cannot see here how far the two sides disagree during the storm. | Not a fault of the page: the event file does not hold it. One line for the data machine if the first read on real files shows a pair whose direction turns with the side read. Session 8470: see gap 15. |

## Gaps found on the real files (session 8470)

Rows 5 to 13 were found and fixed by the first run of session 8470 (commits 523f14cd4, 4529f06c1, 1fc0ee355), rows 14 to 18 by its resumed run. Each fix has its check in `site/scripts/test-events-regions.mjs` (fixture values made by a rule, the edit in the form the real files showed).

| # | Where | The gap | What was done |
|---:|---|---|---|
| 5 | `/events`, each card's "Reached N of 13 regions" | A region's percent rested on fewer hours than the window's with nothing said (the Southwest over Uri, 266 of 435), and a region left out for want of hours was not named. | Fixed: the hover gives the hours where fewer, and names a region not counted (523f14cd4). |
| 6 | The charts | An hour the file does not hold was drawn as a straight line across the gap. | Fixed: the line breaks there, by hour or by day (`lineGap`, 523f14cd4). |
| 7 | "When" of the highest hour | Gap 1's follow-up: with `index.json` on the site, the region's own time can be given. | Fixed for the table: each time gives the region's own hour on hover (Tennessee's peak: 2022-12-23 19:00 CST). The charts stay in UTC: gap 17. |
| 8 | Storage | "not held" in every region for every event before the 2025 heat, with no reason. | Fixed: the hover says EIA's six-month files carry no storage columns before July 2024 and the window or its baseline reaches back before then (523f14cd4). |
| 9 | The pair table, Canada and Mexico | The pairs with Canada or Mexico (seven over Elliott) stood with no word that neither files Form EIA-930. | Fixed: the hover says the flow is the US region's own report (523f14cd4). |
| 10 | The pair table | A pair whose every held hour is 0 MW (the Central region and the Southwest over Uri and over the January 2025 cold) read as "no net flow" with no word. | Fixed: the hover says every held hour is 0 MW, and whether the baseline's are (523f14cd4). |
| 11 | The pair table | The pairs of the two regions chosen were not marked, so a reader scanned 25 rows for them. | Fixed: marked as the region rows are (523f14cd4). |
| 12 | Generation by source | A region's sources summed over fewer hours than its net generation (the Southwest over Elliott, 114 of 267; the Carolinas over Uri, 146 of 435) did not add up to the net generation beside them, with nothing said. | Fixed: named under the table with their hours (4529f06c1). |
| 13 | Generation by source | Storage's few baseline hours (6 or fewer over the 2025 heat) marked every region's sources as short. | Fixed: storage counted apart and named on its own line (1fc0ee355). |
| 14 | Generation by source, case 3 | Over Uri the Northwest's row read "not held" from end to end beside a net generation of +725.7 GWh: the window holds all 435 hours of each source, its baseline (February 2020 and 2019) none. The hover said only "holds no natural gas ... with its baseline", so a reader would take EIA to hold no Northwest fuel data for February 2021. The same in COVID-19 (the Northwest) and the August 2020 heat (the Southwest). | Fixed: the region is named under the table ("held for 435 hours of the window and no hour of the baseline"), and each "not held" cell says which side holds how many hours (`heldApart`, `apartSources`, 50ac02500). |
| 15 | Net imports beside the pair table, cases 1 and 3 | A region's net imports (its own report of its total interchange) and its pairs in the pair table (each pair one side's report) do not agree for some regions: over Uri the Midwest's pairs read as its imports average +9,619 MW against net imports of +5,427 MW; the Mid-Atlantic -11,328 against -7,240; the Northwest -4,505 against -6,920 (over the 430 hours where all are held). Over Elliott, Tennessee's agree (+1,210 against +1,211). A reader adding the pairs gets a figure the table beside contradicts. | Fixed on the page: the net imports hover gives the pairs' sum beside the net imports and says why they need not agree (`pairSum`, b2240ea28). The cause cannot be told from the event file: it holds one side's report a pair. Data request below. |
| 16 | The decisions | The switch from hours to days (21 days) gave no default and no source. | Fixed: the hover gives both (6cd5dd09a). |
| 17 | The charts, cases 1 and 4 | The charts are in UTC: California's peak of 6 September 2022 (17:00 PDT) stands on the axis at 7 September 00:00. | Not changed: the chart component is shared by every page. For Samuel's ruling (default: UTC, said on every chart's hover). |
| 18 | The region drawn first, `/events/uri-2021` and `/events/ercot-heat-2023` | The hover said ERCOT is "among Texas's balancing authorities"; `index.json` gives ERCOT as the Texas region's only one. | Fixed: it says so (95ae3597c). |

## The five cases on the real files (session 8470)

Each page drawn whole at its address (`runs/c503/s8470/draw_cases.mjs`, kept out of git under `runs/`), read as the reader would, hovers included.

| Case | What the reader gets on the page | Gaps |
|---|---|---|
| 1. Elliott, Tennessee | Demand 6,075.7 GWh, +28.3 percent on the baseline, over 267 of 267 hours; highest hour 33,225 MW at 2022-12-24 01:00 UTC (19:00 CST on 23 December, on hover) against 19,830 MW in the baseline; net imports +1,211 MW against +107 MW; natural gas +677.3 GWh, coal +247.1 GWh. Neighbors: the Midwest sent Tennessee 3,407 MW on average (1,220 in the baseline); Tennessee sent the Southeast 1,327, the Mid-Atlantic 590 and the Carolinas 280. The pairs add to +1,210 MW, its net imports +1,211. | 7, 11, 15, 17 |
| 2. Elliott, the Carolinas beside Tennessee | The Carolinas +29.3 percent, highest hour 44,630 MW at 11:00 UTC on 24 December against 26,915; coal +1,802.6 GWh; the pair: Tennessee to the Carolinas, 280 MW on average and 74.7 GWh (56 MW in the baseline), its row marked. | 11 |
| 3. Uri, Texas beside the Central region | Texas +14.7 percent, highest hour 69,215 MW at 19:00 CST on 14 February; net imports +397 MW against -27: the Central region sent it 341 MW and Mexico 59. The Central region imported +956 MW against -1,310 in the baseline. | 5, 12, 14, 15 |
| 4. September 2022 heat, California beside the Northwest | California's net imports +8,993 MW against +8,251; the Northwest sent 5,715 MW (4,722 in the baseline), the Southwest 3,560 (3,496). The hours through 6 September are in each chart's table, in UTC. | 17 |
| 5. January 2025 cold, the Mid-Atlantic beside the Southeast | The Mid-Atlantic's highest hour 144,420 MW at 13:00 UTC on 22 January against 103,980; the Southeast's 46,490 against 26,418; natural gas and coal +1,387.0 and +1,962.0 GWh in the Mid-Atlantic (232 of 243 hours, named under the table), +366.3 and +909.0 in the Southeast. | 2, 8, 12 |

## The cross-check (session 8470)

Web reads, robots file and terms first, on 19 November 2026. No contact string was needed; no personal address was sent.

| Host | Robots (for the path read) | Terms (on automated reading) | Read or not |
|---|---|---|---|
| www.ercot.com | `/files/docs/` not disallowed (the file disallows `/content/news`, `/misapp` and others) | Terms of use (`/help/terms`, 20 July 2023): no word on robots or scraping; forbids use that harms the site's performance; public content may be reused unmodified with notices kept, raw data in analyses | read: two PDFs |
| www.caiso.com | `/Documents/` allowed (only `/resources/*` disallowed) | Privacy and terms of use (`/privacy-terms-of-use`): no word on robots or scraping; content from public records may be used with notices kept and the ISO credited | read: one PDF |
| www.eia.gov | `/todayinenergy/` not disallowed | Copyrights and reuse: public domain, cite EIA; no word on automated reading | searched; no figure for the two cases left found |
| www.spp.org | no robots file (HTTP 404) | Terms and conditions point to an acceptable use policy not read | not read beyond the terms |
| www.tva.com | robots file refused (HTTP 403) | not read | not read |
| www.pjm.com | no path of the read disallowed | terms page not found at `/about-pjm/legal` or `/about-pjm/legal.aspx` | not read |
| www.ferc.gov, www.nerc.com | refused on 19 November | | not asked |

| Figure | Ours (the page) | Theirs | Difference | Why they differ |
|---|---|---|---|---|
| Uri, Texas, the highest hour | 69,215 MW, the hour from 19:00 CST on 14 February (EIA region TEX, whose one balancing authority is ERCOT) | ERCOT, "Review of February 2021 Extreme Cold Weather Event" (Texas Legislature hearings, 25 February 2021, `ercot.com/files/docs/2021/03/03/Texas_Legislature_Hearings_2-25-2021.pdf`, slide 11): new winter peak 69,222 MW at 7:06 pm | -7 MW (-0.01 percent) | Theirs is a reading at one moment, ours EIA-930's hourly value as ERCOT reported it to EIA; the same hour. |
| Uri, Texas, the February peak as settled | 69,215 MW (the page's highest hour); 67,999 MW in the hour from 21:00 CST | ERCOT Monthly, March 2024 (`ercot.com/files/docs/2024/03/29/ERCOT-Monthly-March-2024.pdf`, page 1): February 2021 peak 69,812 MW in the 9-10 p.m. hour on 14 February, the highest net system hourly value of ERCOT's Demand and Energy report | -597 MW on the peak (-0.9 percent); -1,813 MW at their hour | Theirs is ERCOT's settled figure, revised after the event; EIA-930 holds the operating figure. Why the settled peak falls two hours later than both operating figures is not said in what was read. Not adjusted. |
| September 2022 heat, California, the highest hour | 63,622 MW, the hour from 17:00 PDT on 6 September (EIA region CAL: BANC, CISO, IID, LDWP, TIDC) | CAISO, "2022 Statistics" (`caiso.com/documents/2022statistics.pdf`, page 1): record peak 52,061 MW on 6 September at 4:57 p.m. | +11,561 MW | Not the same ground: EIA's California region adds four other balancing authorities to CAISO (the page's hover says a region is not a grid); theirs is a moment, ours an hour. The hour is the same. The file holds no figure for CAISO alone. |
| Elliott, Tennessee; January 2025 cold, the Mid-Atlantic | 33,225 MW; 144,420 MW | none read | | No public figure to stand against: TVA refused, FERC and NERC refused, PJM's terms not found. |

No figure on the page was adjusted.

## Data request (session 8470)

- The event files hold one report a pair (the first side's where held). Gap 15 shows a region's pairs and its net imports disagreeing by thousands of MW for the Midwest, the Mid-Atlantic and the Northwest over every event. Requested of the data machine: each pair's two reports in the event file (`flow_mw_a`, `flow_mw_b` beside `flow_mw`), so the page can say which side reports what. Handed to the chain's main session for `docs/state/data_requests_done_line.md`.
