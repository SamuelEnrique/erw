# Session 2259 (chain 159, deals and datacenters) report: deals' status missed

6 November 2026, from about 12:50 to 12:56 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2259-deals`, cut from `wip/2258-deals`. Model spend **USD 0** (code; the 2249 and 2232 answers replayed). Nothing deployed; no warehouse data written.

- **The class**: deals' status missed, 7 of 106 on the second read (and 1 unsupported), the next by count.
- **The cause**: in each, the deal's evidence sentence states a stage ("to serve as", "will become", "Joins", "partners with", "lease deal with", "source says") and the model left stage and status empty.
- **The fix**:
  - `fields.stage_from_words`: where the model gives no stage, the stage is read from the deal's evidence sentence by `STAGE_WORDS` in order (cancelled, rumored, closed, financed, signed, announced), its span the words;
  - `extract.py`: an empty status takes the stage when the stage is one of the five words the Roundup prints. A field the Roundup reads keeps its meaning; it is filled where it was empty, from the story's words.
- **Before and after**: status missed **7 to 0**. Every replayed row's stage and status compared: on 2249, the seven, plus D012 and D062 (a stage, no status) now with the status; on 2232, D043, D047, D059 the same way. No stage or status the model gave changed.
- **Unsupported, left open (D062)**: a check that "closed" needs words that say so was written, run and taken out. It also changed D100 ("takes 5% stakes") and D026 ("Seals Acquisition"), both graded right by the second read, and stripped "closed" from three raises, which the prompt itself calls closed. The audit file says why.
- **Tests**: `tests/test_session2259_deals.py`, 4 passed; the chain's deals tests and the older extractor tests: 233 passed, 1 skipped.
- **Docs**: `docs/methods/energy_deals.md` ("A stage from the deal's own words"), the audit file's section.

## Decisions made without you

1. **The status filled from the stated stage**, since the Roundup prints status and the words state it; the stage's span is kept in the evidence table (`stage_text`).
2. **No closed check**: the second read's own grades do not separate a present-tense headline that completed from one that did not.

## For Samuel's ruling

- None new.
