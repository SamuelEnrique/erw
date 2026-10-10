# Session 167: the project map, one page (agent report)

**No table write is needed, so there is no early hand-over to run under the lock.** EIA's raw status code has stood
beside the folded `status` since session 8 (`eia_status`, `eia_status_label` in both EIA-860M tables, filled on every
row). The connector is unchanged. `runs/session167/handover.sh` only rebuilds the page's file from the main copy's
tables after session 166's writes and runs the tests.

Branch `wip/167-map` in `C:\Users\lossa\Documents\erw-142`. Last commit `1a77521`. Nothing pushed, merged or locked.

## Read these first

- `/map` is one page: version 2's layout and data, plus version 1's card, state filter both ways, four kinds, "By technology" and Reset. Every list is a multi-select with "Select all" and "Clear", and the address keeps the choice. `/map/v2` redirects to `/map`, carrying its query.
- The page reads its own file, `site/data/map.json`, written by `warehouse/derived/project_map.py` from four tables (`--in-dir` added). `map_v2.json` is still written, its content unchanged, because `/resources` reads it.
- **MISO's queue positions are left out of the file.** That is 1,733 rows that are not withdrawn. The page reads "MISO queue positions: paused while terms are reviewed", greyed, with a hover. This follows the one switch list, `QUEUE_GRIDS` in `site/lib/resources.ts` (session 159). Version 1 drew them, so this is the only data dropped (owner rule 9).
- **The unit card reads its fields from the page's own file, never from Supabase.** They are served once, at the first click on a unit, by `/map/card`, a route built with the site behind the same release gate. Weights (gzip): 994 KB with the fields in the page, 646 KB now.
- All checks pass: browser check 91 of 91, routes, tsc, eslint, build, and the tests. Exit codes are below.

## What to review

URL: https://erw-flame.vercel.app/map (in review: open it in the internal view)

1. Open it. You should see the sentence "In every grid and every state, the map holds 30,921 generating units of EIA's inventory of 2026-08, 1,706,668 MW; 3,737 queue positions, 762,726 MW requested; and 255 datacenters, 18,274 MW stated at 19 of them". Below it, the totals by status in three groups: EIA's 8 statuses, the queue's 4 and the datacenters' 7.
2. Open "Status". You should see EIA's own statuses in plain words, P to TS (OT has no rows this month, so it shows no tile), under "Generating units". Below them are "Queue positions" and "Datacenters".
3. Click "Clear" under Grid, then tick ERCOT and CAISO. The address becomes `?grid=ercot,caiso` and every figure follows.
4. Click Texas on the map. Only Texas is chosen, outlined in red, and the address gains `state=TX`. Click California: it is added. Click Texas again: it is taken away.
5. Click a dot. The card opens under the map. A planned unit's status names its EIA code; a queue position's names the ISO's own words; a datacenter's card has story links.
6. Copy the address into a new tab. You should get the same choice and the same figures.
7. Click Reset. Everything is chosen again and the address is empty.
8. Open https://erw-flame.vercel.app/map/v2?grid=ercot. It should land on `/map?grid=ercot`.
9. Open the Method link: https://erw-flame.vercel.app/data/methods/energy_projects, section "The page: /map, one page".

## Decisions made alone

- **Unit card: in the page's data, read at the first click.** `project_map.py` writes the card's fields into `map.json`. The page leaves them out (`faceOf`) and fetches `/map/card` once, from the same file. I weighed three options, measured gzip on the 9 October file:

  | Option | Size (gzip) |
  |---|---|
  | Page data without the card | 430 KB |
  | Plus the ids that `/api/entity` would need | 582 KB |
  | Every card field in the page (the whole page served was 994 KB) | 835 KB |
  | Whole page now | 646 KB |

  I rejected `/api/entity`: datacenter ids change when the merge rule changes (session 166 changes it tonight), so a card could miss a row the file still holds. If the file is rebuilt between page load and click, the card asks for a reload instead of showing another row's fields.
- **Address:** slugs joined by commas, in the page's own order. `?kind=operating,planned&grid=ercot,caiso&tech=solar,battery&status=u,v&state=CA,TX&min=100&max=500`. An absent or empty parameter means all; `none` means none; an unknown slug is skipped.
- **State click:** with all states shown, a click chooses that state alone. After that a click adds or removes a state. Removing the last one shows all states again, so the map never dead-ends. Unticking the last state in the list gives "none".
- **Method note:** I extended `docs/methods/energy_projects.md` (the map's existing note, which version 1 cited) with a section "The page: /map, one page (session 167)". I did not start a second note.
- **Status vocabularies:**
  - Queue: active, suspended, completed, not stated. Withdrawn positions are left out, as in version 1.
  - Datacenters: the tracker's cleaned `status` (`project_status` is never shown).
  - A status appears in the panel only while its kind is on.
- **MW is never added across kinds.** The sentence gives each kind its own count and MW. The totals are by status, grouped by kind. A datacenter's MW is summed over the facilities that state one, with that count shown.
- **A row with no MW** (304 rows, mostly datacenters) drops out as soon as a size is set.
- **Grids:**
  - Queue position: the ISO whose queue it is.
  - Datacenter: "Grid not stated"; none is guessed from the state.
- **Technology:**
  - A queue's storage request is "Storage (queue positions)", in the storage color. I did not count it as a battery.
  - "Hybrid", "Transmission" and "Datacenter (a load)" are added to the technology list.
- **Datacenters with no US state** (119 of 374) are not written, because this is a US map. They are counted in `counts.datacenters_without_state`.
- **Totals by status** use a smaller tile than the shared `HeadlineNumber`, so a phone reaches the map sooner. The shared component is unchanged.
- **Withdrawn positions and the file size:**
  - Withdrawn queue positions are left out, as in version 1 (7,294 rows across the queues).
  - A file whose content is unchanged except its built stamp is not rewritten, so `map_v2.json` is untouched in git.

## Every block of both versions, and where it went

Version 1 (`/map`, sessions 16 and 22; kept at `site/app/_retired/map-v1`):

| Block | Where it is now |
|---|---|
| Title "Energy project map" | Header "The project map" |
| Intro paragraph | Header lead |
| Scope line (datacenters: news since 2025, operators' lists, queues; not a census) | Method note |
| Queues paragraph (six ISOs, county point, ring, withdrawn not shown) | Method note; the key of marks (a queue position is now a triangle, because the ring means a planned unit, as in version 2) |
| "What the map holds" cards | **Deleted, as the owner asked.** Their text under the cards went to the Method note |
| Kind checkboxes | Kind multi-select |
| Technology, State and Status selects | Multi-selects (Status now holds EIA's detailed codes) |
| MW from and to | Size, MW |
| Reset | Reset |
| "Showing N of n placed points, ... Not drawn ..." | The summary sentence, and the map's line "N of the rows chosen have no place on the drawing" |
| Map with legend toggles for kinds | Map; the toggles are removed and the key is plain |
| Color legend | The key under the map |
| Click card (via Supabase) | Unit card (from the page's file through `/map/card`). Changes: a Grid field added; the datacenter status is the cleaned word; the operator-coordinates location is now named (version 1 printed "not placed") |
| "By technology" table (all rows) | "By technology" (of what is chosen) |
| Colors note under the table | Method note |
| Cite line | Source line |
| Related line | Related line |
| NoData on a Supabase failure | Not needed: the page reads its file |

Version 2 (`/map/v2`, session 105; kept at `site/app/_retired/map-v2`):

| Block | Where it is now |
|---|---|
| Header crumb "Version 2, in review. The map as it was: /map" | Dropped (one page now) |
| Lead | Lead |
| Choose panel (grid, tech, status, size) | Choose panel, multi-selects, plus kind and state |
| Summary sentence | Summary sentence, per kind |
| Three totals by status | Totals by status, grouped by kind |
| "The map" section and its note | Kept; the note is shortened and the mark meanings moved to the key |
| Status series in the chart legend | **Deleted (owner)**; plain key |
| Technology color list | The key |
| "Beside it: the interconnection queue" | **Deleted (owner)** |
| "What is selected" table and its "Show all" | **Deleted (owner)** |
| Fold "What the inventory leaves out" | Method note, word for word where they were EIA's words |
| Fold "How to read it" | Method note |
| Source line | Source line (now the four tables; `interconnection_queue_summary` left with the queue block) |

**Data dropped from the face:**
- MISO's queue positions (rule 9; 1,733 rows).
- Datacenters in no US state (119).
- Withdrawn queue positions, as before.

## Tables: who reads them, what can move

**No table changes.** `eia860m_operating_generators`, `eia860m_planned_generators`, `energy_projects` and `datacenter_facilities` are read only.

`site/data/map_v2.json` is byte for byte unchanged, so `/resources` (its only other reader) cannot move.

Values that move outside `/map`: none.

Shared files changed, each the smallest change:
- `site/next.config.ts`: one redirect.
- `site/lib/release.ts`: the comments on the `/map` and `/map/v2` lines. Both stay `review`.
- `site/lib/audience.ts`: the link `/map/v2` becomes `/map`.
- `site/scripts/check-routes.mjs`: one line.
- `warehouse/scheduled.py`: the `project_map` step now names page `/map` and restores the four tables.
- `warehouse/run_monthly.sh`: one comment.
- `.github/workflows/daily-prices.yml`: commits `site/data/map.json` beside `map_v2.json`.

Not touched: `site/lib/pages.ts`. Its `/map` line still lists "energy_projects, datacenter_facilities"; this is held for the menu.

## Pulls and spend

- Pulls: none. The ceiling was 1 request for EIA-860M's file, which was not needed because the raw codes are already in the tables. `warehouse/raw/eia860/` does not exist in the main copy.
- Model spend: USD 0 against a cap of 0. No code calls a model.

## Checks

Output files are in `runs/session167/`.

| Check | Exit | Output |
|---|---|---|
| `node scripts/check-map.mjs http://localhost:3167` (91 of 91) | 0 | `check_map_3.out` (also `_1`, `_2`) |
| `node scripts/check-map-v2.mjs` (now runs the same check) | 0 | `check_map_v2.out` |
| `node scripts/check-routes.mjs http://localhost:3167` | 0 | `check_routes_2.out` |
| `npx tsc --noEmit -p .` | 0 | `tsc_3.out` |
| `npx eslint` on the map's files | 0 | `eslint_3.out` |
| `npm run build`, under the mutex | 0 | `build_3.out` |
| `tests/test_session167.py` with the main copy's tables (12 passed) | 0 | `test_167_tables.out` |
| `tests/test_session167.py` without tables (10 passed, 2 skipped) | 0 | `test_167_no_tables.out` |
| Neighbours: tests 105, 114_part2, 146_page, 53 (47 passed) | 0 | `test_neighbours.out` |
| 15 more tests that read the shared files (260 passed) | 0 | `test_more_neighbours.out` |
| Hand-over's read-only steps: the raw code on every row | 0 | `raw_code_trial.out` |
| Validator on the two EIA tables | 0 | `validate_eia_trial.out` |
| Whole suite in the working copy (2,420 passed, 224 skipped) | 0 | `test_suite.out` |

- `tsc_1.out` (exit 2) was a stale `.next` type file before the first build. `build_3` had one failed run first: a type error, fixed before the build that passed.
- Checks updated because they pinned what the owner changed:
  - `tests/test_session105.py`: points at the retired version 2 files.
  - `tests/test_session114_part2.py`: `/map` instead of `/map/v2`, the four restored tables, `map.json` in the workflow.
  - `site/scripts/check-map-v2.mjs`: runs `check-map.mjs`.
- Not run: `check-values.mjs`. Version 1's `projects|...` checks of Supabase counts went with the deleted "What the map holds" cards. `check-map.mjs` covers the figures against the file.

## Phone width (390 px)

Screenshots: `map_390_top.png`, `map_390_full.png`, `map_390_card.png`, `map_390_card_datacenter.png`, `map_1440_ercot.png` (`map_1440.png` is from before the tile change).

- It reads top to bottom: the header, then the Choose panel (Kind open, the other lists folded, each saying "all", "none" or "2 of 9").
- After that come the sentence, then the totals in two columns under three small headings, then the map (full width, about 360 by 240), the key, the card and "By technology". The table scrolls inside its own box; the page never scrolls sideways.
- The weak point: with everything chosen there are 19 status totals, so the map starts about 2,400 px down. Choosing a kind shortens the list.
- The card fits the width; long table names wrap. A click on a point scrolls the card into view.

## Hand-over, in order (from the main copy, after merging `wip/167-map`)

1. Run `bash runs/session167/handover.sh` after session 166's locked writes and outside 14:04 to 16:10 UTC. It runs:
   - `has_167`
   - `raw_code`
   - `validate_eia`
   - `project_map.py` under `lock.py run`
   - `tests_167`
   - the neighbours
2. If `site/data/map.json` changed, commit it before the landing build:
   `git add site/data/map.json site/data/map_v2.json && git commit -m "Session 167: the project map's file rebuilt from the tables"`
   - The committed file is from the 9 October 06:4x build of the main copy's tables: EIA 2026-08, queue 2026-09-30, datacenters 2026-10-08.
   - The rebuild is how the file matches session 166's new `datacenter_facilities`.
3. Land: snapshots, `task/` branch, merge.
   - After the deploy, run `node scripts/check-map.mjs https://erw-flame.vercel.app` (internal token needed) and `check-routes`.
   - The redirect `/map/v2` to `/map` is permanent (308).

## Not done, and things that look odd (flagged, not changed)

- `map.json` is rebuilt monthly and by hand, but `datacenter_facilities` changes daily. The map's datacenters therefore lag until the next rebuild; the source line gives their vintage. Adding `project_map` to the daily run belongs to the daily run's owner.
- 270 of 374 datacenters have an empty cleaned `status` (operator site lists), so they read "Not stated". Session 166 is changing the datacenter status words.
- EIA gives SunZia Wind South (New Mexico, 2,561 MW, the largest unit) balancing authority CISO, so the map puts it under CAISO. That is EIA's field, shown as given.
- `/map/card` reads 1.2 MB uncompressed from local `next start`, which does not compress route responses. Vercel compresses them.
- The menu line for `/map` in `site/lib/pages.ts` still names two tables. This is held because that file is shared.

## Five numbers

1. EIA-860M 2026-08 planned units by EIA code: P 684, L 393, T 224, U 486, V 373, TS 156, OT 0 (2,316 in all). Source: `eia860m_planned_generators.eia_status`.
2. Queue positions on the map: 3,737, with 762,726 MW requested. 2,146 are active (521,752 MW). Source: `energy_projects`, not withdrawn, without MISO.
3. MISO queue rows held back: 1,733 (paused while terms are reviewed).
4. Datacenters placed in a US state: 255 of 374; 19 of them state a MW, 18,274 MW in all.
5. Page weight (gzip): 646 KB now, against 994 KB with the card inside and about 400 KB for version 2's data alone.

## Landing state (added by the chain's session 166 at 22:30 UTC on 9 October 2026)

- This report is the agent's report of the session, kept whole; this section is what happened after the hand-over.
- **Not landed.** The account's usage limit paused the chain from about 08:15 to 22:00 UTC, so the deploy cutoff (15:00 UTC)
  passed with nothing of this session on production. Nothing was pushed to `main` or to a `task/` branch after the cutoff.
- The branch is on GitHub: `wip/167-map` (`1a77521`). It is also merged into the landing branch `wip/166-health`, with `site/data/map.json` rebuilt from this machine's tables by `runs/session167/handover.sh` (exit 0, every step). To finish: the landing of `wip/166-health` in `SESSION_166_REPORT.md`, "To finish".
- No em dash in this file (checked).
