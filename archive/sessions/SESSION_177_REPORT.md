# Session 177 report: the security audit, its safe fixes, and usage counts with no cookie

Run on 10 October 2026, 01:00 to about 03:25 local (08:00 to 10:25 UTC), unattended, second of the chain 176 to 180 (`CHAIN_OCT10_PROMPT.md`). Built in the worktree `erw-142` on `wip/177-security`, never pushed. Outputs under `runs/session177/`. Model spend: USD 0, no model call.

## Read these first

- **24 findings: 3 high, 8 medium, 13 low. 12 are fixed in this branch, 9 are left for Samuel (and one step of a fixed one: rotating the token), 3 are noted or not applied.** The ranked list, each with what is exposed, the fix and the fix's risk: `docs/reviews/2026-10-10-security.md`.
- **The database was already sound, and nothing was applied to it.** Row-level security was on for all 19 tables; the anon key reads 8 and is refused by the other 11 (HTTP 401, code 42501); no secret is in the git history (12 of this machine's values searched for exactly: 0 found) or in what a browser gets (0 hits in 2,121 files). Migration 028 changes no existing policy, grant or row; it was tried four times inside a transaction that was rolled back (`sql_trial.out`). The coordinator applies it; the site works before and after.
- **The unlock form's first version would have failed in every real browser, and its 43 scripted checks passed.** A browser posts a form with `Origin: null` when the page's referrer policy is `no-referrer`; the route refused that as another site's form (404). Found by reading the Fetch standard, reproduced in a real browser (`form_in_browser_before.out`), fixed, and now proven by `check-csp.mjs`, which opens the internal view by the form in a real browser (`form_in_browser_after.out`). The old link was never affected. The same check now posts the sign-up form in the browser too.
- **Three things found broken on main, not made by this session.** (1) `check-values.mjs` stopped at "unknown check datacenters|counted" since session 166: fixed here, it runs again (6,894 of 6,925 values match; the other 31 are latest prices a newer interval replaced, checked for staleness). (2) `/data/methods/thesis` showed nothing after the words "cites each as FRED's Cite tab does", footer included: a placeholder in angle brackets was read as a tag. Fixed by the markdown fix (M8). (3) `tests/test_session92.py` expects `/cost-of-power/battery` to be live; it is in review since session 166. Not touched: 1 failed, 2,580 passed in the whole suite on the final tree (the base commit holds the same line of `release.ts`, so it fails there too).
- **This branch moves Next.js from 16.3.6 to 16.3.8** (six advisories). It is its own commit (`6bd10fc`) so it can be reverted alone. Every other worktree of the chain needs `npm ci` (under the build mutex) after it merges main with this in it.

## What to review

- `https://erw-flame.vercel.app/internal/open` (the new door; works for anyone, shows only a form)
  - Paste the token, click **Open the internal view**: the home page opens with "internal view lock" in the menu. The address bar never shows the token.
  - Type a wrong token: back on the form with "That token was not accepted. Nothing was changed."
  - The old link `.../internal/unlock?token=...` still works exactly as before. Say when the form is confirmed; the link is then retired and the token rotated (review, H1).
- `https://erw-flame.vercel.app/internal/usage` (internal view; after migration 028 is applied)
  - Three tiles (events, browsers today, days) and three tables: by day, by page, by tool, each with the four events in columns.
  - Open `https://erw-flame.vercel.app/mix`, change one of its controls, come back and reload: the row `/mix` (by page) and "Energy mix" (by tool) each show 1 more "tool opened" and 1 more "input changed".
  - A browser with Do Not Track or Global Privacy Control on adds nothing.
  - Before the migration it reads "The usage counts could not be read".
- `https://erw-flame.vercel.app/internal/costs` and `https://erw-flame.vercel.app/internal/ask` (internal view): both open with no `?token=` in the address.
- `https://erw-flame.vercel.app/privacy` (internal view; new, in review): five sections. Read "Usage counts" and "Cookies and browser storage": every sentence is checked against the code by `tests/test_session177.py`.
- `https://erw-flame.vercel.app/terms` (internal view): the new section "Usage counts and cookies" and one added sentence under "Questions asked on Ask". Exact text below.
- `https://erw-flame.vercel.app/storage` (internal view): the charts draw (they now load only if the chart library's bytes match its hash).
- `https://erw-flame.vercel.app/data/methods/thesis` (internal view): the publishers' table is whole again and the page has its footer; the FRED row shows the placeholders `<title> [<id>] ... <date>` as text.
- Any page, browser tools, Network, the page's response headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` and `Content-Security-Policy-Report-Only`.
- The footer of every page: "Terms. Privacy." (a visitor sees "Privacy in review", greyed, as Terms is).

### The exact text changed on `/terms`

- Added to "Questions asked on Ask", after the sentence that ends "and is never logged or stored.": "To count the questions one address asks in a day, the database keeps a keyed code of the address for that day only: it cannot be turned back into an address and is another value the next day."
- New section "Usage counts and cookies", before the closing line: "This site sets no tracking cookies. It counts how its tools are used with no cookie and no personal data: the page's path, the tool, one of four events (a tool opened, an input changed, a scenario compared, a download), the day, and a code that stands for one browser for that one day and cannot be matched with any other day. The IP address, the user agent, the referring page and what you type are never recorded, and a browser that sends Do Not Track or Global Privacy Control is not counted. The two cookies the site can set are for people reviewing it, after they open the internal view. All of it, exactly: Privacy."
- Nothing was removed.

## What was built

- **The audit**: `docs/reviews/2026-10-10-security.md`; `scripts/scan_git_secrets.py` (the history scan; never writes a value); `warehouse/supabase/verify_rls.py` (the anon key's reads against the expected list).
- **The database**: `warehouse/supabase/migrations/028_security_usage.sql`, `warehouse/supabase/rollbacks/028_security_usage.sql`, `apply.py --rollback <n>` (rollbacks live outside `migrations/`, so no full run picks one up).
- **Guards and limits**: `site/lib/guard.ts` (`sameOrigin`, `scripted`, `typed`, `limited`), used by `/api/ask`, `/api/subscribe`, `/api/play/finish`, `/api/play/score`, `/api/download`, `/api/thesis/run`, `/api/thesis/provider`, `/api/thesis/pitchbook`, `/api/analysis`; size and form checks on `/api/subscribe/confirm` and `/api/unsubscribe`.
- **Headers**: `site/next.config.ts` (seven headers on every answer; three more on every `/internal` address).
- **The unlock**: `site/app/internal/open/page.tsx` (the form), `POST` in `site/app/internal/unlock/route.ts` (the `GET` untouched); `/internal/costs` and `/internal/ask` also open by the cookie.
- **The chart library**: `ECHARTS_SRI` in `site/components/echarts.ts`.
- **Markdown**: `safeHtml` and `safeHref` in `site/lib/markdown.ts`.
- **Usage counts**: `site/lib/usage.ts` (`track`, for session 179), `site/components/Usage.tsx` (mounted once in `site/app/layout.tsx`), `site/app/api/usage/route.ts`, `site/lib/usagepath.ts`, `site/app/internal/usage/page.tsx`, `docs/methods/usage_counts.md`.
- **Pages**: `site/app/privacy/page.tsx` (new, `review` in `site/lib/release.ts`, linked in the footer), `site/app/terms/page.tsx`, the state "busy" on `/subscribe`; `docs/tools.md`, `docs/release-gate.md` and `warehouse/supabase/README.md` say what changed.
- **Checks and tests**: `site/scripts/check-security.mjs` (46 checks), `check-csp.mjs` (a real browser: every page under both policies, the unlock form, the sign-up form, a chart), `test-usage.mjs` (14), `test-markdown-safe.mjs` (6), `tests/test_session177.py` (28); `check-values.mjs` and `check-routes.mjs` extended; `tests/test_session128.py` reads the internal ask page as it is now.
- **Dependencies**: `next` and `eslint-config-next` 16.3.8; `npm audit fix` (sharp 0.35.5, source-map-js). `requirements.txt` unchanged.
- No file under `site/app/cost-of-power/battery/` or `site/app/network/` was edited.

### Who reads what with the anon key (from the code, not from memory)

- The site (`rest`, `restCount` in `site/lib/supabase.ts`; `/api/download`; `/api/entity`): `series`, `entities`, `events`, `latest_prices`, `catalogue`, `headers`, `game_scores`. A test finds every such call and fails if a table is not public in `verify_rls.py`.
- The site, insert only (unchanged by this session): `subscribers`, `game_plays`, `game_scores`, `site_api_calls`.
- The site, functions (unchanged): the 16 of migrations 007 to 027; new: `site_rate_admit`, `site_usage_record`, `internal_usage`.
- The `erw` package's Supabase backend with the anon key (`package/src/erw/remote.py`): `catalogue`, `series`, `entities`, `events`, `headers` (and `sources`, `latest_prices` by name).
- Scheduled and local jobs: `warehouse/derived/grid_network.py` (`series`), `warehouse/metadata/build_status.py` (`latest_prices`, the anon key when no service key), `code-branch.yml` (the site's build and `check-routes`), `check-values.mjs` (the eight public tables and the public storage object). `warehouse/thesis/eval/prove_accept.py` asks `thesis_runs` with the anon key in order to be refused.
- Public, 8: `series`, `entities`, `events`, `latest_prices`, `catalogue`, `sources`, `headers`, `game_scores`. Blocked, 11 and the 4 new ones. No table was left "unsure".

### How the daily salt is made (asked for exactly)

- The server sends the database `HMAC-SHA256(ASK_VISITOR_SALT, "erw-usage\n" + address + "\n" + user agent)`: no address and no user agent leave the server.
- The database hashes that again under the day's salt: 32 bytes from `gen_random_bytes`, drawn the first time it is needed that UTC day. It is derived from nothing.
- When the day is over (the first call of any of the functions after 00:00 UTC) the day's lines become counts in `site_usage_daily`, and the lines with their hashes and the salt are deleted in the same transaction. A random value that is deleted cannot be computed again from anything kept.
- Two honest limits, both written on `/privacy` or in the method note: Supabase's own backups hold what the tables held when they ran; and the day closes at the first call after midnight, not at midnight.

## Pulls and model spend

- Model spend: USD 0.00 of USD 0. `check-ask-conversation.mjs` asks three paid questions and was not run.
- Production in the internal view, by `check-routes.mjs` as it always does (its baseline is `SITE_URL`): 4 runs, each one unlock by the old link and 156 pages, 628 requests in all. Not a pull this session chose: the check's own design, named here because it puts the token in a production address (review H1).
- Production as a visitor: 28 GET requests (11 pages, 9 routes, 7 static files, the plain-HTTP address), 0.9 MB; later 1 HEAD of the plain-HTTP address. `runs/session177/requests.csv`.
- The chart library: read once more in a browser page of the local site to hash it (cdnjs, the file every chart page already loads).
- npm's registry (`npm audit`, `npm view`, two installs) and PyPI (pip-audit into a throwaway environment in the scratch folder, deleted).
- Supabase, read only: the catalog twice (read-only transactions, `catalog.json`, `catalog_read2.out`); `verify_rls.py` three times; the four rolled-back trials. The first two `verify_rls.py` runs each sent anon queries that ran to the role's 3 second limit and were cancelled (my check was too heavy; it now asks one name a request).
- Written to production by the site's own routes, as that check always does: about 35 finished plays flagged `check = true` (seven runs of `check-battery-game.mjs`, five plays each), which the leaderboard and the research data leave out.

## Checks run (each its own command; exit code read; files in `runs/session177/`)

| Check | Exit | File |
|---|---|---|
| `npm run build`, final (Next 16.3.8, every fix), under the mutex | 0 | `build4.out` |
| `check-security.mjs` (46 of 46) | 0 | `f_check_security.out` |
| `check-routes.mjs` (as a visitor: 1 live and 155 in review; 0 failed) | 0 | `f_check_routes.out` |
| `check-values.mjs`, twice (6,894 of 6,925 match, 31 superseded, both times) | 0, 0 | `f_check_values_1.out`, `f_check_values_2.out` |
| `check-no-request.mjs` (`/battery/customer` still sends nothing after it loads) | 0 | `f_check_no_request.out` |
| `check-csp.mjs`, a real browser: 82 pages, 0 violations of either policy; the unlock form opens the internal view; the sign-up form is taken as the site's own; a chart draws | 0 | `f_check_csp.out` |
| `check-csp.mjs --phone` (4 pages at 390 px, none wider than the screen) | 0 | `f_check_phone.out` |
| `check-analysis.mjs`, `check-thesis.mjs` | 0, 0 | `f_check_analysis.out`, `f_check_thesis.out` |
| `check-ask-ercot`, `-hours`, `-panel`, `-words` (no model call) | 0, 0, 0, 0 | `f_check_ask_*.out` |
| `check-battery-game.mjs` phone and laptop (92 of 92 each) | 0, 0 | `f_check_battery_game_*.out` |
| `test-usage.mjs` (14), `test-markdown-safe.mjs` (6) | 0, 0 | `f_test_usage.out`, `f_test_markdown_safe.out` |
| `pytest tests/test_session177.py` (28) | 0 | `test_session177.out` |
| `pytest tests` (the whole suite, on the final tree): 1 failed (`test_session92`, on main already), 2,580 passed, 226 skipped | 1 | `suite_3.out` |
| One well-formed question to the local `/api/ask`: refused at admission (503, "closed": the local server holds no visitor salt), so the guards let a real request through and no model was asked | | `ask_probe.out` |
| Migration 028 and its rollback in one rolled-back transaction (27 checks) | 0 | `sql_trial.out` |
| `verify_rls.py --before-028 --catalog` | 0 | `verify_rls_before.out` |
| `scan_git_secrets.py` (4 hits, all stand-ins in test scripts) | 1 | `git_secrets.out` |
| Production's files and the local build's searched for secrets | 0, 0 | `prod_bundle.out`, `local_bundle_scan.out` |
| `curl -I` of four local addresses; the plain-HTTP redirect (308) | | `curl_headers.out`, `curl_http_redirect.out` |
| `npm audit` before (8 high) and after (5 high, all the linter's packages); `pip-audit` (4 packages) | 1, 1, 1 | `npm_audit_before.json`, `npm_audit_after.json`, `pip_audit.json` |

- The whole list was run three times, on three builds: before the markdown fix (`first_run/`), before the form's fix (`second_run/`), and on the final build (the files above). Every run: every check exit 0. The second run is the one that did not see the form's fault: no script could.
- The whole suite was run three times; the last, on the final tree, is the one in the table.

## Decisions made without you

- **The full Content-Security-Policy is report-only.** 82 pages load under it with 0 violations, but what a page does after a click is not proven. The four directives that cannot break a page are enforced. Reversible: one line in `next.config.ts`.
- **Rate limits fail open to the memory count**, never closed: a limit that cannot ask the database behaves as before. A right unlock token is never limited.
- **The new database functions take the internal token** (`INTERNAL_COSTS_TOKEN`), so the anon key alone cannot fill the counts. No new secret.
- **The usage hash uses `ASK_VISITOR_SALT`** as the server's secret. A server without it records nothing.
- **A visitor who asks for a page in review is counted** under that page with the tool "In review (not opened)". The internal view is counted with the tool's real name.
- **Pages that promise nothing typed is sent** (`/battery/customer`, the contract boxes of `/cost-of-power` and its tabs, `/severance`, `/learn/bill`) get the page view counted and nothing after it. On `/cost-of-power/battery` this means no "input changed" is recorded; session 179's `track("scenario compared")` still works there, and should not be called from inside the contract box.
- **`track(event, detail?)`: `detail` is `{ path?: string }` only.** Nothing else can be sent, because nothing else is stored.
- **Tool names** are the menu's own labels (`site/lib/pages.ts`); a page with no menu entry has an empty tool name.
- **`/privacy` was created** (none existed), `review`, linked in the footer beside Terms.
- **Earlier per-day counts are kept two years**, as counts only.
- **The chart library's hash was computed from the file as received**, not compared with a hash the host publishes (not an approved request). Worth one look.
- **Next.js was moved by a patch release** although `npm audit fix` alone does not do it (the version is pinned exactly).
- **`tests/test_session128.py` was edited** (two assertions): the internal ask page now also opens by the cookie.
- **The anon key's direct inserts (H3, M1) were not closed**: the ledger's write cannot be proven without a model call, and the site and the database must change in order.
- **Default privileges (M6) were not changed**: it sets the rules for every later migration.
- **`verify_rls.py` lists every table.** A table it does not know fails `--catalog`, so the next migration that adds a table must add it to the list.

## For the coordinator (in order)

1. Before anything: `node site/scripts/snapshot-live.mjs take before177` (its own command).
2. Apply the migration (it changes nothing a page reads; safe before the deploy): `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/supabase/apply.py --only 028 > runs/session177/apply_028.out 2>&1; echo "exit=$?"`. Must be: exit 0, the line "applied 028_security_usage.sql (Postgres connection)".
3. Verify: `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/supabase/verify_rls.py --catalog > runs/session177/verify_rls_after.out 2>&1; echo "exit=$?"`. Must be: exit 0, "PASS: 0 mismatch(es)"; the eight public tables "public"; the four new tables "blocked"; line 3 "REFUSED" with HTTP 401 and 42501; `internal_usage` "refused"; section 5 shows 23 tables, each "rls on".
4. `node site/scripts/check-values.mjs https://erw-flame.vercel.app > runs/session177/check_values_prod_before.out 2>&1; echo "exit=$?"`: exit 0 (no page lost a read). A first failure is run a second time.
5. In the main copy after the merge: `npm ci` then `npm run build` under the build mutex (Next 16.3.8); `pytest tests/test_session177.py`.
6. Deploy the usual way. Then `take after177` and `compare before177 after177`. Expected on all 25 pages: the footer gains "Privacy in review" after "Terms in review". No checked number moves. Anything else is not meant.
7. After the deploy: `node site/scripts/check-security.mjs https://erw-flame.vercel.app --recorded > runs/session177/check_security_prod.out 2>&1; echo "exit=$?"`: exit 0, 47 of 47. It posts two wrong tokens and two real counts (`/terms`, `/privacy`). `--recorded` needs `ASK_VISITOR_SALT` on Vercel; if `/internal/ask` says the tools are closed for lack of it, run without `--recorded` and tell Samuel the counts need that variable.
8. `node site/scripts/check-csp.mjs https://erw-flame.vercel.app --recorded > runs/session177/check_csp_prod.out 2>&1; echo "exit=$?"` (a real browser; about three minutes): exit 0, and these lines: "the form at /internal/open opens the internal view in a real browser", "0 enforced violation(s)", "/storage: the chart library loaded and drew" (the hash holds on production), "the sign-up form, posted by the browser, is taken as this site's own", and "--recorded: opening /storage in this browser added to the counts". It writes real counts for the pages it opens (about 85 page views, one browser). Without `ASK_VISITOR_SALT` on Vercel, drop `--recorded`.
9. `node site/scripts/check-values.mjs https://erw-flame.vercel.app` once more: exit 0.
10. Write the time of step 2 in `warehouse/supabase/README.md` (the 028 row of the record).
11. After main holds this: each remaining worktree of the chain runs `npm ci` under the mutex before its final build.
- To undo the database part: `apply.py --rollback 028` (drops the four tables with their counts and the six functions; the site falls back). To undo Next: `git revert 6bd10fc`.
- Session 179: `import { track } from "@/lib/usage"; track("scenario compared");` from a click handler. It never throws.

## To finish (Samuel)

- The old link cannot be retired yet: 31 check scripts under `site/scripts/` and the workflow `code-branch.yml` open the internal view by it. Moving them to the form is one session's mechanical work (review H1).
- Open `/internal/open` once and confirm it; then retire the old link and rotate `INTERNAL_COSTS_TOKEN` (review H1 gives the steps; rotation was not done here because it can lock you out).
- Rule on H3 and M1 (the anon key's direct inserts) before the anon key is given to any reader of the package.
- Rule on the default privileges (M6) and on enforcing the full policy (M4).
- Supabase dashboard, Auth: disable sign-ups (L8).
- `lxml` and `cryptography` need major versions (M7); `gridstatus` holds `lxml` at 5.x.
- `tests/test_session92.py` expects `/cost-of-power/battery` live: correct the test or the status.
- Set `ASK_VISITOR_SALT` on Vercel if it is not there: without it nothing is counted and the limits are per instance.

## The landing

