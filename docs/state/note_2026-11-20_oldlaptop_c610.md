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

## The chain's end (session 9401, the old laptop, 26 November 2026)

- **How it got here:** the old laptop took the resume file (611), put it back as 612, and continued from the progress file.
- **Rows 7 to 13 of `docs/state/landing_request_desktop_w3.md` have all landed** (each head is an ancestor of `origin/main`; row 7 reached `main` on 21 November in the merge `0d1200daa`). The first item of "What waits for Samuel" above is done.
- **The held-back finding is now written:** H9811 in [`docs/security.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/security.md), section "The finding held back, written after its fix landed". In short: for a held grid (ISO-NE, MISO, NYISO), rows of the interconnection queue table were not dropped, because the hold read only the column a series row has. Only a holder of the internal cookie could see them, since every page is in review. Fixed and tested; nothing to rule.
- **Security review by severity, final:** high 1 (fixed, landed), medium 0, low 3 (T1 fixed and landed, its number for Samuel; T2 needs the key; T3 noted).
- **Part B again:** nothing landed after 20 November adds a route, page, header, workflow or new input. Nothing new found (`docs/security.md`, "Part B again").
- **The weekend pack** was not updated after Saturday 21 November 10:00 PST, the chain's own end for it.
- **What still waits for Samuel:** the rest of the list above. T1's number, the old link and the token, the linter's packages, part C's seven rows, and T2 when the key returns.
- **The resume file is removed** by this session, and the queue step runs next.
