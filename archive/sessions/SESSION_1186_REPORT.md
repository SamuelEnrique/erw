# Session 1186 report: the Grid pages under check-values, fast

24 October 2026, from about 04:45 to 05:45 UTC, on samueloldlaptop (the code machine, the old laptop), the ninth session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1186-grid`, cut from `wip/1185-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1186`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. Light reads of Supabase's REST API with the anon key: the pages' and check-values' own reads, each distinct request sent once through a proxy on this machine (below).

## Read these first

- **Without a server, check-values was run as it is against pages drawn outside Next.** The new `site/scripts/check-values-cost.mjs` does it in four steps:
  - it draws each of the 48 Grid addresses check-values reads (41 distinct pages) as `same-figures.mjs` does, to their server HTML;
  - a local site serves that HTML at check-values' own addresses;
  - a proxy stands where `SUPABASE_URL` points, sends each distinct request to Supabase once and holds the answers in memory;
  - it counts every request against the page check-values is reading.
- **The script was run five ways, old and new on the same answers:** every address in one run, each address alone (`CHECK_VALUES_PAGES`), a run a key kind, and a run with every page value moved.
- **Where check-values read more than the page did for the same figure, and what it reads now:**
  - **The network snapshot** (about 2 MB in Storage) was fetched once per `net|`, `nettie|`, `netbal|` or `netsnap|` key. CAISO's Exchange tab made 88 requests (14.1 MB); the page reads the snapshot once. Now it is fetched once a page.
  - **Shared operands.** A `calc|` key's operands and a `fmt|` key's inner key were recomputed for every key that names them: each fuel's share re-read the day's total. Now each value is kept for the run.
  - **Pairs of keys** (`fcerr|`, `degday|`, `netbal|`) each read the same two series. Now they are read once.
  - **`gridq|`** read the whole queue for each key: 27 keys and 2,000 rows each on ERCOT's Mix tab. Now the queue is read once a run.
  - **`awe|days`** read `caiso_grid_emergencies` once a key. Now it uses the rows `awe|last` and `awe|ndays` already read once.
  - **`series|`, `series_sum|`, `series_max|`** sent one request a key, where the page reads the hour or window once (the Flex Alert scorecard made 395 single-row reads). Now a page's keys are read together, one request a group: by table, entity and hour; or by table, window and entity, `calc|` operands included.
- **A group's answer is used only where it holds what the key's own query would have.** That means a variable with no row or one row, and an answer under PostgREST's page of 1,000 rows. Otherwise the key sends its own query, as before, and it does the same when the group's read fails. A failed read is never kept.
- **Every result is the same, and no check is weaker.** Old against new, over 68 pairs of runs, every key line was identical value for value: 2,275 key lines on the whole Grid run, 0 FAIL in both. With every page value moved, all 2,033 key lines FAIL in both scripts, the same lines. The other 242 lines compare committed files with their tables, which no page value reaches.

## Requests and rows, before and after

One proxy kept open for the session (24 October 2026, the pages drawn at 05:02 UTC, the runs 05:02 to 05:08). 1,729 distinct requests went to Supabase through it, each once. "Seconds" means the time of Supabase's answers: each request counted at the time its first answer took. It is an estimate, not a live run's timing (that waits for a build).

| Run | Requests before | After | Rows before | After | MB before | After | Seconds before | After |
|---|---|---|---|---|---|---|---|---|
| Every Grid address in one run (as a landing) | 1,865 | 467 | 203,367 | 108,608 | 66.7 | 9.5 | 153 | 34 |
| Each of the 48 alone, summed | 7,389 | 1,659 | 730,329 | 361,041 | 154.2 | 26.9 | 547 | 125 |

The slowest ten addresses, alone (the page's own draw is in the last column):

| # | Address | Requests before | After | Rows before | After | Seconds before | After | The page: requests, rows |
|---|---|---|---|---|---|---|---|---|
| 1 | `/grid?grid=caiso&mixp=month` | 425 | 91 | 26,199 | 12,741 | 28.1 | 6.6 | 70, 47,400 |
| 2 | `/grid/caiso` | 399 | 82 | 26,093 | 12,635 | 26.2 | 5.9 | 69, 46,925 |
| 3 | `/grid?grid=caiso` | 399 | 82 | 26,093 | 12,635 | 26.2 | 5.9 | 69, 46,925 |
| 4 | `/grid/caiso/alerts` | 395 | 46 | 395 | 395 | 25.0 | 3.0 | 6, 3,774 |
| 5 | `/grid?grid=ercot&mixp=month` | 278 | 66 | 70,044 | 23,011 | 20.9 | 5.0 | 61, 36,922 |
| 6 | `/grid/ercot` | 277 | 58 | 70,515 | 22,906 | 20.2 | 4.5 | 60, 36,447 |
| 7 | `/grid?grid=ercot` | 277 | 58 | 70,515 | 22,906 | 20.2 | 4.5 | 60, 36,447 |
| 8 | `/grid?grid=ercot&view=mix` | 277 | 58 | 70,515 | 22,906 | 20.2 | 4.5 | 60, 36,447 |
| 9 | `/mix?ba=erco&state=TX` | 277 | 58 | 70,515 | 22,906 | 20.2 | 4.5 | 60, 36,343 |
| 10 | `/grid/spp` | 277 | 51 | 50,181 | 18,594 | 18.9 | 3.8 | 52, 32,221 |

By kind, each kind's keys alone over every address (requests before and after):

| Kind | Requests |
|---|---|
| `nettie|` | 188 to 7 (36.6 MB to 1.4 MB) |
| `series|` | 719 to 188 |
| `calc|` | 279 to 29 |
| `gridq|` | 135 to 5 (88,899 rows to 3,293) |
| `awe|` | 124 to 2 |
| `net|` | 77 to 16 |
| `series_sum|` | 124 to 57 |
| `fcerr|` | 32 to 16 |
| `netbal|` | 12 to 6 |
| `bsup|`, `degday|`, `ercotn|`, `file|`, `series_esum|`, `series_max|`, `series_n|`, `states_sum|`, `storage|` | unchanged |

All 48 addresses' rows are in `runs/s1186/alone_table.md` on this machine.

## What to review

There is no landing yet (below). After the landing:

1. Read `site/scripts/check-values.mjs`: the session 1186 block above `truth` (`truth` and `truthOf`, `keptRead`, `networkStored`, `networkCommitted`, `batchGroupOf`, `leavesOf`, `planBatches`, `groupRows`), and the changed kinds (`netsnap`, `net`, `fcerr`, `degday`, `netbal`, `nettie`, `awe` days, `series`, `series_sum` and `series_max`, `gridq`), plus the two lines in `readOne` and `readPage`.
2. Run `node scripts/test-check-values-light.mjs` in `site/`: 8 tests.
3. At the landing's build, run check-values on the Grid pages (To finish): the same verdicts, and a shorter run.
4. Read `docs/methods/grid_network.md`, section "The Grid pages under check-values, lighter (chain 091, 24 October 2026)", with its Decisions.
5. Screenshots: not taken, no build.

## Checks

- Precheck for session 1186: run by the orchestrator, exit 0.
- `check-values-cost.mjs`, old (`git show HEAD:site/scripts/check-values.mjs`, a copy kept outside the tree after) against new, with `--alone --kinds --perturb` through the session's proxy: exit 0. 68 pairs, every pair the same.
- `node scripts/test-check-values-light.mjs` (new, 8 tests): exit 0. The same test on the old script (`CHECK_VALUES_LIGHT_SCRIPT`) exits 1. Its three verdict tests pass (every right key ok, every wrong key FAIL); its request-count tests fail.
- Node tests that read `check-values.mjs` or the note, one at a time, each exit 0:
  - plain node: `test-scarcity-strip`, `test-mix-hourly`, `test-grid-keys`, `test-check-values-run`, `test-check-values-slow`, `test-caiso-alerts`, `test-ercot-notices`, `test-check-revised`, `test-lower48`;
  - with the loaders: `test-grid-file-keys`, `test-grid-replay`, `test-grid-methods`.
- `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553 named, 57 pages.
- `python -m unittest`, one module at a time: every module that reads `check-values.mjs`, `grid_network.md`, `check-calc.mjs`, `check-format.mjs` or the new files (99 modules, `test_session1186` among them, 8 tests). 99 of 99 exit 0. No assertion of an older module was changed or removed. Session 1165's pinned lines (`xs.push(Number(await truth(k)))`, `return K.netbalValue(...)`), 1167's (`return K.nettieValue(...)`), 1152's (`variable.includes(",") ? ...`), 54's and 1154's stand word for word.
- `npx eslint` on the three changed or new scripts: exit 0, with the same 5 warnings as before, none in the lines added.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. The junction was removed with `rmdir`, and the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values against a server, screenshots.

## The landing

- None in this session. Chain 091 works code-only, stacked on `wip/1176-grid`; this branch lands with them. Pushed: `wip/1186-grid`.

## To finish

- Land with the chain's combined landing. At its build, against the running site (Git Bash, `MSYS_NO_PATHCONV=1`), run `CHECK_VALUES_PAGES=/grid,/emissions,/mix,/network node scripts/check-values.mjs`. Expected:
  - every key's verdict as the old script gives it;
  - the run shorter: about a quarter of the requests;
  - its time in the report beside the old script's on the same build (the old file is `git show 20362370:site/scripts/check-values.mjs`).
- The full check-values run of the landing reads the other tools' pages through the same changes (`series|` groups, the run's memo). Their verdicts should be the same; any line that differs from the last full run goes in that landing's report.
- The snapshots before and after: no page changes in this session (check-values only).

## Decisions made without you

- **A memo of each key's value for the run**, not for a page. It works like readOne's `truths`, which already kept every key the pages carry. A failed read is not kept.
- **The snapshot is fetched once a page, not once a run.** The Storage object changes every hour, and each page is drawn from one object. An answer that is not ok is not kept.
- **Groups only where each key's own query would give the same rows.** A variable held twice at the hour sends its own query, and a group answer of 1,000 rows or more is not used. The window's sums keep the rows' order (entity, hour, variable).
- **Bytes can grow where rows fall.** A group's answer names each row's variable: for the sums, 0.8 MB became 2.6 MB for the same rows in fewer requests. Over every address, bytes fell from 66.7 MB to 9.5 MB.
- **Left as they read, since neither reads more than the page:**
  - the Clean tabs' single hours of `carbon_intensity_hourly` (one variable at several hours: 38 one-row requests, where the page makes 17 to 22 requests of about 10,000 rows);
  - `series_n|` (one window a key).
- **The tool is committed** (`check-values-cost.mjs`) so the landing can measure again. It has `--serve-proxy` and `--proxy`, so runs share one set of answers and no distinct request goes to Supabase twice.
- **One new fixture of real rows** (`site/scripts/fixtures/caiso_queue_positions.json`: CAISO's queue in `energy_projects`, 513 rows, four fields, read from the proxy's held answers). CAISO's queue is public. ISO-NE's held rows were not used.

## For Samuel's ruling

- None new.

## Files

- New:
  - `site/scripts/check-values-cost.mjs`
  - `site/scripts/test-check-values-light.mjs`
  - `site/scripts/fixtures/caiso_queue_positions.json`
  - `tests/test_session1186.py`
  - this report
- Changed:
  - `site/scripts/check-values.mjs`
  - `docs/methods/grid_network.md` (the chain 091 section with its Decisions)
- On this machine only: `runs/s1186/` in the worktree, which holds:
  - the drawn pages and every run's output (`compare/`, `before2/`);
  - the per-address table;
  - the test outputs;
  - the old script's copy.
