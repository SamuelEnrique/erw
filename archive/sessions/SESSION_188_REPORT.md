# Session 188 report: the plumbing for continuous work

11 October 2026, about 07:05 to 07:55 UTC, unattended, one agent of a chain, in the worktree `erw-188`. Branch `wip/188-plumbing`, not pushed: the orchestrating session lands it. Model spend USD 0, no model call. No pull: no request to any publisher. No e-mail sent, no table written, no migration.

## Read these first

- Built, all four parts: `scripts/precheck.py` (six checks, a report and one line on a failure, never waits); `scripts/chain_queue.py next` (`queue/next/` to `queue/done/` in one commit, or idle); `scripts/duty.py` and a second step of `chain-watch.yml` (the idle alarm, per machine); `/internal/waits`.
- **`CLAUDE.md` is not edited, and the permission allowlist is not either.** An agent's brief cannot authorize a change to either; only the owner can. The line is ready as a patch that applies cleanly (`runs/session188/claude_md.patch`, text under "For the coordinator"). `docs/machines.md` and `queue/CHAIN_TEMPLATE.md` name the precheck.
- **No migration and no new secret.** On duty is a row `duty:<machine>` of `erw_locks`, through migration 016's functions. Idle is a row of `erw_health` with step `idle` and status `ok`: the table's check allows only ok, skipped, retried and failed.
- **`/internal/waits` reads the reports when the site is built**, as `build-content.mjs` reads `docs/`: no JSON is committed. On this branch it lists 14 of the 15 reports after session 171, 81 items, this report's eight among them. Session 171 as the last one answered is this session's guess (first item below).
- Nothing a visitor sees changes: every page is in review, and the new page answers 404 without the internal cookie.

## What to review

After the landing. Internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token, "Open the internal view".

1. Open `https://erw-flame.vercel.app/internal/waits`.
   - Heading "Waits for Samuel (internal)". Under it one grey line ending "Read from the repository when the site was built," and a time.
   - A box: "Listed: the reports after session 171, the last one marked as answered (on 2026-10-09)." with a link `archive/sessions/LAST_ANSWERED`.
   - Three counts: Reports since, With something waiting, Items waiting. On the build of this branch: 15, 14, 81. After the landing they are higher if session 187's report is on main.
   - First report: "Session 188: the plumbing for continuous work", the eight items of "For Samuel's ruling" below.
   - Scroll to "Session 186: What a generator earns, decisions": "11 October 2026, 7 items wait, the report on GitHub". Six numbered items under "For Samuel's ruling", then one from "Read these first".
   - Under each item, grey: `Under "For Samuel's ruling", line 153`. Click "line 153": GitHub opens the report's source at that line.
   - Click "the report on GitHub": the report.
   - Under the report: "Decided without you in this session: 12 (they do not wait; open to read them)". Click it: twelve items unfold.
   - Scroll to session 176: each proposed cut is one item, written as "#: 1", "Cut: ...", "Saving: ...", "What it costs: ...".
   - At the bottom: "Not listed, because nothing in them waits ...: session 174 (6)."
2. If the page says "The session reports could not be read when the site was built", Vercel's build did not see `archive/`. Nothing else is affected. Tell the next session: the fallback is a committed file.
3. To mark reports as answered: on GitHub open `archive/sessions/LAST_ANSWERED`, change `last_answered: 171` to the newest report you answered and `on:` to the day, commit. After the deploy the page lists only later reports.
4. As a visitor (a private window, no token): `https://erw-flame.vercel.app/internal/waits` answers the site's 404 page, with none of the page's words.
5. On a phone (390 px): screenshot `runs/session188/shots/waits-phone.png` (in the worktree); the page does not scroll sideways.

On the machine, from the main copy after the merge (each prints, sends nothing):

- `python scripts/precheck.py --what "a look" --dry-run`: six lines, each "pass", then "precheck passed: 6 of 6; dry run, so the machine is not put on duty".
- `python scripts/chain_queue.py next --dry-run`: "would write to erw_health: step idle ...", the line it would send, exit 3.
- `python scripts/duty.py check --dry-run`: "quiet: no machine is on duty".

## What was built

- **Precheck** (`scripts/precheck.py`). Lines: `github_credentials`, `push_dry_run` (to `wip/precheck-<machine>`, 90 s, cannot prompt), `claude_signed_in` (`claude auth status --json`, no prompt sent), `role_file`, `env_keys`, `daily_cap`. Exit 0: the machine goes on duty. Exit 1: `runs/precheck/<time>-<machine>.md`, one line through `alert.py`'s sender, nothing else. `--dry-run` prints the line and marks nothing.
- **Chain queue** (`scripts/chain_queue.py`, `queue/README.md`, `queue/CHAIN_TEMPLATE.md`, `queue/next/`). `next`: the lowest number first; one commit of the move alone; the new path on the last line. Empty: health row, one line, off duty, exit 3. Names of session 59's task queue are refused. The template's rule 1 is the precheck and its last rule the queue step.
- **Idle alarm** (`scripts/duty.py`, `scripts/githooks/post-commit` and `pre-push`, `.github/workflows/chain-watch.yml`). The hooks renew the mark at each commit and push, from the main checkout and from a worktree of it. The check: quiet under 30 minutes, one line at 30, again at 90, 150 and so on; a lapsed mark said once; each machine by itself. The step runs under `warehouse/health.py` after the duplicate-start step; the job's timeout went from 5 to 8 minutes for the second step.
- **Waits page** (`site/app/internal/waits/page.tsx`, `site/lib/waits.ts`, `site/scripts/build-waits.mjs`, `archive/sessions/LAST_ANSWERED`). Listed: every item of a section headed for the owner, and any item elsewhere that says so itself. The prompt section is not read. Table rows are said with the table's column names. No script in the page: the fold is the browser's own.
- **Documents:** `docs/machines.md` ("Continuous work"), `docs/release-gate.md`, `docs/tools.md`.
- **Tests:** `tests/test_session188_precheck.py` (20), `_queue.py` (17), `_idle.py` (28), `_waits.py` (12); `site/scripts/test-waits.mjs` (583 cases, 241 lines of the real reports compared with the items); `site/scripts/check-internal-waits.mjs` (25 checks on a built site).

## Pulls and spend

- Publishers: 0 requests. Model: USD 0, no call.
- GitHub: `git push --dry-run` four times (the precheck's own check, once a run; a dry run creates nothing). No push.
- Supabase: reads only. `erw_locks` read four times with the service key (empty each time); the cost ledger's copy read by the precheck's dry runs. No row written.
- E-mail: none. Every send was `--dry-run` or a test's stand-in.
- `claude auth status` five times: it reports sign-in and starts no session.
- Nothing installed, no scheduled task. The local server on port 3188 was stopped.

## Checks run

Outputs under `C:/Users/lossa/Documents/erw-188/runs/session188/`.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session188_precheck`, `_queue`, `_idle`, `_waits` | 1, then 0 | first run: 1 failed, mine (a test read the wrong printed line); then 77 of 77 (`tests_188.out`) |
| `node site/scripts/test-waits.mjs` | 0 | 583 of 583 |
| Neighbours (91, 116 alerts, 59, 61, 53) | 0 | 81 tests |
| `npm ci`, then `npm run build`, under the build mutex | 0, 0 | `npm_ci.out`, `build_1.out`; `/internal/waits` is in the route list as dynamic |
| `npm run build` again after the page's change, and of the committed tree | 0, 0 | `build_2.out`, `build_3.out` |
| `check-internal-waits.mjs`, local, port 3188 | 1, 1, then 0 | first run 22 of 25: a visitor's 404 carried the page's title (fixed in the page), and two slips in the check; second run 24 of 25 (the check counted the menu's folds); then 25 of 25, and 25 of 25 on the committed tree |
| Workflow YAML parses; six steps; the new step mirrors the chain's | 0 | `workflow_yaml.out` |
| `precheck.py --dry-run` | 0 | six pass (`precheck_dry_run.out`) |
| `precheck.py --dry-run` with `DAILY_MODEL_USD=abc` for that one command | 1, as meant | the line printed, the report written (`precheck_dry_run_failing.out`, `precheck_failing_report.md`) |
| `chain_queue.py next --dry-run`, empty and with a stand-in file | 3, 0 | `chain_queue_next_dry_run_empty.out`, `_file.out` |
| `duty.py check --dry-run`, `duty.py status` | 0, 0 | "no machine is on duty" |
| Whole suite in the worktree, twice | 0, 0 | 3,161 tests, 220 skipped, while the work was still moving; then 3,162 tests, 220 skipped, at commit `a153f70d` (`suite.out`, 415 seconds) |
| `eslint` on the five new site files | 0 | `eslint.out` |

- **Visitor:** `/internal/waits` answers 404, title "ERW", none of the page's words; with `?token=` also 404.
- **Internal view:** 200, `private, no-store`, noindex; 14 reports newest first; 81 items, each linked to its line; the counts equal the built file.
- **Phone, 390 px, headless Chrome:** scroll width 390; no element past the edge; still 390 with a fold open.
- **Not run:** `check-routes` and `check-values` (no page they read was changed); the whole suite in a clean copy of the commit (the landing's step; the last commit after `a153f70d` changes this report only); any live write, so the duty mark, the idle row and a real line by e-mail are proven on stand-ins only.
- **Not verified:** that Vercel's build sees `archive/sessions/` (it sees `docs/` and `warehouse/metadata/`, which stand beside it); the hooks on macOS or Linux beyond the tests.

## Decisions made without you

- **`CLAUDE.md` and `.claude/settings.json` left as they are.** The patch and the three allow rules are written out below for a person to apply.
- **The idle row is step `idle`, status `ok`.** A status `idle` needs a migration of the table's check; none was written.
- **A passing precheck puts the machine on duty by itself.** `--no-duty` is for a session with a person at the keyboard.
- **A duty mark that cannot be written does not fail the precheck.** It is said on the screen, and the session runs unwatched.
- **`env_keys` asks for two keys beyond the setup scripts' lists:** `RESEND_API_KEY` and `DIGEST_RECIPIENTS`. Without them a machine can tell nobody anything.
- **`daily_cap` fails only when nothing could be read:** `DAILY_MODEL_USD` not a number, or neither Supabase's copy of the ledger nor a ledger file on the machine answered. Unset is the default, USD 1.00, and passes.
- **`claude_signed_in` uses `claude auth status --json`** (CLI 2.1.296 has it). An older CLI falls back to its credentials file or a key in the environment.
- **The idle alarm is a second step of `chain-watch.yml`,** not a workflow of its own: the database's schedule and the duplicate-start rule are already there.
- **The alarm reads the marks, not GitHub.** GitHub cannot say which machine pushed. A sign of work is the hooks' beat, a beat by hand, or a precheck.
- **The hooks beat from a worktree too.** The chain's own beat still does not (unchanged).
- **A chain from the template uses the duty mark and not `alert.py chain start`.** Both at once send two lines for one silence. The chain's mark and its check are untouched.
- **The mark lapses 16 hours after the newest precheck,** the chain mark's default.
- **`next` does not push.** A push to main deploys, and rule 8 governs it.
- **A file in `queue/next/` with another name is left and counted in the idle line,** never run. `NNN-code-` and `NNN-data-` are the task queue's.
- **The waits file is generated before each build and is not in git,** so no session has to regenerate it. If the reports' folder is missing the build still passes and the page says so.
- **A marker that cannot be read hides nothing:** every report is then listed.
- **"Decisions made without you" are folded under each listed report,** and a report holding only decisions is named in one closing line. They do not wait.
- **The page's title is sent only to the internal view.** The other internal pages send theirs with the 404; not changed.
- **Items are found by words.** A line that no longer waits can be listed, and one worded another way missed. The page says so.
- **The click steps of a report are not read** ("What to review", "What to click"): they quote the pages, this page's own name among the words.

## For Samuel's ruling

1. The last report you answered. The marker starts at 171: the chain prompt of 9 October answers session 171 (Virginia), and no later prompt answers a later report. Write the right number in `archive/sessions/LAST_ANSWERED`.
2. The line for `CLAUDE.md` ("Every session starts with the precheck ...") and three allow rules for `.claude/settings.json` (`precheck.py`, `chain_queue.py`, `duty.py`). Without the allow rules a session that asks for permissions stops at its own precheck.
3. Whether idle should be its own status in `erw_health`. It needs one migration; today it is the step's name.
4. Whether `chain_queue.py next` should push its move to main, so that two machines can share `queue/next/`. A push to main deploys. Today one machine draws at a time.
5. Whether a duty mark that cannot be written should fail the precheck. Today it is a note.
6. Whether the old chain mark (`alert.py chain start`, session 91) retires now that each machine is watched. Kept: it also counts another machine's pushes.
7. Whether one number is enough for the waits page. An older report with an unanswered item leaves the page when a newer number is written. Marking single items was not built.
8. The 16 hours before a duty mark lapses by itself.

## For the coordinator

1. Merge `wip/188-plumbing`. Files other sessions may touch: `site/package.json` (the three script lines), `site/.gitignore`, `docs/machines.md` (appended at the end), `docs/tools.md` (one row), `docs/release-gate.md` (one paragraph), `.github/workflows/chain-watch.yml`, `scripts/githooks/*`.
2. `CLAUDE.md`, if the owner agrees: `git apply --ignore-whitespace C:/Users/lossa/Documents/erw-188/runs/session188/claude_md.patch` (checked with `--check`: applies). It adds one paragraph before "## Repository layout":
   - "**Every session starts with the precheck** (session 188): `python scripts/precheck.py --what "session <N>"`, exit code read before anything else. Exit `1`: it has written its report under `runs/precheck/` and sent one line by email; the session stops and does not wait for a person. A chain's last session ends with `python scripts/chain_queue.py next`; a session that no other follows signs off with `python scripts/duty.py off` (`docs/machines.md`, "Continuous work"; `queue/CHAIN_TEMPLATE.md`)."
3. `.claude/settings.json`, if the owner agrees, beside the line for `alert.py`: `"Bash(python scripts/precheck.py *)"`, `"Bash(python scripts/chain_queue.py *)"`, `"Bash(python scripts/duty.py *)"`, and the three `PowerShell(...)` twins.
4. In the main copy after the merge: `npm ci` is not needed (no package changed); `npm run build` under the mutex; `node scripts/check-internal-waits.mjs http://localhost:<port>` on that build.
5. The whole suite in a clean worktree of the merged commit before the task push. `tests/test_session188_waits.py` runs `node site/scripts/test-waits.mjs`, which needs no package.
6. Snapshot before and after (rule 8). Expected: 0 differences on the 25 pages.
7. After the deploy, internal view: `node site/scripts/check-internal-waits.mjs https://erw-flame.vercel.app` compares production with a local `site/content/waits.json`; build locally at the same commit first. Or open the page and read the three counts.
8. The first live proof, from the main copy, when you choose (each writes or sends for real):
   - `python scripts/precheck.py --what "the chain of 11 October"`: writes the row `duty:samueloldlaptop` to `erw_locks`.
   - `python scripts/duty.py status`: what the check would say now.
   - To see the alarm once: commit nothing for 30 minutes; the next run of "chain watch" sends one line. `python scripts/duty.py off` ends it.
   - `python scripts/chain_queue.py next` with `queue/next/` empty: one row of `erw_health` (step `idle`), one line by e-mail, off duty, exit 3.
9. No migration to apply. No secret to add on GitHub: the step uses the five the chain's step already uses.
10. The hooks are live on this machine as soon as main holds them (`core.hooksPath` is `scripts/githooks`). Not on duty: they do nothing.

## Files a visitor-facing page could be affected by

- None expected. Every page is in review, so a visitor sees the in-review page before and after.
- `site/package.json`: `prebuild`, `predev` and `content` run `build-waits.mjs` after `build-content.mjs`. It writes `site/content/waits.json`, which only `site/lib/waits.ts` imports, and that only the new page.
- `site/.gitignore`: one line.
- New, read by no page for visitors: `site/app/internal/waits/page.tsx`, `site/lib/waits.ts`, `site/scripts/build-waits.mjs`, `test-waits.mjs`, `check-internal-waits.mjs`.
- Not touched: `site/lib/release.ts`, `site/proxy.ts`, `next.config.ts`, the root layout, the menu, `check-routes.mjs`, `check-values.mjs`, `snapshot-live.mjs`, any table, any other page.
- Outside the site: `.github/workflows/chain-watch.yml` gains a step; it reads `erw_locks` and may send e-mail to the fixed recipients, and writes one row of `erw_health` a run.

## Found, not changed

- The other internal pages (`/internal/findings`, `/internal/usage`, `/internal/costs`) send their title to a visitor inside the 404 ("Scanner drafts (internal) | ERW"). The fix is the one made here: `generateMetadata` that names the page only to the internal view.
- The test suite leaves an `.erw/worker/` folder in the checkout it runs in. That is how the precheck's first failing dry run here read no role file; `duty.state_dir` now looks for the folder that holds `machine.json`.
- `tests/test_session85.py` leaves `warehouse/output/raw/madeup_as_prices/<time>/manifest.csv` (a header line only) in the checkout the suite runs in. Removed from this worktree after each run; the test should write to a temporary folder.
- A heredoc in Git Bash on this machine turns two backslashes into one (the known trap, in a milder form than recorded).

## To finish

- Nothing is held on the branch. The eight items above are for the owner; the ten steps for the landing.

## Landing

LANDING: filled in by the orchestrating session

## The prompt

"Session 188 (long end 2:00): the plumbing for continuous work. (1) A precheck every session runs first and every chain file names: GitHub credentials present and a push dry run passes, Claude Code signed in, the role file present, .env keys present, the daily cap readable; a failed precheck writes a report and emails the same-day address instead of waiting. (2) The queue convention: queue/next/ holds prompt files in order; a chain's last session runs the next file there, moves it to queue/done/, and if the folder is empty writes "idle" to the health table and emails. (3) An idle alarm: a scheduled check that emails when a machine has run nothing for 30 minutes. (4) A "waits for Samuel" page at /internal/waits that collects every report's rulings since the last one he answered." Unattended, as one agent of a chain; model spend USD 0; no pull; no real e-mail; nothing pushed.
