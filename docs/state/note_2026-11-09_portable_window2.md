# The personal laptop's second window, chain 178: a fresh audit of the policy monitor's rules (written 6 November 2026)

Chain 178 (`queue/done/178-night-8-november-portable-window2-continued.md`) ran as sessions 3134 to 3145, 14:22 to 15:00 UTC on 6 November. Nothing of chains 166, 169 and 178 has landed yet: row 10 of `docs/state/landing_request_portable.md` (`wip/3144-policy`) holds every earlier row of these chains (2, 3, 5, 6, 9).

## Read these first

- `docs/reviews/policy-audit-2026-11-06-fresh.md`: the fresh audit, 80 actions never used to write a rule, and what sessions 3140 to 3142 fixed.
- `docs/methods/policy_monitor.md` section 17: what chains 169 and 178 changed and how well the rules hold.
- The notes of chains 166 and 169 (`note_2026-11-07_portable_window2.md`, `note_2026-11-08_portable_window2.md`) and their questions.

## One line a session

| Session | What | Head |
|---|---|---|
| 3134 | the next file (`queue/next/186-...`); the ground: nothing landed | `589bff276` |
| 3135 | what the build found: not landed; main changed none of the monitor's files | `0d2a12900` |
| 3136 | the page at 390 and 1280 from a snapshot: not landed | `612d5ded7` |
| 3137 | the trace on the data machine's copy: none exists; pushed | `05e11a707` |
| 3138 | your rulings: none yet | `82fe2887b` |
| 3139 | **a fresh audit**: 80 actions never used to write a rule | `9f878e82f` |
| 3140 | its instruments: 80 of 80 (71 before) | `3d0bf9210` |
| 3141 | its dates: 60 of 60 rows (47 before; my first pass had counted 51 of 59) | `73c723773` |
| 3142 | its figures 12 of 12 (10 before) and scope 80 of 80 (79 before) | `b254f60ad` |
| 3143 | the method note's section 17 | `4e80a3e43` |
| 3144 | the push and request (row 10): 3,188 related tests passed | `2bbbe02b1` |
| 3145 | this note; the next file updated; the queue | `de6ae9b5c` |

## What the fresh audit says

The rules of chains 166 and 169 were written against one sample of 80 and measured on it (206 faults before, 21 after there). On 80 others they held: the instrument for 71 of 80, the dates for 47 of 60 rows that state a step, the figure for 10 of 12, the scope for 79 of 80; the places and bodies with no fault found. Those are the honest numbers of rules written elsewhere. After sessions 3140 to 3142 every class holds on the fresh 80 too, which is again a fitted number: a third sample would measure those fixes as this one measured the first.

## What was asked of the desktop

- **Land row 10** (`wip/3144-policy`, task `3054-3144-policy`, port 3260). The gate's build is the monitor's first compile.
- After the landing, the connector's next run on the data machine derives the fields from its store of texts, and `python scripts/check_policy.py` on that copy is the real trace.

## Decisions made without you

- **The steps that wait on the landing or a ruling were not waited for** (sessions 3135 to 3138 say so in their reports); the fresh audit was done instead.
- **Two new kinds of date** (`filing_due`, `review_petition_due`) rather than stretching "comments due".
- **My own faults found and fixed**: the fresh audit's first pass undercounted class 1 (it looked for dates near "due" and "deadline" and missed "must be filed ... by"); a wider figure read let a listed unit win over a stated total until a test caught it; three report times written ahead of the clock (corrected from the commits); three branches left uncommitted by a `grep -c` that stopped an `&&` chain, then committed in order.

## For Samuel's ruling

- Chain 169's two stand: the rescoring under the scorer's note (with about 29% fewer actions at 5 or more on the default view), and chain 166's questions 2 to 7.

## Cost

- Model: none in chain 178 (USD 0.00). Chains 166, 169 and 178 together: USD 1.2123.
