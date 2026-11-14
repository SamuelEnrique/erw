# Note: the old laptop's chain 274 (sessions 6050 to 6063), 14 November 2026

Energy Research Warehouse (ERW), samueloldlaptop (code role). Chain file `queue/done/274-day-17-november-oldlaptop-forecast-continued.md`; report `archive/sessions/SESSION_6050_6063_REPORT.md`. Model spend under the owner's key: USD 0 (no model call by any tool).

## What this chain did

- Rebuilt the empty step list (chain 273 stopped in its session 6036; its readers wrote nothing).
- The forecast tool (`/impact`, in review): the 25 states with a sales tax and no exemption read now each have a hover saying what was read, and figures where an official source settles it: Missouri solar 100, New Mexico geothermal 100 (Laws 2024, chapter 67, section 39, which the partial veto left standing), and the generating machinery's share in twelve machinery-exemption states plus Georgia and Mississippi. The machinery shares come from JEDI's own lines in the saved workbooks: solar modules and inverters 67.2 percent, wind turbines and blades 66.9, gas power generation equipment 58.3 (California at 43.6 percent of the tax, Mississippi at 5.5 of 7.06 points, Wisconsin's solar and wind with the mounting and towers its statute names).
- A fourth search for Plains and Southwest solar and gas impact studies: none usable.

## What landed, what waits

- Landing row 12 (`wip/6000-forecast`): landed to `53dcfa64b` (land-c, `f359090f9`); waiting from `35444185f` to `4a9ec60bf` (sessions 6051 to 6054: `sales_exemptions.json`, `site/scripts/test-forecast.test.mjs`, `docs/methods/forecast.md`). Tests on this machine: node 52 passed; `tests/test_session409.py`, `test_session4203_forecast.py`, `test_session4221_forecast_readers.py` 21 passed. Not built here (memory): the landing gate's build is the first. Snapshot differences to expect: none on a live page (`/impact` is in review).
- Landing row 13 (`wip/6021-five`, `8a9a87a90`): not landed; the portable laptop's row 31, which it stacked on, has landed, so it can land alone.

## Waiting for Samuel (default in brackets)

- 30. New York holds 100 percent for a machinery-only exemption while the states read today hold the machinery share: one rule? [New York as it is]
- 31. Wisconsin's solar exemption reaches the mounting and trackers, not the electrical materials. [as written, 83.6]
- 32. Missouri's machinery exemption and California's 3.9375 points also reach foundations or special purpose buildings; not counted. [not counted: the tax shown errs high]
- 33. Wind's machinery is the turbines and blades (towers left out, as solar's mounting); gas's is JEDI's power generation equipment (84.5 percent with the plant equipment). [as written]
- Still unsettled, each 0 with its reason: Arkansas, Oklahoma, Tennessee, Wyoming, New Mexico gas, Kentucky wind and gas (hosts refusing automated reads, or no official text naming generation). A person with a browser could read Tennessee's green energy guide and Arkansas's revenue opinions 20190510 and 20201111.
- Rulings 21 to 29 of `archive/sessions/SESSION_6001_6004_REPORT.md` still wait; nothing waits on them.

## Next

The periodicals file `queue/next/300-day-26-november-oldlaptop-periodicals-continued.md` once the W46 Roundup (Sunday 15 November, 23:00 UTC) and the 16 November Digest exist; until then file 275.
