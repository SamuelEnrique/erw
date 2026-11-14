# Session 5276: the chat's effort is medium; a refusal's fixed words are the loop's

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (10:17 to 10:30 UTC), Fable, unattended. Chain 256. Branch `wip/5200-ask-close` (worktree `erw-p3-5264`). Nothing built, nothing landed, no model call, no warehouse data written.

## Read these first

- **The general chat now runs at effort `medium`, where it ran at `high`.** One constant, exported to the site's spec. Ask ERCOT has run at `medium` since session 143 and is not changed.
- **What it rests on:** 61 questions asked at `medium` today, 60 right, USD 4.53 where the same questions had cost USD 7.35 at `high`. Twenty of them had never been asked through this loop.
- **The one not right is mended in the loop, not in the prompt.** A refusal that carries none of its fixed words is given the first by both loops, before the model's own sentence.
- **The way back needs no deploy:** `ASK_WRITER_EFFORT=high` on the server.
- **Session 5275 left two stored tests failing; this session's commit corrects them.** They pin the count of the history's rows and of the refusals by class, and the trader's asking added one of each.

## What was done

- Precheck from the main checkout: exit 0.
- **The effort:** `warehouse/chat/ask.py` `EFFORT = "medium"`, with the measure beside it; `site/lib/chat/spec.json` exported again (`check_spec.py` exit 0). `tests/test_session92.py` pinned "high" for the general chat: it now reads the constant.
- **A refusal's fixed words:** `with_refusal_words` in `ask.py`, `withRefusalWords` in `site/lib/chat/refused.ts`. A refusal of the general chat with none of "not in the warehouse", "license needed", "paused" gets the sentence "Not in the warehouse." before it. A refusal that has one is left as written. Ask ERCOT's refusals are not touched.
- **Measured first, with no model:** of 135 refusals for want of a figure in the stored runs, two carry none of the words (oi09 of 13 November, at `high`; gp02 of today, at `medium`).
- **A window with no row, on a table of more than one step:** said not held when the window has steps at every step the table may have. Both functions, three more made windows (38 in all).
- **The turn-by-turn test** gains the scenario `a_refusal_without_its_words`: both loops give the same sentence.
- **`docs/methods/ask.md`:** the section "The chat's effort is medium, and a refusal's fixed words are the loop's", with the measure as a table, and the decisions of sessions 5264 to 5276.

## Checks run

- `tests/test_session5276_ask.py` (13 tests), `test_session1300.py` (18 scenarios, both loops), `test_session5267_ask.py`, `5268`, `5272`: 47 passed.
- Every Node script of the chat on the main checkout's packages (21): each exit 0. One had to be respected: `test-ask-168.mjs` holds a line of the loop word for word, so the refusal's words are set on the line before it.
- Type check of the four changed modules: no error in them.
- The wide run (136 files): 1,835 passed, 126 skipped, 2 failed, both the pinned counts named above; corrected, and the five files around them passed (32 tests).

## Model spend

- Estimate before: USD 0.00. Actual: USD 0.00. Chain 256: USD 9.1343 of USD 20.

## Decisions made without you

- **The effort is changed, not left for a ruling.** It is one constant, measured on 61 questions, in line with the model's own documentation and with Ask ERCOT's setting, and undone on the server by one variable. It reaches production only through the landing desk.
- **The limit of 12 calls and the output limit of 16,000 tokens stay.** The effort and the rule cut what the chat does; a lower limit would cut what it may do.
- **The refusal's words are added, never rewritten.** The model's sentence stays as it wrote it; the reader sees the fixed sentence first.
- **Not for Ask ERCOT.** Its refusals say where to look, in their own form.
- **Rule 11 stays.** With it and `medium` together the nine heavy figure answers cost half; the cut-off it was blamed for is not its doing (session 5272).

## For Samuel's ruling

- **The general chat at `medium`.** Decided here, on the measure. If you would rather keep `high`: `ASK_WRITER_EFFORT=high` on the server, or the constant. **Default: `medium`.**
