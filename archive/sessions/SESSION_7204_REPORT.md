# Session 7204 report: the policy monitor read as a regulator's staffer would read it (chain 302, after goal 4)

Energy Research Warehouse (ERW). 16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7200-large-load`, stacked on sessions 7201 and 7203 (landing request row 15). Model spend: USD 0.00.

## At the top

- **The laws block said "No law or bill on large loads was read" for a state with no row.** That was wrong in three ways and is fixed: Texas's S.B. 6 was read and is withheld; Georgia's and five other legislatures' sites were not read; Arizona and fourteen others were searched and nothing found.
- **Read from drawn HTML, not in a browser** (no build on this machine on the day).

## The read

- `docs/reviews/policy-read-2026-11-16.md`: ten states (Texas, Virginia, Arizona, Ohio, Georgia; then Utah, Alaska, West Virginia, Kentucky, Michigan, the next five by the megawatts `datacenter_facilities` holds), 11 numbered rows.
  - 5 site faults, fixed;
  - 4 data faults, rows 26 to 29 of `docs/state/data_requests_large_load.md`;
  - 2 for a ruling.

## What was fixed

- **A state with no law in the table says what the research records:** "none found where searched" (15 states), "not read" (6: California, Georgia, Kentucky, New Hampshire, Oklahoma, Tennessee), "S.B. 6, read and not shown" (Texas, a row of its own with blank cells), "not searched" (Alaska, Hawaii). What was searched is on hover. Where the research's words hold a lead from the news they are not carried: the hover names the research file (5 states).
- **"28 are held for other states"** read as a license hold: now "The table has 28 rows for other states".
- **A chosen state links its utilities' own rules** on the All grids tab, with their count and the changes' ("11 in TX (13 changes in the last 90 days)"). On the tab, the rules' State filter now chooses the 90 days of changes too.
- **The State filter's hover says what a record is:** a federal action or a release of four bodies; a state commission's own dockets are not records.
- **A topic a law names twice is numbered** ("curtailment or backup generation (1 of 2)").

## Tests

- `site/scripts/test-large-load-rules.mjs` (92 checks, 9 new), `site/scripts/test-large-load-render.mjs` (58 checks, 6 new), `tests/test_session7204_policy_read.py` (8), `tests/test_session7200_large_load_rules_page.py` (8, 1 new).
- The touched test files of the whole branch: see the landing request row's count (the sweep ran at the end of this session).

## What to review (after the landing)

1. `https://erw-flame.vercel.app/policy?view=monitor&state=TX#large-load-laws`
   - "TX: S.B. 6, read and not shown". Hover it: the reason. Below, "The utilities' own large-load rules: 11 in TX (13 changes in the last 90 days)". Click it: the All grids tab opens on Texas's 11 rules, and "What changed in the last 90 days" reads "13 of 94 changes, TX".
2. `https://erw-flame.vercel.app/policy?view=monitor&state=GA#large-load-laws`: "GA: not read".
3. `https://erw-flame.vercel.app/policy?view=monitor#large-load-laws`
   - Under the 28 rows and Texas's blank row: "No row for 22 states the ERW searched", each state a hover.
   - Virginia's row, "Requires": "curtailment or backup generation (1 of 2)" and "(2 of 2)".
   - Left, the filter "State": hover its name.

## Decisions made without you

- **A bill withheld for a robots file is drawn blank and called "not shown", not "license needed".** Your page rule covers a held or internal value; this one is neither, and "license needed" would be false.
- **"None found where searched", not "no law".** The research's searches were of indexes and section lists, some thin; the words claim no more than was done.
- **The next five states were chosen from `datacenter_facilities` on this machine** (megawatts by state: Ohio, Utah, Alaska, West Virginia, Kentucky, Michigan, Georgia). The tracker holds megawatts for few sites, so the order is rough.

## For Samuel's ruling

- **PJM-wide records under a state.** 9 of 16 records that name PJM name no state, so a Virginia staffer filtering by state does not see them. Default: left; the hover now says to use Grid.
- **Michigan's row** is a sales tax exemption for data centers, not a connection law. Default: left as the table has it.
