# Session 5185 report: the stack's first part has landed; eight rows closed

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5182-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: three GET requests of production as a visitor (no cookie, no token). Nothing built, nothing landed by this window, no warehouse data written.

Clock: precheck 20:57 UTC, the proof 20:57 UTC, the records by 20:59 UTC. Inside the long end of 1:00.

## Read these first

- **Landed: sessions 5150 to 5158 are on `main` and live since 20:47 UTC** (`ad7f16ca6`, the desktop's session 4012). The desk's own words in landing row 23: every step of `land_check.py` passed; the gate's checks did not trip the new limits; snapshots before and after, 0 differences.
- **Eight rows of the list are closed**: 2 and 15 to 21. The list now reads 9 closed, 2 fixed and not yet live, 15 rulings, 8 noted; none open.
- **Proven on production at 20:57 UTC, as a visitor**: `/internal/lock` at a request a browser marks cross-site answers 303 and sets no cookie; marked same-origin it clears the two cookies as before. Row 15 is live.
- **Not yet live**: row 27 (the policy names one Supabase project). It is in the row's later head, "in the desk's next gate" by the desk's note. Production's policy still reads `connect-src 'self' https://*.supabase.co`, as expected until then.
- **Live now and off**: the two settings (`USAGE_VISITORS`, `USAGE_TOOL_PAGES`). Nothing changes until you set one.
- **Found by the way, a fault of mine in session 5184's reading, corrected**: I first compared `main` with a commit of my own branch and took my own unlanded change for a change on `main`. Compared from the right commit, the files that had moved on `main` were my stack's: that is how the landing was seen.
- The scan of the git history is still running (80 minutes at 20:57 UTC).

## What was done

- **The landing read**: `5411fef7d` (row 23's first head) is an ancestor of `origin/main`; `f300710e7` and the later heads are not. Landing row 23's state on `main` says so in the desk's words.
- **The list**: rows 2, 15, 16, 17, 18, 19, 20, 21 marked closed, with the landing's commit and time; row 15 with the proof; the table "Where the list stands" and a sentence on what landed (`runs/s5185/close_rows.py`, each replacement matched exactly once).
- **`docs/security.md`** and **the note**: a paragraph each on what landed.
- **Sessions 5184's steps, folded in here**: no ruling answered (the roadmap's "Rulings" unchanged; no prompt for this window); the standing tests on the merged tree 108 passed; `verify_rls.py --catalog` exit 0, nine steps.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5184 (window P2)"`, `"session 5185 (window P2)"` | 0, 0 | on duty |
| `git merge origin/main` (twice) | 0, 0 | merged |
| `git merge-base --is-ancestor 5411fef7d origin/main` | 0 | the first part landed |
| the same for `f300710e7` | 1 | the second part not yet |
| `pytest` on the eleven standing test files, the merged tree | 0 | 108 passed |
| `warehouse/supabase/verify_rls.py --catalog` | 0 | PASS, nine steps |
| `runs/s5185/lock_proof.py` (three GETs of production) | 0 | as above |
| `pytest tests/test_session5163.py` and the list's other readers, first run | 1 | my new table cell held a second number the test read as a row; reworded |
| `pytest` on this window's 19 test files and `test_session371` | 0 | 180 passed |

- **Not run:** the build, the whole suite (the desk's gate ran both for what landed).
- **Not verified on production:** the four new limits (proving one needs hundreds of requests), the secrets' scan (a property of the source). The gate proved the routes still answer.

## Decisions made without you

- **Three requests of production**, as a visitor, for the one landed change a visitor can see. A request to `/internal/lock` without the internal cookie changes nothing for anyone.
- **Session 5184 has no report of its own**: its two reads are in this one, since the landing was found in the middle of them.
- **No worktree removed**: `erw-p2-5150` holds this chain's branch, which has not landed.

## For Samuel's ruling

1. `/privacy`, the sentence on limits (session 5162's ruling 1): the limits on the map's cards and the email's links are live now, and the sentence does not name them. Default: a session adds them; the page says less than the site does, and nothing false.

## The prompt

`queue/done/259-day-16-november-portable-p2-security-continued.md`, "Sessions 5183 to 5190: chain 247's unfinished steps", steps 2, 4 and 5.
