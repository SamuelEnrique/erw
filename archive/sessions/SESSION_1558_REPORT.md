# Session 1558 report: the open faults read again, on a build of main

Energy Research Warehouse (ERW), session 1558, chain 173, samueloldlaptop, 6 November 2026, 14:34 to 14:57 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. A gate run on `origin/main` (`9ee7e847b`), not a landing.

## What it did

- **Main, checked whole after today's landings** (this machine's two, and the board's rows 1 and 2): `scripts/land_check.py --ref origin/main --task 1558-read`.
  - The suite passed (7894 tests, 343 skipped), as did the build.
  - `check_values` matched 7815 of 7815 values and failed only on the two known floors (`/deals`, know-your-grid).
- **Each open fault read again on that build**, in the internal view:
  - `/board`: AccessLint still finds `#other > details > div > div`, a scrolling region not reachable by keyboard (serious). The board's stack is in flight (`task/1600-1610-board` and `task/1611-1639-board`, and about 40 `wip/16xx-board` branches on origin), so it stays with that chain.
  - `/cost-of-power`: AccessLint still finds `figure > details > div` on main. Its fix is session 1526's, in the held landing.
  - The siting cards: `/research/card/siting_battery_swing`, `siting_flexible` and `siting_gigawatt` each link two pictures (`/findings/siting_<card>_1080x1350.png` and `_1600x900.png`), and all six answer 404. Their "/findings/" link answers 308, a redirect, not a 404. These are the desktop's files.
  - `/internal/open`'s `autocomplete="off"` and the battery page's decisions block wait for your ruling.
- The browser and the server were stopped, and the gate folder removed.

## Decisions made without you

- The faults were read again on main rather than fixed: none of the four is this chain's to fix today.

## For Samuel's ruling

- None new.
