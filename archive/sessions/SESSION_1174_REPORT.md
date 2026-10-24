# Session 1174 report: ERCOT's notices, as CAISO's are

24 October 2026, from about 01:00 UTC, on samueloldlaptop (the code machine, the old laptop), the eleventh session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1174-grid`, cut from `wip/1173-grid`, worktree `C:\Users\lossa\Documents\erw-1174`. Code, tests and documents only (chain 078's brief: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher (Supabase's REST API read lightly with the anon key, as the brief allows).

## Read these first

- **ERCOT's Mix tab opens on ERCOT's notice state**, `data-grid-panel="grid_ercotnotice_ercot"`, `id="ercot-notices"`, after CAISO's line (which draws only for CAISO) and before the Now blocks (`site/components/grid/ErcotNoticeState.tsx`, `site/lib/ercotNotices.ts`, the read in `site/lib/gridErcotNotices.ts`). On the live set today it reads: "Today, 2026-10-23 (Central), is not held yet: the table holds ERCOT's notices to 2026-10-15, read from ERCOT's pages on 2026-10-19 (UTC), so whether a notice is in force today is not said here. The last day with a call on supply or demand: 2026-08-25 (OCN for extreme weather). Days with one in 2026, as held: 10." Then the last day of each kind: an EEA or rotating outages 2023-09-06 (EEA 2); a conservation appeal 2024-01-16; a Weather Watch 2026-01-27; an OCN for extreme weather 2026-08-25. Then "Not calls, named apart": last on 2026-10-15 (Advisory, a notice ended or cancelled), on 19 days in 2026. Then the links to the strip and to the monthly mix, and the source line crediting ERCOT with the method link (`/data/methods/ercot_grid_notices`).
- **The table checked first.** `ercot_grid_notices` (events, 178 rows, 2011-02-02 to 2026-10-15, every row's `retrieved_at` 2026-10-19T21:02:01Z) has its method note (`docs/methods/ercot_grid_notices.md`, session 322), is `public` in `site/data/license_status.json` and `coverage.csv` (ERCOT's terms, read 2), and is in the live set under `review_hold` (readable by the site, in no visitor count); its two sources are under `sources_hold`. `event_date` is the Central day the notice covers, stored as midnight UTC; `extra` holds `x_text`, `x_label`, `x_counts`, `x_region`, `x_issued_at` (UTC), `retrieved_at`.
- **A call is the method's own `x_counts` `yes`** (a system-wide call on supply or demand, what `grid_stress_days` counts): kinds `eea` (EEA 1 to 3, rotating outages), `conservation` (conservation appeals, Voluntary Conservation Notices), `watch` (Weather Watches, 2011's Power Watches), `ocn` (OCN for extreme weather); `other` is every row that does not count (control-room Advisories and Watches on its own tools, tests, statements, other updates, the Rio Grande Valley's notices), named apart and never marked.
- **A new key kind, `ercotn|`**, not CAISO's `awe|` (whose keys carry no table word and whose groups are CAISO's types): `ercotn|last|<group>|<day>`, `ercotn|ndays|<group>|<from>|<to>`, `ercotn|read` (the UTC day of the newest `retrieved_at`). Recomputed in `check-values.mjs` with the page's own function (`ercotnValue`) on every row, read once a run with the same three fields of `extra`; tested in `site/scripts/test-ercot-notices.mjs` (14 tests) on a fixture of every real row; named by the method note under `check-methods.mjs`'s own rules (the node test runs `figures()` and `named()` on every key of the three panels).
- **"None today" is never claimed past the table:** a day after the newest notice is "not held yet", with the newest notice and the day the ERW last read ERCOT's pages beside it. No schedule runs the ERCOT notices connector (searched every workflow, shell script, PowerShell registration and python file), so the read day is what tells a reader why a week is empty.
- **ERCOT's scarcity strip marks call days** (triangles under the day, `HeatChart`'s `colMarks` from 1155), each cell's hover naming the day's notices, with a keyed line under it. The window, 1 to 30 September 2026, holds no call day (0, keyed), so nothing is marked today; the Advisories of 15, 28 and 29 September are named, not marked (3, keyed).
- **ERCOT's monthly mix (`mixp=month`) marks the months with a call day** (a dashed line, the days in its name) and keys the count: the 24 months drawn (September 2024 to September 2026, December 2025 not built) hold 22 call days in four marked months: 2025-01, 2025-02, 2026-01, 2026-08.
- **One read a render:** the state line, the strip and the monthly view call `ercotNotices()` (React's `cache`), about 48 KB for 178 rows (three fields of `extra` by PostgREST's `->>`, not ERCOT's words, which no panel draws). It is in its own file so the Clean tab, which draws `lib/reliability.ts`, does not read it.
- **The tabs' table lines** (`lib/gridtables.ts`): the Mix and the Clean tab now name `ercot_grid_notices` (public), as `tests/test_session502.py` requires: the Clean tab draws `MixView.tsx`'s `MixClean`, whose file reads the notices for the Mix tab, exactly as it names `caiso_grid_emergencies`.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. First block: "ERCOT's notices: today". Read the paragraphs and the list of four kinds; hover a dotted date or count: its table and rule in one line.
3. Press **the scarcity strip**: under ERCOT's strip, the triangle's line ("0 days of these 30", the Advisories "3 days (2026-09-15, 2026-09-28, 2026-09-29)"). No triangle is drawn this month. Press **ERCOT's notices today**: back to the block.
4. Back on the block, press **the monthly mix**: `https://erw-flame.vercel.app/grid?grid=ercot&mixp=month#hourly`. Four dashed lines on the chart (January and February 2025, January and August 2026); hover one: its days. Under the table: "Days with a call on supply or demand in ERCOT's notices ..., 2024-09-01 to 2026-09-30 (ercot_grid_notices): 22; each month that holds one is marked on the chart (2025-01, 2025-02, 2026-01, 2026-08)."
5. Open `https://erw-flame.vercel.app/grid?grid=caiso`: CAISO's line, strip and monthly view as before; no ERCOT block.
6. View source of step 2, search `grid_ercotnotice_ercot` and `ercotn|`.
7. Screenshots: not taken, no build (chain 078's brief).

## Checks

- Precheck for session 1174: run by the orchestrator, exit 0.
- `node scripts/test-ercot-notices.mjs` (new): exit 0, 14 of 14.
- Node tests, one at a time: `test-caiso-alerts` 12 of 12, `test-scarcity-strip` 10 of 10, `test-grid-keys` 8, `test-mix-hourly` 10, `test-grid-390` 5, `test-grid-balance` 11, `test-check-revised` 12 of 12, each exit 0; through the junction with the alias loader `test-grid-addresses` (8 tests, 61 addresses), `test-session502` (11 of 11), and with the tsx loader `test-grid-file-keys` (14 of 14), each exit 0.
- `node scripts/check-methods.mjs` (the recorded keys): exit 0, 553 of 553 figures named. The new keys are not in the recorded file (no build); `test-ercot-notices.mjs` runs `figures()` and `named()` on every key of the three panels against `ercot_grid_notices.md`: all named.
- `python -m unittest`, one module at a time, on every test that reads a file changed here (the Grid page, `ScarcityPanel.tsx`, `MixView.tsx`, `MixFigures.tsx`, `lib/gridtables.ts`, the two method notes, the pack): `test_session1152`, `1153`, `1154`, `1155`, `1157`, `1158`, `1159`, `1160`, `1161`, `1162`, `1167`, `1170`, `1171`, `1172`, `1173`, `1174` (new), `118`, `133`, `168_mix`, `168_network`, `237`, `254`, `297`, `299`, `306`, `322`, `401`, `473`, `502`, `538`, `54`: each exit 0. And the 71 other modules that read `check-values.mjs`: each exit 0.
- `test_session502` first failed on the Clean tab's list (the walk finds `ercot_grid_notices` through `MixView.tsx`'s imports, as it finds `caiso_grid_emergencies`); fixed by naming it in the Clean list too, then exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir` (the main checkout's packages intact).
- Supabase reads (anon key, light): `events` for `ercot_grid_notices` (4 newest rows; all 178 rows whole once; all 178 with three fields of `extra`, the form the page and check-values use), `generation_mix_hourly_profile` months for `iso:ercot` (2024-08 to 2026-09, December 2025 not built), `scarcity_hours_by_grid`'s newest ERCOT hour (2026-10-01 05:00 UTC).
- No build, no check-values run, no screenshots (chain 078's brief).

## The landing

- None in this session: chain 078 is code only, and chain 077's landing B (`wip/1162-grid`) is not on main (its gate was stopped by a low-memory reap). This branch stacks on it and lands with it. Pushed: `wip/1174-grid`.

## To finish

- Land `wip/1174-grid` with the chain's combined landing: `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed. Expected: on `/grid?grid=ercot` (and the addresses that open it), the new first block and its keys; under ERCOT's scarcity strip one more line with two keys; on `/grid?grid=ercot&mixp=month`, four marks and one more line with one key; on the Mix and Clean tabs of every grid, `ercot_grid_notices` in the table line under the title (and in the Clean tab's source line, which lists the same tables). Nothing else.
- At that landing, rewrite the floors of the Grid pages from a passing check-values run: `/grid?grid=ercot` gains 12 keys today (10 in the block; 2 under the strip), its monthly address 1.
- Screenshots of the block, the strip's line and the monthly marks at 1280 and 390, under `docs/brand/review-1174/`, from that build.

## Decisions made without you

- **`ercotn|`, a key kind of its own**, not `awe|` pointed at ERCOT's table: `awe|` carries no table word, its groups are CAISO's types, and session 1155's tests pin its recomputation to `lib/caisoAlerts.ts`. ERCOT's groups need `x_counts` and `x_region`.
- **A call is the method's own `x_counts`**, so the panel, the strip and the months mean the days `grid_stress_days` counts for ERCOT; the OCN for extreme weather is a kind of its own beside "an EEA, a conservation appeal or a watch", since the table counts it and it is ERCOT's latest call.
- **The read day is said** (`ercotn|read`), beyond what CAISO's line says: every run rewrites each row's `retrieved_at`, so its newest is the last read. The page does not claim the days between the newest notice and the read were quiet.
- **"Today" is the Central day the page was drawn** (`renderTime()`); the key carries the day, so check-values recomputes the same question whenever it runs.
- **The notice's Central day is set on the strip's column of the same date** (the strip's days are Central standard time days), as CAISO's Pacific days are; said in the line under the strip.
- **The hourly 7-day mix is not marked**: the task named the strip and the monthly mix; the hourly chart's marks are its peak hour.
- **The fixture** (`site/scripts/fixtures/ercot_notices.json`): all 178 real rows read once with the anon key on 24 October 2026, without `x_text` (ERCOT's words are not copied, so its terms' "not modified" is not in play).
- **`sources_hold` and `review_hold` left as they are**: every page is in review; when the Grid tool opens, `ercot:news_releases` and `ercot:operations_messages` come off `sources_hold` with it (written in the method note).
- **In `ScarcityPanel.tsx`, CAISO's line reads its days as `caiso`** (renamed from `alerts` inside the line only) so that `colMarks={alerts?.cols}` (pinned by `tests/test_session1155.py`) now carries CAISO's or ERCOT's marks; CAISO's output is unchanged.
- **The Grid pack's blind spot 16** says ERCOT's state is drawn on this branch (`docs/reviews/packs/grid.md`); its numbering is unchanged.
- **`tests/test_session473.py` extended** with the new component (its one `check=`); no assertion removed.

## For Samuel's ruling

- Whether the ERCOT notices connector should run on a schedule (it is run by hand; the read of 19 October 2026 is the newest, so ERCOT's state line says "not held yet" for every day since 15 October). A daily run on the data machine would keep the operations messages' six-month window from being lost.

## Files

- New: `site/lib/ercotNotices.ts`, `site/lib/gridErcotNotices.ts`, `site/components/grid/ErcotNoticeState.tsx`, `site/scripts/test-ercot-notices.mjs`, `site/scripts/fixtures/ercot_notices.json`, `tests/test_session1174.py`, this report.
- Changed: `site/app/grid/page.tsx` (one import, the block), `site/components/grid/ScarcityPanel.tsx` (the call days), `site/components/grid/MixView.tsx` and `site/components/grid/MixFigures.tsx` (the monthly view's call months), `site/lib/gridtables.ts` (the table in the Mix and Clean lines), `site/scripts/check-values.mjs` (`ercotn|`), `docs/methods/ercot_grid_notices.md` (section 6, its keys and decisions), `docs/methods/scarcity_hours_by_grid.md` (one bullet), `docs/reviews/packs/grid.md` (blind spot 16), `tests/test_session473.py`.
