# Ruling alternatives: /policy (17 November 2026)

Session 7626 (portable-laptop, code role). The three lines of `docs/reviews/ruling-impact-policy-2026-11-17.md`. Two are built, each on its own branch from origin/main with a test that pins it, in order of size of change; the third is the end of a hold and is not built. **No branch asks to land; no default on main changed; no hold lifted.** Model spend USD 0.

- **Build:** the worktree `erw-alt` (2,953 and 3,272 MB free before the two builds), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px.
- **Tests:** the new test of each branch and every test file that names a changed file: 42 passed (`wip/alt-policy-1`); 115 passed and 3 skipped (`wip/alt-policy-2`, after moving the four checks of test 7201 and its two node scripts that pinned 27 laws, 26 states and "2 of 28" to the other choice).

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 2 | Filtering the monitor by Virginia shows 7 records and not the PJM-wide actions that bind Virginia: show PJM-wide records under each PJM state | `wip/alt-policy-1` (`005f9ccd0`) | `/policy?view=monitor&state=VA`: "7 shown of 1533 records held" (significance 5 or more) | **"14 shown of 1533" (+7, +100 percent)**; each PJM state gains the same 7 records that name PJM and no state: DC, Delaware, New Jersey 0 to 7; Indiana, Maryland 2 to 9; Michigan, North Carolina, West Virginia 3 to 10; Ohio 4 to 11; Illinois 6 to 13; Pennsylvania, Tennessee 7 to 14; Kentucky 8 to 15. With the floor lifted Virginia 27 to 35. Texas unchanged (45). The list, the calendar and the CSV follow the filter | `site/lib/policymonitor.ts`, `tests/test_session7626_alt_policy_pjm_wide.py` | The page's filter on `monitor.json` (built 16 November 2026) gives every count above; 7 records are PJM-wide | `docs/reviews/ruling-alternatives/policy-1-pjm-wide-virginia-1280.png` |
| 3 | Michigan's one law in the large-load laws table is a sales tax exemption with no smallest load: keep it among the 27? | `wip/alt-policy-2` (`c6eb19cbe`) | `/policy?view=monitor#large-load-laws`: 27 laws and bills, 10 in effect; Michigan's row (Enrolled H.B. 4906, Public Act 207 of 2024); the All grids tab links Michigan to the table | **26 laws and bills (-3.7 percent), 9 in effect (-10.0 percent)**; states with a public law 25 to 24; Michigan's row gone and the All grids tab no longer links Michigan to a law; the check key `largeload\|laws\|public` reads 26 | `site/lib/largeloadrules.ts`, `site/lib/sitingdata.ts`, `site/app/policy/page.tsx`, `site/scripts/test-large-load-render.mjs`, `site/scripts/test-large-load-rules.mjs`, `tests/test_session7201_large_load_on_site.py`, `tests/test_session7626_alt_policy_michigan_law.py` | On `large_load_rules.json` (built 16 November 2026): 27 to 26, 10 to 9 in effect, 25 to 24 states, the key 26, Michigan out of the link list; every reader takes the same list | `docs/reviews/ruling-alternatives/policy-2-michigan-law-out-1280.png` |

## Line not built

- **Line 1, the end of the monitor's hold (the PUCT's news releases): not built.** The license holds stand (the owner's rules of 16 November 2026, rule 5): no hold is lifted, switched off or worked around on any branch. Its "PUCT rows leave" variant moves the counts by 1.4 percent (records held 1,533 to 1,512) and 0.7 percent (the open view 295 to 293), and taking rows out of `policy_actions` is the data machine's to do, not a page's.

## Decisions made without you

- **PJM's footprint is its 13 states and DC** (five of them in part), and "PJM-wide" is a record that names PJM and no state, as the impact file counted; a record naming PJM and one state keeps its own state.
- **The State filter's counts beside each state in the facet list are left as each record's own states**; only the rows kept change.
- **Michigan's law is taken out by its id with its reason** (`OUT_OF_SCOPE_LAWS`); the scope rule in words is "no term for a large load's connection or its rates, and no smallest load". Whether that rule takes out other laws is the ruling's to say; on this file no other law is taken out.
- **The laws' header says "27 of 27 shown"** on the branch: that count includes the one held law (26 in scope and 1 held), as origin/main's "28 of 28" did.
