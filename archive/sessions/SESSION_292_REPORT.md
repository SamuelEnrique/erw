# Session 292 report: the tour, guided

14 to 15 October 2026, unattended, on samueloldlaptop (the code machine), the fifth session of the afternoon chain. Branch `wip/games-v2` (origin/main merged: it had not moved), pushed, **not landed**. Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **The tour is a guided path** (ruling 11a): its first page lists seven stops and one action, "Start the tour"; each stop is a page of its own (`/tour/1` to `/tour/7`) with the progress bar, "Stop 3 of 7", Back and Next, what to look at, and a button that opens the stop's page.
- **Seven stops at today's addresses, in the ruled order:** what a battery earns, what a generator earns, what a datacenter pays (the three tools), the grid, research, the price board, the Digest. About five minutes. None is an old address answered by redirect (the old tour had two).
- **The bar sits on the tour's own pages, not on the stop pages themselves.** The stop pages are outside the Games tab (the chain's rule), and the site forbids framing a page (`frame-ancestors 'none'`), so the bar cannot travel with the reader onto `/grid` or `/board`. The reader comes back with the browser's Back button, as each stop says. A one-line way to put the bar on the stop pages is under "For Samuel's ruling".
- **The heading check passes, 47 of 47:** `site/scripts/check-tour.mjs` opens every stop in a real browser and fails when a heading the tour quotes is gone.

## What to review

Screenshots: https://github.com/SamuelEnrique/erw/tree/wip/games-v2/docs/reviews/games-2026-10-14/292

1. Before: `before/01-tour-1280.png`, `before/01-tour-390.png` (five links, no way back).
2. After: `after/01-tour-1280.png` (the first page), `after/02-stop-1-1280.png` to `after/08-stop-7-1280.png`, the same at 390 px, and `after/10-stop-1-opened-1280.png` (the battery page the first stop opens).

Locally: `C:\Users\lossa\Documents\erw-279\site`, `npx next start -p 3289`, unlock at http://localhost:3289/internal/unlock?token=<INTERNAL_COSTS_TOKEN>, then http://localhost:3289/tour , "Start the tour", Next, Back.

## What was done

- `site/lib/tour.ts`: the seven stops, each with its address, seconds, a line, what to look at and the headings it quotes (as the pages have them on 14 October: read from a local build of today's main).
- `site/app/tour/TourBar.tsx`: the shared progress bar: a segment a stop (each a link 24 px tall around an 8 px bar; done and current in ink, the rest in the rule colour), "Stop k of N", Back and Next with `rel="prev"` and `rel="next"`.
- `site/app/tour/[stop]/page.tsx`: the stop pages (static, seven), inside `<Brand>`.
- `site/app/tour/page.tsx`: the first page, the bar at stop 0.
- `site/scripts/check-tour.mjs`: the heading check, in a real browser (a link to a page in review is drawn as a link only once the browser knows the internal view).
- The menu's line for the tour (`site/lib/pages.ts`) and `check-routes.mjs` (`/tour/1`, `/tour/7`).
- Tests: `tests/test_session292.py` (7); session 53's tour test follows (seven stops, about five minutes).
- Found by the screenshots and fixed: the cardinal buttons' words were cardinal on cardinal (the site's base link colour wins over a colour class on a link, `docs/brand.md` section 9): the words sit in a white span.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `tsc`, `eslint` | 0, 0 | |
| Tests of sessions 292, 53, 203, 239, 242, 288 | 0 | 71 |
| `npm run build` (worktree) | 0 | `/tour/1` to `/tour/7` static |
| `node scripts/check-tour.mjs http://localhost:3289` | 0 | 47 of 47 |
| `check-values.mjs`, Games pages | 0 | 105 of 105 |
| Screenshots after | 0 | 18, no sideways overflow, no page error |

## Decisions made without you

- **"The three tools" read as the battery, generator and datacenter tools** (`docs/state/rulings_2026-10-11.md`, "The three tools together").
- **The tour's pages carry the bar; the stop pages do not** (above).
- **The order is the prompt's:** the three tools, the Grid, Research, the price board, the Digest.
- **Each stop names two or three headings to read, and one thing to change** where the page is a tool.

## For Samuel's ruling

- **The bar on the stop pages themselves.** A ready patch, not applied: mount the bar from the root layout when the address carries `?tour=k`, and make each stop's "Open" link add it. In `site/app/layout.tsx`, inside `<main>` before `{children}`: `<TourBarFromAddress />`, a client component of six lines in `site/app/tour/` that reads `useSearchParams().get("tour")` and renders `<TourBar at={k} />` for k from 1 to 7. It touches a file outside the Games tab, so it waits for you.
- The home page still says "five stops, about three minutes" beside its link to the tour (`site/app/page.tsx`, shown only once the tour is live): outside the Games tab, left.

## Files

- New: `site/app/tour/TourBar.tsx`, `site/app/tour/[stop]/page.tsx`, `site/scripts/check-tour.mjs`, `tests/test_session292.py`, `docs/reviews/games-2026-10-14/292/`, this report.
- Changed: `site/lib/tour.ts`, `site/app/tour/page.tsx`, `site/lib/pages.ts` (the tour's line), `site/scripts/check-routes.mjs`, `tests/test_session53.py`.
