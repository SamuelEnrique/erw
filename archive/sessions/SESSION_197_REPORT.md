# Session 197 report: the planner, built and unarmed

11 October 2026, 21:33 to about 21:55 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/197-planner`, from `main` (it does not depend on sessions 195 and 196), pushed as `wip/197-planner`. Model spend USD 0, no model call. No pull. No data lock taken.

## Read these first

- **Not landed, for the reason of sessions 195 and 196:** `main` fails GitHub's check on five tests of sessions 153, 183 and 190, so no code branch merges. Looked again at 21:42 UTC: `main` is still `27a10ea0`. The work is complete and tested, on `wip/197-planner`. It changes no page.
- **The planner is built and off.** `python scripts/planner.py check` on this machine prints "planner: off" and refuses. Nothing runs until a person writes `planner: on` in `docs/roadmap.md`.
- **`docs/roadmap.md` is the empty template:** six headings, one line each that says what goes there. Tonight's roadmap goes into it.
- **It is a prompt builder.** No model call. Every sentence of a planned chain is the roadmap's own, a rule of `queue/CHAIN_TEMPLATE.md`, or one of the planner's fixed lines.
- **One thing to know before turning it on:** "Status" needs two start hours, an earliest and a latest, both in UTC. One hour alone cannot say when a night ends (item 2 below).

## What to review

No page changed. To see the planner work, on a machine with the repository:

1. `python scripts/planner.py check`
   - Prints "planner: off", then every reason it would not run: the planner is off, "Status" states no budget, no start hours and no cutoffs, "This week" has no open item. Exit 3.
2. `python scripts/planner.py draft --dry-run --roadmap tests/fixtures/roadmap_sample.md --machine sample --role code`
   - Prints "planner: on", then "would write queue/next/199-planned-the-battery-page-says-which-strategy-its.md:" and the whole chain. Nothing is written.
   - First line: "PLANNED by scripts/planner.py from docs/roadmap.md as of <time>".
   - Rule 1 is the precheck; rule 12 the queue step; rule 6 reads "Pulls: none"; rule 11 holds the start hours (13:00 to 05:00 UTC) and the two cutoffs of the sample.
   - Two sessions, 199 and 200. Only 200 says "Landing: this session lands".
3. The same command without `--machine sample --role code`, today: refused, "the budget is reached: samueloldlaptop has 6 sessions for 2026-10-11 UTC, and the budget is 3". The budget stop on this machine's real day.
4. `python scripts/chain_queue.py next --dry-run`: as before this session. "would write to erw_health: step idle ...", the one line, "would take the machine off duty". Exit 3.
5. Read `docs/roadmap.md` (the template), `docs/machines.md`, "The planner", and `queue/README.md`, "The planner".

## What was built

- `scripts/planner.py`: `check`, `draft`, `--dry-run`, `--machine`, `--role`, `--roadmap`. Exit 0 drafted (or nothing against running), 3 refused, 1 could not, 2 bad input.
- `docs/roadmap.md`: the template. Sections "Status", "This week", "Rulings", "Holds", "Input from Ben and Khalid", "Review log".
- `scripts/chain_queue.py`: with nothing waiting and the planner on, `next` runs the planner; a chain it writes is committed alone, pushed to `wip/<name>` and taken, exit 0. Off, or refused: idle exactly as before.
- `queue/CHAIN_TEMPLATE.md`: one sentence more in the last rule. `queue/README.md` and `docs/machines.md`: "The planner".
- `tests/test_planner.py` (30 tests) and `tests/fixtures/roadmap_sample.md`.

## How the roadmap is read

- **Status**, one line each: `planner: on` (anything else, or no line: off); `budget: N sessions a day per machine`; `earliest start: HH:MM UTC`; `latest start: HH:MM UTC`; `deploy cutoffs: HH:MM to HH:MM UTC; ...` or `none`.
- **This week**: `N. [ ] title` is open, `N. [x] title` closed. Indented under it: `machine: code` or `data`; `where:`; `done:`; `rulings:` (one a line); and where wanted `session:` (up to three), `cap: USD n`, `lands: yes` or `no`.
- **Rulings** and **Holds** are pasted into every planned chain as they stand. The other two sections are for people.

## When it refuses

Every reason is printed; exit 3; nothing is written.

- The planner is off.
- The roadmap is older than 7 days (its last commit; the file's own time when it holds an edit not yet committed).
- `queue/next/` already holds a file.
- The machine is at its budget of sessions for the UTC day.
- The hour is outside the start hours.
- "Status" does not state the budget, a start hour or the cutoffs, or states one that cannot be read.
- "This week" has no open item for the machine's role that was not planned before.
- The item does not say where or what done means, asks for more than three sessions, or names something a planned chain never does.

## The hard stops, each tested

- The budget and the start hours of "Status".
- The deploy cutoffs and the start hours are copied into every planned chain (rule 11); a chain without them is not written.
- An item that names a pull, a migration, a secret, a release-gate change, a change to `CLAUDE.md` or a permission file, or a deletion is refused. It is not skipped for the next item: it waits for a person's own prompt.
- One to three sessions; at most one lands, the last.
- An item is planned once: an item already in a planned chain, waiting or taken, is not taken again.
- The file is checked before it is kept: its name by the chain queue's own rule, its first line, the precheck as first rule, the queue step as last, no em dash, no unfilled blank, "Pulls: none".
- A planner that breaks does not break the queue step: the machine idles.

## Checks run

Outputs under `runs/session197/`.

| Check | Exit | Result |
|---|---|---|
| `tests.test_planner` | 0 | 30 tests, first run |
| `tests.test_planner` with the queue's own tests (188: queue, idle, precheck) | 0 | 95 tests |
| `python scripts/planner.py check`, this machine | 3 | "planner: off", refused |
| `python scripts/planner.py draft --dry-run`, the sample roadmap, this machine | 3 | refused: the budget (6 sessions today against 3) |
| The same for `--machine sample-machine --role code` | 0 | a chain of two sessions printed; `queue/next/` still empty |
| `python scripts/chain_queue.py next --dry-run` | 3 | idle, as before the session |
| Whole suite, clean copy, at `fefb5367` | 1 | 3,358 tests, 6 failures: the same 6 that fail on a clean copy of `origin/main` (sessions 149, 153, 183, 190), none of this session's |

- The printed chain's name, `199-planned-the-battery-page-says-which-strategy-its.md`, passes the chain queue's name rule: the test takes it with `chain_queue.waiting`.
- **Not run:** a real `draft` on this machine (the planner is off, and the repository's queue is not written to by a test). The planned chain's commit and push in the queue step are tested with stand-ins for git, not against GitHub.
- **Not verified:** nobody has run a planned chain. The first one is the test of whether a session can work from it.

## The landing

- **Not made:** `main` fails "Tests (tests/)" on GitHub (session 195's report, first bullet).
- No snapshot taken, none needed: nothing was pushed to `main` or to a `task/` branch. The session changes no page.
- Pushed: `wip/197-planner`.

## To finish

- When the five tests pass on `main`, each its own command:
  1. `git checkout task/197-planner`, `git merge origin/main`; the whole suite in a clean copy
  2. `python scripts/freeze.py status`
  3. `node site/scripts/snapshot-live.mjs take s197-before`
  4. `git push origin task/197-planner`
  5. after the deploy: `node site/scripts/snapshot-live.mjs take s197-after`, then `compare s197-before s197-after` (expected 0 differences: no page changed)
  6. delete the remote `wip/197-planner`
- This branch does not hold sessions 195 and 196. The three land in any order; 196 needs 195 first.
- To arm the planner, once it is on `main`: fill "Status" and "This week" of `docs/roadmap.md`, write `planner: on`, commit and push.

## Decisions made without you

- **Two start hours, not one.** The prompt names "the latest hour a session may start". A single hour of the day does not say when sessions may start again, so "Status" takes `earliest start` and `latest start`; the span may pass midnight.
- **All times in the roadmap are UTC.** A Pacific hour would need a time-zone table that not every machine's Python holds; I did not test which do.
- **The budget's day is the UTC day**, and its count is a floor: the sessions of chain files the machine took from the queue that day, or the reports committed that day that name the machine, whichever is larger.
- **An item is planned once**, without the planner writing to the roadmap: it looks for the item in the planned chains already in the queue. Otherwise an item left open would be planned again each time the queue emptied.
- **An item that names a forbidden thing is refused, not skipped.** Skipping would run the week out of order.
- **The session number** is one above the highest known on any branch on the machine and in the last 30 days' commit subjects. From `archive/sessions/` on `main` alone it would have been 195, which three unlanded sessions already hold.
- **The planned file's number is its first session's number** (`199-planned-...`), as the README's own example names a chain.
- **The planned chain is pushed to `wip/<name>`**, not to `main`: a push to `main` deploys.
- **Each session's long end is 2:30**, a fixed line: the roadmap's items carry none.
- **A cap named by an item is split evenly** over its sessions.
- **The sample roadmap is in `tests/fixtures/`**, not in `docs/`, so no page and no reader takes it for the roadmap.
- **Not landing on a red `main`**, as in sessions 195 and 196.

## For Samuel's ruling

1. `main` still fails GitHub's check (session 195, item 1). Sessions 195, 196 and 197 wait on `wip/` branches.
2. "Status" asks for two hours, `earliest start` and `latest start`, in UTC. Confirm, or name the one rule you meant by "the latest hour a session may start".
3. The budget counts what git can see of a machine's day. A chain pasted by hand whose reports do not name the machine is not counted. Whether each session should write one line to a per-machine log instead.
4. An item is planned once, and is planned again only if a person rewrites it. Confirm, or rule that a session marks its item closed in the roadmap.
5. Two machines planning in the same minute can take one session number. Whether the number should come from a counter in the cloud.
6. Whether a planned chain may ever land more than a page in review: today a planned chain may land any page its item names, with the snapshot rule.
7. The list of what a planned chain never names is matched by words ("pull", "migration", "delete", ...). It can refuse an innocent item ("pull request"), and a person then writes that prompt. Confirm the list.

## The prompt

Chain of 11 October (day), sessions 195 to 197; its text for this session: "Session 197: the planner, built and unarmed. Long end 2:30. Model spend USD 0. Pulls: none. Branch task/197-planner", with the roadmap's six sections, `scripts/planner.py` (`draft`, `--dry-run`, `check`), the closing step in `queue/CHAIN_TEMPLATE.md` and `scripts/chain_queue.py`, the hard stops, `tests/test_planner.py`, and the two documents.
