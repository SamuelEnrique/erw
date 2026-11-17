# Session 7535 report: the home battery game (/play/battery) at the done line

Energy Research Warehouse (ERW), chain 304 (second run), samueloldlaptop, 16 November 2026. Branch
`wip/7535-play-battery`, worktree `C:\Users\lossa\Documents\erw-7535`. A first session stalled part way (its work is
`b6c39e141` and `8aaf2b803`); this continued session read both, ran what was there (the figures script as committed;
the replication at 3,274 of 3,295) and finished the five parts from there.

## What was done

- **The method note** (`docs/methods/battery_game.md`): a new section "The done line (session 7535)": every view and
  the rule of every figure it shows, the decisions block's 15 keys, two corrections, what the game does not hold, the
  replication, the cross-check and the faults. "Version 3"'s cap date corrected in place. Nothing deleted.
- **The replication** (`replication/battery_game/`): `replicate.py` from the note's rules, not the page's code; 105 plays
  on the seven days and four modes; 3,290 figures read off the page's own components drawn to HTML
  (`site/scripts/battery-game-figures.mjs`), the day list's 5 figures, and with the tables the 672 frozen prices and the
  two claims about the tables: **3,304 of 3,304** (3,295 of 3,295 where the tables are not beside the checkout).
  `replicate.do` for the five headline figures (not run: no Stata here), from `stata_input.csv` (`replicate.py --write`).
- **The cross-check** (`docs/reviews/battery-game-crosscheck-2026-11-16.md`): 9 rows. Uri's day and the heat day agree
  with Potomac Economics' 2021 and 2023 reports; the cap's date was a year late (ERCOT notice M-A120721-01); the value
  of lost load named beside the market's USD 5,000; the real fleet beside the market monitor's 2025 figure (no figure at
  the same date); the CAISO days: none read.
- **The decisions block** (`site/app/play/battery/Decisions.tsx`, mounted at the page's foot): 15 choices, each with
  its default, source and session on hover; the five battery settings marked editable (they are edited in place in the
  game's settings on Normal and Hard); the defaults read from `lib/battery.ts`.
- **The faults** (`docs/reviews/battery-game-faults-2026-11-16.md`): 10: 6 site (all fixed, rows 1 to 3 by the first
  session, 4 to 6 here), 1 data machine (row 8), 3 rulings.
- **Tests:** `tests/test_session7535_battery_game.py` (13 passed); `site/scripts/test-battery-game-render.mjs` (85 of
  85); the 18 older test files that name the game or its library, each run together: 190 passed, 4 skipped;
  `site/scripts/test-battery.mjs`, `test-battery-rulings.mjs`, `test-usage.mjs`, `test-battery-customer-read.mjs`: exit
  0; the eleven files that sweep every page: 108 passed, 1 failed (`test_session161.py`, the /ask fixtures: it fails
  the same way on the main copy at `5c997c9de`, not this change). `tests/test_session111.py` changed: its pinned line
  follows `keepWordsFor`, moved unchanged in `b6c39e141`.
- **License:** no committed file holds a held row (ERCOT's and CAISO's only; a test checks it); none of the page's eight
  check keys is held, so the known hold fault does not reach this page.

## What to review

1. `https://erw-flame.vercel.app/play/battery?mode=hard` (review cookie): the rules section's "Hard's grid emergency"
   says "ERCOT's system-wide offer cap since 1 January 2022". At the foot, open "Decisions in this game (15)"; hover or
   tap each "i": a default, a source and a session; the first five say "(editable)".
2. Same address, the day "A summer scarcity day", Hard, the rooftop add-on on, Start, play to 16:00: the outage banner
   says the roof carries the house through the whole outage (it said a dark house would pay $0.00).
3. `https://erw-flame.vercel.app/play/battery?mode=normal`, the day "CAISO SP15: the steepest evening ramp", play to the
   end: the debrief's sales include "07:00 to 07:15" (it said 07:30).
4. `https://erw-flame.vercel.app/data/methods/battery_game`: the section "The done line (session 7535)".

## Needs the key

Nothing. No model was called; `ERW_SPEND_CAP_USD=0`.

## Decisions made without you

- The debrief's runs are the perfect plan's trades; the outage's two hours are not a run (the replication reads it so;
  faults row 7 asks whether to name them).
- "A move that moves nothing" is read at the program's own grain, a nanowatt-hour, so a rounding residue's sale is not
  a move; no score changes on any day or mode.
- Potomac Economics publishes no terms page a search found; its public reports were read once each (robots: only
  `/wp-admin/` disallowed).
- The cross-check's fleet row cites the 2025 report as read on 13 November 2026 (session 5073), not read again.

## For Samuel's ruling

1. Faults row 7: name the battery's work in the outage in the debrief ("then carried the house from 16:00 to 18:00")?
   Default taken: no; the notice and the banner say it.
2. Faults row 9: the heat day's line could say 2023-08-10 was ERCOT's all-time demand record of 2023 (85.7 GW, Potomac
   2023, page 8). Default taken: leave the builder's line.
3. Faults row 10: say beside the USD 35,000 that ERCOT's own shortage pricing uses USD 5,000? Default taken: leave it.

## Rows for the coordinator

### (a) The landing request (row 33)

| 33 | `wip/7535-play-battery` | `HEAD` | `7535-play-battery` | 7535 | 2026-11-16 | `tests/test_session7535_battery_game.py` (13 passed) and `site/scripts/test-battery-game-render.mjs` (85 of 85, the changed pieces drawn to HTML without a build); the 18 older test files that name the game or `lib/battery.ts` (`test_session111`, `177`, `203`, `239`, `242`, `288`, `289`, `290`, `294`, `3600_batterygame`, `38`, `50`, `5171`, `53`, `55`, `56`, `66`, `70`): 190 passed, 4 skipped; `test-battery.mjs`, `test-battery-rulings.mjs`, `test-usage.mjs`, `test-battery-customer-read.mjs`: exit 0; `battery-game-figures.mjs --check` exit 0; `replication/battery_game/replicate.py --tables` (this machine's tables): 3,304 of 3,304, exit 0; not built and not type checked here (memory); `check-values` and `check-routes` not run | |

## Row 33: what it holds (chain 304, session 7535, the home battery game at the done line)

- **Stacked on** origin/main at `900fa95fc` (the branch's base). Report: `archive/sessions/SESSION_7535_REPORT.md` on
  the branch.
- **What changes:** `/play/battery`: `site/lib/battery.ts` `optimum` keeps no move that moves nothing (a full battery's
  charge, an empty one's sale, a residue's sale under a nanowatt-hour; no score changes); `Game.tsx`: Hard's wear said
  per kWh drawn out of the battery (mode line, end sentence), the end screen's pieces exported (`EndTable`, `WorstHour`,
  `EarlyEnd`, `Preview`, `EndDetail`, `Debrief`, `keepWordsFor`, `outageChargeFor`, `OutageBanner`: moved, words
  unchanged but the banner's roof case); `page.tsx`: the cap "since 1 January 2022", the source line's seven days and
  three tables, the new decisions fold (`Decisions.tsx`, 15 choices, server-drawn words, no state, no request). New:
  `replication/battery_game/`, `docs/reviews/battery-game-faults-2026-11-16.md`,
  `docs/reviews/battery-game-crosscheck-2026-11-16.md`, `site/scripts/battery-game-figures.mjs`,
  `site/scripts/test-battery-game-render.mjs`, `tests/test_session7535_battery_game.py`; the note's new section;
  `tests/test_session111.py` follows the moved line.
- **What does not change:** every score and perfect score on every day and mode (the render test replays each plan to
  its score), the rules' constants, the leaderboard, the presets (`v5`), the server's rescoring, the eight check keys
  and their figures, `site/lib/release.ts`, every table.
- **Before landing:** a build on the landing machine (the first build of `Decisions.tsx` and the changed `Game.tsx`), a
  play in each mode in a browser (the game is client-side), and `check-values` on `/play/battery` (the same keys).
- **Snapshot differences to expect:** none on the 25 addresses (the page is in review and not among them). With the
  review cookie: `/play/battery` differs by the rules section's cap date, the source line, and the decisions fold;
  `/data/methods/battery_game` by its new section. **Tables:** none.
- **After the landing:** rows 116 to 119 of `docs/state/browser_reads_wanted.md`; data request row 89.

### (b) Browser reads (rows 116 to 119)

| 116 | 2026-11-16 | 7535 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery`, at 1280 and at 390 px | The fold "Decisions in this game (15)" at the foot: open it, hover (1280) and tap (390) several "i" | Each tip shows Default, Source and Made in, inside the page's width at 390 px; the first five lines end "(editable)"; no horizontal scroll | wanted |
| 117 | 2026-11-16 | 7535 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery?mode=hard` | Day "A summer scarcity day", the rooftop add-on on, Start, play to 16:00 Central (the outage) | The banner: "Today the roof carries the house through the whole outage, so the battery cannot run dry"; no "$0.00" | wanted |
| 118 | 2026-11-16 | 7535 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery?mode=normal` | Day "CAISO SP15: the steepest evening ramp", play to the end; the debrief and the replay's "Every switch of the perfect plan" | The debrief's sales read "00:15 to 01:45, 04:30 to 06:30, 07:00 to 07:15 and 13:30 to 13:45, and 4 more"; no run ends at 07:30 | wanted |
| 119 | 2026-11-16 | 7535 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery?mode=hard` | Hard's mode line under the picker, then a play's end table sentence | "wear on every kWh drawn out of the battery"; the end sentence "of wear on each kWh it draws out of the battery (each kWh sold is less, after the loss on the way out)" | wanted |

### (c) Data requests (row 89)

| 89 | 2026-11-16 | 7535 (chain 304, samueloldlaptop; branch `wip/7535-play-battery`) | `site/data/battery_levels.json` (`warehouse/derived/battery_levels.py`), the level `solar`'s line | The line "solar made 19.5 percent of ERCOT's net generation, the most of the days the warehouse holds EIA's fuel mix for (from 2026-08-26)" names no end of the window. Write the window's end (the day the level was frozen), or re-read the claim on the days held now and say the new window; do not move the level's date (`--rebuild-ercot` is not wanted) | docs/reviews/battery-game-faults-2026-11-16.md, row 8 | requested |

### (d) The progress line (part A, row 15)

| 15 | `/play/battery` | done `HEAD` on `wip/7535-play-battery` (landing row 33): the note's done-line section (every view and its figures' rules, 15 decisions, two corrections); the replication 3,304 of 3,304 (3,290 figures of 105 plays read off the page's components, the day list's 5, 672 frozen prices and 2 table claims; `replicate.do` for five headline figures, not run); the cross-check (9 rows: Potomac's 2021 and 2023 reports agree on Uri's day and the heat day, ERCOT's notice dates the cap 1 January 2022, the fleet beside the 2025 report, CAISO days not read); the decisions block (15 choices, 5 editable in the game); faults: 10 found, 6 fixed, 1 data machine, 3 rulings | 7535 |
