# Session 1184 report: the method from each panel

24 October 2026, from about 03:55 to 04:30 UTC, on samueloldlaptop (the code machine, the old laptop), the seventh session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1184-grid`, cut from `wip/1183-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1184`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. The only reads were light anon-key reads of Supabase's REST API and the public snapshot object, made through `same-figures.mjs`'s proxy and held in memory, never written.

## Read these first

- **Each of the 17 panels now links the section of its note that defines it.** The panels are 1183's, listed in `site/lib/gridAnchors.ts`. The link is `/data/methods/<note>#<heading id>`, and the id is the one the site's renderer writes (`lib/markdown.ts` `headingSlugs`). The ids were printed by `render` itself, never written by hand, and a test holds them to it.
- **One constant a panel** (`METHOD_NETWORK` ... `METHOD_STRESS_GRIDS`), gathered by panel in `GRID_METHOD` for the tests. A component imports only its own constant. A first version had the components import the whole object, and `tests/test_session502.py` failed. The reason: `scripts/page_tables.py` reads the constants a component imports, and the object holds two notes named like tables (`ercot_grid_notices`, `scarcity_hours_by_grid`). Those names then read as table reads on the Network tab. With one constant a panel, the page-table lists are unchanged.
- **Where each link stands.** Most panels gain one line at their foot, "Method: <the section's words>.", drawn by `components/grid/PanelMethod.tsx` (`data-grid-method`) inside the panel. Three panels already had a source line with a method link:
  - The scarcity strip and CAISO's alerts: the existing link now opens its section. Its words are unchanged.
  - ERCOT's notices: session 1174's link to the whole note is pinned by its test, so it stays, followed by "Method: the notice state on the Grid tool".
  - The scarcity panel of the Lower 48, and of a grid without a strip, draws the foot line.
- **Which section each panel opens:**

| Panel | Section |
|---|---|
| The network's figures, gravity table, last 24 hours, stored answers | `grid_network`: "The Grid tool's panels, every figure keyed (chain 077, ...)" |
| The balance | `grid_network`: "The balance, said where the figures are (chain 078, ...)" |
| Exchange: the seven grids, the ties | `grid_network`: "The Exchange blocks under the gravity shape (session 1167)" |
| Exchange: twelve months | `grid_network`: "Who supplies a grid (session 68)" |
| The replayed day | `grid_network_v3`: "The outside grids' demand in the replay (chain 078, ...)" |
| The energy mix panel | `generation_mix_hourly`: "The Mix tab's energy mix, keyed, hourly and by month (chain 077, ...)" |
| Scarcity / CAISO / ERCOT | each note's "On the Grid tool ..." section (1154, 1155, 1174) |
| Stress: ramp, seven grids / tight, calm | `grid_stress`: "The views' figures, keyed ... (chain 078)" / "The large tables, keyed whole (session 1168)" |

- **check-links already checks fragments.** It checks each `#fragment` against the ids of the served page it names, and it reads the method pages in the internal view (session 581, `judge` and `anchorOk`). No change was needed, and no `node --check` was needed because the file is unchanged.
- **check-methods needed no change either.** A constant holding a note's address already counts as a link, so `href={METHOD_<PANEL>}` is read as a note. `/grid`'s notes gain `grid_network_v3` and `grid_stress`, and all 553 of 553 figures are still named.
- **`site/scripts/test-grid-methods.mjs` (new, 5 tests)** renders each committed note with `lib/markdown.ts` `render`. For every panel it checks that:
  - the fragment is an id under the expected heading, judged by check-links' own `internalTarget`, `anchorOk` and `judge` (an id one letter off is a finding);
  - the section says what the panel draws;
  - the link is written in the component, and its words say "Method";
  - check-methods reads every note for `/grid`;
  - every other `#` link in the Grid tool's code resolves (`STRESS_METHOD`).
- **No figure moved.** `same-figures.mjs` compared `ce10fd21` (in a temporary worktree, now removed) against this tree on 22 addresses covering every panel: 3,171 figures, every page the same, 147 requests, 0 new after.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`. Under the ties table, click "Method: the Grid tool's panels, every figure keyed": the method page opens at that heading. Under the balance, "Method: the balance, said where the figures are".
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`. Under "Over the last twelve months", "Method: who supplies a grid, the twelve months" opens "Who supplies a grid (session 68)".
4. Open `https://erw-flame.vercel.app/grid?grid=ercot`. Click the scarcity strip's "Method: each grid's own scarcity signal" (it opens "On the Grid tool"). In ERCOT's notices, the second link opens section 6.
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&mix=stress&year=2024`: each of the four tables ends with its method line.
6. Read `site/lib/gridAnchors.ts` (the constants) and the method note's section "The method from each panel (chain 091, 24 October 2026)" with its Decisions.
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1184: run by the orchestrator, exit 0.
- `node scripts/check-methods.mjs` (no server): exit 0, before and after, 553 of 553 named, 57 pages.
- `test-grid-methods` (new, both loaders): exit 0, 5 of 5. Mutation check: with one fragment cut short, it exits 1 and names the link. Restored before the commit.
- `test-grid-files` (both loaders): exit 0, 92 cases, 19 of them new (each drawn panel carries its link on 18 pages, plus one that every panel's link is drawn). A first run failed one case, the Lower 48's scarcity panel, which had no link; that panel now draws the line.
- Other node tests, one at a time, each exit 0:
  - plain node: `check-revised`, `ercot-notices`, `grid-390`, `grid-balance`, `grid-exchange`, `network-map`, `network-split`, `scarcity-strip`, `check-links`, `caiso-alerts`, `mix-hourly`, `gravity`, `grid-keys`;
  - alias loader: `grid-addresses`, `grid-ask`;
  - both loaders: `grid-file-keys`, `grid-held`, `grid-replay`, `grid-stress`, `grid-units`, `grid-failed-reads`, `grid-reads`, `grid-generation`.
- `python -m unittest`, one module at a time, 58 modules: every module that reads a changed file, the three that use `scripts/page_tables.py` (248, 410, 502), and the new `test_session1184` (8 tests). Each exit 0. `test_session502` failed once, on the first version (above); its assertion stands. No assertion was removed or changed.
- `same-figures.mjs`, `ce10fd21` against this tree: 22 addresses, exit 0, every page the same.
- `npx eslint` on the 14 changed or new code files: exit 0.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. Both junctions were removed with `rmdir`, and the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values, check-links and check-routes against a server, screenshots.

## The landing

- None in this session. Chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main), and this branch lands with them. Pushed: `wip/1184-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site, run `node scripts/check-links.mjs http://localhost:3000` (it needs a browser: one heavy process) and read its exit. Expected: no `anchor` finding for any `/data/methods/...#...` link of `/grid`.
- check-values on the addresses of "What to review": every key as before. No key changed.
- The snapshots before and after, every difference listed. Expected on each Grid page: the new "Method: ..." lines in the visible text, and the changed `href` of the scarcity and CAISO method links. Nothing else.

## Decisions made without you

- **The section that defines the panel, not the note's top.** Where a panel has no heading of its own (the network's figures, the gravity table, the last 24 hours, the stored answers), the link opens the chain 077 section, which holds them.
- **The twelve months open "Who supplies a grid (session 68)"**, which defines `ba_supply_monthly`'s measures, not session 1167's section, which only changed the table's words.
- **One constant a panel, not the object, in the components.** This keeps the page-table lists (`page_tables.py`) true. Rather than change that shared reader, the constants are split.
- **A pinned link is kept and a second one added** (ERCOT's notices): session 1174's test holds its words and address.
- **No link in the failure words**: the replayed day whose file was not read, and CAISO's and ERCOT's state lines when their read fails, keep only the words session 1181 set. Every other panel's line is drawn in its no-data state too.
- **The ids come from the renderer in the test**: a heading renamed in a note fails the test by name.

## For Samuel's ruling

- The link words, "Method: <the section's words>" (for example "Method: the Grid tool's panels, every figure keyed"), one line under each panel. This is a wording change, if shorter words are wanted.
- ERCOT's notices carry two method links (the whole note, pinned by session 1174, and the section). Recommendation: keep only the section's link, which needs session 1174's assertion changed by a person.

## Files

- New: `site/components/grid/PanelMethod.tsx`, `site/scripts/test-grid-methods.mjs`, `tests/test_session1184.py`, this report.
- Changed:
  - `site/lib/gridAnchors.ts` (the 17 constants and `GRID_METHOD`);
  - `site/components/grid/NetworkFigures.tsx`, `ReplayDay.tsx`, `ExchangeView.tsx`, `Emissions.tsx`, `MixView.tsx`, `ScarcityPanel.tsx` (its `METHOD` constant replaced), `CaisoAlertState.tsx`, `ErcotNoticeState.tsx`, `AskExamples.tsx`, `site/components/mix/views.tsx`;
  - `site/scripts/test-grid-files.mjs`;
  - `docs/methods/grid_network.md` (the section "The method from each panel (chain 091, 24 October 2026)" with its Decisions).
- On this machine only: `runs/s1184/` in the worktree (every test's output, check-methods before and after, same-figures' output and figure lists, the renderer's ids).
