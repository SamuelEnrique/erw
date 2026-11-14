# Session 6000 report: the queue, the ground, Montana's life, the readers sent (chain 270, samueloldlaptop)

14 November 2026, from about 08:40 UTC. Branch `wip/6000-forecast` (worktree `C:\Users\lossa\Documents\erw-6000`), cut from `origin/main` at `5b1301928`. Model spend under the owner's key: USD 0 (no model call by any tool); the subagents' own tokens are the harness's.

## The queue

- `queue/next/268-...periodicals-continued.md` renamed with `git mv` to `300-...`, with a line "Not before: the W46 Roundup (15 November, 23:00 UTC) and the Digest of 16 November exist"; committed alone, pushed (`045881141`). No queue number from 270 to 309 was used on any branch.
- `queue/next/270-night-14-november-oldlaptop-forecast.md` written (`machine: samueloldlaptop`, sessions 6000 to 6019, each free on origin/main and every branch), committed alone, pushed (`d99765278`), taken by name (`b74bb4981`).
- The next file `queue/next/271-day-15-november-oldlaptop-forecast-continued.md` (sessions 6020 to 6035) written first (`5b1301928`), then rewritten with the owner's corrected goal (`f7d3fac25`).

## The owner's correction (mid-session)

- Window D finished every state and DC (row 7 landed). Its held states are not read again. The work is narrowed, in order: (1) the states held at cost (CA, TN, NM, SC, WV, KY, TX, WA gas and geothermal); (2) Montana's 19-year life against the PDF; (3) a study per technology per region; (4) D's open faults and its rulings' defaults where reversible; then the five tools' build-free fault rows after P1's note lands; then file 300 once the Roundup exists.
- The original plan of eight readers over all 51 jurisdictions was not sent. Six readers were sent instead: four for (1) (CA and WA; TN and NM; SC, WV and KY; TX), two for (3) (gas and geothermal; solar and wind gaps).

## The ground

- Precheck passed; memory free 2.3 GB; disk 81 GB free.
- Window D's newest branch `wip/4290-forecast` (`829a1dfb6`, session 4304) is an ancestor of origin/main; so are `wip/4250-forecast` and `wip/4270-forecast`.
- Worktrees: `erw-3457` (landed branch, holds one untracked dry-run file of chain 252, `warehouse/news/facts/items/2026-11-13.json`: left for its chain, not removed); `erw-1425` and `erw-1600` hold open branches: left.
- P1's close-out note (portable laptop, chain 269) not yet on main at about 08:50 UTC; the W46 Roundup does not exist yet.

## (2) Montana's 19-year life: confirmed

- The PDF read again (robots file allows every path; HTTP 200, 27 pages), by word position, not text flow (`runs/s6000/mt_rows.py`, `mt_col.py`, local):
  - page 22: "Renewable Energy Generation 87 (11) 19" on one line;
  - page 21: "Electric Power Equipment 20 (11) 19";
  - page 27: the column under economic life 19: 97, 93, 89, 85, 81, 77, 72, 68, 63, 57, 52, 47, 42, 37, 33, 29, 25, 23, 21, 20, then 15.
- The rule's schedule equals it. No figure changes: the source's `checked` record, both quotes and the method note's line (the medium confidence of session 4303 withdrawn).
- Test: `site/scripts/test-forecast.test.mjs`, "session 6000": the schedule pinned to the PDF's column, and a hand-worked gas year (100 MW at USD 1,500 per kW, levy 600 mills, the 8th year: 150,000,000 x 0.68 x 0.03 x 0.6 = 1,836,000, plus the license tax 100 x 8,760 x 0.65 x 0.20 = 113,880; 1,949,880). Node 46 of 46; the three Python test files naming the changed files 21 passed.
- Pushed (`81517cfb3`); landing request row 12 (`00edb5141`).

## (4) D's open faults and rulings

- Faults 13 and 21 (the shared `SeriesChart`'s labels and figures): each fix moves every page that uses the chart; ruling 12's default "left as it is" already holds. Nothing reversible to apply without the ruling.
- Rulings 1 to 20: each default is already what the code does (page name "Local impact"; STEO's deflator; Tax Foundation's tables with attribution; Virginia's subsection F steps; value at cost where no schedule is read; and the rest as D's note lists).

## Decisions made without you

- The readers return their rows in their final message only and write no file anywhere; their requests and refusals come back with the rows.
- `erw-3457` is not removed: its untracked file belongs to the periodicals chain.
- The cross-check is rerun on this machine with the local `nlr_jedi_multipliers.csv` (`node site/scripts/forecast-crosscheck.mjs`): its 13 studies reproduce D's stored JSON exactly.

## For Samuel's ruling

- None new in this session.
