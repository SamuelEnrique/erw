# Session 2115 report: the siting gaps read again

23 October 2026, from 22:44 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: none of 10.

## Read these first

- **No row of `docs/reviews/siting-gaps.md` changed state, and none can without a ruling or a key,** for session 959's reasons. Rulings 16 (a 2026 sub-region table) and 18 (the OpenEI key) are still "not ruled" (`siting-rulings-answered.md`). Large-load tariffs wait on the OpenEI key. Substations and lines wait on a publisher of record. ERCOT's settlement point mapping is under `/misdownload`, which its robots file disallows. A large load's own wait outside NYISO has no public table.
- **This chain's tables fill no open row:** BLM's federal oil and gas statistics, NOAA's measured sunlight, EIA's household energy spending, the Energy Commission's total system power, the Treasury's 1603 awards and the USGS's streamflow describe no node, zone, tariff, reserve margin or line.
- **A state section for chain 069 is added, and three earlier ones are put back in order.** The merges of chains 057, 066 and 067 had left chain 057's heading empty, its text (session 2022's) under chain 067's heading, and chain 067's text (session 2078's) under chain 066's. Each text now stands under its own heading, word for word. The table's rows are untouched.
- **Tests:** the siting and coverage tests (`test_session7*`), 195, pass but `test_session705`, the known artifact of a run from a worktree (it passes in the main checkout and is skipped on GitHub).

## Errors

- None.

## Decisions made without you

- **The three sections' order repaired** (a reversible edit of text the merges had displaced).

## For Samuel's ruling

- None new (rulings 16 and 18 stand).

## Files

- Changed: `docs/reviews/siting-gaps.md` (the sections), this report.
- On the data machine only: `runs/c069/s2115/`.
