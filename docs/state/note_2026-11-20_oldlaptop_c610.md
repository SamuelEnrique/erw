# Note of chain 610, 20 November 2026 (parts B to D, written by the desktop's third window)

Energy Research Warehouse (ERW). Chain 610 was written for the old laptop, which is down and never started. Part A (the weekend pack) was written on Samuel's own laptop (session 9800). Parts B, C and D were done by the desktop's third window (`C:\Users\Shared\Documents\erw-w3`), sessions 9810 to 9819, by the owner's instruction of 20 November; part E goes on there. The name of this file is the chain's.

## The weekend pack (part A)

- [`docs/reviews/weekend-2026-11-21.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/weekend-2026-11-21.md), written by session 9800 on the personal laptop; this window did not touch it. Its minutes are on its own first lines.

## The security review (part B)

- **Ground:** [`docs/reviews/security-ground-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/security-ground-2026-11-20.md): 45 route handlers, 61 pages that read the request, what each trusts.
- **By severity:** high 1, medium 0, low 3.
  - High: **one finding held back until its fix lands** (row 7 of `docs/state/landing_request_desktop_w3.md`, requested). Its detail goes into `docs/security.md` after the landing.
  - Low, T1: every try of the internal token is now counted, right or wrong, 30 an hour from one address (row 8, requested).
  - Low, T2: the chat trusts the numbers of an earlier turn the browser sends back; open until the key returns (its fix needs the chat's evaluation set).
  - Low, T3: limits per address meet a visitor with many addresses once each; noted (the ceilings behind them hold).
- **History:** nothing to rotate (one made-up test address; no secret's exact value in any commit since 12 November).
- **Dependencies:** what the site ships has no advisory; the linter's seven moderate findings now close with a minor version (listed for Samuel); four Python packages need major versions (as on 13 November).
- `docs/security.md` has the section "The review of 20 November 2026".

## What part C found (privacy and terms against the code)

- [`docs/reviews/privacy-against-code-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/privacy-against-code-2026-11-20.md): seven rows; nothing changed. The three a careful reader would take as promises:
  - an address stays in a server's memory longer than "the hour of the limit";
  - the chat's model also receives the earlier turns and, on Ask ERCOT, the page and settings the reader came from;
  - Resend receives the sign-up address and neither page names it.

## Part D (what a browser would complain of)

- [`docs/reviews/browser-without-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/browser-without-2026-11-20.md): no broken link or printed address; seven faults fixed on four branches (rows 9 to 12, requested): `/policy?view=week`'s unnamed buttons and faint zeros, `/severance`'s unnamed tier list, two h1 on `/data/licenses` and `/map?tab=resources`, a skipped level on `/map?tab=queues`, faint dots on `/grid`. `/policy`'s missing h1 is already on the second window's row 4.

## What waits for Samuel, in plain words

- **Land rows 7 to 12** of `docs/state/landing_request_desktop_w3.md` (the first window's desk does it; row 7 first: it is the held-back one).
- **T1's number:** 30 tries an hour from one address, or the old rule (a right token always opens).
- **The old link and the token** (H1, L4, L5): retire the link and rotate the token, as `docs/security.md` items 1, 2 and 6 say; six of the eight token doors go with the link.
- **The linter's packages:** apply `npm audit fix --package-lock-only` (a minor version, developer-only) or leave it.
- **The seven rows of part C:** change the words of `/privacy` and `/terms`, or leave them.
- **Needs the key:** T2 (the chat's turns signed by the server, then the evaluation set).
