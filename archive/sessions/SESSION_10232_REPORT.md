# Session 10232 report (chain 710, part D goes on: the deep-dive report library audited)

- Audited the two drafts of platform tool 13 (`/reports/draft/shape-premium`, `/reports/draft/ai-gigawatts`) as a hostile editor would; evidence in `docs/reviews/reports-model-audit-2026-11-26/`.
- The numbers are right: 246 of 246 figures drawn with the site's own code and re-done independently to the digit; 134 of 149 measures of `ai_power_regions` re-done from its inputs, the other 15 moved with their inputs after the build of 2 October.
- Nine findings: 2 high, 6 medium, 1 low. Words branches 1, 3, 4, 5, 7 (merged as `wip/audit-reports-words`); figure branches 2, 6, 8, 9 not for landing.
- `docs/reviews/reports-model-audit-2026-11-26.md` itself is not in this commit: this session's file tool refused to write it ("subagents should return findings as text"), and the session did not work around the refusal. Its full text went back to the chain's desk in the hand-back, to be written there.

## Decisions made without you

- Drew the pages with stand-ins for the token gate, Brand and next/headers (no figure or word in them), every read answered from the main checkout's CSVs.
- Split the words fixes into one branch a finding and merged them, resolving the one conflict by keeping both sides.

## For Samuel's ruling

- Finding 2: rank and draw profiles on the latest whole month. Default left as it is. Measured: 48 of 744 hours; CAISO -0.38 against 0.81.
- Finding 6: rebuild `ai_power_regions` for `cold_2026`. Default left as it is. Measured: ERCOT 8.78 to 31.15, six of seven regions move.
- Finding 8: show the held regions' public-source measures. Default left as it is. Measured: 53 rows; MISO would be the dirtiest region.
- Finding 9: exporters below zero, months by date, whole tonnes. Default left as it is.

## Needs the key

- Nothing.
