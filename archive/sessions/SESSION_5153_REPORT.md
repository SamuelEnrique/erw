# Session 5153 report: row 22, the policy's inline scripts: what a nonce would cost

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. No pull: the framework's guide was read from the package already on this machine. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 18:59 UTC, the read and the tests by 19:00 UTC. Inside the long end of 1:00.

## Read these first

- **A nonce would make every page render on each request.** Next 16.4.5's own guide says so in as many words: with a nonce, "all pages must be dynamically rendered", regeneration on a clock is off, and the host caches no page.
  - Today 28 of the site's 104 pages render on each request, and 39 regenerate on a clock (the home page every 15 minutes, `/storage` every hour).
- **The word `'unsafe-inline'` is there for the framework only.** The site's own source writes no script into a page. Now a test says so.
- **Row 22 is a ruling, default: keep the word.** A third way exists (hashes at build time, experimental): it needs a window that builds. Ruling 1.

## What to review

1. `docs/security.md`, "The policy's inline scripts": the three choices in one table.
2. `tests/test_session5153.py`: 8 tests.
3. `docs/reviews/security-faults-2026-11-13.md`, row 22.

## What was done

- **The policy read** in `site/next.config.ts`: `script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com`; no `'unsafe-eval'`.
- **The source read**, 528 files of `app/`, `components/`, `lib/` (`runs/s5153/read.py`):
  - No script element, no `next/script`, no `eval`, no `new Function`, no `document.write`.
  - One script added by the site: the chart library from cdnjs, with its integrity hash (`components/echarts.ts`).
  - Markup set on a page at 14 places; all 14 go through `render`, `renderDigest` or `renderRoundup` (`site/lib/markdown.ts`: raw HTML escaped, an unsafe link refused).
  - One copy of markup in the browser: `components/GateRestore.tsx` copies what the server already rendered, in the internal view. Not a fault.
- **The framework's guide read** (`node_modules/next/dist/docs/01-app/02-guides/content-security-policy.md` in the main checkout): the nonce's requirement, and the experimental hashes (`experimental.sri`).
- **The test** pins the four facts above and the policy's line, so a later inline script or a new raw-markup place fails the suite.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5153 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | up to date |
| `runs/s5153/read.py` | 0 | the counts above |
| `pytest` on `test_session5153`, `5152`, `5151`, `5102`, `371`, `1501`, `177` | 0 | 85 passed |

- **Not run:** the build, `check-csp.mjs` (it needs a built site), the experimental hashes.
- **Not verified:** whether the experimental hashes let the framework's inline data pass without the word. The guide's example suggests it; only a build with `check-csp.mjs` says.

## Decisions made without you

- **No change to the policy.** A stricter rule cannot be proven without a build, and a policy that blocks the framework's own scripts leaves every page blank.
- **The page counts are of the source** (a page that names `force-dynamic` or `revalidate`), not of a build's route table.

## For Samuel's ruling

1. Row 22. Default: (b) keep `'unsafe-inline'` for scripts. (a) a nonce: every page rendered on each request. (c) the experimental hashes tried on a branch by a window that builds (P1, or the desktop), with `check-csp.mjs` on every page as the proof.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 4 of the list session 5150 rebuilt.
