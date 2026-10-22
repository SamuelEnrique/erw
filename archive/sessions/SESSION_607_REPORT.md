# Session 607 report: chain 023's deployment confirmed, its branches deleted, the ten floors explained

22 October 2026, from about 04:49 UTC, unattended, on samueloldlaptop (the code machine), from `queue/done/036-night-22-october-code-607.md` (written by portable-laptop's session 563), taken after session 589's queue step. Precheck 0. Model spend USD 0. No warehouse data written.

## Read these first

AFTER_TOP

- **Chain 023 is deployed.** GitHub's Production deployments include `a3043fe1` (02:14 UTC), `95224f02`, `38bebe26` and `5283179e` (03:46 UTC), all after `87c343cc`; in production's internal view (`unlockPost`, the cookie) `/board` shows "Tables read, with their licenses" (session 502) and `/cost-of-power/battery` "25 published figures" (session 501), at 04:49 UTC.
- **`s563-after` is not on this machine** (portable-laptop took it), so `compare s563-after s607-after` could not be made. The pair this machine holds is `s589-before` (04:15 UTC, production on `5283179e` or later, chain 023 in it) against `s607-after`, which also covers session 589's landing of chain 034.
- **The ten floors are a hold** (below): no read fails and no floor was set wrong; their tables are "license needed" since 21 October.

## Step 1: the deployment

| Check | Exit | Result |
|---|---|---|
| `runs/s589_deploys.py` (GitHub's Production deployments) | 0 | newest `5283179e`, 03:46 UTC, success; none yet for `5b20c0f1` (session 589's merge, 04:27 UTC) at 05:00 UTC |
| production's internal view, `/board` | 0 | 200, "Tables read, with their licenses" present |
| production's internal view, `/cost-of-power/battery` | 0 | 200, "25 published figures" present |
| production's internal view, `/internal/holds` (session 587, in 589's landing) | 0 | 404: 589's build not yet served |
| the home page's style sheets | | `400q07hjrdmqm.css`, `4031mistz2237.css`, the build before 589's (whose `tokens.css` changed) |

## Step 2: the snapshots

STEP2

## Step 3: the branches deleted

Each only after `git merge-base --is-ancestor origin/<branch> origin/main` exited 0: `wip/429-combined`, `wip/430-check-values`, `wip/497-faults`, `wip/498-digest-numbers`, `wip/499-500-row-license`, `wip/501-battery-rows`, `wip/502-license-lines`, `wip/503-fresh-suite`, `wip/504-buildlock`, `wip/505-check-holds`, `wip/555-land-023`, `wip/562-land-023`, `wip/563-land-023`, and session 429's list: `wip/461-combined`, `wip/474-checks`, `wip/475-note`, `wip/416-417-charts`, `wip/418-digest-check`, `wip/419-faults`, `wip/421-csp`, `wip/422-tool-checks`, `wip/423-footer-targets`, `wip/424-ask-fixtures`, `wip/425-waits`, `wip/426-dc-cost-checks`, `wip/428-performance`, `wip/427-note`. 27 deleted; `task/563-land-023` was already gone. Session 589 had deleted chain 034's own.

## Step 4: the ten floors on main

`/map`, `/events`, `/events/uri-2021`, `/events/covid-2020`, `/events/caiso-heat-2020`, `/events/caiso-heat-2022`, `/events/east-heat-2025`, `/learn/bill` and `/research/card/gas_sets_price` (with `/deals`) draw fewer checked numbers than `site/scripts/check-values-floor.json` asks because **their figures come from tables held since 21 October**, and a held figure is drawn as "license needed" without a key. `warehouse/metadata/license_status.csv`: `event_window_daily` (the event pages and `/events`), `energy_projects` (`/map`), `cost_of_power_monthly` (`/learn/bill`), `energy_deals` (`/deals`), each "license needed" from 2026-10-21; `/research/card/gas_sets_price` draws two figures of the held grids' price tables. Session 408's report counts each page's held figures, and the full check-values runs of sessions 506 and 589 (6,457 and 6,456 values equal) found the pages showing "license needed" in place. Not a failed read (every value read is equal, and production fails the same floors), and not a floor set wrong (each was met before the holds). No fix here: lowering a floor, or counting a held figure toward it, is Samuel's ruling (chain 024's rule).

## Decisions made without you

1. **`s589-before` stands in for `s563-after`**, which is on portable-laptop; it was taken here on a build that holds chain 023.
2. **The wait for 589's deployment was held to 20 minutes** (04:50 to 05:10 UTC), as this file asks for 563's.
3. **The floors are explained, not changed.**

## For Samuel's ruling

- The ten floors under the holds: lower them while the tables are held, count "license needed" toward them, or keep them failing as a reminder.

## To finish

TO_FINISH_607

## Files

- `archive/sessions/SESSION_607_REPORT.md` (this report). Not in git: `runs/snapshots/s607-after`.
