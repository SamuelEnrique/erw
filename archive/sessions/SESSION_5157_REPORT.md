# Session 5157 report: the old link's retirement, prepared on a branch of its own (rows 3 and 4)

13 November 2026, unattended, `portable-laptop` window P2. Two branches: the stack `wip/5150-security` (this report and the list's two rows) and the new `wip/5157-retire-link` (`3118c0a7a`, worktree `erw-p2-5157`, cut from the stack). Model spend USD 0. No pull. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 19:14 UTC, the branch pushed at about 19:25 UTC. Inside the long end of 1:00.

## Read these first

- **Nothing about the link changes until you say so.** The retirement is a branch, `wip/5157-retire-link`. It is in no landing row. The stack `wip/5150-security` does not hold it.
- **To land it**: tell a session "land `wip/5157-retire-link`". Before that, use `/internal/open` once on production (paste the token, press the button), as the ruling's default asks: after the landing it is the only door.
- **What the branch does:**
  - `GET /internal/unlock` answers 404 and sets no cookie, whatever its address carries. It no longer reads the address.
  - `/internal/costs`, `/internal/ask`, `/internal/usage`, the two report drafts, the severance finder, its download and its lease loader open with the internal cookie alone.
  - No page writes the token into a link or a form any more (the finder and the lease loader did, when the address brought one).
  - The three plain comparisons of the token (`!==` in the link, `token !== want` in five pages, `token === want` in the finder) are gone. The token is compared at the form's door only, in constant time.
- **It was not built.** It type-checks, and 388 tests pass. The check that proves it on a build (`check-security.mjs`) was edited and not run. The landing's gate runs it.

## What to review

1. On `wip/5157-retire-link`: `site/app/internal/unlock/route.ts` (the `GET` is three lines now).
2. The same branch: `git diff wip/5150-security wip/5157-retire-link --stat`: 22 files, the site's 12 and the tests and documents that follow.
3. On the stack: rows 3 and 4 of `docs/reviews/security-faults-2026-11-13.md`.

## What was done, on `wip/5157-retire-link`

- **The link**: `GET` in `site/app/internal/unlock/route.ts`. The `POST` (the form's door) is untouched.
- **Five pages** (`/internal/costs`, `/internal/ask`, `/internal/usage`, `/reports/draft/ai-gigawatts`, `/reports/draft/shape-premium`): the gate is the cookie alone; the pages no longer take `searchParams`.
- **The severance finder, its download, the lease loader** and `site/lib/finder.ts`: `internalOpen(cookie)`; `tokenOk` removed; the links and the two hidden form fields that carried a token removed.
- **`site/scripts/check-security.mjs`**: "the old link works as it did" became "the old link is retired: the right token in the address gets 404 and no cookie".
- **Six older tests** pinned the old lines word for word (`test_session48`, `57`, `111`, `128`, `177`, `371`): each now pins the new line and says why.
- **`tests/test_session5157.py`**, 10 tests: no file of the site reads a token from an address, compares it plainly, or writes it into a link or a form; the `GET` opens nothing; the form is the door.
- **Documents**: `docs/release-gate.md` (the internal view opens by the form), `docs/battery_game_demo.md` (the demo's first step), `docs/security.md` (H1, L5, item 1).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5157 (window P2)"` | 0 | on duty |
| `git merge origin/main` (the stack) | 0 | merged (`f1ae5c277`) |
| `tsc` on 19 files (the retirement's 10 and this stack's 9 earlier ones), a scratch config, the main checkout's TypeScript, nothing emitted | 0 | no error; 58 files of the site read |
| `pytest` on 33 test files that name the touched files, with `test_session5157` | 0 | 388 passed, 17 skipped |
| `node ... scripts/test-usage.mjs`, `scripts/test-curtain.mjs` | 0, 0 | 16 and 8 tests passed |
| `node --check scripts/check-security.mjs` | 0 | it parses |

- **Not run:** the build, `check-security.mjs`, `check-csp.mjs`, `check-values.mjs` (they need a built site), the whole suite.
- **Not verified:** that the eight pages open with the cookie on a built site after the change (the gate's checks read five of them with the cookie; the severance pages need the finder's files, which only a machine that built them holds).

## Faults of mine, corrected before any commit

- A scripted edit replaced the gate's line in the five pages with a comment (the same slip as in session 5155: a comma binding tighter than a plus). All five were restored from git and edited again by hand, one at a time. Since then every change to code in this chain is made with the editor, not a script.

## Decisions made without you

- **The branch is cut from the stack**, so it is one landing after the stack's. Cut from `main`, it would have missed this chain's tests of the routes.
- **404 at the old link**, not a redirect to the form: it is what a wrong token always got, and an old bookmark then stops sending the token to the host's log.
- **`site/lib/release.ts` is not touched**, as the chain rules. Its comment (lines 10 and 13) still says the link opens the internal view; after the landing that comment is out of date. Ruling 2.
- **Six older tests edited.** Each pinned the link "until then"; `docs/security.md` says the pin goes with the retirement.
- **The three checks that send the real token in an address to prove it opens nothing** (S3) are left as they are.

## For Samuel's ruling

1. Rows 3 and 4: when the link is retired. Default: after you have used `/internal/open` once on production, say "land `wip/5157-retire-link`". Then row 5 (the token's rotation) is yours.
2. The comment in `site/lib/release.ts` that names the link. Default: a session corrects the two lines when the hold on that file is lifted; no behaviour depends on it.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 8 of the list session 5150 rebuilt.
