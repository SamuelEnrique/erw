# Session 173 report: Automated Analysis finished and landed

Run on 10 October 2026 (UTC), 02:13 to about 03:00, unattended, second of the chain 172 to 175 (`CHAIN_OCT9_PROMPT.md`).
Built in the main copy on `wip/173-land` (from `wip/172-land`, with `origin/wip/170-analysis` merged). Outputs under
`runs/session173/`. Model spend: USD 0 of 0 (no code of this session calls a model).

## Read these first

- **Session 170 is on production** (`task/170-173-chain`, merge `8513ba0`, deployed 02:54:32 UTC): `/analysis` with the
  three finding cards, their downloads, the six renders in the bundled fonts, the request queue and "Use in Roundup".
  Snapshots `173_before` and `173_after`: 0 differences on the 25 pages (expected: nothing of this lands on them).
- **The fonts are bundled** (9 requests, 3.95 MB of the 10 and 15 MB allowed): Google Fonts' copies of Source Serif 4
  (upright and italic) and Inter from the `google/fonts` repository, with both OFL texts; sha256 of every file in
  `site/public/fonts/README.md` and pinned by a test. The renderer refuses a fallback face; it rendered all six.
- **The queue works end to end on production.** A request made on `/analysis` at 02:55:07 UTC was taken by the worker on
  this machine and was done at 02:55:21 (14 seconds). **But the worker is not running now:** the permission layer of
  this unattended session refused to register a scheduled task and to start a detached process (both "persistence").
  Until Samuel registers it (one PowerShell command, under "To finish"), a request waits as a queued row and the page
  says so with the time it was asked; the worker takes it when it runs.
- **"Use in Roundup" works both ways** and no choice is left in the table: the Roundup of Sunday 11 October falls back to
  the rule's chart of the week, labeled, unless Samuel chooses a finding before 23:00 UTC that day.
- **Two faults found and fixed before the landing:** the findings' `common.py` clashed with the templates' `common.py` in
  one test process (renamed `findings_common.py`), and a Windows checkout converted the cards' CSVs and the OFL texts
  (now pinned to exact bytes in `.gitattributes`). The whole suite in a clean copy: 2,737 tests OK.

## What to click on /analysis (internal view first: `https://erw-flame.vercel.app/internal/unlock?token=...`)

1. `https://erw-flame.vercel.app/analysis`: three cards in order. Each has its title in capitals, the italic subtitle,
   the interactive chart (hover a point or bar: the series, the category and the value with its unit), two or three
   callouts with before and after numbers, the why paragraph, the method footnote. Under each card: "Download the data
   (CSV)", "Python", "Stata do-file" (each answers 200), "Render 1080 x 1350" and "Render 1600 x 900" (the PNGs), and
   "Use in Roundup".
2. Click **Render 1600 x 900** under "BATTERIES ATE THEIR OWN LUNCH?": the whole card on one picture in Source Serif 4
   and Inter, no site menu, the paragraph, the effect table and the footnote all on it
   (`https://erw-flame.vercel.app/findings/batteries_lunch_1600x900.png`). The tall one:
   `https://erw-flame.vercel.app/findings/batteries_lunch_1080x1350.png`.
3. Scroll to **Ask for a finding**: pick a finding (for example "Gas sets the price less often?"), set its inputs (heat
   rate 6.5, 7 or 8; first year), click **Queue**. The note reads "queued at ...: the card appears here in 1 to 5 minutes
   when the data machine is awake"; the request shows in the list as "queued, waits for the data machine" until the
   worker runs here, then "done" with the card. Two done requests are in the list now (02:26 and 02:55 UTC, both by
   `SamuelOldLaptop`). At most 24 run requests a UTC day.
4. Click **Use in Roundup** under a card: it reads "Chosen for the Roundup" with the week (2026-W41). That choice is
   what Sunday's Roundup prints first; click it only if you mean it (this session's test choice was deleted).
5. `https://erw-flame.vercel.app/analysis/card/queue_divorce`: one card on its own page.
   `https://erw-flame.vercel.app/analysis/card/queue_divorce?render=1`: the render frame itself (what the renderer
   photographs).
6. `https://erw-flame.vercel.app/data/methods/automated_analysis_findings` (internal view): the section "Finished by
   session 173".
7. As a visitor (a private window): `https://erw-flame.vercel.app/analysis` is the in-review page; `/api/analysis` 404.

## The pull against its ceiling (fonts)

| Request | Host | Status | Bytes |
|---|---|---|---|
| `robots.txt` | github.com | 200 | 16,739 |
| `robots.txt` | raw.githubusercontent.com | 404 (no robots file) | 14 |
| `repos/google/fonts/contents/ofl/inter` (API listing) | api.github.com | 200 | 5,650 |
| `repos/google/fonts/contents/ofl/sourceserif4` (API listing) | api.github.com | 200 | 6,044 |
| `ofl/sourceserif4/SourceSerif4[opsz,wght].ttf` | raw.githubusercontent.com | 200 | 1,209,508 |
| `ofl/sourceserif4/SourceSerif4-Italic[opsz,wght].ttf` | raw.githubusercontent.com | 200 | 855,432 |
| `ofl/inter/Inter[opsz,wght].ttf` | raw.githubusercontent.com | 200 | 876,576 |
| `ofl/sourceserif4/OFL.txt` | raw.githubusercontent.com | 200 | 4,400 |
| `ofl/inter/OFL.txt` | raw.githubusercontent.com | 200 | 4,377 |

- 9 requests of 10; 2,978,740 bytes of files, 3,949,893 bytes in all, of 15 MB. User-Agent "ERW research project,
  github.com/SamuelEnrique/erw". One request every 1.5 s to the raw host.
- Terms: github.com's robots file (its `User-agent: *` block) disallows `/*/raw/`, `/*/archive/`, `*/zipball/` and the
  like on github.com itself and points programs to the API ("We also provide an extensive API"); the API listed the
  folders and gave each file's `download_url` on raw.githubusercontent.com, which has no robots file (404). GitHub's
  releases were not used: Inter's release archive is far over the 15 MB ceiling. The two licenses are the SIL Open Font
  License 1.1, recorded beside the fonts (`OFL-SourceSerif4.txt`, `OFL-Inter.txt`) and in the folder's README with each
  file's sha256 and retrieval time; `tests/test_session173.py` pins the five files byte for byte.
- Saved: `runs/session173/pull/` (the robots files, the two listings with git blob ids, the five files, `requests.csv`).

## What was built

- **Fonts and renders.** The five files in `site/public/fonts/`; `render-cards.mjs` from the built site on port 3170:
  six PNGs, `site/public/findings/<card>_1080x1350.png` and `_1600x900.png` (exit 0, every face loaded from the bundle).
  The first renders carried the site's menu and, at 1600 x 900, cut the paragraph at the foot; `render.css` now hides
  the header and footer in the frame and, for the wide aspect, uses a 280 px chart and smaller type so the whole card
  fits (checked by eye on all six, `runs/session173/render_cards2.out`). The 1600 x 900 renders are also in
  `docs/analysis/findings/` for the Roundup's e-mail.
- **The three cards recomputed on this machine** against the full histories (`run_finding.py`, each exit 0): every
  number as session 170 reported it (only `computed_at` and the CSV header's time moved; the CSV sha256 in each card
  follows). `catalogue.json` regenerated.
- **The queue.** Migration 027 (applied by session 172). Locally: a request through the built site's `/api/analysis`
  (`queue_divorce`) at 02:26:40 UTC, `worker.py --once` took it at 02:26:44 and wrote the card into the row; the list
  showed queued then done. On production after the landing: `gas_sets_price` at 02:55:07, done 02:55:21.
- **The worker.** Runs as `python warehouse/analysis/findings/worker.py --loop 60`. Not left running (see "Read these
  first"); started by hand it takes the oldest queued row within a minute. Note for the next session: the worker also
  rewrites `site/data/findings/<card>.json` and the downloads in the working tree on every request it runs (session
  170's design: the card goes to the row and to the default card directory); this session reverted those files to the
  committed ones after each probe (`git checkout -- site/data/findings site/public/findings`).
- **"Use in Roundup".** A `roundup` row written through the local site (02:27:47 UTC), `roundup_pick.py 2026-W41` read
  it ("queue_divorce chosen for 2026-W41", the card's markdown with its 1600 x 900 render); the row deleted;
  `roundup_pick.py` then says "no finding chosen", and `roundup.py` prints the rule's chart labeled "(the rule's pick;
  no finding was chosen for this week)". The Roundup's tests (`test_session119`, 43) pass.
- **`roundup.yml`'s truncated histories.** Session 170 had added the findings' tables to the restore. This session
  measured the templates' own tables against every restore: 41 templates read 39 tables; 28 are in the watch list's or
  the findings' pattern, 8 more are rolling tables the Redivis restore brings, 2 are in git, and
  `portwatch_chokepoint_transits` was brought by no step (its template was skipped on the runner). `run.py --tables`
  now prints the templates' tables as one pattern and the workflow syncs it after the findings' pattern, never stopping
  the Roundup on a failure. `tests/test_session173.py` holds the pattern covers every template table and the step order.
- **Sunday's run of 11 October still works:** the Roundup's tests pass on the landed code, `run.py --tables` and
  `run_finding.py --tables` print their patterns (exit 0), the workflow's restore chain is intact, and the Roundup's
  fallback was proven above. Nothing of `roundup.py`'s model step was run (USD 0).
- **Renamed `findings_common.py`** (was `common.py`): in one unittest process the templates' `common` was imported first
  and the findings got it (`AttributeError: module 'common' has no attribute 'DEFAULT_IN_DIR'`); the same for `worker`
  (`scripts/worker.py` of session 59 took the name), so `test_session170` loads the findings worker by its path.
- **`.gitattributes`:** `site/public/fonts/* -text`, the cards' CSV, Python, Stata and JSON files `text eol=lf`. Without
  it a Windows checkout turned the committed CSVs and OFL texts into CRLF and the sha256 checks failed in the clean copy
  (GitHub's Linux runner would have passed; the main copy, written by Python, passed; only a fresh Windows checkout
  failed).

## Checks, each its own command, exit code read (outputs under `runs/session173/`)

| Check | Exit | File |
|---|---|---|
| `npm run build` (three times: fonts and cards; the rename; the render frame) | 0, 0, 0 | `build_1.out`, `build_2.out`, `build_3.out` |
| `render-cards.mjs` on 3170 (six PNGs, no fallback face) | 0 | `render_cards2.out` |
| `check-analysis.mjs` on 3170 (79 of 79) and against production (79 of 79) | 0, 0 | `check_analysis2.out`, `check_analysis_prod.out` |
| tests 119, 170, 173 in one process (80) | 0 | `test_119_170_173.out` |
| tests 59 and 170 in one process | 0 | `test_59_170.out` |
| `npx tsc --noEmit` | 0 | `tsc.out` |
| whole suite in the clean worktree at `1d0dd31` (2,737, 228 skipped; the merge of main changed no file) | 0 | `suite_clean3.out` |
| `snapshot-live.mjs take` 173_before, 173_after; `compare` (0 differences) | 0, 0, 0 | `snap_173_*.out`, `compare_173.out` |
| `gh_api.py wait task/170-173-chain` | 0 | `wait_173.out` |
| `worker.py --once` (three runs: empty queue; the local request; the production request) | 0, 0, 0 | `worker_once.out`, `worker_once2.out`, `worker_prod.out` |
| `roundup_pick.py 2026-W41` with a choice and without | 0, 0 | `roundup_pick_chosen.out`, `roundup_pick_none.out` |

- The first two clean-copy runs failed (4, then 3) on the two faults above (`suite_clean.out`, `suite_clean2.out`);
  the third passed. The servers on 3170 were stopped; no process of this session is left running.

## Decisions made without you

1. **Google Fonts' repository copies, not the releases.** Inter's release archive alone is over the 15 MB ceiling; the
   `google/fonts` files are the same fonts under the same license, variable, with an `opsz` axis the frame does not use.
2. **The worker is not left running.** The permission layer refused a scheduled task and a detached process; a
   session-scoped process would die with the session. The command for Samuel is under "To finish".
3. **The test choice for the Roundup was deleted** so that Sunday's Roundup prints the rule's pick unless Samuel
   chooses. The two done run requests stay in the queue table as the proof.
4. **The render frame changed** (header hidden, the wide frame fitted): the first renders were not fit to post.
5. **`portwatch_chokepoint_transits` goes through the archive sync**, not through the Redivis restore list, so the
   Redivis configuration is unchanged.
6. **The cards were recomputed** on this machine before the renders, as session 170's hand-over asked; nothing moved
   but the timestamps.

## To finish (Samuel)

- **Register the worker once** (PowerShell, as yourself; it starts at log on and restarts after a failure; the log is
  `runs/findings_worker.log`):

```
$py = "C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe"
$a = New-ScheduledTaskAction -Execute "cmd.exe" -Argument ('/c ""' + $py + '" warehouse\analysis\findings\worker.py --loop 60 >> C:\Users\lossa\Documents\erw\runs\findings_worker.log 2>&1"') -WorkingDirectory "C:\Users\lossa\Documents\erw"
$t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$s = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ERW findings worker" -Action $a -Trigger $t -Settings $s -RunLevel Limited
Start-ScheduledTask -TaskName "ERW findings worker"
```

  To remove it: `Unregister-ScheduledTask -TaskName "ERW findings worker" -Confirm:$false`. Until then, to run a queued
  request by hand: `python warehouse/analysis/findings/worker.py --once`.
- The report of this session and the landing notes reach main with session 174's landing (`wip/173-land` is pushed).
