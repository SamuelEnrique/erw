# Session 817 report: the emails read by a reader

22 October 2026, 12:09 to about 12:13 UTC (the landing is session 818's), unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-817` on `wip/817-periodicals` (cut from `wip/816-periodicals`). Chain `queue/done/061-day-22-october-code-periodicals-2.md`, session 817. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written, no web request.

## Read these first

- **The Roundup's email follows the page's order**: the week in five numbers, the weekend, the five of the week, the policy of the week, the numbers, the chart (it put the numbers before the policy). The Digest's order stays (the top five, the numbers, the chart of the day, the fun fact).
- **The stories folded under an item go with it in the email** (session 802's "Also on this topic" line, which the email had left out): in the text part each outlet by its name and never an address, in the HTML with its links. Read on the dry runs of sessions 807 and 808 (`runs/periodicals/s817/`): the Digest's top five carry their "also" lines, the Roundup's first item its Anthropic line.
- **Left as it is, for the owner**: the text part's numbers table prints one line a row with the column names ("ISO: ERCOT; Hub or zone: HB_NORTH; ..."), complete and long; a compact form would be a choice of words. Two tests in `tests/test_periodicals.py` (`TheEmailsRead`).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 817"` | 0 | on duty |
| `tests.test_periodicals` (22 tests) with 810, 803, 470, 63 | 0 | 92 tests OK (a module named in error, `test_session23`, does not exist) |
| the two dry-run emails rendered again | 0 | `runs/periodicals/s817/roundup_W43.txt`, `digest_21.txt` |
| em and en dashes | 0 | none |

## The landing

LANDING_PENDING

## Decisions made without you

1. **The Roundup's order follows the page**; the Digest's does not change.
2. **The "also" line is under the item's source line**, in a smaller grey line in the HTML.

## For Samuel's ruling

- The text part's table lines (above).

## Files

- Changed: `warehouse/news/email_digest.py` (`numbered`, `story_list`, `render`), `tests/test_periodicals.py`. New: this report.
