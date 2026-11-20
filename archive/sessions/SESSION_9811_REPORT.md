# Session 9811: one finding held back until its fix lands

Energy Research Warehouse (ERW). 20 November 2026, 19:50 to 20:03 UTC. Chain 610, part B, the desktop's third window.

## What was done

- **One finding held back until its fix lands.** The chain's rule for a finding of high severity: it is fixed on a branch whose commit says only "hardening", its landing is requested at once, and its detail is written only after the landing.
- The fix is `wip/9811-hardening` at `f675174b3`, one commit on `origin/main` at `26dfe42cc`, with a new test (`tests/test_session9811.py`, which runs `site/scripts/test-heldrow-ids.mjs` under node) that fails on the code before the fix and passes after it, and two older tests' pins brought to the new line.
- Tests on the head: the 29 test files that name the changed code and the 14 that name the changed component: 494 passed, 58 skipped, 0 failed (2 min 8 s).
- Landing requested: row 7 of `docs/state/landing_request_desktop_w3.md`.

## Not done

- Not built here; the whole suite not run here (this window runs no gate). `npx tsc --noEmit` was run on rows 7 and 8 merged (session 9812): no error in a changed file.

## Needs the key

- Nothing.

## For Samuel's ruling

- Nothing until the landing; the detail follows in `docs/security.md` then.
