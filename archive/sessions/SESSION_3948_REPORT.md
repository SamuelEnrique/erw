# Session 3948 report: JEDI's construction cost (forecast request 2), with 3949 (large-load request 17's rest)

Energy Research Warehouse (ERW). Chain 272, data machine (lab-desktop), 14 November 2026, 13:36 to 13:42 UTC. Opus 5.5. Model spend USD 0. No request to a publisher (Redivis's API for the draft).

## 3948: forecast request 2

- **The request asked** for JEDI's default construction cost per MW in `nlr_jedi_multipliers`. That table's connector needs `jedi_recalc.py`'s files, which are on no machine since window 4's `runs/w4/` went with its worktree (session 3938).
- **Done in the warehouse's record another way:** `forecast_tool_parameters` now carries `construction_cost` (USD/MW, each model's dollar year) for every technology and location, from `site/data/forecast/jedi_costs.json`. That file's every location's 24 figures were checked against `nlr_jedi_multipliers` when `jedi_costs.py` wrote it. 206 rows; the table 768 rows.
- **Under the data lock:** written, validated, archived (206 new), in coverage; the license record, release list, package catalogue and the Redivis draft updated. Test 3938 checks a value against the file. The method's section names the file.
- **A slip, put right:** the write script's put-back removed `forecast_tool_parameters.py` from the main checkout (it was new when the script was written and is on main since land-g); restored from git at once, with the lock free.

## 3949: large-load request 17's rest

- **ERCOT's provisional Batch Zero classification** (3 September 2026: 204 projects, 66.4 GW base load; 158, 127.9 GW studied) and **Utah's R746-318 amendments under comment** noted in their registry files. No step changed: the deck is a status update, and no Utah amendment is adopted.
- **The PUCT's exception order** (Project 59142) stays out under the PUCT's link-policy hold.

## Decisions made without you

- **JEDI's construction cost went into `forecast_tool_parameters`,** not `nlr_jedi_multipliers`: the checked file is the record now, and the recalculation would mean downloading the four workbooks again and a pycel environment for a figure already checked.

## For Samuel's ruling

- None new.
