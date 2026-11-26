# Session 10238 report (chain 710, part D, the old laptop)

The small pages audited as a hostile first reader would: `/about`, `/resources`, `/shoulder`, `/attention`, `/subscribe`. The audit: `docs/reviews/small-pages-audit-2026-11-26.md`, its evidence in `docs/reviews/small-pages-audit-2026-11-26/`.

## What was done

- Every figure of each page's default view restated independently from its own files: `/shoulder`'s ERCOT from EIA's own workbook (2,132 of 2,132 monthly figures, the ten worst days of 2026), `/attention`'s default cell, rising rows and footer from the week files, the resource map's legend from its grid files, `/about`'s platform counts. All equal; one note counts two stories no week holds (finding 14).
- 14 findings: 4 medium, 9 low, 1 very low. Eleven words branches (`wip/audit-small-1` to `-3`, `-5` to `-12`) merged as `wip/audit-small-words` (`0f3979b6b`), drawn with the site's own code and read: pass; no figure moved. Three test-only branches for ruling (`-4`, `-13`, `-14`).
- Tests on the merge: the words tests and the 33 other test files reading a changed file: 655 passed, 33 skipped, 1 failed (`test_session1880`, the same 8 checks fail on clean origin/main: they expect the attention file of 6 November).
- No table written, no lock, no model call, no request to any service; the subscribe route was never called. Nothing on main but the audit, its evidence and this report.

## Decisions made without you

- The words of `/subscribe` and `/about` were treated as the audit's to fix (only `/privacy` and `/terms` are yours); their disagreements with the code are listed in the audit, not changed.
- The "(4 PM Pacific)" of `/digest/<day>` and `/roundup` was left alone: those are the Digest audit's pages.
- The resource map's drawing of ISO-NE's held queue rows was not made a new finding: it is the map audit's open ruling (faults row 6, `wip/alt-map-1`), the same tables on another tab; only the note's claim "whose operators allow it" was fixed.
- Session 8603's dated section of `docs/methods/resources.md` was not rewritten; one sentence was added saying the coal fields arrived later that day.

## For Samuel's ruling (default "left as it is")

- Finding 4 (`wip/audit-small-4`): the confirmation link confirms on a GET, as the unsubscribe link did until session 59; a mail scanner can confirm an address that did not ask. Fix: the link asks, a POST confirms.
- Finding 7: where a reader asks for an address to be removed (neither `/subscribe` nor `/terms` says).
- Finding 13 (`wip/audit-small-13`): the unsubscribe form draws any address text a crafted link carries.
- Finding 14 (`wip/audit-small-14`): `/attention`'s note says 27,419 stories held; the weeks hold 27,417.
- `/terms` and `/privacy` (your words): the site's server holds the service key; the unsubscribe link is two steps; the confirmation is not only a person's; Resend is not named; the suppression list is not on `/privacy`.

## Needs the key

- Nothing.
