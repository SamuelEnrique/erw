# Session 7620 report: ruling alternatives, /cost-of-power/battery (and the chain's ground)

Energy Research Warehouse (ERW). The chain of 17 November 2026 (pasted in chat): for each tool of `docs/state/ruling_impact_claims.md`, from the bottom up, claim it in `docs/state/ruling_alternative_claims.md`, then build the other choice of each impact line of 1 percent or more (or that adds or removes a figure) on its own `wip/alt-<tool>-<n>` branch with a pinning test, a build and a screenshot at 1280. Rules of `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md` and its owner's rules of 16 November held. portable-laptop (code role). Model spend USD 0.

## At the top

- **The chain is done: every one of the 40 tools is claimed**, 12 by this machine (sessions 7620 to 7631, from the bottom up), 28 by samueloldlaptop (from the top down, sessions 7700 on). No branch asks to land; no default on main changed; no hold lifted.
- **One commit of mine put merge markers in `docs/state/ruling_alternative_claims.md` on origin/main for about a minute** (`07f66e874`): a Write was refused and the `git add` in the same step committed the conflicted file. Fixed by the next commit (`d181b263f`), checked on origin.

## This session

- `docs/state/ruling_alternative_claims.md` created (it was on no branch), the battery claimed alone (`5cded9d91`).
- A worktree for every branch: `C:\Users\lossa\Documents\erw-alt` (packages installed in place), built and served with `runs/c7610_build.ps1` (the repository's `.env`, no model key, port 3320), read with the internal cookie in an isolated browser context. Every build measured first: 2,070 MB free at the lowest, never under the 2 GB rule.
- Record: `docs/reviews/ruling-alternatives-battery-2026-11-17.md`. `wip/alt-battery-1` (the note follows the data: 81.40 to 80.34 per kW), `wip/alt-battery-2` (the fold's 72 cells to `months.csv`).
- Found: the battery page already follows the data (November 2025 to October 2026); what stays on October 2025 to September 2026 is the signed note and its hourly export.

## Decisions made without you

- Branch names number the items in the order built (largest change first), not the impact file's row numbers; each record maps them.
- A line whose other choice is already on origin/main, or moves no figure today, gets no branch and is said so in its record.

## For Samuel's ruling

- The rulings these branches stand for are in `docs/reviews/rulings-for-samuel-2026-11-17.md`; each record gives the figure under each choice.

## Commits

- main: `5cded9d91`, `c9b39cc72`, `07f66e874`, `d181b263f`. Branches: `wip/alt-battery-1` `c34c80188`, `wip/alt-battery-2` `c723a6297`.
