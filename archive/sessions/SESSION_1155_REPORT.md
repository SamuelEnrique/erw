# Session 1155 report: the CAISO alerts, tied in

23 October 2026, from about 20:00 UTC, on samueloldlaptop (the code machine, the old laptop), the sixth session of `queue/done/077-day-23-october-code-grid-tool.md`, beside session 1156 and chain 076. Branch `wip/1155-grid`, cut from `wip/c077-land2` (sessions 1150 to 1154 merged with main), worktree `C:\Users\lossa\Documents\erw-1155`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher (Supabase's REST API read lightly with the anon key, as the brief allows).

## Read these first

- **The CAISO Mix tab opens on CAISO's alert state**, `data-grid-panel="grid_caisoalert_caiso"`, `id="caiso-alerts"`, before the Now blocks (`site/components/grid/CaisoAlertState.tsx`, `site/lib/caisoAlerts.ts`). On the live set today it reads: "Today, 2026-10-23 (Pacific), is not held yet: the table holds CAISO's notices to 2026-10-08, the newest day in the report as last read, so whether an alert is in force today is not said here. The last day with an Energy Emergency Alert or a Flex Alert in force: 2024-07-24 (EEA Watch, CAISO Grid). The last Flex Alert: 2022-09-09. Days with one in 2026, as held: 0." Then "Not alerts, named apart": restricted maintenance, last 2026-10-08 (CAISO Grid), 6 days in 2026; a transmission emergency, last 2025-04-30 (Northern CA Region). Then the link to `/grid/caiso/alerts` with one line of what it holds, and links to the strip and to Reliability.
- **Every date and count is a key:** `awe|last|<group>|<day>` (the newest Pacific day on or before the day with a notice of the group, compared as text) and `awe|ndays|<group>|<from>|<to>` (distinct days). Groups: `any`, `signal` (EEA Watch, EEA 1 to 3, Flex Alert, and the pre-May 2022 Alert, Warning, stages: the scarcity table's `own_signal` set), `eea`, `flex_alert`, `rmo`, `transmission_emergency`. One new sub-form of session 58's `awe` family: check-values reads every row of `caiso_grid_emergencies` once (1,906 rows) and recomputes each key with the page's own function (`aweValue`); `awe|days|...` is unchanged. The method note names them (`check-methods.mjs` names all eight keys of the panel).
- **"No alert today" is never claimed past the table:** the table holds the report's notices to 2026-10-08 (its newest rows are restricted maintenance, not alerts). A day after the newest notice is said "not held yet", with the newest notice keyed beside it. The report's revision date itself (9 October 2026) is only in the table's CSV header, not in the live set, so the page gives the newest notice day, not the revision date.
- **There is no other notices table for CAISO**: `caiso_grid_emergencies` is the only one in the live set (and `caiso_reliability_daily`'s `notices_<type>` are derived from it). Searched `site/lib/`, the catalogue row and `live_set.yaml` by name.
- **The scarcity strip (CAISO) marks alert days on its day axis:** a triangle under each day with an EEA or a Flex Alert that Pacific day (`HeatChart` gained an optional `colMarks`, off by default, so no other chart moves), each cell's hover naming the day's notices, and a line under the strip with the keyed counts. The strip's window, 1 to 30 September 2026, holds no alert day (0, keyed), so nothing is marked today; restricted maintenance on 9 and 10 September is named and not marked (2, keyed).
- **The mix chart:** CAISO's hourly mix is withheld by the session 118 ruling (`CaisoMixWithheld`) and stays undrawn, so it has nothing to mark. The monthly view (`mixp=month`) marks a month that holds an alert day (a dashed line, the days in its name) and keys the count; its 24 months today (September 2024 to September 2026) hold none (0, keyed), so nothing is marked. The code marks one when a month holds one (tested on August and September 2022).
- **The grid picker's CAISO context line was not added:** the picker sits above every tab, and a line there would add the notices read to the Network, Clean and Gravity tabs; the state line stands first on the Mix tab, which the picker opens. Recorded below.
- **`/grid/caiso/alerts`:** one line under its breadcrumb, linking `/grid?grid=caiso#caiso-alerts` and `/grid?grid=caiso#scarcity`. Nothing else on it changed (no key added or removed).

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=caiso`. First block: "CAISO's alerts: today". Read the three paragraphs; hover a dotted date or count: its table and rule in one line.
3. Press **The Flex Alert scorecard**: `/grid/caiso/alerts`. Under the breadcrumb, the new line; press **whether an alert is in force today**: back to the block. Back on the scorecard, press **the alert days on the scarcity strip**.
4. On `https://erw-flame.vercel.app/grid?grid=caiso#scarcity`: under the strip, the triangle's line ("0 days of these 30", restricted maintenance "2 days (2026-09-09, 2026-09-10)"). No triangle is drawn this month. Hover a cell: the tip is as session 1154 left it (an alert day would add "CAISO's notices that Pacific day").
5. Open `https://erw-flame.vercel.app/grid?grid=caiso&mixp=month#hourly`: under the monthly table, "Days with an Energy Emergency Alert or a Flex Alert in force, 2024-09-01 to 2026-09-30 (caiso_grid_emergencies): 0, so no month of the chart is marked."
6. View source, search `grid_caisoalert_caiso` and `awe|last|`.
7. Screenshots: not taken, no build (see Checks).

## Checks

- Precheck for session 1155: run by the orchestrator, exit 0.
- `npm ci` in `site/`: exit 0. `npm run content`: exit 0. `npx next typegen`: exit 0. `npx tsc --noEmit -p .`: exit 0.
- `node scripts/test-caiso-alerts.mjs` (new, 12 tests on the committed fixture): exit 0, 12 of 12.
- `node scripts/test-scarcity-strip.mjs`: exit 0. `node scripts/test-grid-keys.mjs`: exit 0. `node scripts/test-mix-hourly.mjs`: exit 0. `node --import ./scripts/alias-register.mjs scripts/test-mix.mjs`: exit 0. `node --import ./scripts/alias-register.mjs scripts/test-session502.mjs`: exit 0.
- `node scripts/check-methods.mjs` (the recorded keys): exit 0, 553 of 553 figures named. The eight new keys checked against the note by `figures()` and `named()`: all named.
- `python -m unittest` on `tests.test_session1152`, `1153`, `1154`, `1157`, `118`, `133`, `144_page`, `154_audit`, `168_mix`, `168_network`, `236`, `237`, `241a`, `241b`, `241c`, `299`, `317`, `318`, `328`, `331`, `351`, `370`, `401`, `412`, `416`, `473`, `502`, `533`, `538`, `54`, `58`, `583`, `584`, `588` (every test that reads the Grid page, the alerts page, `Reliability.tsx`, the scarcity panel, the mix components or `svgchart.tsx`): exit 0, 451 tests, 6 skipped. `tests.test_session1155` (new, 15 tests): exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0 at 20:20 UTC (0.49 s).
- `scripts/buildlock.py acquire 1155-grid --wait-min 20`: waited 20:20 to 20:40 UTC behind `s1126` (held since 19:28 UTC), `duty.py beat` every five minutes; given up, exit 1, the lock never held by this session (no release needed). **No build**, so no check-values run and no screenshots: the keys are proved on the fixture by the node test, which recomputes each as check-values does.
- Supabase reads (anon key, light): `caiso_grid_emergencies` (the newest 12 notices, the newest 12 alerts, every notice since 2022-01-01 for the fixture: 123 rows), its `catalogue` row (1,906 rows, to 2026-10-08), `generation_mix_hourly_profile` months for `iso:caiso` (2024-06 to 2026-09, December 2025 not written).

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1155-grid`.

## To finish

- Land `wip/1155-grid` with the chain's combined landing (it stacks on `wip/c077-land2`): `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed. Expected: on `/grid?grid=caiso` (and the redirects that open it, `/grid/caiso`), the new first block and its keys; under CAISO's scarcity strip, one more line with two keys; on `/grid?grid=caiso&mixp=month`, one more line with one key; on `/grid/caiso/alerts`, one more line of links. Nothing else.
- At that landing, rewrite the floors of the Grid pages from a passing check-values run (`CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid node scripts/check-values.mjs <base>`): `/grid?grid=caiso` gains 7 keys (8 figures, the last EEA's key is computed but not drawn: 7 drawn when the last Flex Alert differs from the last alert day, as today), its scarcity address 2.
- Screenshots of the block, the strip's line and the monthly line at 1280 and 390, under `docs/brand/review-1155/`, from that build (or session 1158's).

## Decisions made without you

- **The state line stands first on CAISO's Mix tab**, above the Now blocks: a trader opening CAISO reads whether the grid is on alert before the latest hour. It moves the blocks below it down the page; no figure's value or key changes.
- **No line in the grid picker:** the picker is shared by the four tabs (`ToolPicker`), and a CAISO line there would read the 1,906 notices on every tab; the Mix tab, the picker's default, carries the line. Session 1158 or 1159 can add a static link there if the owner wants one.
- **"Today" is the Pacific day the page was drawn** (`renderTime()`, the page is cached up to an hour); the table covers a day when it holds a notice of that day or a later one. The key carries the day (`awe|last|signal|2026-10-23`), so check-values recomputes the same question whenever it runs.
- **A day is a key written as text** (`data-raw="2024-07-24"`, shown as written): check-values already compares a non-numeric truth as text (session 315's rule), so no change to its comparison was needed.
- **An alert is the scarcity table's own signal set** (EEA and Flex Alert, and the pre-2022 alerts and stages), so the strip's squares and its triangles mean the same notices, one by hour, one by day.
- **The strip marks the notice's Pacific day on the column of the same date** (the strip's days are standard-time days; in summer they share 23 hours), said in the line under the strip. The exact hours stay the own signal's squares.
- **The notices are read once per page:** the state line, the strip and the monthly view all call `gridNotices()` (lib/reliability.ts) with no bounds, the same request as the Reliability section, which Next's fetch dedupes; no new request reaches the database on the CAISO page.
- **The fixture** (`site/scripts/fixtures/caiso_alerts.json`): every notice from 2022-01-01, 123 real rows read once with the anon key on 23 October 2026; nothing made up.
- **`tests/test_session473.py` extended** with the new component (its one `check=`); no assertion removed.

## For Samuel's ruling

- The scorecard's line "CAISO's Grid Emergencies History Report runs to 2025-04-30" (`/grid/caiso/alerts`, "Limits") is stale since the report's revision of 9 October 2026 (notices to 2026-10-08, none an alert); left as it is, since this session was told to change nothing else on that page. Recommendation: "runs to 2026-10-08, with no alert after 2024".

## Files

- New: `site/lib/caisoAlerts.ts`, `site/components/grid/CaisoAlertState.tsx`, `site/scripts/test-caiso-alerts.mjs`, `site/scripts/fixtures/caiso_alerts.json`, `tests/test_session1155.py`, this report.
- Changed: `site/app/grid/page.tsx` (one import, the block), `site/components/grid/ScarcityPanel.tsx` (the alert days), `site/components/svgchart.tsx` (`HeatChart`'s optional `colMarks`), `site/components/grid/MixView.tsx` and `site/components/grid/MixFigures.tsx` (the monthly view's alert months), `site/app/grid/caiso/alerts/page.tsx` (one line of links), `site/scripts/check-values.mjs` (`awe|last`, `awe|ndays`), `docs/methods/california_reliability.md` (the keys; "On the Grid tool: the alert state"), `docs/methods/scarcity_hours_by_grid.md` (one bullet), `tests/test_session473.py`.
