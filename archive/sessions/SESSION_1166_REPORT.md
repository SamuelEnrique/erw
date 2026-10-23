# Session 1166 report: the Clean tab and the Mix tab's last unkeyed figures

23 October 2026, from about 23:10 UTC, on samueloldlaptop (the old laptop), the third session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1166-grid`, cut from `wip/1165-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1166`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (a fixture of 96 rows, and two one-off probes below).

## Read these first

- **A license finding, not changed (ruling 1):** the Clean tab's "How clean, and when", table "The seven grids, <year>" (`components/mix/views.tsx` `CleanView`) draws ISO-NE's, MISO's and NYISO's `clean_energy_summary` figures, which `site/data/license_status.json` holds by grid since 21 October 2026; every other block of the view says "license needed" for them. Not moved (no default figure moves); those cells are left unkeyed, so no key carries a held figure.
- **Every figure session 1151 listed as unkeyed on the Mix tab now has a key**, its text unchanged, a one-line source in its tip:
  - "Yesterday" (`components/grid/Conditions.tsx`): the miss at the peak in MW `fmt|pm0|calc|diff|<D>|<F>` and in percent `fmt|f1|calc|diffpct|<D>|<F>`; the day's mean absolute miss `fmt|f1|fcerr|mape|eia930:<BA>|<from>|<to>` and its hours `fcerr|hours|...`; each degree day `fmt|f1|degday|<cdd|hdd>|nws:<station>|<day>`.
  - "Generation mix, as a table": each fuel's share `fmt|f1|calc|pct|series_sum~...~<the group's variables>~...|series_sum~...~net_generation_mw~...`.
  - "Hours held" (`components/grid/YourGrid.tsx`): `series_n|...` (session 1154's kind).
  - CAISO's "The table holds N notices, the latest on <day>" (`components/grid/Reliability.tsx`): `awe|rows|any`, `awe|newest|any`.
- **Five additions to check-values, none changing an existing key:**
  - `fmt|<form>|<key>`: a figure written in a form of the page's own; its value is the inner key's, and its text must be that recomputed value in the form, exactly (`site/scripts/check-format.mjs`: f1, n0, n1, n2, pm0, sn0, sn1).
  - `file|<data file>|<path>`: a figure of a committed file of `site/data/`, recomputed from the file in the repository (`site/scripts/check-file.mjs`); where the file is a build of a live-set row, a second line compares the two ("same" or "DIFF", counted apart, not a failure; ruling 4).
  - `fcerr|`, `degday|` (the arithmetic moved as it stood into `site/lib/gridYesterday.ts`, which the page and check-values both call); `awe|rows`, `awe|newest` (`lib/caisoAlerts.ts aweValue`); calc op `diffpct`.
- **The committed-file views keyed: their headline tables** (which and why below). On a server render for ERCOT and CAISO: 573 keys, every one recomputed from its file by the node test; 370 are builds of a live-set row, and all 370 equalled the table on 24 October (anon reads, 40 requests).
- **The database keys proven live without a build:** a one-off probe drew "Yesterday" for ERCOT and ISO-NE and the Reliability section through session 1160's tsx loader with the anon key and recomputed each new key by check-values' rule: 20 of 20 matched, value and text (CDD and HDD both, the minus sign both ways).
- **Hover:** every chart on these views already answers a hover with its value, unit and hour or period (list below); nothing needed a prop.

## Keyed and not keyed, by view

| View (where) | Keyed | Not keyed, and why |
|---|---|---|
| How clean, and when (the Clean tab) | "Carbon-free share and hours" (share, flat load, hours at 50, 75, 90 percent) for each grid not held; "The seven grids" (share, hours at half, 100 percent purchase, 20 percent moved: carbon and cost) for the four not held | held grids (ruling 1); "Months held" (text "11 of 12"); the purchase matrix, the cleanest hours by month (computed from the day arrays), moving a flat load by year (large tables) |
| How hard the system works (`mix=stress`) | the ramp and lowest net load table, every year (7 figures a year); "The seven grids" (5 shares) | the hours ("When"), the fuels in the tightest hours, the dark and calm stretches, "The longest" (words) |
| Availability by source (`mix=supply`) | the tightest hours by source, every year (nuclear keeps the NRC note first in its tip) | the mean, lowest and highest hour (computed from arrays); capacity chart |
| The average day (`mix=day`) | shares and MWh by source; the largest source's share, solar's and wind's shares, days held | solar and wind at their peak, MW and hour (computed) |
| Records (`mix=records`) | every record, since the first year and in the year (generation_mix_records and the mixplus file) | the hour of each (a time) |
| Wind and solar forecasts (`mix=forecast`) | the hours held; the month table's hours, mean actual, forecast, mean error, mean absolute error | the error as a share of the mean actual (a ratio the page computes) |
| Year after year (`mix=duck`), Since 2001 (`mix=history`) | none | every figure is computed from arrays (net load, peaks, shares, million MWh): needs a key kind of the page's rule |

## Hover (item 3)

- `components/svgchart.tsx CategoryChart` (the views' HourStack, Lines, Bars): the card names the hour ("14:00") or the year or month, then each series' value and unit. `HeatChart` (clean, forecast): "row, column: value unit". `TimeChart` (Yesterday's 7 days, the 30-day mix): time, each value and unit. `ShareBar` (the day's mix): value, MWh and share (a day's sum; the day is in its label).
- Not fixed, listed: the average day's card says "14:00" and the chart's label says "local hour"; the card itself does not say "local" (`notes` per hour could carry it).

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. Under "ERCOT: yesterday": the forecast line ("...MW; error +N MW (x.x% of demand)"), the mean miss ("x.x% over 24 hours") and the degree days under the chart are dotted; hover each: table, entity, variable, hour or day.
3. Same page, "Generation mix, as a table": every share is dotted; hover names the day's variables.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot` and scroll to the 30-day mix table: "Hours held" is dotted.
5. Open `https://erw-flame.vercel.app/grid?grid=caiso`, the Reliability section: "The table holds 1,906 notices, the latest on 2026-10-08", both dotted.
6. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`: "How clean, and when", the two tables' percents are dotted (MISO, ISO-NE, NYISO are not: ruling 1). Hover: `clean_energy_summary, iso:ercot: years.2025.carbon_free_share_pct (the committed file site/data/clean/ercot.json)`.
7. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=mix&mix=stress`, `...&mix=supply`, `...&mix=day`, `...&mix=records`, `...&mix=forecast`: the tables listed above are dotted.
8. View source, search `fmt|` and `file|`.
9. Screenshots: not taken, no build.

## Checks

- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-file-keys.mjs` (new): exit 0, 12 tests (forms, paths, table rows, rounding, the moved arithmetic on real rows, awe, every view drawn and every key recomputed, no held grid keyed).
- `node scripts/test-caiso-alerts.mjs`, `test-grid-balance.mjs`, `test-grid-keys.mjs`, `test-mix-hourly.mjs`, `test-scarcity-strip.mjs`, `test-check-values-run.mjs`, `test-check-values-slow.mjs`: exit 0 each.
- `node --check` on `check-values.mjs` and `check-methods.mjs`: exit 0.
- `python -m unittest`, one file at a time, the 89 test files that read a changed file (grep of `tests/` for each) and `tests.test_session1166` (new, 9 tests): first run 86 of 89 exit 0, `tests.test_session1155`, `1165`, `315` exit 1 (each pins a line of check-values or check-calc that I had rewritten); the code restructured so each pinned line stands as it was (no assertion changed), then all 90 exit 0.
- `tests/test_session473.py`: its count of `check=` extended for Conditions.tsx (3 to 11), YourGrid.tsx (17 to 18), views.tsx (0 to 1); no assertion removed.
- One-off probes (scratchpad, not committed): the database keys live, 20 of 20; the views' file keys against their tables for ERCOT and CAISO, 370 same, 0 DIFF, 203 file only.
- Every new figure named by the method notes: `check-methods.mjs`'s own `figures()` and `named()` over the views' keys and the new database keys against the two notes, 0 not named.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values run, no check-methods run against a page: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build; check-values on `/grid,/network` (new keys on every Mix tab, the Clean tabs and the mix views; expect "same" lines for the files, "file" lines for mix_forecast, mixplus and the mix years); the floors rewritten from a passing restricted run (`CHECK_VALUES_WRITE_FLOOR=1`); `check-methods.mjs --values <the run> --write`; screenshots at 1280 and 390 under `docs/brand/review-1166/` (the dotted figures and one tip each); the snapshots before and after, every difference listed (expected: no word or number moves; the figures above gain a dotted rule and a tip).
- If the views' other addresses are wanted in check-values' list (`/grid?grid=ercot&view=mix&mix=stress` and the rest are not read today), add them with floors at that landing.

## Decisions made without you

- A form in the key (`fmt|<form>|`) rather than a looser text rule: the text is recomputed exactly and no existing key's reading changes.
- The page's arithmetic for the forecast miss and the degree days moved, as it stood, into `lib/gridYesterday.ts` (the node test holds it to the expressions that stood in the page), so the page and check-values share one rule.
- `awe|newest|any` is the newest day of any row (no "as of" day): the section names the table's newest notice, whatever the day.
- A committed file against its table is a line of its own and a tally, not a failure (ruling 4): the files are rebuilt by hand, the tables by their jobs.
- The mix file's years are checked against the file alone: the profile table holds months only (anon read: no P1Y row); the clean file's years map to `year_<variable>`, P1Y.
- In the clean view's table of the seven grids, the held grids' cells are left unkeyed, as they were drawn (ruling 1).
- The headline tables were keyed, not every table (above); a later pass can take the large ones.
- The fixture `site/scripts/fixtures/grid_yesterday.json` is real rows (ERCOT's demand and forecast, KDFW's and KBOS's temperatures, 21 October 2026), read with the anon key.
- Pinned lines of check-values and check-calc (tests 1155, 1165, 315) were kept by adding branches beside them, not by changing the tests.

## For Samuel's ruling

1. The clean view's "The seven grids" draws ISO-NE, MISO and NYISO figures of `clean_energy_summary`, held by grid since 21 October. Recommendation: "license needed" in their cells, as every other block of the view.
2. "Generation mix, as a table" draws California's EIA-930 fuel shares of the day, which session 118 withholds in the same block's bar and in the hourly mix. Recommendation: the withheld words in CAISO's row.
3. "Yesterday" writes the miss in MW with a minus sign (U+2212) and its percent with a hyphen ("−1,117 MW (-1.8% of demand)"). Recommendation: the minus sign in both (the text would move).
4. Whether a "DIFF" between a committed file and its live-set table should fail check-values. Recommendation: not a failure, a line in the landing report.

## Files

- New: `site/lib/gridYesterday.ts`, `site/scripts/check-format.mjs`, `site/scripts/check-file.mjs`, `site/scripts/test-grid-file-keys.mjs`, `site/scripts/fixtures/grid_yesterday.json`, `tests/test_session1166.py`, this report.
- Changed: `site/components/grid/Conditions.tsx`, `site/components/grid/YourGrid.tsx`, `site/components/grid/Reliability.tsx`, `site/components/mix/views.tsx`, `site/lib/caisoAlerts.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-calc.mjs`, `site/scripts/check-methods.mjs`, `docs/methods/generation_mix_hourly.md`, `docs/methods/grid_stress.md` (each a "(chain 078, 24 October 2026)" section with its decisions), `tests/test_session473.py`.
