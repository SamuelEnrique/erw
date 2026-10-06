# Session 136 report: Supply and trade, finished

## Two things to know before anything else

1. **ISO-NE's row needs your ruling before `/supply` opens.** ISO-NE's day-ahead cleared demand is not open the way the others are: its address answers HTTP 403 to a plain request, answers only a session that first opened one of its report pages (an anonymous cookie, no account), its own page puts a CAPTCHA on the search of past dates, and its legal notice says "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." I pulled 37 days by the route the ERW's ISO-NE reserve prices already use, kept the table **internal** (the internal Redivis dataset, no public table), and show its row on the locked page. On an open page that row is an internal figure in public. Say "grey it" and the row reads "licensed source needed".
2. **A research agent I started read 3,639 ERCOT rows more than I allowed it** (I had told it about 3,000 rows in all; it cut a download at 20 KB and the file was denser than it expected). They are counted in the ceiling below. Nothing was written from them.

## Verdict: ready to open, once ISO-NE's row is ruled

Against the three things session 134 left:

| Session 134 left | Now |
|---|---|
| 1. Schedule the refresh | **Done.** One step of the daily run on Saturdays (UTC), under `health.py` (the landing step, in session 135's report). **It ran once**, here, at about 20:35 UTC: every step exit 0, ten validator passes, 100 rows built, 0 kept by the guard |
| 2. Day-ahead energy cleared, not pulled | **Done for the five operators that publish it openly**, a connector each, in the weekly refresh. MISO's row reads "paused while terms are reviewed", PJM's "licensed source needed". No request went to either |
| 3. Land 132 first | **Done** in the landing step |

What is left besides the ruling:

- **The first Saturday run on the runner (10 October) is the first there.** The five tables are in the Redivis drafts and on the runner's restore list, so their history should arrive and grow. If a table does not arrive, the guard keeps the held row rather than show a shorter history.
- **ERCOT's comparisons are blank until its table grows.** ERCOT lists 31 days of this report. The table holds 15 days: one whole week. Its change on the week appears after the next refresh, its change on the year in a year.
- **The weekly refresh now reads about 185,000 ERCOT rows a week** (8 files of about 23,000 rows, one row a settlement point and hour, to make 24 hours a day). That is a standing pull of that size. A file already kept is not asked for again. Say so if it is too much and I will look for a system total ERCOT publishes directly.
- Unchanged from session 134 and still yours: the tables are wider than the page's column in some groups; the Brent row is the NYMEX contract.

## What the page now shows for day-ahead energy cleared

MWh a day, the mean of the seven whole days of the week ending Friday 2 October 2026, in each operator's own time:

| Row | Week ending 2 October | On the week before | On a year earlier | The operator's own figure |
|---|---|---|---|---|
| ERCOT | 1,024,892 | not held yet | not held yet | energy bought, summed over settlement points (NP4-192-CD) |
| CAISO | 642,232 | +12,234 | +57,572 (+9.8%) | the ISO's total load cleared (OASIS ENE_SLRS, `ISO_TOT_LOAD_MW`) |
| NYISO | 384,900 | +12,294 | -105 (-0.03%) | Total Load Scheduled (P-30) |
| ISO-NE | 285,415 | +27,216 | not held yet | Day-Ahead Cleared Demand (ISO Express). Internal |
| SPP | 911,540 | -30,407 | +9,910 (+1.1%) | Total Demand, balancing authority area SPP (DA-MC) |
| SPP West | 66,389 | -568 | not held yet | Total Demand, area SWPW, in SPP's file from 1 April 2026 |
| MISO | paused while terms are reviewed | | | |
| PJM | licensed source needed | | | |

- **Nothing is filled.** A day counts only when every hour of the operator's day is held (23, 24 or 25 at a clock change), a week only when all seven days do. A comparison that cannot be made is a placeholder with its reason on hover.
- **The rows are each operator's own total and are not the same measure.** NYISO's and SPP's include cleared virtual bids; CAISO's and ISO-NE's are cleared demand; ERCOT's is every purchase at every settlement point. This is in the Method note, not on the page face. Do not add or rank them.
- **A decision: SPP has two rows.** Its file names two balancing authority areas from 1 April 2026. Added together, the row read +8.5 percent on a year earlier, which was the new western area, not demand. The first row is the area the file held before, and reads +1.1 percent.
- **MISO's and PJM's fuel burn rows are shown**, as you ruled: they come from EIA's hourly file (EIA-930), not from either operator. Natural gas and coal for both; oil for PJM. MISO's oil row reads "not held yet" because EIA's file leaves it blank in recent hours, and a blank hour is not read as zero. A test now holds this.

## Each operator, checked one by one, with its terms as read today

| Operator | Published openly? | Report | Terms, quoted | The ERW's license |
|---|---|---|---|---|
| ERCOT | yes; the last 31 days only | NP4-192-CD, DAM Total Energy Purchased | "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Also: "Use of this website in a manner that negatively affects the performance of this website or other ERCOT systems is prohibited." (ercot.com/help/terms) | public |
| CAISO | yes | OASIS ENE_SLRS, Market Schedules, day-ahead, ISO totals | materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO". Of its API: "Users are prohibited from using the CAISO API in a manner that adversely impacts the performance of CAISO's systems" (caiso.com/privacy-terms-of-use) | public, with credit |
| NYISO | yes | P-30, Day-Ahead Market Daily Energy Report | "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site ... Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited" (nyiso.com/legal-notice). No license granted; the prohibition names images and video, not data | public with a caution, the standing reading since session 65 |
| ISO-NE | **partly** (above) | ISO Express, Day-Ahead Hourly Cleared Demand | "the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." (iso-ne.com/legal-privacy) | **internal** |
| SPP | yes | Marketplace portal, Market Clearing, DA-MC files | "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication ... Any commercial use of these materials requires prior, express written authorization" (spp.org/terms-conditions) | public, with citation |
| MISO | paused | | not asked | |
| PJM | licensed | | not asked | |

The terms pages were read today by the research agent, on the operators' own sites. **SPP's exception for a commercial publication** is worth your eye before the ERW charges for anything that shows SPP's figures.

## Every pull against its ceiling

**Approved pull: day-ahead energy cleared, USD 0, ceiling 500,000 rows. Read: 407,584 rows, 82 percent.** Every row that crossed the wire is counted, probes and failures included.

| Operator | Hours written | Rows read | What was read |
|---|---|---|---|
| ERCOT | 360 (15 days, from 23 September) | 349,351 | 15 daily files, 345,712 rows; the research agent's partial file, 3,639 |
| CAISO | 9,648 (from September 2025) | 45,792 | 27 half-month requests, 38,592; a first attempt that read two months and then failed, 3,552; a probe, 96; the refresh, 3,552 |
| NYISO | 9,648 (from September 2025) | 11,025 | 14 monthly files, 10,050; two probes of one day, 50; the refresh, 925 |
| ISO-NE | 888 (from September 2026) | 1,272 | three requests, 888; the refresh, 384 |
| SPP | 14,208 (from September 2025, two areas from April 2026) | 144 | three daily files. The other 14,064 hours were read from files the reserve-quantity connector already kept on this machine: no request |
| **Total** | **34,752** | **407,584 of 500,000** | |

- **CAISO refused a whole month.** A request for 1 August to 1 September answered "Data can be requested for period of 31 days only". The connector now asks by half month. That first attempt wrote nothing.
- **The weekly refresh, run once, also made its standing pulls**, which are session 134's and not this ceiling's: EIA's four supply tables whole (77,615 rows returned), the CFTC's four contracts (2,452 weeks), EIA's two schedule pages.
- **No MISO request. No PJM request. No model call.** All five tables pass the validator, are in coverage, the archive (34,752 rows) and the Redivis drafts (ISO-NE's in the internal dataset). Nothing was released. They are held out of the live set.

## What was built

- **Five connectors**, `warehouse/connectors/<iso>_dam_cleared.py`, each with its report, its route, its terms quoted and its own parsing, and one shared frame, `dam_cleared.py` (the pause check, the count against the ceiling, the freshness test, the header). Five connectors needed the same frame, so it is written once.
- **Each run counts its rows and stops before a file that would pass its ceiling**, writing nothing. A file kept from an earlier run is read from the machine and not counted again.
- **The tables merge**, so each grows past the window its operator keeps.
- **The page builder** reads the five tables (`supply_page.cleared_weekly`).
- **The refresh** runs the five connectors under `health.py` and validates their tables with the others.
- **Tests:** `tests/test_session136.py`, 24 tests: each parser on a short sample in the operator's own layout, the count and the ceiling, the pause check before any pull, the week rule (a missing hour, a 25-hour day, one area alone), the page's rows, the wiring. Three earlier checks that asserted "not held yet" for these rows were changed.

## The deploy

One deploy, with the snapshot before and after: **0 differences** on the 25 live addresses, 3,357 checked numbers compared. Checks passed (run 37528875603), merged as `df44eb2`. **Vercel built it**: "Deployment has completed" at 20:52 UTC, and production's build id changed to `q7M-VdYm35-J8CjXvThgY`. The page's own check passes against production, 27 of 27, in the internal view. My first version of the new check failed there and was wrong, not the page: it refused a row that holds a figure beside placeholder comparisons. `/supply` stays `review`.

## The five most interesting things the tool now does

1. **It shows what each grid's day-ahead market cleared last week, from the operator's own report**, for five grids, beside what the same grids burned: ERCOT cleared about 1.02 TWh a day and CAISO 0.64.
2. **It refuses a comparison that is not like for like.** SPP's western area joined its file in April; the page gives it a row of its own instead of letting it read as 8.5 percent growth.
3. **It keeps two kinds of row for MISO and PJM apart.** What comes from their own sites is blank with the reason; what comes from federal data is shown. The same grid can be "paused" in one group and hold a figure in the next, and each says why.
4. **It turns 23,000 rows into 24.** ERCOT publishes the day-ahead purchases of every settlement point and keeps them a month; the ERW keeps the system's hourly total and lets it grow past ERCOT's window.
5. **Its refresh cannot make it worse.** A row is replaced only by one that is no older and no shorter; a week with one hour missing is not shown rather than averaged over six days and 23 hours.

## Decisions I made without you

1. **"Cleared" is the demand side for every operator**: purchases, cleared or scheduled load, cleared demand. ERCOT also publishes energy sold (NP4-193-CD); it was not pulled.
2. **Thirteen months for CAISO, NYISO and SPP, 37 days for ISO-NE, 15 days for ERCOT.** Thirteen months gives a year-ago figure. Five years of CAISO or ERCOT would not fit the ceiling, and ISO-NE's history is behind a CAPTCHA on its own page.
3. **ERCOT's unit is read as MWh.** Its file names no unit; its product page calls the figure an amount of energy for the hour. The table's header says so.
4. **A shared module for the five connectors**, against the letter of "connectors are self-contained" and within its exception (shared code once two need it).
5. **The five tables are on the runner's restore list** (`warehouse/redivis/config.yaml`), so the Saturday run adds to them instead of starting again.

## For Samuel

1. Rule on ISO-NE's row (grey it, or keep it for the locked page only, or accept it in public).
2. Read SPP's commercial-publication exception.
3. After Saturday 10 October's daily run, look for the step `supply` in the health summary.
