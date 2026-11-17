# Session 7546 report: `/grid/caiso/alerts` read as its reader (chain 304, part B form, samueloldlaptop, 16 November 2026)

Branch `wip/7532-caiso-alerts` (the tool's own, after its done line, session 7532), worktree `C:\Users\lossa\Documents\erw-7532`.
The read: [`docs/reviews/caiso-alerts-read-2026-11-16.md`](../../docs/reviews/caiso-alerts-read-2026-11-16.md).

## What was done

- **The reader:** a CAISO or utility demand-response analyst, or a fund analyst valuing demand response. **Five cases:**
  2022-09-06 (EEA 3, the text alert), 2020-08-17 (Stage 2), 2022-09-06 hour by hour, how sure, and what 2022-09-06 was
  worth. The whole page drawn to HTML with its own function (no build on this machine).
- **14 rows:** 6 site, fixed with a test; 3 data machine; 3 browser; 2 rulings. License 0, key 0.
- **Site fixes, on `/grid/caiso/alerts`:** (1) a new caution sets the published figures for two evenings beside the
  page's rows: CAISO, CPUC and CEC's 4,655 MW for 2020-08-17 (day-ahead peak forecast 49,824 against the peak 45,169,
  Final Root Cause Analysis, Table 5.1) beside the model's highest hour that day, 45,349.58 MW; the EIA's 2,100 MW in
  five minutes on 2022-09-06 (against the hour-ahead forecast) beside the page's -1,452.00 MW; (2) every hour of the 38
  day charts carries a hover with served, model, band and predicted less served (456 hovers); (3) the sentence linking
  the two heat-wave pages says their day estimate is another measure (the heat, not an alert's cut); (4) the first
  caution adds the years ELRP (2021) and DSGS (2022) began and what ran in August 2020.
- **Site fixes on another tool's pages (the `/events` stack):** (5) `/events/caiso-heat-2020` said "The warehouse holds
  no weather or supply data to say more", untrue (its own estimates control for temperature; the scorecard models
  14 to 19 August): replaced by a link to the scorecard, the old words in a code comment; (6) `/events/caiso-heat-2022`
  links the scorecard in its paragraph "The peak". Both edits are a few lines away from `wip/7531-events-b`'s changes to
  the same two files (imports and the foot): they should merge without a conflict.
- **The replication** now rebuilds the 458 new figures: 1,092 figures, 929 rebuilt, 925 agree, the same 4 named, 0 fail,
  163 panel-only. `page_figures.json` and `page_figures.csv` redrawn on the same tables (the same retrieval stamps).
- **The cross-check** gains section 5: Table 5.1 of the Final Root Cause Analysis (read today, one request, robots read
  first) beside the scorecard's nine 2020 alert days. On 2020-08-17 the model's highest hour stands 4,474 MW under
  CAISO's day-ahead forecast: nearly all of CAISO's 4,655 MW is the forecast standing above what the day's weather
  predicts.
- **Files changed:** `site/app/grid/caiso/alerts/page.tsx`, `site/scripts/caiso-alerts-figures.mjs` (hover strips are
  not counted as alert-hour boxes; the hovers are kept), `replication/caiso_alerts/replicate.py`, `page_figures.json`,
  `page_figures.csv`, `docs/methods/caiso_alerts.md` (extended), `docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`
  (section 5 added). New: the read file, `site/scripts/test-caiso-alerts-read.mjs`. Other machine's stack touched:
  `site/app/events/caiso-heat-2020/page.tsx`, `site/app/events/caiso-heat-2022/page.tsx`.
- **Tests:** `test-caiso-alerts-read.mjs` 28 of 28 (the page drawn from the committed public rows; includes the check
  that nothing held is committed); `test-caiso-alerts-render.mjs` 30 of 30; pytest `test_session7532_caiso_alerts`,
  `47`, `58`, `60`, `118`, `142`, `147`, `158`, `160`, `241a`, `246`, `254`, `310`, `322`, `369`: 347 passed, 10 skipped
  by their own rules; `tsc` with the site's settings on the three page files, exit 0; `replicate.py` exit 0.

## What to review

- `https://erw-flame.vercel.app/grid/caiso/alerts` (in review: with the review cookie). Click 2022-09-06 in the ranked
  table; in its panel hover the 18:00 strip: "18:00 to 19:00: served 50,378 MW, model 49,006 (band 45,513 to 52,196),
  predicted less served -1,372, alert hour". Scroll to "What the estimate can and cannot say": the first point's new
  sentences on ELRP, DSGS and August 2020; the point "Published figures for these evenings are measured against a
  forecast, not against this model" with 45,349.58 and -1,452.00; the closing sentence on the event pages' measure.
- `https://erw-flame.vercel.app/events/caiso-heat-2020`: the paragraph "Not on the outage days" ends with the link to
  the scorecard. `https://erw-flame.vercel.app/events/caiso-heat-2022`: "The peak" ends with the link.

## Needs the key

Nothing.

## Decisions made without you

- The published figures go in the cautions as facts with their baselines, not in the ranked table: the table stays the
  scorecard's own.
- The hover is a native SVG title over a full-height strip of each hour (whole MW), not a new chart component.
- The 2020 event page's false sentence was replaced, not kept beside a correction: the page standard keeps every
  figure; this was a statement that the warehouse lacks data it holds. The words are kept in a code comment.
- The event pages' day estimates are named as another measure where the scorecard links them; no figure of theirs is
  drawn on the scorecard.

## For Samuel's ruling

- Read row 9: once a daily on-peak index (EIA, ICE) is held for 2018 to 2022, value those days at it? Default: no, an
  hour at its own day-ahead price or "no price".
- Read row 11 (part A's row 11 again): the clause "the size a statewide conservation call might plausibly have" is a
  view. Default: unchanged; the published figures now stand two sections below.

## Rows for the coordinator

**(a) Landing row 30.** The read moves its head: new head `<the commit of this report, given in the return>` on
`wip/7532-caiso-alerts`. One line to append to "## Row 30: what it holds":

- **Session 7546 (the read, `docs/reviews/caiso-alerts-read-2026-11-16.md`):** `/grid/caiso/alerts` gains a hover on
  each hour of the 38 day charts, a caution with the published figures for 2020-08-17 (CAISO, CPUC and CEC, Table 5.1)
  and 2022-09-06 (EIA) beside two checked numbers (`predicted_mw` 2020-08-17T23:00:00Z, `reduction_mw` 2022-09-06),
  the programs' years in the first caution, and the event pages' measure named; `/events/caiso-heat-2020` and
  `/events/caiso-heat-2022` link the scorecard (the 2020 page loses "The warehouse holds no weather or supply data to say
  more"). Tests: `site/scripts/test-caiso-alerts-read.mjs` 28 of 28, the render test 30 of 30, pytest 347 passed, `tsc`
  on the three pages exit 0, `replicate.py` 929 rebuilt, 925 agree, 4 named, 0 fail. `check-values` must find the two new
  keys on `/grid/caiso/alerts`. Snapshot: none on the 25 addresses; with the review cookie the three pages differ by
  those words and the hovers. Tables: none. After the landing: browser rows 226 to 228; data request rows 199 to 201.

**(b) Browser reads** (`docs/state/browser_reads_wanted.md`):

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 226 | 2026-11-16 | 7546 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts#d2022-09-06` | The panel 2022-09-06: hover, tap and keyboard on the strip of 18:00, and on two other hours, at 1280 and 390 px | A tip "18:00 to 19:00: served 50,378 MW, model 49,006 (band 45,513 to 52,196), predicted less served -1,372, alert hour"; the lines and boxes of the chart still visible; the strips do not darken the chart | wanted |
| 227 | 2026-11-16 | 7546 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts` | "What the estimate can and cannot say": the first point and the point "Published figures for these evenings ...", at 1280 and 390 px, on the live set | 45,349.58 and -1,452.00 as checked numbers; the links open CAISO's Final Root Cause Analysis and the EIA's Today in Energy of 28 September 2022; no sideways scroll | wanted |
| 228 | 2026-11-16 | 7546 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/events/caiso-heat-2020` and `https://erw-flame.vercel.app/events/caiso-heat-2022` | The paragraph "Not on the outage days" (2020) and "The peak" (2022), with the review cookie | Each ends with a sentence linking "The Flex Alert scorecard", which opens `/grid/caiso/alerts`; the 2020 page no longer says the warehouse holds no weather data | wanted |

**(c) Data requests** (`docs/state/data_requests_done_line.md`):

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 199 | 2026-11-16 | 7546 (chain 304, samueloldlaptop; branch `wip/7532-caiso-alerts`) | `flex_alert_effects` (`warehouse/derived/flex_alert_scorecard.py`) | Write each alert day's cut under the four other specifications (`minimal`, `base`, `base_prev24sq`, `base_cdh_dew`), with their 90 percent bounds, as P1D rows (for example `variant_<id>_reduction_mw`, `_lo`, `_hi`), from the refits the builder already makes; today only the pooled figure of each is written. Then a reader can see whether one day (2022-09-06, 2020-08-17) moves with the model, as the pooled figure does (-503.18 to +861.16 MW) | `docs/reviews/caiso-alerts-read-2026-11-16.md`, row 7 | requested |
| 200 | 2026-11-16 | 7546 (chain 304, samueloldlaptop; branch `wip/7532-caiso-alerts`) | `eia_ice_electricity_daily` | Extend the table back to 2018 from the EIA's yearly ICE wholesale electricity files (the same publisher and columns; SP15 and NP15 among the hubs as "Southern California" and "Northern California"): today it starts 2025-12-29, so no daily price is held for any alert day of 2018 to 2022. Robots and terms of eia.gov read first | `docs/reviews/caiso-alerts-read-2026-11-16.md`, row 8 | requested |
| 201 | 2026-11-16 | 7546 (chain 304, samueloldlaptop; branch `wip/7532-caiso-alerts`) | new: CAISO five-minute demand on the alert days | CAISO's Today's Outlook publishes five-minute demand by day; the warehouse holds that page's hourly fuel history only (`caiso_fuel_supply_history`). Pull the five-minute demand for the 39 alert days of 2018 to 2024 (the method's rule), after reading CAISO's robots file (it disallows `/resources/*` only) and terms, so the minutes after a text alert (2022-09-06) can be read | `docs/reviews/caiso-alerts-read-2026-11-16.md`, row 10 | requested |

**(d) Progress, part C of `docs/state/progress_c304.md`:**

`| /grid/caiso/alerts (read) | samueloldlaptop | done <head> on wip/7532-caiso-alerts (landing row 30): the reader a CAISO or utility demand-response analyst (or a fund analyst valuing demand response); five cases (2022-09-06 alert hours, 2020-08-17 against CAISO's own 4,655 MW, 2022-09-06 hour by hour, how sure, what 2022-09-06 was worth); rows: 14 (6 site fixed, 3 data machine, 3 browser, 2 rulings) | 7546 |`
