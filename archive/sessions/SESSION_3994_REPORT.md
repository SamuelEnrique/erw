# Session 3994 report: the Energy Roundup of 15 November

Energy Research Warehouse (ERW). Chain 285, data machine (lab-desktop), 15 November 2026, 23:38 to 23:45 UTC. Opus 5.5. Model spend USD 0. No request to a publisher. `erw_health` read over `SUPABASE_DB_URL`; GitHub's API, 3 requests.

**Not published: no Roundup this week.** The owner's API key is at its limit.

- **The run** (`energy roundup`, run 43772350195, dispatched 23:00 UTC by the outside scheduler): the job ends "success" at the workflow level, but its steps "Commit the Roundup and the analysis" and "Send the Roundup by email" were skipped.
- **Why:** `write the Roundup` failed at 23:27 UTC: "news_roundup FAILED: anthropic.BadRequestError: Error code: 400 ... 'You have reached your specified API usage limits. You will regain access on 2026-12-01 at 00:00 UTC.'" No other key or route tried (the limit is the owner's setting).
- **The cost ledger's steps:** coverage row and archive ok, the Redivis draft ok; `ledger: live set` failed (its reason opens with the catalogue hold list; most likely the stale IEA source row of chain 279's ruling, read in the next job log).
- **Not a fault of this repository's code:** nothing to fix. The Roundup for week 46 can be written once the key answers (from 1 December), if wanted.

## Decisions made without you

- **No second dispatch of the Roundup:** it would hit the same limit.

## For Samuel's ruling

- **The key's limit** (set by you; access back 1 December): until then no Roundup, no Digest's model parts, no news or policy scoring. Default: wait for 1 December; nothing is tried with another key.
