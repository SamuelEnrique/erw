# Session 814 report: commentary ranks under news

22 October 2026, 11:52 to about 12:00 UTC (the landing is session 818's), unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-814` on `wip/814-periodicals` (cut from `wip/811-periodicals`). Chain `queue/done/061-day-22-october-code-periodicals-2.md`, session 814. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written, no web request, no past issue rewritten.

## Read these first

- **Among equals in significance a reported event ranks before commentary** (`brief.build_clusters`: a `kind` column by the title's form, `brief.title_kind`; the sort is significance, then event before commentary, then the tie-break as before; the model's score is untouched). A title is commentary when it carries a reported opinion ("says", "sees", "warns", "argues", "expects"), a format word (Q&A, interview, explainer, opinion, analysis, column, podcast, newsletter, "tracks"), a question mark, or opens with "How", "Why", "What", "Should", "Can", "Will".
- **Proved on the 13 issues by selection alone** (`docs/reviews/periodicals-commentary-regen-2026-10-22.md`): the order changes on 4 of 13 days. The chain's two named cases read differently than it expected: 13 October's "Brookfield's Teskey sees no slowdown" and "Land & Expand tracks" were already out of the top ten under session 802's one-topic rule (datacenter power holds one item), and 20 October's "Iran war tilts balance of global oil power towards the Americas" stays at 3, because its title carries no mark of commentary (no "analysis", no reported verb); the rule reads the title's form, not the piece, and that one's form is a reported event's. Two tests in `tests/test_periodicals.py`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 814"` | 0 | on duty |
| `tests.test_periodicals` (20 tests) with 802, 470, 532 | 0 | OK |
| `runs/periodicals/s814_regen.py` | 0 | the review file above |
| em and en dashes | 0 | none (a publisher's en dash in a title written as a hyphen in the review) |

## The landing

LANDING_PENDING

## Decisions made without you

1. **The kind is read from the title's form**, with the list of words above; a piece whose title reads as news ranks as news.
2. **The AI tie-break stays** between the kind and the story count (the ruling waits).

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/news/brief.py` (`COMMENTARY_WORDS`, `COMMENTARY_START`, `title_kind`, `build_clusters`), `tests/test_periodicals.py`. New: `docs/reviews/periodicals-commentary-regen-2026-10-22.md`, this report.
