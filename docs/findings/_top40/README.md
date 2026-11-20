# The sheet of forty in one Stata run

Energy Research Warehouse (ERW). Written by session 8905 (chain 590) on 19 November 2026 for Samuel. **Read, not run:** the machine that wrote these files has no Stata. Each line was read against the forty `reproduce.do` files it calls, and a test holds the runners to the sheet and to those files (`tests/test_session8905_top40_runner.py`). Nothing here approves anything: a finding is approved only by your click at `/internal/findings` after your own run.

- The sheet: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md
- `run_top40.do`: all forty, in the sheet's order.
- `run_top10.do`: the ten of tonight's page (sheet numbers 1, 2, 3, 4, 10, 11, 14, 16, 17, 19): the top of the sheet and every finding the audit found new; none that only repeats a publisher's own figure.

## What to do

1. **Pull the repository** so `docs/findings/` is today's.
2. **Put the tables in `docs/findings/_top40/tables/`** (git ignores that folder). The do-files read each table's CSV with the variable names on the first line.
   - From Redivis: download each table as CSV, under its own name (`eia930_ba_demand_hourly.csv`). Nothing else to do.
   - From the ERW's own files (`warehouse/output` on the lab desktop, or the site's Download CSV): those open with lines that begin with `#`. Run `python docs/findings/_top40/strip_hash_lines.py <the folder of the CSVs>` (add `--ten` for tonight's ten). It copies each table the sheet needs into `tables/` without those lines and says which are missing. `--list` prints the list and copies nothing.
   - The ten need 18 files, the forty 35. Some are large: the hourly emissions table is about 1 GB, the two ERCOT price histories about 0.5 GB each, and finding 1 reads seven yearly hourly files.
3. **Open Stata**, change the one line `global erw "..."` at the top to the folder of your copy of the repository (forward slashes), and run `do "<that folder>/docs/findings/_top40/run_top10.do"` (or `run_top40.do`).
4. **Read the table at the end** (also kept in `tables/run_top10.log`):

| Column | What it is |
|---|---|
| number | the finding's number on the sheet |
| finding | a short name and its unit |
| sheet | the figure the sheet gives for the last year |
| stata | the figure your run got, read from the data the do-file leaves in memory |
| result | `match`, `differs`, `no figure` or `failed, error N` |

- **match:** the last year's figure and the change since the first year are both within 0.5 percent of the change, the tolerance each draft states on its first line. Finding 18 (the large-load minimum bill) is a summary: its median, lowest, highest and count each within 0.5 percent of themselves.
- **differs:** the run finished and the figure is outside the tolerance. First compare with the do-file's own first line (`* Expected: ...`): if your table is newer than the sheet's run, the data may have moved (finding 10 already moved once, from 46.6193 to 46.5676, inside its tolerance). The sheet's figure is the one compared.
- **no figure:** the run finished but left no row for one of the two years (the table you used stops earlier, or its rows were filtered out).
- **failed, error N:** the do-file stopped; the runner went on to the next. Its own output, above the table, shows the line.

## If a line fails

- `error 601` (file not found): the table is not in `tables/`, or is named otherwise. `strip_hash_lines.py --list` gives the names.
- `error 111` (variable not found): the CSV's columns are not the ERW's (a file with its `#` lines still in it reads the first `#` line as the names; run the helper).
- `error 198` or any other: paste the line and the message to Claude in chat; the runner and each do-file are plain text and can be mended in a minute.
- A runner line itself fails before any finding runs: the usual cause is the `global erw` line (a backslash, or a folder that does not exist).

## How the files are made

- `build_runners.py` writes both `.do` files from the sheet: each finding's do-file, its two years and the sheet's figures. Rerun it if the sheet changes, then the test.
- Your Stata rules hold: no line continuation, one empty line between commands outside loops and none inside, and no string turned into a number in the runner (the do-files it calls destring with `force`, as before).
- The runner uses only global macros to carry results from one do-file to the next, because each do-file begins with `clear all`, which clears stored results but not global macros.
