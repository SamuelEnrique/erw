# Session 712 report: the method note v1 and the replication

22 October 2026, from 09:47 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-712` on `wip/712-allgrids` (cut from `wip/711-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 712. Model spend USD 0. No warehouse data written. The only requests: the live set with the anon key (the replication), the ERW's own archive bucket (one table rebuilt, below) and the live site's own pages.

## Read these first

- **`docs/methods/siting.md` v1**:
  - every column's formula, table, filter, vintage, license and its words where it cannot be filled;
  - the four profiles and their sources;
  - the screen;
  - the replication;
  - sixteen dated decisions;
  - the limits.
  - It is at `/data/methods/siting`, in review like every page.
- **`warehouse/replication/siting.py`** (standard library only) computes every figure the tab draws for three rows (ERCOT HB_HUBAVG, CAISO SP15, NYISO N.Y.C.) and three ERCOT nodes, under each of the four profiles, and sets each beside the page's `data-raw`.
  - It reads the live set with the anon key for the tables the live set holds (the four peaks, Berkeley Lab's queue, the hourly carbon), and the tab's own files for those it does not (the price history, the node basis, eGRID, EIA-861, the Commission's rate). The note says which is which.
  - It ports `lib/datacenter.ts`'s hours, months and twelve-month window to Python. `tests/test_session712.py` holds the port equal to the site's code on a fixture year.
  - **Run in a new virtual environment** (`runs/chain_050/venv712`, Python 3.14.7, nothing installed), from a folder of its own, against a build of this branch: **81 figures computed, 69 set beside the page, 0 differ, exit 0.** The other 12 are figures the page does not draw for those rows (the hours off and the four-peak charge per node, which the list draws once).
- **The first run of the replication found two differences, both mended**:
  1. **The months to connect**: the tab's file writes the median to the cent. The replication now rounds as the file does.
  2. **The electrolyzer's hourly carbon** (three rows off in the sixth figure): this machine's copy of `carbon_intensity_hourly` ended on 5 October, while the live set's ends on 18 October, and 48 of 8,592 hours differ in value (EIA's revisions). The table was rebuilt from the ERW's archive into `runs/archive_restore/` (not `warehouse/output`). `siting_page.py` gained `--in-dir-first` to read it before this machine's own, and `carbon.json` was rebuilt. Only the hourly part changed; eGRID's rates did not.
- **check-values on this build** (it holds 706 to 712) failed the text of 28 figures the first time, all of them display rules, never a value:
  - a sign written inside the checked figure ("+3.64");
  - whole MW written where check-values expects two decimals.
  - Mended: the sign stands before the figure, and check-values' list of keys written whole gains `allgrids|planned|year|mwh|yeardiff|capratio`. Then **2,487 of 2,487**.
- **The floors of three addresses were written** (A and B, the node list sorted by energy, a node's panel): 10 each.

## What to review

1. After the landing, `https://erw-flame.vercel.app/data/methods/siting` (internal view): the note.
2. `warehouse/replication/siting.py` on GitHub, and its run: `runs/chain_050/repl712.out` on this machine (one line a figure: the key, the replication, the page, equal).
3. To run it yourself: `SUPABASE_URL=... SUPABASE_ANON_KEY=... INTERNAL_COSTS_TOKEN=... python warehouse/replication/siting.py --repo . --page https://erw-flame.vercel.app`.

## Checks

Every gate redirected to a file under `runs/chain_050/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session700` to `712` and `215` | 0 | OK, 1 skip |
| `db_probe.py` | 0 | 0.60 s |
| `npm run build`, first | 1 | a type error of 709 (the hub table's caption tested for nodes); mended on 709's branch and merged forward |
| `npm run build` (lock `s712`, beat), after the mends | 0 | no statement timeout |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power`, first | 1 | 28 text failures, display rules only (above) |
| the same, after the mends | 0 | 2,487 of 2,487 on 29 addresses |
| the same with `CHECK_VALUES_WRITE_FLOOR=1` | 0 | floors of three new addresses |
| `check-existing-tab.mjs` production against the build | 0 | 0 differences |
| `python -m venv runs/chain_050/venv712` | 0 | |
| the replication in it, `-I`, against the build | 0 | 81 computed, 69 beside the page, 0 differ |

## The landing

Sessions 706 to 712 land in one push from this branch (below, once done). Sessions 700 to 705 landed at 10:09 UTC: `SESSION_705_REPORT.md`, "The landing".

## Decisions made without you

1. **The replication reads the tab's own files for the tables the live set does not hold.** The prompt asked for the anon key only; the price history, the node basis, eGRID and EIA-861 are not in the live set. The note says which figure comes from where.
2. **The hourly carbon was rebuilt from the archive's newer copy** (a read of our own bucket into `runs/`), so the tab and the live set agree.
3. **The display was mended to check-values' rules** rather than check-values to the display, except the list of keys written whole, which every tool extends.

## For Samuel's ruling

- Whether the hourly carbon table (and the other tables the tab's files are built from) should be rebuilt into the tab's files by the data machine's daily run, so the tab never lags the live set.

## Files

- New: `warehouse/replication/siting.py`, `tests/test_session712.py`, `docs/brand/review-706/` to `review-711/` (taken on this build), this report.
- Changed:
  - `docs/methods/siting.md` (v1);
  - `site/app/cost-of-power/AllGridsView.tsx` (signs outside the checked figures);
  - `site/scripts/check-values.mjs` (keys written whole) and `check-values-floor.json`;
  - `warehouse/derived/siting_page.py` (`--in-dir-first`) and `site/data/siting/carbon.json`;
  - sessions 700 to 705's reports (their landing).
