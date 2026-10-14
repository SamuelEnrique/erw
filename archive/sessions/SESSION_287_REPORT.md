# Session 287 report: the afternoon note

14 October 2026, 19:35 to about 19:50 UTC, unattended, on lab-desktop (the data machine), the last session of the daytime chain of 14 October. Branch `task/287-afternoon-note`. Model spend USD 0: no model call. Pulls: none.

## Read these first

- **`docs/state/morning_2026-10-14.md`, the new section "Afternoon":** what the chain refreshed and scheduled (the board's ERCOT rows on this machine's daily run; everything else at its cadence or its source), ERCOT's pause of data-center energizations found in its August decks, the twelve new drafts and their verdicts (2 strong, 6 usable, 4 drop), the landings, and ten rulings.
- **Sessions 284, 285 and 286 landed, each with 0 differences on the 25 snapshot pages.** Session 286's first push failed two earlier sessions' tests; fixed and landed on the second.
- **The code machine landed session 280 at 19:19 UTC,** during this chain; it was merged before sessions 286 and 287 landed, and session 286 took a second before snapshot after its deploy.

## The landing of session 286, recorded here

- Before `s286-before` 19:09:46 UTC, and `s286-before2` 19:24:56 (after session 280's deploy; `s286-before` against it: 0 differences); pushed 19:10:02 (`3d253b55`): check run 116049437758 failure 19:14:10; fixed and pushed 19:24:45 (`4aeb415e`): check run 116056523826 success 19:33:12 (workflow run 38623443627); merged `4621b7f7`; deployed 19:34:30; after `s286-after` 19:34:30; `compare s286-before2 s286-after`: 0 differences. Expected: documents, tests and the motion proofs; no page changed.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 287"` | 0 | six of six |
| `tests.test_session250` (the notes' form) | 0 | 8 tests |
| no em dash in the section and this report | | checked |

## Decisions made without you

1. **The section is appended to the morning note,** as the prompt asked, and nothing above it changed; ruling 54 of the morning list is answered in the section, not edited where it stands.
2. **This session's own landing is in no committed file,** as session 278 did: a commit to record it would be one more landing. It is in the chain's closing message and in `runs/session286/landing287.out`.

## For Samuel's ruling

- None of its own: the section's list is the list.

## Files

- Changed: `docs/state/morning_2026-10-14.md` (the section "Afternoon").
- New: this report.
