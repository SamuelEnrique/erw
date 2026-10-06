# The freeze hold: what the scheduled jobs do while a reviewer is on the site

Session 131. **Built, tested, and not switched on.** While `warehouse/config/freeze_hold.yaml` says `enabled: false`
every scheduled job does exactly what it did before this session, freeze or no freeze.

## Why

A review freeze (`REVIEW_FREEZE`, `CLAUDE.md` rule 9) bound sessions and not the clock. On 5 October 2026, inside a
freeze, the daily run loaded the live set and committed to main twice, and Vercel rebuilt production twice (16:20 and
16:29 UTC). A before and after snapshot of the live pages showed 179 differences that no person had made.

## The rule

A scheduled job asks one question, `python scripts/freeze.py hold`, and gets one of two answers.

- **run**: no freeze today, or the hold is not switched on. Nothing differs from before.
- **hold**: the site is frozen (the file is there and today is from its start to its end, or the file cannot be read)
  **and** the switch says `enabled: true`.

Under **hold**:

| | What happens |
|---|---|
| **Kept live** | The 15-minute prices (`latest-prices.yml`) and the hourly network (`hourly-network.yml`). Their workflows and scripts are not touched by this design, and a test says so. A visitor expects both to move. `chain-watch.yml` too: it only reads |
| **Fetched, as on any day** | Every pull, the consolidation, the validator, coverage, the archive (the bucket `erw-archive`) and the Redivis draft. The warehouse stays whole and current; only its public face waits |
| **Held: the live set** | `warehouse/supabase/load.py` is not run (the daily script records `supabase_load skipped: held by the review freeze`). The Sunday Roundup's one load, the cost ledger, is skipped the same way |
| **Held: every scheduled commit** | The daily run's files (status, coverage, the digests, the news tables, the site's data files), the health summary, the Roundup and the weekly vacuum's sizes are committed to the branch `held/scheduled`, never to main. No scheduled commit reaches main, so none redeploys the site |
| **Still sent** | The Energy Digest and the Roundup by email, and the failure alert |

## How the held files come back

`scripts/held.py`, three commands, each in the workflows.

1. **`restore`, at the start of every scheduled run.** No branch `held/scheduled` on origin: nothing happens. A branch:
   every file the held runs committed is written into the working tree over main's copy. So the second day of a
   freeze starts from the first day's state (the stories already scored, the archive's manifest, the status history),
   as it would have started from main.
2. **`commit`, in a held run, where the push to main was.** The commit is built without touching the checkout: its
   parent is the branch's tip (main's, on the first held day), its tree is the parent's with this run's files. The
   branch keeps its own list of every held path (`.held/files.txt`), which never reaches main.
3. **The first run after the freeze** is an ordinary run. `restore` has put the held files in its working tree; the
   commit step adds them to its own commit to main, pushes, and calls **`clear`**, which deletes the branch. Its
   loader then writes whatever differs between the tables and the live set, however many days that is.

**Queued where.** The data is queued in the archive and the Redivis draft (every table, every day of the freeze). The
files are queued on `held/scheduled`. Nothing is queued only on a runner.

A change a person lands on main during the freeze (an approved deploy) is kept: `restore` writes only the files the
held runs changed. Where a held run and a person both changed one file, the held copy wins, which is the daily run's
standing rule for a conflict (its version is built from the newer data).

## What you must approve to switch it on

1. **The one line.** `enabled: true` in `warehouse/config/freeze_hold.yaml`, landed by the usual route. With it,
   change `tests/test_session131.py`, `test_it_is_not_switched_on`, which exists to stop the line changing by accident.
2. **That Vercel does not build `held/scheduled`.** On 5 October every commit on a `wip/` or `task/` branch read
   "Canceled by Ignored Build Step" in GitHub's record of Vercel. I could not read the rule itself. If it is "build
   only main", `held/scheduled` is covered. If it names `wip/` and `task/`, add `held/`. A preview build would not be
   production, but it would be a build per held day.
3. **That email goes out during a freeze** about pages the site does not yet show. The digest's links to that day's
   page will open the site's in-review page until the freeze ends. Say so if email should hold too; it is one more
   guard in `run_daily.sh`.
4. **That the price board and the network move during a freeze.** That is the design: a reviewer sees live prices and
   a live network, and everything else still.
5. **The first run after a freeze is a long one**: it loads every held day at once. With the loader fix of this
   session (`docs/loader_stamps.md`) that is the new days' rows, not whole tables.
6. **A manual run during a freeze is held too.** `workflow_dispatch` goes through the same steps. To load on purpose
   during a freeze, a person runs the loader from a data machine, with the snapshot before and after.

## What it does not do

- It does not stop a session. Sessions follow `python scripts/freeze.py status`, as before.
- It does not pin production. A person's approved deploy during a freeze deploys main as it is, without the held files.
- It does not hold the 15-minute prices' table (`latest_prices`) or the network's object in storage.
- It does not hold the Redivis draft, which no visitor sees and nothing releases.

## Tested

`tests/test_session131.py`: the switch (only a plain `enabled: true`), the answer for every pairing of freeze and
switch, the command's exit code; the held files on real git repositories (a held run moves neither main nor the
checkout; the next run starts from the held state; a person's change on main survives; the run after the freeze brings
everything to main and deletes the branch); every scheduled push to main and every scheduled load, found in the
workflows' own text, sits behind the hold; the three kept-live jobs are byte for byte main's; and the daily script's
own lines, run in bash, skip the load and nothing else.

Not tested, because it cannot be without pushing to GitHub: a held run on GitHub's runner. The first held day should
be watched: `python scripts/held.py status` lists what the branch holds.
