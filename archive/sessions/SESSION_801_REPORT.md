# Session 801 report: the why line says the consequence

22 October 2026, 09:36 to about 09:50 UTC (the landing later, below), unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-801` on `wip/801-periodicals` (cut from `origin/main` at `2242cbd2`, session 800's push). Chain `queue/done/060-night-23-october-code-periodicals.md`, session 801. Model Fable 5.1. Precheck 0. Model spend USD 0 (no model called; the fixture is saved items). No warehouse data written, no web request, no past issue rewritten.

## Read these first

- **The rule of the why line is now a check, not a hope.** `brief.why_check` names each fault: an adjective of the list (massive, unprecedented, significant, major, critical, key, huge, and their adverbs), two sentences, a figure the headline already gives. `brief.why_line(text, head)` holds every printed why line to it: the adjectives go (session 470's `plain`, with the seven), the first sentence stays, a figure the headline holds is taken out where the sentence still reads ("A 600 MW load with a secured anchor customer" to "A load with a secured anchor customer"), and what cannot be mended falls back to the headline's own clause (`brief.why_fallback`: the publisher's suffix and "Exclusive:" off, one money style, a stop), never an invented fact. Session 577's stop stays.
- **The figures line prints no figure the headline holds** (`brief.detail(r, head)`): "Anthropic may spend USD 750 billion ... USD 750 billion; parties: Anthropic" (21 October, top 1) prints "parties: Anthropic".
- **The scorer asks for it too**: `score.SYSTEM`'s rule for `one_line_why` now asks for one sentence on the consequence (who pays, what gets built or cancelled, which price or flow moves, what rule changes), no adjective of the list, no figure the title gives; `rubric.md` carries the same sentence. A prompt is not a gate; the check is.
- **Proved on 20 saved items** (`tests/fixtures/periodicals/why_lines.json`, from `news_stories.csv` as the repository holds it): each item's printed line was read and pinned; 13 of the 20 had a fault (11 adjectives, 2 figures of the headline); none of the 20 fell back. Over the 13 issues' top items (52 whose why line repeats a headline figure), 40 are mended by taking the figure out and 12 fall back to the headline's clause.
- **The Roundup takes it through `brief.why_line`** (its weekend, its five, the policy of the week and its two others pass their headline or title).

## What to review

- `/digest` after the next scheduled issue (the first written with this): every why line one sentence, no adjective of the list, no figure of the headline repeated on the figures line.
- `tests/fixtures/periodicals/why_lines.json`: the 20 lines as they will print.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 801"` | 0 | on duty |
| `tests.test_session801` (20 tests) with 577, 470, 498 | 0 | 72 tests OK |
| every test module that imports the news code (15 modules) | 0 | OK (skipped 3) |
| em and en dashes in the changed files | 0 | none |

## The landing

**Not landed by this chain.** The branches land together through `wip/811-periodicals` (sessions 801 to 811 over `origin/main` at 11:13 UTC), gated by session 818 of the next chain after 16:15 UTC. The gate ran twice on `wip/807-periodicals` (sessions 801 to 807): the suite in a clean worktree passed (5,965 tests, 21 minutes), the build passed (173 s), and check-values read 12,412 of 12,423 values equal to the live set, with 13 failures: the ten license-hold floors of session 408's list (a pass by rule), `/digest`'s floor (the page carries no number until the day's issue is written, about 15:45 UTC), and two pages whose fetch timed out on the slow database (`/roundup`, `/cost-of-power?view=allgrids&profile=flexible`); 16 pages were not read in the 45-minute limit. The exact commands are under "To finish" in `docs/state/review_2026-10-24_portable.md`.

## Decisions made without you

1. **"key" and "critical" are cut as adjectives** wherever they stand before a word ("Key chokepoint disruption" to "Chokepoint disruption"); "critically" too. A noun "key" ("the key to") would lose its word; none of the 16,247 saved why lines has it.
2. **A year is not a figure the headline gives**: "by 2032" stays in a why line whose headline names 2032; the rule is about amounts.
3. **The figure comes out of the sentence only after an article or a preposition** (a, an, the, at, for, with, about, over, nearly, some, around, up to, another, new) and before a word; after a verb or "of" ("totaling 2.1 GW", "a total of 2.1 GW") the line falls back to the headline's clause rather than lose its object.
4. **Session 577's test** counts the call form `why_line(r['why'], heads[` now that the headline goes with the line.
5. **"Oct. 6", "Inc.", "No. 5"** and one-letter initials are not a sentence's end (`brief.ABBREVIATIONS`).

## For Samuel's ruling

- Whether the fallback (the headline's own clause as the why line) may print, or the item should carry the headline alone when the model's line fails the check (listed in the plan).

## Files

- Changed: `warehouse/news/brief.py` (`WHY_ADJECTIVES`, `HYPE`, `figures_of`, `why_check`, `why_fallback`, `without_figures`, `fix_article`, `sentence_end`, `why_line`, `detail`, the callers), `warehouse/news/roundup.py` (the callers), `warehouse/news/score.py` (the prompt), `warehouse/news/rubric.md`, `tests/test_session577.py` (the call form).
- New: `tests/test_session801.py`, `tests/fixtures/periodicals/why_lines.json`, this report. Not in git: `runs/periodicals/s801/`.
