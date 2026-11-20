# Session 9812: every try of the internal token counted (finding T1, low)

Energy Research Warehouse (ERW). 20 November 2026, 20:03 to 20:10 UTC. Chain 610, part B, the desktop's third window.

## The finding

- **T1, low.** Eight doors take the internal token: the old link `/internal/unlock?token=`, the form (`POST /internal/unlock`), `/internal/costs`, `/internal/ask`, `/internal/usage`, the two report drafts, the refund finder and its download. Session 177 chose that "a right token always opens, whatever was tried before", so the form's limit on wrong tries (10 an hour) never refused anything a guesser needed: every try still told right from wrong. The old link and the five pages had no limit at all. What stood between a guesser and the internal view was the token's length alone (the pages refuse a token under 24 characters, so it is at least that long).
- Shown against the code by reading it (`site/app/internal/unlock/route.ts`, the pages' `token !== want` lines): no test could show a guess succeed without the real token.

## The fix (`wip/9812-token-tries`, `1ab4a793c`)

- `site/lib/guard.ts`: `TOKEN_TRIES = 30`, `tokenTriesLeft(req)` and `pageTokenTriesLeft(headers)`: every try that brings a token is counted in the bucket `token_tries`, right or wrong, by the database across instances and by the instance's memory as the floor. Past 30 in an hour from one address the door answers as to a wrong token (404, or "wait" on the form).
- The internal view's cookie is never counted: a reviewer who has unlocked once is never met by this.
- Each of the eight doors counts before it compares. The lines of the old link that `tests/test_session177.py` pins word for word are unchanged.
- Tests: `tests/test_session9812.py` (new): the guard, each door's order, the list of doors (a ninth door fails it), and `site/scripts/test-token-tries.mjs` under node (30 tries pass, the 31st does not, another address keeps its own count, a page's headers count for the same address). `tests/test_session408.py` gains `/severance/finder` among its exemptions (internal; it now reaches `lib/supabase.ts` only through the guard).
- On the head: the 20 test files that name the guard or a changed door, 211 passed; the standing security tests, 130 passed; 0 failed. `npx tsc --noEmit` on rows 7 and 8 merged: no error in a changed file.
- Landing requested: row 8 of `docs/state/landing_request_desktop_w3.md`.

## For Samuel's ruling

- **The number of tries, or the old way back.** Default taken (the safer choice): 30 tries an hour from one address, right or wrong. The other choice: session 177's rule, a right token always opens, and the token's length is the only guard. Either way, retiring the old link (H1) removes six of the eight doors.

## Needs the key

- Nothing.
