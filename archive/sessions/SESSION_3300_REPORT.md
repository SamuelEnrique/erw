# Session 3300 report (chain 200, the desktop's third window, session 1 of 13): the next file and the ground

lab-desktop, 6 November 2026, 19:06 to about 19:25 UTC. Opus 5.5. Branch `wip/3300-companies` (worktree `../erw-3300`, cut from `origin/main` at `d377b50a6`).

## What was done

- **Numbers.** The queue's first free number at or above 198 was 200 (199 was taken by the portable laptop's Ask evaluation chain minutes earlier, `2865db0b8`); the next file is 201. Sessions start at 3300: no report, branch, commit or queue file on origin main or any branch uses a number at or above 3300 (the other chains of the day hold 3247 to 3282).
- **The prompt** saved word for word as `queue/done/200-day-6-november-desktop-window3-companies.md` (`71c5c894a`, pushed to main alone).
- **The next file** `queue/next/201-day-7-november-desktop-window3-continued.md` (`machine: lab-desktop-window3`, twelve sessions: chain 200's unfinished steps, then the resolution's and the pages' faults), committed alone as `d377b50a6` and pushed to main.
- **Snapshots** of that push: `s3300-q201-before` (19:09:56) and `s3300-q201-after` (19:16:07, after Vercel's `success` for `d377b50a6`): 25 pages, **0 differences** (expected: a queue file changes no page).
- Precheck passed (exit 0); freeze status exit 0 (no `REVIEW_FREEZE`); the data lock was free; `lab-desktop` is a data machine.

## The ground

| Table (main) | Rows | Name fields | Anchor | License in force |
|---|---|---|---|---|
| `energy_deals` | 529 | buyer (245 forms), seller (309), other_parties (77, `;` lists) | event_id | license needed since 21 Oct: internal rows |
| `datacenter_projects` / `datacenter_facilities` | 163 / 428 | operator (61 / 65), developer (65 / 65), utility (5) | entity_id | license needed: internal rows |
| `eia860_generator_owners` | 5,680 | owner name (2,038), operator (826) | owner id in entity_id, operator x_utility_id, owner state | public |
| `eia860_plants_annual` | 17,349 | operator (6,916) | x_utility_id, x_state | public |
| `eia860m_operating_generators` / `_planned_` | 28,712 / 2,361 | operator (6,025 / 995) | utility_id, energy_source, nameplate_mw, operating year | public |
| `eia861_utility_data` | 22,716 | name (3,754) | x_utility_number, x_ownership, x_state, the RTO flags | public |
| `utility_service_territories` | 11,893 | name (2,909) | x_utility_number, state, county | public |
| `ercot_interconnection_queue` | 1,758 | operator = interconnecting entity (1,317 forms, case variants) | queue_id | public |
| `nyiso_interconnection_queue` | 1,814 | operator = developer (846) | queue_id | license needed: internal rows |
| CAISO, ISO-NE, MISO, SPP, Berkeley Lab queues | | no developer field (Berkeley Lab's utility is the transmission provider) | | |
| `policy_actions` | 2,020 | agency (9), parties (31 forms: "Energy Department", "NRC") | event_id | public |
| `nrc_power_reactors` | 130 | operator, x_licensee (30), x_parent_company (21) | docket | public |
| `energy_companies` | 504 | tool 10's seed (Thesis Builder and deal parties, `erwco:` ids) | | public |

- **Menus.** Infrastructure holds four (Project map, Datacenter tracker, Storage, Deals) of the eight allowed; Games holds five. `/companies` is a permanent redirect to `/deals?tab=companies` (`site/next.config.ts:84`, `site/lib/tabs.ts:39`), the deals page's Companies tab (`energy_companies`). No `/capital`.
- **release.ts**: `/companies` is listed `review`; an unlisted path takes its parent's status or `review`, so `/companies/<id>` and `/capital` are in review with `release.ts` untouched.
- **Machine:** 4.7 GB of 15.7 GB memory free, 18 node and python processes (1.1 GB) of other windows; 247 GB disk free.
- **Writes:** chain 147's `runs/c147/write_table.sh` (lock waited for, validator, coverage `--only`, archive, metadata diffed and put back before release, patch applied to the branch) is the pattern for this chain's write (`runs/c200/`).

## Decisions made without you

- **New tables beside `energy_companies`**, not in place of it (rule 3): `companies`, `company_aliases`, `company_links`. The deals page's Companies tab keeps reading `energy_companies`; `/companies` becomes the new page (its redirect removed when the page lands).
- **Chain 156's counterparties branch has not landed** (`wip/3233-deals`); the deals' parties are read from main's `energy_deals`, and that branch's `aliases.yaml` is read for evidence only, each alias taken cited to it.
- **A link row's license**: `internal` where its input is internal in coverage or "license needed" in `license_status.csv` without a permission (`energy_deals`, both datacenter tables, the NYISO and ISO-NE queues), else `public`. The companies table's columns built from internal rows are marked so in its header and left out of public downloads.
- The push of the prompt file (`71c5c894a`) had no before snapshot (the rule was read after it); `s3300-q201-before`, taken after it deployed, matched the next push's after snapshot exactly, and a queue file changes no page.

## For Samuel's ruling

- Whether `energy_companies` (the Thesis Builder's table) should in time be folded into `companies`, or stay the Thesis Builder's own.

## Cost

- No model call. USD 0.00.
