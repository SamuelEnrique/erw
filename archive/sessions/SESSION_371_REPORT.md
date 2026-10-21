# Session 371 report: the documents an agent reads first, and the security review's open items

20 October 2026, from about 18:10 UTC, unattended, on samueloldlaptop (the code machine), a session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`, its "Session 371" paragraph). Branch `wip/371-docs-security` in the worktree `erw-371`, from origin/main (`ae894d37`). Model spend USD 0. No pull from any publisher, no warehouse data written, nothing written to Supabase, Redivis or Vercel (every database question below was a read in a read-only transaction).

## Read these first

1. **Todo 007 is done, and its CLAUDE.md part is a patch for you.** `ARCHITECTURE.md` gains one paragraph on the data lock and sync's restore (archive first since session 305, Redivis last under the export ceiling), linking `docs/machines.md`. `docs/runbook.md` says the outside trigger is done (pg_cron since session 59; read today with `scheduler.py --status`: six jobs active, each last run succeeded, every recent answer HTTP 204) and keeps the GitHub-side steps as the fallback. `package/llms.txt` is unchanged: it does not describe how the warehouse is refreshed. The CLAUDE.md change (the Schedules row, "Running things", two Key conventions bullets, `scripts/`, `queue/` and `exports/` in the layout table) is `runs/chain_oct20d/s371/claude_md.patch`; `git apply --check` passes on origin/main's and the main copy's CLAUDE.md.
2. **One fact in the todo was no longer true, and the patch says so.** The todo asked to keep "No crontabs on anyone's machine". The cloud jobs still run on no one's machine, but since sessions 181, 185 and 233 the data machine's daily run, the weekly hunt and the findings worker are Windows scheduled tasks (`scripts/register_*.ps1`). The Schedules row now says both.
3. **`docs/security.md` is new: every item of the review, closed or open.** 27 items: the review's 24 (H1 to H3, M1 to M8, L1 to L13) and four this session found (S1 to S4). Closed today: S1, S2, S4, and M5's "one look". Read again today: migration 034 is in the database (no anon insert policy or grant, no sequence right, no execute on `site_ask_admit`), so H3, M1 and L6 are closed; M6, L7 and L8 are as the review found them.
4. **S2 is the one that mattered.** Five internal addresses (`/severance/finder`, its download, `/severance/lease/real`, the two draft reports) opened only with `?token=`. The finder wrote the token into its own links and form, and `check-values.mjs` opened the drafts with it, so every landing's check against production put the production token into a production address, the thing session 301 set out to end. They now open with the internal cookie as the `/internal` pages do. An address with `?token=` still opens them.

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first). After the landing, each of these opens with the cookie and no token. Before, production answered "No page at this address":

1. https://erw-flame.vercel.app/reports/draft/shape-premium
2. https://erw-flame.vercel.app/reports/draft/ai-gigawatts
3. https://erw-flame.vercel.app/severance/finder
4. https://erw-flame.vercel.app/severance/lease/real
5. `docs/security.md`, section "What needs Samuel, with the choice".
6. `docs/brand/review-371/`: the four pages before (production, cookie only: "No page at this address") and after (the local build), at 1280 and 390.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session371` and every module that reads a file this session changed (`test_session48`, 49, 57, 58, 59, 67, 86, 87, 128, 177, 188_queue, 206, 216, 239, 241b, 276, 301, 45) | 0 | the last runs: 226 tests OK before the S4 test; then `test_session371`, 177, 301: 47 OK. Three earlier tests pinned the old code (`test_session48`, `57`, `86`), and they now pin the new lines |
| `verify_rls.py --catalog` (read only) | 0 | 0 mismatches; 25 tables, row-level security on for every one |
| `scheduler.py --status` (read only) | 0 | six jobs active, last runs succeeded, HTTP 204 |
| `npm ci` | 0 | |
| `npm audit --json` | 1 | 5 high, all L9's linter chain (`eslint-config-next` 16.3.8 through `braces`); the only fix is `eslint-config-next` 14 (not applied, listed) |
| `npm run build` (erw-371 at `5eff1d65`) | 0 | no statement timeout |
| `check-security.mjs` | 0 | 50 of 50 |
| `check-csp.mjs` | 1, then 0 | the first run: 89 pages, 0 violations, but "/storage: the chart library loaded and drew" FAILED. `/storage` draws in SVG now and loads no library, so the probe was stale (S4). The probe now opens `/map`: exit 0 |
| `check-routes.mjs` | 0 | 211 pages in review and the live list asked as a visitor, 0 failed |
| `check-values.mjs` | 1 | 6,592 of 6,629 match; 31 latest prices superseded; 6 FAILED, the six of `/learn/problems/know-your-grid` that production fails too (session 369's fix). The two drafts were read with the cookie alone and every value matched |
| S2 probe on the local build (`runs/chain_oct20d/s371/probe_s2.mjs`) | 0 | each of the five: a visitor is shut out, the cookie opens it, no token in the page |
| Impeccable `detect --json` on the four pages | 0 | no finding |
| Shots, before and after, 1280 and 390 | 0 | sixteen, `docs/brand/review-371/` |

## Landing

(the orchestrator's)

## Decisions made without you

- **The CLAUDE.md part goes as a patch**, per the brief; the patch's paragraph on schedules says the data machine's scheduled tasks exist (point 2 above) instead of copying the todo's "stays true".
- **"Running things" starts with the precheck, then sync**: the todo named sync first, but every chain session runs `scripts/precheck.py` first today (`queue/CHAIN_TEMPLATE.md`, `docs/machines.md`).
- **The two bullets went under Key conventions, not the numbered non-negotiables**, so rules 1 to 9 keep their numbers.
- **The runbook's pg_cron section was amended, not rewritten**: its "cron-job.org is the first choice" stays, followed by a sentence that session 59 chose pg_cron and that pg_cron is in use.
- **The done line of todo 007 is the first line after its front matter**, not above it: `scripts/taskqueue.py` and `test_session59` read a file of `queue/done/` from its front matter.
- **L5 is left with H1.** `test_session177` pins the old link "word for word" until its retirement. The `?token=` comparisons of the pages go with it. S1 made the cookie comparisons constant-time.
- **S2 opens the pages with the cookie but keeps `?token=` working**: retiring the token in addresses is H1's ruling. The finder writes the token into a link only when its own address brought it.
- **M5's "one look" was done by this session**: one request to `api.cdnjs.com` and one to cdnjs for the file. The browser of every visitor of the map already asks cdnjs for that file. The published SHA-512 matches, and the file's SHA-384 is the hash in the code.
- **The report-only header (M4) is not dropped today**: it was set beside the enforced one on 19 October for a week. The row in `docs/security.md` says what to do on or after 26 October.
- **The roadmap's item 7 is not ticked**: only a person writes `docs/roadmap.md`.
- **No usage count was turned on or changed** (a ruling). `docs/security.md` says what is recording today (days from 10 October) and leaves the reading against "no usage count on tool pages" to you.

## For Samuel's ruling

- **The CLAUDE.md patch**: `runs/chain_oct20d/s371/claude_md.patch` (the orchestrator applies it, or you do: `git apply runs/chain_oct20d/s371/claude_md.patch`).
- **The nine items of `docs/security.md`, "What needs Samuel, with the choice"**:
  1. H1, retire the old link.
  2. H1, rotate the token.
  3. H3, look that `SUPABASE_SERVICE_KEY` is on Vercel (034 is applied, so the site's writes need it).
  4. M6, the default privileges.
  5. M7, the Python packages.
  6. L4, the cookie's lifetime.
  7. L7, `search_path`.
  8. L8, sign-ups in Supabase Auth (on today).
  9. L9, the linter's packages.

  Each has its choice written out there.
- **S3**: three internal checks send the real token in an address to prove it opens nothing. Run them against a local build only, or against production after the rotation.

## Files

- New:
  - `docs/security.md`
  - `tests/test_session371.py`
  - `docs/brand/review-371/` (16 shots and a README)
  - this report
  - outside git: `runs/chain_oct20d/s371/` (the patch, the probes, every check's output)
- Changed:
  - `ARCHITECTURE.md`
  - `docs/runbook.md`
  - `queue/todo/007-code-docs-for-machines.md` moved to `queue/done/`, with its line
  - `site/lib/release.ts` (`cookieOpens`)
  - `site/proxy.ts`
  - `site/app/cost-of-power/battery/read.ts`
  - `site/lib/finder.ts` (`internalOpen`)
  - `site/app/severance/finder/page.tsx`
  - `site/app/severance/finder/download/route.ts`
  - `site/app/severance/lease/real/page.tsx`
  - `site/app/reports/draft/shape-premium/page.tsx`
  - `site/app/reports/draft/ai-gigawatts/page.tsx`
  - `site/scripts/check-values.mjs`
  - `site/scripts/check-csp.mjs`
  - `tests/test_session48.py`, `tests/test_session57.py`, `tests/test_session86.py`
