# Session 6291 report: file 284 taken a thirteenth time; the probe is refused again (samueloldlaptop, 15 November 2026)

Energy Research Warehouse (ERW). The owner again asked for the queue step and the chain it prints, run unattended until the step exits 3. The step (`scripts/chain_queue.py next`, about 01:10 UTC on 15 November 2026) took `284-day-18-november-oldlaptop-ask-continued.md` again. 285 belongs to the data machine and was left. 300 is still waiting.

**In one line: the API refused the probe the file names (`eval_site.py --session 6291 --set heldout --only h30 --cap 0.40 --day-cap 20`, run in `erw-6100` on `wip/6100-ask` at d2a73f136) at USD 0.0000, with "You have reached your specified API usage limits. You will regain access on 2026-12-01". No step was done, no next file was written, and file 284 is back in `queue/next/`.**

- Precheck: exit 0 ("session 6291"; USD 0.00 spent today in 0 calls). Freeze: none (`scripts/freeze.py status` exit 0).
- Session number 6291: free in the reports and the remote branches.
- The probe's run file (`eval_s6291_site_heldout_run.json`, h30 recorded as an error, no cost) and its output were moved out of the worktree to `runs/s6291/` (not in git). `erw-6100` is clean.

## Decisions made without you

- **The probe was run**, as in sessions 6280 to 6290: a refusal costs nothing, and only a probe shows whether the limit was raised. It was not.
- **File 284 is moved back**, and the queue step's local "taken" commit and the return are folded into this one commit (`git reset --soft origin/main`): on origin, 284 never left `queue/next/`.
- **The queue step was not run again, so the chain stops without its exit 3**, as in sessions 6220 and 6280 to 6290.
- **Not pushed, so no deploy and no snapshots.** Twelve sessions each spent a deploy and two snapshots to record the same refusal. This commit is on the local main only; the next push from this machine carries it (it touches only this report). To push it now: take rule 8's before snapshot, `git push origin main`, wait five minutes, take the after snapshot and compare.

## For Samuel's ruling (default in brackets)

- Session 6282's ruling stands unchanged: raise the key's monthly limit in the Anthropic console [otherwise chain 284 waits until 1 December], or allow a `hold:` line that `chain_queue.py next` skips until a date [not built]. Until then, every request for the plain queue step takes 284 and does nothing. Taking a file by name (`chain_queue.py next --file ...`) avoids the loop.
