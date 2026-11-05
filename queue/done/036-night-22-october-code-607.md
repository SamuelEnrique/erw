# Chain of 22 October 2026, night: session 607, code machine, unattended (chain 023's landing: the deployment and the cleanup)

machine: code

Written by portable-laptop at about 00:45 UTC on 22 October, by session 563, on the owner's instruction. Session 563 landed chain 023 on main through the full gate (`87c343cc`, run 39697392914). In the 20 minutes it waited, Vercel made no production deployment of that commit (rate limited, as sessions 483 and 488 found), so the snapshot after the deployment and the cleanup are left for this session.

## Session 607: the snapshot after chain 023's deployment, and the merged branches deleted

Long end 1:00. Precheck first (`.venv\Scripts\python.exe scripts/precheck.py --what "session 607"`). Read `archive/sessions/SESSION_563_REPORT.md` on main first, then do its "To finish", each command its own, never piped, each exit code read:

1. Find whether Vercel has deployed main at or after `87c343cc`. Use GitHub's deployments list for the Production environment (`https://api.github.com/repos/SamuelEnrique/erw/deployments?environment=Production`), and confirm in the internal view of production: with the internal cookie (`unlockPost` of `site/scripts/browser.mjs`), `/board` shows "Tables read, with their licenses" (session 502) and `/cost-of-power/battery` reads "25 published figures" (session 501). If it has not deployed, do not wait more than 20 minutes: write that down and leave step 2 under "To finish".
2. Once it has: `node site/scripts/snapshot-live.mjs take s607-after`, then `compare s563-after s607-after`. Every line goes into the report, marked expected or not. 0 differences are expected, since no page is live (`site/lib/release.ts`), and any line not expected goes at the top.
3. Delete the merged wip branches the report names, each only after `git merge-base --is-ancestor origin/<branch> origin/main` exits 0. Do not touch another machine's branch that is not merged.
4. If time is left, the first item of the report's "Left from the branches' own To finish": why the ten pages on main (`/map`, `/events` and its event pages, `/learn/bill`, `/research/card/gas_sets_price`) draw fewer checked numbers than their floors. Name the cause; a fix that changes a page lands through `task/` with rule 8's snapshots.

Write `archive/sessions/SESSION_607_REPORT.md` (the checks with their exits, decisions, "For Samuel's ruling", "To finish", files), push it to main, and stop.
