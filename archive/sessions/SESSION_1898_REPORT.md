# Session 1898: the lab path's three site faults (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, session 1898, samueloldlaptop, unattended, Opus 5.5. Run by one agent in `erw-1898` on `wip/1898-lab`, cut from `wip/1896-periodicals` (`c1e3d7ed9`). About 01:30 to 01:40 UTC. The agent committed three fixes and stopped before pushing, building or writing a report, and before the landing its session was to end with; session 1902 of chain 219 pushed the branch and wrote this from the commits and `runs/s1898/`. Lab path faults 2 to 4 of session 1885 (`docs/reviews/lab-path.md`).

## What it did, with commits (branch head `6482a971a`, pushed by session 1902)

- **Fault 2, `/datacenters`, the grids view:** "The facilities against each grid" printed "license needed" in every grid's Peak hour MW and Capacity MW and in ERCOT's reserve margin. `heldBy` read every `dcgrid|` key as `datacenter_facilities`; the grid's own figures come from `grid_peak_vs_capacity` and `ercot_cdr_reserve_margins`, both public in `sources.csv` and absent from `license_status.json`. `KEY_STAT_TABLE` names the table by the key's second word, read before `KEY_TABLE`, in `Num.tsx` and `check-holds.mjs` alike. `a05a17e9b`.
- **Fault 3, `/grid`, the Lower 48:** the Net export card read "by grid MW" (a grid with no tie "not reported MW"). The card takes its MW only beside a figure. `9c5745d4b`.
- **Fault 4, `/grid`, In the news:** "license needed scored stories since ..." then "No story in the last 14 days matched". Held, the section is one sentence: "The scored stories are held for a license (license needed): the outlets' terms ask for permission and none is recorded yet, so this section shows neither their count nor their headlines." `6482a971a`.

## Tests

- `tests.test_session1898` 10 OK (`runs/s1898/t3.out`; 4 and 6 at the two earlier commits). The run of the 120 related test files (`runs/s1898/related.out`) broke off before its result; the landing's gate runs the whole suite.
- Not built or read by the agent (`runs/s1898/shots/` is empty): the read is done on the landing's build (session 1903).

## Decisions made without you

- (Session 1902) The branch was pushed as committed and lands with the stack.

## For Samuel's ruling

- None new.
