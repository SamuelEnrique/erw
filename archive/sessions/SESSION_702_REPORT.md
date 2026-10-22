# Session 702 report: the load profiles' math on the All grids tab

22 October 2026, from 09:05 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-702` on `wip/702-allgrids`, cut from `wip/701-allgrids`. Chain `queue/done/050-night-23-october-code-allgrids.md`, session 702. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **A profile now reshapes the energy column.** The figure is the day-ahead price weighted over the hours the load runs, inside the flat load's own twelve whole months, from the same hourly files. Each month is `lib/datacenter.ts`'s `monthsOfYear` (`lib/siting.ts`, `profileTwelve`).
  - **Datacenter**: every hour, so it equals the flat figure (HB_HUBAVG 34.30).
  - **Heavy industry**: also every hour, because no table holds the hours a grid interrupts a heavy load. The tip says so.
  - **Flexible compute**: off at or above the strike, USD 1,000 by default (HB_HUBAVG 32.25, off 14 hours; N.Y.C. 72.56, off 5; SP15 and SPP North never reach it). It is also off in ERCOT's four summer peak intervals (`site/data/siting/ercot_4cp.json`, new, from `ercot_4cp_intervals`). None of those falls inside the window (October 2025 to September 2026): summer 2026 is published by 1 December 2026. The tip says so.
  - **Electrolyzer**: with no strike typed, it runs at or below each row's own price at the load factor, the cheapest 55 percent of its hours (HB_HUBAVG 18.82 with a strike of 27.79; SP15 14.61). With a strike typed, it runs below it.
- **The hours off are a second figure in the cell** ("off 3,942 h") and in the tip, with the hours run and held and a flat load's price beside it.
- **ERCOT nodes**: HB_HUBAVG's figure under the same rule, plus the node's mean daily basis. The tip says "daily".
- **A strike field in the left box** for the two profiles whose rule has one, with its default in grey, its source on hover, and "Reset strike".
- **The all-in rule is written** (`allIn`): the figure is drawn only when energy, transmission and capacity are each held or zero by market design. It draws nothing until sessions 703 and 704 give the other two.
- **Keys**:
  - `allgrids|energy|<row>|da|profile=<p>&lf=<lf>&strike=<s or row>`;
  - `allgrids|lost|<row>|<same>`.
- check-values reads three more addresses (`&profile=flexible`, `electrolyzer`, `industry`). The five new addresses have floors of 10.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view).
2. In "Profile", choose Flexible compute. "ERCOT HB_HUBAVG (hub)" reads 32.25, off 14 h. Hover 32.25: the rule, the strike, the four peaks not held for summer 2026, and a flat load's 34.30.
3. Choose Electrolyzer. The strike field is empty ("each row's own"). HB_HUBAVG reads 18.82, off 3,942 h.
4. Type 20 in the strike and press Show: every row now runs below USD 20, and "Reset strike" appears.
5. Screenshots: `docs/brand/review-702/` (the flexible and electrolyzer profiles at 1280 and 390; before is 701's build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session702` (fixture: every profile against the same arithmetic in Python), `701`, `700` | 0 | 24 tests OK, 1 skip |
| `db_probe.py` | 0 | 0.87 s |
| `npm run build` (lock `s702`, beat) | 0 | no statement timeout |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power?view=allgrids` | 0 | 985 of 985 on five addresses |
| the same with `CHECK_VALUES_WRITE_FLOOR=1` | 0 | floors of the five addresses written (10 each); every other floor as it was |
| `check-existing-tab.mjs` production against the build | 0 | 0 differences |

## The landing

Sessions 700 to 702 land together; see the end of this report once landed.

## Decisions made without you

1. **The load factor does not change the price per MWh**: it scales the energy and the cost alike. It moves the electrolyzer's default strike, and later the per-MWh share of the capacity and transmission charges.
2. **Heavy industry runs every hour.** "Interruptible" moves the capacity column (704), not the energy, because no table holds the hours a grid interrupts it.
3. **The electrolyzer's default strike is the row's k-th cheapest hour**, k the load factor's share of the window's hours, and the load runs at or below it. A typed strike is strict ("below").
4. **The four peaks are matched to the hour that holds the interval**, in the grid's standard time, as `model.ts`'s four-peak block does.

## For Samuel's ruling

- The heavy industry profile's interruptions: no table holds them. Should a grid's emergency notices (CAISO's are held, `caiso_grid_emergencies`) count as interruptions where held?

## Files

- Changed: `site/lib/siting.ts` (`profileTwelve`, `profileCell`, `profileKey`, `allIn`, the strike input), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`ProfileTd`), `AllGridsForm.tsx` (the strike), `site/scripts/siting-files.mjs`, `site/scripts/check-values.mjs`, `site/scripts/check-values-floor.json`, `warehouse/derived/siting_page.py` (`ercot_4cp.json`; a file whose content is unchanged is kept), `tests/test_session701.py` (a pin follows 702's longer list).
- New: `site/data/siting/ercot_4cp.json`, `tests/test_session702.py`, `docs/brand/review-702/`, this report.
