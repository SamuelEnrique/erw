# Session 1159 report: the brand pass

23 October 2026, from about 21:00 UTC, on samueloldlaptop (the code machine, the old laptop), session 1159 of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075/076. Branch `wip/1159-grid`, cut from `wip/1158-grid` (sessions 1150 to 1158 merged with main), worktree `C:\Users\lossa\Documents\erw-1159`. Model spend USD 0. No warehouse data written, no Supabase read or write, no web request.

**The machine was short of memory** (2.0 GB free of 7.3 GB): on the orchestrator's instruction, no `next build`, no `next start`, no browser, no whole python suite. So **no screenshots** (before or after) and no live check: every check below ran on the source. `site/node_modules` was a junction to the main checkout's (the same `package-lock.json`), as in session 1158, and was taken down (the link only) before the hand-over.

## Read these first

- **The pages were already on the brand in the large**: `/grid` and `/grid/caiso/alerts` are wrapped in `<Brand>`, and `tokens.css`'s rules (unlayered, so they win over every Tailwind class) already turn the shared pieces' cardinal titles and header bands into ink titles, light rules above sections and an ink rule under each table header. No raw hex colour and no `text-[..px]` size is in any of the three pages' files (searched; Impeccable `detect` on 14 files: `[]`, exit 0).
- **What did not reach the brand, and is now fixed (styles only, no figure, key, word or panel moved):**
  1. The tables the chain's panels draw by hand (the energy mix's two, session 1152; the Clean tab's last 24 hours, session 1151) had rows of 25 to 29 px and a rule at 60 percent: now the shared table's rows (6 px above and below a cell, about 33 px; the brand's 32 to 36) and its full rule, by one rule in `tokens.css` scoped to `[data-grid-panel]`. Panels drawn by `ToolTable` or the shared charts' table already had both and do not move.
  2. "license needed" and "not held yet" had three looks: italic with a dotted rule (`Missing`, the scarcity panel's PJM, NYISO, ISO-NE, MISO, SPP lines, the CAISO hourly mix), plain grey with no mark that a hover holds the publishers (`Num`, `NoData`). Now one look across the tool: captions grey, upright, a dotted rule under words that hold a reason; in a figure's cell those words, and "not held", "no tie reported", "none", are set in the sans (they were in the figures' mono), as the All grids tab does since session 715.
  3. CAISO's alert state (session 1155) set its dates and counts in mono inside running text; the brand keeps mono for figures in table cells and hover cards. Now in the text face, as the other four panels' figures.
  4. The scarcity panel (session 1154) drew its title with `components/Section.tsx`; every other panel of the chain uses `ToolSection`. Now `ToolSection` (the same look under the brand: 20 px serif ink, the light rule above).
  5. The last 24 hours' table (Clean tab) scrolled with its note inside the frame, in a frame a keyboard could not reach, and its ISO column (a `td`) scrolled away. Now the table alone scrolls, in a `scrollRegion` frame named by its caption (as `ToolTable` and session 1158's mix tables), and each ISO is the row's header, which the brand's rule keeps in place.
  6. The hour beside each figure of that table ("05:00", written `text-xs`) was set at 14 px by the figure cell's span rule; now 12, the size the panel gave it.
  7. The two network panels (Network and Gravity tabs) stood 32 px under the drawing's notes; every other panel of the tool stands 40 px (`mt-10`). Now 40.
- **Nothing for the Ask column or the network drawings was changed:** what the critique found there is a design choice (below, "For Samuel's ruling").
- **A failing test that is not this session's:** `tests.test_session78` fails on this branch (and on `wip/1158-grid`) since session 1153: `app/network/NetworkGravity.tsx` writes "16 December 2025" in the gravity note, which session 78's test allows only in `lib/caisoJoin.ts`; session 1153's own test pins the literal. Not changed here (it is neither a style nor this session's file); see "To finish".

## The critique, panel by panel (against `docs/brand.md`)

New panels first (sessions 1151 to 1157), then the old.

| Panel | Type scale | Spacing | Accent and rules | Numbers | Section heading | Source line | "license needed", "withheld" | Links | Done here |
|---|---|---|---|---|---|---|---|---|---|
| `grid_network_<grid>` (1151) | ToolSection 20, body 14, note 12 | 32 px under the notes, the tool's gap is 40 | ink header rule (tokens), light row rules | `Num` in `F` (dotted, `title` tip); mono in cells | ToolSection | in the note | "no tie reported" grey, but mono in the cell | none | 7 (gap); 2 (sans) |
| `grid_gravity_<grid>` (1151) | as above | as above | highlighted row fog, but also an ink rule above it (the shared total-row rule) | as above | ToolSection | in the note | "not held", "none" mono in the cell | none | 7; 2 |
| `grid_clean24_<grid>` (1151) | table 14, hours 12 meant, 14 drawn | rows 25 px | ink header rule (tokens) | `F`; mono | the old `Section` above it ("The last 24 hours") | the shared `Cite` | none | none | 1, 5, 6 |
| `grid_mix_<grid>` (1152) | 14 and 12 | rows 29 px, rule at 60 percent | ink header rule (tokens) | `F`; mono in cells; headline figures in sentences, not `HeadlineRow` | inside the Mix view's own header (24 px "Energy mix") | none of its own | empty share cells are blank, not "not held" (ruling) | chips | 1 |
| `grid_scarcity_<grid>` (1154) | 14 and 12 | 40 px | `HeatChart` legend (shared), ink swatches by token | `F`; mono in cells | `Section`, not ToolSection | its own last line (12 px grey), not `SourceLine` | `Missing` italic | underlined in text | 2, 4 |
| `grid_caisoalert_caiso` (1155) | 14, note 12 | first on the tab | none | `F` with `font-mono` in running text | ToolSection | its own last line | none | underlined in text | 3 |
| `grid_ask_<grid>` (1157) | h3 "Stored answers" drawn at 20 (the brand's h3), the same as the column's "Ask" h2 | 32 px, light rule above | summaries in cardinal, underlined (as the page's Decisions) | stored text, no keys | its own h3 | its own run line | the license words in a sentence | none | none (ruling) |
| Map and gravity drawings (1153, 1156) | svg text in drawing units (scaled with the drawing) | | frame fog; hover cards white (`bg-panel`), 2 by 8 px padding, where the shared charts' card is fog, 8 by 12 | MW in the card | | notes under the frame, 12 px | public interchange only, said | regions link to `/grid` | none (ruling) |
| Old: Now blocks, Mix view, Clean, Exchange, Reliability, `MixTable` | on the scale through tokens; the Mix view's titles at 24 (h2 `text-3xl`) | rows 25 to 29 px in the old tables | Mix view's chips and view links: selected in cardinal fill; the shared picker and segments: selected in ink | `Num`; mono in cells | `Section` and ToolSection, the same look | `Cite` and `SourceLine` | `NoData` and `Num`: plain grey; `CaisoMixWithheld`: a fog panel with a cardinal left bar | underlined in text; chips by inline colour (the global `a` colour wins over classes) | 2 (one look) |
| `/grid/caiso/alerts` (session 60) | the pooled answer at 18 px (`text-lg`), off the scale | rows 29 px | the pooled answer boxed by a cardinal left bar | `Num` | `Section` | `Cite` | "not held", "no price" grey | underlined | none (ruling) |

Tool readings, written here and in no design file:

- Impeccable `detect --json` on the three pages' 14 files before, and on the 5 changed files after: `[]` both, exit 0 (`runs/session1159/detect-before.json`, `detect-after.json`). No `critique` run (it needs a served page: no build). Questions skipped; nothing written to `.impeccable/`, `PRODUCT.md` or `DESIGN.md`; no hook.
- web-design-guidelines, from the copy kept in `runs/session201/vercel-skills/guidelines_command.md` (no fetch): "Handle empty states: don't render broken UI for empty strings" (the mix tables' blank share cells, ruling 1); "Interactive elements need keyboard handlers" (the keyed figures' tips are `title` only, and the map's lines answer no key: session 1158's ruling stands).

## What to review

After the chain's combined landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. `https://erw-flame.vercel.app/grid?grid=ercot`: scroll to "ERCOT: hourly mix, last 7 days". The fuel table's rows are as tall as the network tab's tables (about 33 px), with a full light rule between them.
3. Scroll to "ERCOT: the scarcity hours, last 30 days held": the title looks as before (serif, a light rule above). Open `https://erw-flame.vercel.app/grid?grid=pjm#scarcity`: "license needed" is upright grey with a dotted rule; hover it for the reason.
4. `https://erw-flame.vercel.app/grid?grid=caiso`: in "CAISO's alerts: today", the dates (2026-10-08, 2024-07-24) are in the text's face, not a typewriter face.
5. `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`, at 390 px wide: under "The last 24 hours", press Tab until the table's frame is outlined, then the right arrow: the figures scroll, the ISO names stay; the line "The hour beside each figure..." stays under the frame.
6. `https://erw-flame.vercel.app/grid?grid=ercot&view=network` and `...&view=gravity&shape=gravity`: the panel under the drawing stands a little lower (40 px, as the other panels).
7. `https://erw-flame.vercel.app/grid/caiso/alerts`: unchanged.

## Checks

- Precheck for session 1159: run by the orchestrator, exit 0.
- `impeccable detect --json` (14 files before, 5 after): exit 0, `[]` each.
- `python -m unittest`, one file at a time: `tests.test_session1159` (new, 9 tests), `1155`, `473`, `1154`, `502`, `1153`, `1158`, `1152`, `168_network`, and every test that reads `tokens.css`: `1016`, `179`, `186`, `194`, `235`, `236`, `237`, `238`, `239`, `240`, `241a`, `241b`, `241c`, `267`, `268`, `296`, `299`, `314`, `319`, `351`, `412`, `416`, `423`, `583`, `584`, `714`, `715`, `717`: exit 0 each.
- `tests.test_session78`: **exit 1**, one failure, not this session's (above): `test_no_other_code_names_the_date` finds `site/app/network/NetworkGravity.tsx` (session 1153's note).
- `node scripts/test-scarcity-strip.mjs`, `test-network-map.mjs`, `test-grid-390.mjs`, `test-caiso-alerts.mjs`, `test-grid-keys.mjs`, `test-gravity.mjs`: exit 0 each.
- In `site/`: `npm run content`, `npx next typegen`, `npx tsc --noEmit -p .`: exit 0 each.
- No `db_probe`, no build lock, no build, no browser, no server (the orchestrator's memory instruction).

## The landing

- None in this session: no build, and the chain lands its sessions together once the database answers (the brief). The branch is pushed: `wip/1159-grid`.

## To finish

- Screenshots, each as its own command (`MSYS_NO_PATHCONV=1` in Git Bash), at 1280 and 390, of `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=ercot&view=network`, `/grid?grid=ercot&view=gravity&shape=gravity`, `/grid/caiso/alerts`, under `docs/brand/review-1159/`:
  - before, from production in the internal view, before the landing: `node scripts/check-390.mjs https://erw-flame.vercel.app runs/session1159/before390.json docs/brand/review-1159 --pages /grid?grid=ercot,/grid?grid=caiso,/grid?grid=ercot&view=network,/grid?grid=ercot&view=gravity&shape=gravity,/grid/caiso/alerts` (rename the shots `before-*`), and the same pages at 1280;
  - after, from the landing's build (the lock free, `db_probe` 0, memory enough): `npm run build`, `next start -p 3159`, the same command against `http://localhost:3159` (shots `after-*`); then `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/grid,/grid/caiso/alerts,/network node scripts/check-values.mjs http://localhost:3159` (expected: no key added or removed, every value matching); stop the server by its PID and its port; release the lock.
- `tests.test_session78` against session 1153's note: write the date in `NetworkGravity.tsx` as `{caisoJoinDay()}` (`lib/caisoJoin.ts`, the same words on the page) and pin that in `tests/test_session1153.py` beside the words it pins; this changes an assertion of 1153's test, so it is the orchestrator's or the next session's call, before the landing gate.
- Land `wip/1159-grid` with the chain's combined landing. Expected differences in the snapshot: none in any number or word. Served HTML: the last 24 hours' table (a new inner frame with `tabindex`, `role="region"` and its name; the ISO cell a `th`); the scarcity section's title markup (`h2` with the rule class in place of a `div` around it); the network panels' class; CAISO's alert figures lose `font-mono`.

## Decisions made without you

- The hand-drawn tables of the new panels were brought to the shared table's rows by a rule in `tokens.css` scoped to `[data-grid-panel]`, not by redrawing them with `ToolTable`: session 1158's tests pin the energy mix's two scroll frames by their markup, and the rows carry `data-mix-fuel`, which `ToolTable` has no place for. The old tables of the page (rows 25 to 29 px) keep their density.
- The one look for "license needed" and "not held yet" is scoped to the Grid tool (`[data-grid-tool]`): `Num` and `NoData` are drawn on every page, and other pages are other sessions' passes.
- The keyed figure's dotted rule and `title` tip (the panels' `F`, five copies in five files) were left as they are: one shared `F` would move each file's `check=` count, which `tests/test_session473.py` pins.
- `/grid/caiso/alerts` (session 60's page) was read and left as it is: every finding there is a word or a design choice.
- No screenshots: no browser and no build (the orchestrator's memory instruction), so none from production either.

## For Samuel's ruling

- The energy mix tables leave a share cell blank when a fuel has no share; the brand says "not held" in captions grey. Recommendation: "not held".
- `/grid/caiso/alerts`, "Year by year": the note says the bars are "green where demand was below the model", but they are drawn in ink since session 319 (`--color-down`); and a cardinal bar for the other sign judges it. Recommendation: both signs ink, the sign written on the bar, the note "ink bars: the estimate; whiskers: the 90 percent interval".
- `/grid/caiso/alerts`, "The answer, pooled": set at 18 px (off the scale) in a box with a cardinal left bar. Recommendation: the brand's summary sentence (serif 20 px), no bar.
- The cardinal left bar on fog (`CaisoMixWithheld`, `CaisoBreakNote`, the carbon note, `HeldRows`, and on the battery page) is not one of cardinal's three jobs. Recommendation: a fog panel with a rule-coloured edge, site-wide in one landing.
- California's hourly mix says "not held yet" (the Mix view's `Missing`) where the Now block says "Not shown: ... " in the withheld panel: two words for one ruling. Recommendation: the withheld panel's words in both places.
- The Mix view's chips and view links mark the chosen one in cardinal fill; the tool's grid picker and tabs mark it in ink. Recommendation: ink, as the shared segments.
- The map's and gravity shape's hover cards are white with tight padding on a fog frame; the brand's card is fog with 8 by 12 px. Recommendation: the frame white with a rule-coloured edge, the cards as the shared charts' card.
- A highlighted row (the grid in view) takes the total row's ink rule above it (`tr.font-semibold`, shared). Recommendation: fog only, no rule, for a highlight.
- "Stored answers" (h3) is drawn at 20 px, the size of the column's "Ask" (h2). Recommendation: 16 px sans 600 for a heading inside the Ask column.
- The panels' headline figures are written in sentences, not as `HeadlineRow` numbers, and each panel ends with its own source sentence, not `SourceLine`. Recommendation: keep the sentences (they say the window and the age); a `SourceLine` per panel only if the owner wants the tables named the same way everywhere.
- The Mix view's and the Clean view's own titles ("Energy mix", "How clean, and when") are drawn at 24 px, the headline number's size, above 20 px section titles. Recommendation: keep (a view's title is the page's second size, as the battery page's questions).

## Files

- `site/app/tokens.css`: the session 1159 block, appended (rows of the hand-drawn tables, the hour's size, one look for "license needed" and "not held yet", their face in a figure's cell).
- `site/components/grid/CaisoAlertState.tsx`: `F` without `font-mono`.
- `site/components/grid/ScarcityPanel.tsx`: `ToolSection` in place of `Section`.
- `site/components/grid/Emissions.tsx`: the last 24 hours' table in its own scroll region, the ISO cell a row header.
- `site/components/grid/NetworkFigures.tsx`: `mt-10`.
- `tests/test_session1159.py` (new).
- `archive/sessions/SESSION_1159_REPORT.md`.
