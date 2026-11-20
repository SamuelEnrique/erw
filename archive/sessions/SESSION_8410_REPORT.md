# Session 8410 report: the events pages for the whole country (chain 503, part B)

19 November 2026, samueloldlaptop (code role), unattended. Branch `wip/8410-events-regions`, from `origin/main` at `2bca0266c`. Model spend USD 0: no model call. Nothing landed, no table written, `site/lib/release.ts` not touched: every page stays in review.

## What was built

- **"The whole country" on each of the nine event pages** (`site/app/events/WholeCountry.tsx`, mounted under the event study and above the decisions block): EIA's thirteen regions of the lower 48 across the event against the baseline the data machine's file names.
  - **Each region across the event:** demand over the window (GWh) and its percent on the baseline; the highest hour, when it was, and the baseline at that hour; mean net imports and the baseline's; hours held.
  - **Generation by source, the event less the baseline:** thirteen regions by eight sources and net generation, GWh; each cell's hover gives the two sums and the hours.
  - **Power between regions, pair by pair:** which region sent and which took over the window, the mean MW and the GWh, and the same for the baseline. Nothing is summed across pairs.
  - **A region hour by hour:** Region A and Region B chosen from two lists (the address carries the choice, `?region=ten&b=car#whole-country`); for each: demand, generation by source and net imports, the event and the baseline, on the site's own charts (they answer the mouse).
  - The six regions the site never showed (the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest) are named, each with a hover saying so.
- **`/events`:** each event's card says how many regions it reached (demand over the window 5 percent or more from the baseline, above or below), names them, and gives the rule, its default and its source on hover.
- **The library** `site/lib/countryfiles.ts`: the contract's types, the reader of `site/data/regions/`, and the sums. It is written for parts C and D too.
- **The method note** `docs/methods/events.md`, a new section "The whole country (session 8410, 19 November 2026)".

## The file it waits for

- The data machine's `site/data/regions/events/<event>.json` (contract `docs/state/page_files_regions.md`, step B7 of chain 501) was **not on origin/main** when this session ran. Checked at the start and before the commit.
- Until a file is there the section reads "not built yet" and draws no figure; the card's line reads the same. Nothing was waited on.
- The section was coded against the contract with a fixture in its form (`site/scripts/regions-fixture.mjs`). Its values are made by a rule a test recomputes; they are not data, the file says so, and the site's reader refuses a fixture in the site's own folder.

## Add, never change: how it is held

- **The pin:** `site/scripts/test-events-pin.mjs` draws the ten pages with the site's own code on the public rows beside the replication, cuts out what this session added (it stands between marks), and compares the rest, byte for byte, with the page as origin/main drew it before the session (`site/scripts/pins/events-pages-8410.json`: a hash, the length and the count of checked figures of each page). 21 of 21 as a visitor's build draws the pages, 21 of 21 with the hold stood aside.
- **The section:** `site/scripts/test-events-regions.mjs`, 77 of 77: the sums against the fixture's rule; the thirteen rows; the six new regions; pair by pair; the choice from the address; held and not built; the whole pages with and without a file.
- **Python:** `tests/test_session8410_events_regions.py` (11 tests) runs both and holds the source rules. With `tests/test_session7531_events.py`: 26 passed. `tests/test_session241a.py, 319, 92, 7602_event_day_table, 308, 332`: all passed (17 skipped by their own rules).
- **Types:** `tsc` on `app/events/**` and `lib/countryfiles.ts`, exit 0.
- **Not done here:** no site build (this machine's memory does not hold one), no browser, no `check-values`, no `check-routes`. No screenshot is claimed.

## What to review

Each page needs the review cookie (every page is in review). Until the data machine's files land, each shows "The whole country: not built yet".

- `https://erw-flame.vercel.app/events/elliott-2022#whole-country`: once its file is there: the table "Each region across the event" with thirteen rows; Tennessee and the Carolinas highlighted and drawn first, side by side; choose "Southeast" as Region A and "None" as Region B and press Show: one column of three charts for the Southeast.
- `https://erw-flame.vercel.app/events/uri-2021#whole-country`: Texas drawn first; the pair table names which regions sent power to Texas and which took it.
- `https://erw-flame.vercel.app/events/covid-2020#whole-country`: the line at the foot of the section reads "Drawn by day" (the window is 92 days).
- `https://erw-flame.vercel.app/events`: under each card's headline, "Reached N of 13 regions:" and their names; hover the names for the rule and every region's percent.
- The same section on `https://erw-flame.vercel.app/events/caiso-heat-2020`, `/events/caiso-heat-2022`, `/events/ercot-heat-2023`, `/events/cold-2025`, `/events/east-heat-2025` and `/events/cold-2026`.

Browser reads wanted: rows 377 to 382 of `docs/state/browser_reads_wanted.md`. Landing: row 51 of `docs/state/landing_request_oldlaptop.md`.

## Needs the key

- Nothing.

## Decisions made without you

- **The event pages read their address now** (`searchParams`), so the region choice works without a script. A page that reads its address is drawn at each request, not once an hour. `/demand` and `/supply` already work this way.
- **The regions drawn first** are each page's own: Texas for the two ERCOT events; California for the two CAISO events and COVID-19; the Mid-Atlantic for the three events whose first grid is PJM; Tennessee and the Carolinas for Winter Storm Elliott (the page's own quote of FERC and NERC). Each default is said on hover.
- **A window longer than 21 days is drawn by UTC day** (COVID-19's 92 days would be about 26,000 points an hour by hour).
- **Hours are shown in UTC**, as the file writes them. The contract gives each region's time zone only in `index.json`, which is not built yet.
- **The baseline at a region's highest hour is the file's hourly baseline** (the mean of that hour at each offset). The older sections take each baseline day's own highest hour. The head's hover says the two are not the same comparison.
- **The new library is `site/lib/countryfiles.ts`.** `site/lib/regions.ts` already exists (session 18, the explorers' lists); I wrote over it in the worktree by mistake, saw it at once, restored it from git before any commit, and gave the new file its own name. Nothing of it reached a commit.
- **The decisions of the new section are hovers inside the section**, not new lines of the page's decisions block: a new line there would change the block the pin holds.

## For Samuel's ruling

- **"Reached": 5 percent.** A region is counted as reached when its demand over the window stood 5 percent or more from the baseline, above or below. No publisher's threshold stands behind the 5 percent; it is this session's default and the hover says so. Default taken: 5 percent. Other choices: another percent; the highest hour against the baseline in place of the window's energy.
- **EIA's regional figures for New England, New York and the Midwest on an event page.** The older sections of these pages are under the hold of 21 October (the table `event_window_daily` is "license needed" because it holds ISO-NE's, MISO's and NYISO's hub prices), and entry 71 of the ranked list still asks whether EIA's public figures that the hold blanks should be drawn. The new section reads other files, which the contract gives as public (EIA Form EIA-930, public domain), so it draws all thirteen regions, as `/demand` already draws the seven grids from EIA. Default taken: drawn, by the file's own license line and the status file. To hold them instead, put the region codes in `REGIONS_HELD` in `site/app/events/WholeCountry.tsx`: their cells are then drawn blank with "license needed" on hover (a test holds that this works).
