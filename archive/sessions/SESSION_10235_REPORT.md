# Session 10235 report: the Energy Digest and the Sunday Roundup audited as a hostile editor would

Chain 710, part D, 26 November 2026, on the old laptop, in the worktree `erw-c710-c` (branch `wip/audit-digest-doc`). Model spend USD 0; no script under `warehouse/news/` that writes or calls a model was run.

## What was done

- `docs/reviews/digest-model-audit-2026-11-26.md` and its evidence folder: the ten newest Digests (9 October to 12 November) and the three newest Roundups (W43 to W45), every number traced.
- Tables' figures re-done by code that imports nothing of the ERW: 152 of the Digests (122 equal to the digit, 4 revised by EIA since and noted on the pages, 26 on NYISO and ISO-NE rows this copy lacks) and 98 of the Roundups (77 equal, 20 on rows this copy lacks or held grids, 1 a known fault).
- 361 story numbers traced to the stored story text: 341 there, 3 only in the scorer's own why line, 17 the Roundup's own counts. Fun facts: every quoted span found word for word in its stored source.
- The literal-number check exercised on crafted text: it stops a number in no source; it reads no unit, scale, date, list marker, direction or number in words.
- Seven findings, seven branches from origin/main: 1 and 2 for landing (page code and words, drawn and read), 3 to 7 a test each, for ruling.

## Decisions made without you

- `/roundup` now drawing the newest Roundup with `renderRoundup` (branch 1) is returned for landing: it applies the hold you already ruled for Roundup pages (rows 94 and 108) to the one page that missed it, and changes no figure's value.
- Extending the news index hold to the Digest's opening number and story rows and to the Roundup's stories (finding 6) is left for your ruling: it changes what visitors see of the issues beyond the hold you set.
- Faults already in `docs/reviews/periodicals-faults-2026-11-05.md` are cited by row, not filed again (rows 69, 79, 80, 81, 82, 87, 93, 94, 108).

## For Samuel's ruling (default for each: left as it is)

- Check every number of the why line against its story, and take the why line out of the headline check's sources (finding 4): 3 lines of the ten issues would not have printed, among them "adds ~2% to nuclear fleet" (about 0.2 percent).
- Make the literal-number check read units, scales, dates and list markers (finding 3): no printed number of the thirteen issues changes; the check would stop more.
- Hold the opening number's story figure, the block's story rows and the Roundup's stories while news_index is held (finding 6).
- Print the named outlet's own date beside a story's figure (finding 7): 2 dates in the issue of 12 November.
- Name the grids with no real-time row of the day (finding 5): 4 of 9 issues.

## Needs the key

- Nothing in this audit needs the model key. A rerun of any issue under a ruled change does (the brief and the Roundup call the model).

## Rows returned to window A and the chain

- Landing: `wip/audit-digest-1` (page code, the Roundup index's hold) and `wip/audit-digest-2` (words, the weekend days' Roundup line).
- Data requests: NYISO and ISO-NE day-ahead and real-time rows of 11 October to 5 November for 16 Digest and 8 Roundup figures; three chart tables not on this machine.
