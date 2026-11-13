# Session 4010 report: land-f, this window's demand-revision fix and reports

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 16:49 UTC. Opus 5.5. Model spend: USD 0.

## What `wip/w2-land-f` holds

- **The commits:** land-e (`96489ad29`) with `wip/w2-4000` merged (`47c595dc9`), then `origin/main` merged after the lock (`ccbc42704`, 17:16 UTC; `build_llms.py --check` exit 0 on it).
- **This window's fix of session 4009:** a Digest's US48 demand peak that EIA revised after the issue is a note, not a failure.
- **Reports and work:** the reports of sessions 4004 to 4009, chain 228's note so far, and `suite_batches.py --verbose` with its test.
- **No new row was requested** when it was built. Window 4's branch past `ea34a1ea8` is unrequested code and is not in it.
- **The gate waited for the lock** from 16:49 to 17:15, behind window A's gate (`c227-gate`).

## The gate

- **The first gate** (`ccbc42704`, 17:15 to 17:47 UTC):
  - the suite (8,822 OK), the build and the hand checks passed;
  - **check-values still failed `/digest/2026-11-12`'s demand line, with no revision note on the page.** Not landed.
- **Why the note was missing, found under node with the site's alias loader** (`node --import ./scripts/alias-register.mjs`, on the 12 November issue):
  - `digestRevisions` returned the revision (488,341 MW) and `digestMarkdown` built the note.
  - The news index's hold (21 October) then rewrote the story sections by their lines' places in the issue as written. "What moved" begins exactly where the notes were inserted, so its splice began on the notes and removed them.
  - **That predates this chain.** Any revised figure in an issue whose story sections are held lost its note. The 21 October issue kept its fuel note only because its sections fall differently.
- **The fix** (`site/lib/digest.ts`):
  - The notes go in after the hold, at the same place. The hold changes only lines after "The numbers", and the chart step reads its shift from `out.length`.
  - One note per key: the demand line is printed twice under one key.
  - Under node: the 12 November page shows its note once, and the 21 October note is as before. `tsc --noEmit` reports 0 errors.
  - Test 4010 (3 tests); the digest tests pass.
- **The second gate:** started at 17:51 UTC on `943295956` (land-f with the fix). It waited for the lock behind window A's `c227-gate2`. Meanwhile window 4 asked for row 5 (`wip/4250-forecast` at `2fc4d9ac8`; to `279dd3121` only a report), which was merged in before the gate took the lock: `3b1aae438`. The forecast's tests, 4010 and 2207 pass, and `build_llms.py --check` exits 0.
- (its result and the landing: written when they come)

## Decisions made without you

- **This window's own fix is gated like any row,** with no request file of its own; the note records it.

## For Samuel's ruling

- None.
