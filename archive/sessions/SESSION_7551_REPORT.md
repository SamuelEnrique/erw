# Session 7551 report: `/play/battery` read as the reader it is for (chain 304, part B, samueloldlaptop, 16 November 2026)

- Branch `wip/7535-play-battery` (the tool's own, this machine's), worktree `C:\Users\lossa\Documents\erw-7535`, from `544328a5b` (session 7535's done line). Pushed.
- The read: `docs/reviews/battery-game-read-2026-11-16.md`. The reader: a student or new analyst playing a named day and asking what a real battery would have earned; a teacher setting the game for a class. Five cases: Uri (15 February 2021, Normal), the 2023 heat (10 August 2023, Hard), the CAISO duck day (24 July 2026, Easy), a teacher's class on Uri's day, the fleet section beside `/storage`, the awards page and the grid page.
- 15 rows: 5 site (all fixed, `site/scripts/test-battery-game-read.mjs`, 44 of 44), 1 data machine (request 239), 5 rulings, 4 browser (reads 266 to 269). License 0, key 0.
- The shared figures: Uri's and the heat's daily average and highest real-time price agree with `/events/uri-2021` and `/events/ercot-heat-2023` to the last digit; ERCOT's fleet agrees with the home page and the grid page by key; the battery page's stress days are not the same measure as the game's day (row 2), and the page now says why.
- The tool's own tests: `test-battery-game-render.mjs` 85 of 85; `battery-game-figures.mjs --check` exit 0 (after regenerating `page_figures.json`); `replicate.py --tables` (the main copy's tables) 3,549 of 3,549; `tests/test_session7535_battery_game.py` 13 passed; `tests/test_session5171.py` 9 passed; `test-battery.mjs`, `test-battery-rulings.mjs` exit 0. Not built, not type checked (memory).
- Files changed (all this machine's own stack): `site/app/play/battery/Game.tsx` (`EndDetail`, `dayIndex`, `gameAddress`, `DayLink`, the day list and the mode buttons), `site/app/play/battery/page.tsx` (`initialDay`, the three hovers, the fleet's source line, the cards moved out), new `site/app/play/battery/RealFleet.tsx`, `site/scripts/battery-game-figures.mjs` and `replication/battery_game/replicate.py` (the Easy line in detail and the two figures per kW), `replication/battery_game/page_figures.json` (regenerated: 3,535 figures of 105 cases), `docs/methods/battery_game.md` (a new section, nothing removed), the read, the test, this report. No other machine's file touched.

## What to review

1. `https://erw-flame.vercel.app/play/battery?day=uri&mode=normal` (with the review cookie): the list opens on "Winter Storm Uri, 2021-02-15", Normal pressed; under the list "The link to Winter Storm Uri, 2021-02-15". Press Easy: the address becomes `?day=uri`. Pick "CAISO SP15: the steepest evening ramp": the address becomes `?day=caiso-duck`.
2. On Easy, play Uri's day to its end (or press Start and wait 90 seconds). Under the end table: "In detail: ... in the market, plus the fleet bonus ...", hover "fleet bonus"; then "A real battery is paid by other rules. Per kW of this battery's 5 kW, your trades netted ... and the perfect battery's $39.05 ...", and the link "The battery page".
3. The section "The fleet: fictional and real": three cards (the game's 50 MW, ERCOT 18,204.5 MW, CAISO 17,094.2 MW), the hover "the latest inventory", and the ratios 364.09 and 341.88.
4. The section "The fleet call": hover ECRS, Non-Spin and Base Point Deviation.

## Needs the key

Nothing.

## Decisions made without you

- The real-battery sentence draws no figure of the battery page: the two are not the same measure, so a figure set beside the game's would invite the comparison the sentence warns against. It gives the game's own trades per kW (the battery page's unit) and the battery page's rules.
- The per kW figure is the market's money alone (`cash`): no fleet bonus, before wear. Wear is a game setting and the bonus a game rule.
- Today's level gets no `?day=` of its own (it moves daily); an unknown day opens the first level, with no error shown.
- The fleet cards moved to `RealFleet.tsx`, a new file: a Next.js page file may not export a component, and the test must draw it.

## For Samuel's ruling

1. Easy shows no link to the event page (Uri, the 2023 heat). Default: Easy unchanged (your ruling 16, less on screen). Other choice: the one link on Easy's pick screen.
2. The score counts selling the half charge the battery starts with (on Uri's day about USD 45.66 of 240.23). Default: the rule stands. Other choice: a score net of the starting charge.
3. The game's battery is 2.7 hours; the battery page models 2, 4 and 8. Default: unchanged.
4. Grey text on the game page (the mode line, the day's reason, the leaderboard's note, the fleet call's source, the foot). Default: unchanged. Other choice: hovers or the page's ink.
5. No other page links to the game. Default: none added (other machines' pages). Now possible: `/play/battery?day=uri` from `/events/uri-2021`, `?day=heat` from `/events/ercot-heat-2023`.

## Rows for the coordinator

### (a) Landing request: no new row. Row 33's head moves

- Row 33 (`wip/7535-play-battery`): the head moves from `544328a5b` to the commit that adds this report (the return names it).
- One line to append to row 33's section: `- **Session 7551 (the read, chain 304 part B):** docs/reviews/battery-game-read-2026-11-16.md (15 rows); Game.tsx's EndDetail draws the line in detail on Easy and a real-battery sentence (the trades per kW, the battery page's rules, its link), ?day= opens a frozen day and DayLink gives its link, RealFleet.tsx (new) draws CAISO's fleet beside ERCOT's (ERCOT's keys unchanged; four new keys storage|iso_*|CAISO|operating and one calc ratio), three hovers in the fleet call section; page_figures.json regenerated (3,535 figures), replicate.py --tables 3,549 of 3,549, test-battery-game-read.mjs 44 of 44. Before landing as above, plus check-values on the four new CAISO keys. Snapshot: none on the 25 addresses; with the review cookie /play/battery differs by the fleet's third card and its ratio, the three hovers, and (client-drawn) the day's link; /data/methods/battery_game by its new section. After the landing: browser reads 266 to 269, data request 239.`

### (b) Browser reads (`docs/state/browser_reads_wanted.md`)

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 266 | 2026-11-16 | 7551 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery?day=uri&mode=normal` | The day list and the mode buttons as the page opens; press Easy; pick the CAISO duck day; reload; open the link under the list in a new tab | Opens on "Winter Storm Uri, 2021-02-15", Normal; Easy makes the address `?day=uri`; the duck day makes it `?day=caiso-duck`; the reload keeps the day; "The link to ..." opens the same day and mode | wanted |
| 267 | 2026-11-16 | 7551 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery?day=uri` | Easy, play to the end; the line under the end table; hover "fleet bonus"; at 390 px | "In detail: ... in the market, plus the fleet bonus ..."; the hover says it is a game rule; "Per kW of this battery's 5 kW, your trades netted ... and the perfect battery's $39.05 ..." and the link "The battery page" opening `/cost-of-power/battery`; no sideways scroll | wanted |
| 268 | 2026-11-16 | 7551 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery` | "The fleet: fictional and real" at full width and at 390 px; hover "the latest inventory" | Three cards side by side on a wide screen, one column at 390 px; ERCOT 18,204.5 MW (259 units), CAISO 17,094.2 MW (310 units) or the live set's newer figures; the line "ERCOT's real fleet has 364.09 times ...; CAISO's real fleet has 341.88 times ..."; the hover says the latest inventory, not the day played | wanted |
| 269 | 2026-11-16 | 7551 | `wip/7535-play-battery` (row 33) | `https://erw-flame.vercel.app/play/battery` | "The fleet call: how it mirrors ERCOT's ADER pilot": hover ECRS, Non-Spin, Base Point Deviation | Each underlined with dots; each tip shows its words and stays inside the screen at 390 px | wanted |

### (c) Data requests (`docs/state/data_requests_done_line.md`)

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 239 | 2026-11-16 | 7551 (chain 304, samueloldlaptop; branch `wip/7535-play-battery`) | `site/data/battery_levels.json` (`warehouse/derived/battery_levels.py`, or `battery_solar.py`, which already writes each day's solar nameplate at its month) | For each frozen level, the grid's operating battery storage at the level's month: MW, MWh where given, and the unit count, from the EIA-860M operating and retired generators (as the solar nameplate is: "5,120.6 MW of solar nameplate installed in ERCO in 2021-02"), with its source line. The game's fleet section can then say what the real fleet was on the day played; today it can only give the latest inventory (ERCOT 18,204.5 MW now; of today's 259 operating units, 19 with 218.4 MW give an operating year of 2020 or earlier). Do not move a level or a price | EIA-860M, the operating and retired generator sheets, the month of each level | requested |

### (d) Progress line (part B of `docs/state/progress_c304.md`)

`| /play/battery (read) | samueloldlaptop | done <head> on wip/7535-play-battery (landing row 33): the reader a student or new analyst playing a named day and a teacher setting it for a class; five cases (Uri 15 February 2021 Normal, the 2023 heat 10 August 2023 Hard, the CAISO duck day 24 July 2026 Easy, a class on Uri's day, the fleet beside /storage and the grid page); rows: 15 (5 site fixed, 1 data machine, 4 browser, 5 rulings) | 7551 |`
