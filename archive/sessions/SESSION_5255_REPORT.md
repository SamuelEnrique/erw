# Session 5255: the first half whole

Energy Research Warehouse (ERW). portable-laptop, window P3, 13 November 2026 (19:37 to 19:42 UTC), Fable, unattended. Chain 238. Branch `wip/5200-ask` (worktree `erw-p3-5200`), `origin/main` merged at 19:37 UTC. Nothing built, nothing landed, no warehouse data written. Model spend USD 1.57.

## Read these first

- **The first half is whole: 75 asked, 72 right as graded, USD 8.96.** All on one state of the chat: nothing of it has changed since the chain began.
- **One of the three not right is the chat's.** oi07: a table of the record that the live set lacks, answered as an answer. The other two are the key's: tx07 (two tables answer it differently) and de07 (the key's words too narrow; this session).
- **No wrong figure in 43 figure questions** but tx07's choice of table. Units, local days and weeks, sums over twelve months, counts of rows: all right. 26 refusals, 25 right.
- **The cost is in the calls.** 19 of 42 figure answers made three or more calls after the figure was in a tool result. The list of 140 tables is 45 KB and every later call reads it again.

## What was done

- Precheck (main checkout) exit 0; `origin/main` merged; `platform_questions.py --check` exit 0.
- **Asked, at most USD 2.00 written before:** the last 12 of slice a, de05 to dc09. USD 1.5731.
- All 12 answers read beside their keys. The 11 graded right are right; de07 is right too, and its key is wrong.
- The review file: "The first half, whole", with the classes and whose each is.
- Measured from the stored records: how each question began; which refusals listed every table first.

## The first half by class

| Class | Questions | Whose |
|---|---|---|
| A table the live set lacks, answered as an answer | oi07 (1 of 6 of its kind) | the chat's tools and loop |
| A question two tables answer differently | tx07 | the key's |
| A key's words too narrow | de07 | the key's |
| A held grid's answer graded wrong | pr11 | the grader's (fixed in 5251) |
| Calls past the figure | 19 of 42 figure answers | cost |

- **Refusals from a filtered list alone: none.** Of 26 refusals, 19 listed every table first; 6 were told by a tool that the table is held, paused or not in the live set; 1 was a grid's own chat.

## Checks run

- `tests/test_session5251_ask.py` and the four tests that pin the records: 50 passed.
- `history.py`, `replay.py`, `refusals.py`, `platform_scores.py`: `--check` of each exit 0.

## Model spend

- Estimate before: at most USD 2.00. Actual: 12 questions, USD 1.5731.
- Chain 238: USD 8.96 of USD 20. The second half (59 questions) is about USD 8 at this session's rate.

## Decisions made without you

- **The three stay counted as not right** until their fix or their key is in and, where the question changed, it is asked again.
- **Session 5256 is the fix of oi07's class, then the second half starts on the fixed chat.**

## For Samuel's ruling

- **The list of tables is the largest part of a question's cost.** A question that began with the whole list cost USD 0.145 on average; one that needed none USD 0.037. Default: nothing changed here (the list's shape is read by both loops and many tests). A shorter list (name, area, grids, span, whether loaded) would cut a visitor's question by about a third.
