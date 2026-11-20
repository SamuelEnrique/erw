# Sessions 9816 to 9819: what a browser would complain of, found without one (chain 610, part D)

Energy Research Warehouse (ERW). 20 November 2026, 20:19 to 20:40 UTC. The desktop's third window. One report for the four sessions (9816 the reads and `/policy`, 9817 `/severance`, 9818 the headings, 9819 `/grid`); `SESSION_9817_REPORT.md` to `SESSION_9819_REPORT.md` point here.

## What was done

- [`docs/reviews/browser-without-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/browser-without-2026-11-20.md): links and printed addresses (none broken), and eight faults a checker would name, seven fixed on four branches and one already fixed on another window's branch.
- **The HTML of 138 addresses read from production**, one ordinary read each, a second apart, in the internal view opened by the form (the token read from the main folder's env file into memory and never printed), no script run, no usage counted. Every address answered 200.
- **Landing requested**, rows 9 to 12 of `docs/state/landing_request_desktop_w3.md`:
  - row 9, `wip/9816-a11y-policy`: `/policy?view=week`'s buttons named; its zeros at full strength;
  - row 10, `wip/9817-a11y-severance`: `/severance`'s tier list named;
  - row 11, `wip/9818-a11y-headings`: one h1 a page on `/data/licenses` and `/map?tab=resources`, no skipped level on `/map?tab=queues`;
  - row 12, `wip/9819-a11y-grid`: `/grid`'s empty reliability cells darker and said as "none".
- Each branch has its own test that fails on the code before it (`tests/test_session9816.py` to `9819`); the test files that name each changed file pass; rows 7 to 12 merge together with no conflict, and `npx tsc --noEmit` on rows 7 to 11 merged finds no error in a changed file.

## What to review

All pages are in review: open the internal view first ([`https://erw-flame.vercel.app/internal/open`](https://erw-flame.vercel.app/internal/open)). After rows 9 to 12 land:
- [`https://erw-flame.vercel.app/policy?view=week`](https://erw-flame.vercel.app/policy?view=week): the zeros of the grid are as dark as the other muted words.
- [`https://erw-flame.vercel.app/data/licenses`](https://erw-flame.vercel.app/data/licenses): the record's headings under the page's title are one size smaller.
- [`https://erw-flame.vercel.app/map?tab=resources`](https://erw-flame.vercel.app/map?tab=resources): open the method note's fold; its headings one size smaller.
- [`https://erw-flame.vercel.app/grid`](https://erw-flame.vercel.app/grid): the reliability table's dots are darker.

## Decisions made without you

- Not redone: `/policy`'s missing h1, which the portable laptop's `wip/9601-policy-held-page` fixes (row 4 of the second window's file, requested 19:37 UTC).
- The page reads used the internal view as the chain allows ("an ordinary page read with the internal cookie"); 138 reads, a second apart.

## Needs the key

- Nothing.
