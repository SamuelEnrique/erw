# Sessions 1894 and 1895: the W45 Roundup's rows 63, 64, 68 and 71 (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, sessions 1894 and 1895, samueloldlaptop, unattended, Opus 5.5. Run by one agent in the worktree `erw-1894` on `wip/1894-periodicals`, cut from `wip/1883-board` (`30b5b3573`). About 00:45 to 01:15 UTC. No table or Supabase write, no model call, no site build.

## What it did, with commits (branch head `fb29d58e3`, pushed)

- **Row 63 (session 1894)**, W45, What mattered 1: "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne" told "one outlet has reported it so far", though the deal is in `energy_deals` since 14 October. Now: "A step in a deal first reported before this week: in `energy_deals` since 2026-10-14 (Google and AEP, Wyoming fuel cell project, 702 MW, USD 4 billion, a 20-year power purchase agreement). What the evidence does not establish: what the week's step changes in that deal." A step ranks below the week's first reports. Commits `4f8e5e784`, `d139d4186`, `ae94d7133`. Left open in part: the earlier issues' items are not read, only `energy_deals`.
- **Row 64 (session 1895)**, What mattered 3, Revolution Wind: "What the evidence does not establish: EIA-860M (September 2026) lists Revolution Wind at 715 MW nameplate, planned for 2026-11-01; the 704 MW is the outlet's, and EIA has not yet listed the plant as operating." With the table absent, the line is as before. Commits `d3f350a33`, `638ed03a2`.
- **Row 68 (session 1895)**, the five numbers' stand-in: "... in its place, capacity: Revolution Wind (offshore wind turbine, RI), named in the week's stories (POWER Magazine): EIA-860M (September 2026) lists it at 715 MW nameplate, planned for 2026-11-01." The row's second choice, a policy stand-in, stays open.
- **Row 71, its open part (session 1895)**: "302.71 USD/MWh at HB_SOUTH (ERCOT), the 15-minute interval starting 2026-11-03 17:45 Central (23:45 UTC) [4], ERCOT's real-time settlement point price."; the source id moves to the Tables line. `scripts/check_roundup.py` and `site/scripts/check-values.mjs` read both forms (`df48a9b98`).
- The faults file's states set (`fb29d58e3`).

## Tests

- `test_session1894` 19 OK; `test_session1895` 20 OK; each with `test_session1882` and `test_periodicals`: 179 and 180 OK, 1 skipped; 22 older tests that load `roundup.py` OK (806, 498, 802, 801 and others). Outputs `runs/s1894/*.out`.
- Read-only checks on the real tables: the W45 story matches the 14 October deal; plant names over 12,547 stories matched only Revolution Wind and Swan Solar, both right.

## Decisions made without you

- More open rows (8) than fault sessions (5): two rows a session, in the file's order, sessions 1894 to 1897; session 1898 takes the lab path's site faults and lands.
- The session 1895 landing of file 217 is folded into session 1898's, one landing of the whole stack, to keep the gate's 45 minutes and this machine's memory to one run.

## For Samuel's ruling

- None new.
