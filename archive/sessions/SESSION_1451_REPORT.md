# Session 1451 report: the second dry runs, the previews sent, the before and after

Energy Research Warehouse (ERW), session 1451 (chain 149's "1448"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 03:00 to 03:14 UTC. Model Fable 5.1, high effort. **Model spend USD 0.080** (the Digest twice, USD 0.0315 and 0.0260 with the summary's second call not priced in the log line; the Roundup twice, USD 0.0115 and 0.0117; cap USD 4; the ledger off as session 2705 ran it, the costs from the run logs). No warehouse data written; two preview emails to the fixed recipient; web requests to the Claude API, the ERW's own database (reads) and Resend. Branch `wip/1451-periodicals` over `wip/1450-periodicals`.

## What is in your inbox

- 03:07 UTC, **"[preview, dry run 1451, after] ERW Daily | Henry Hub natural gas: 2.52 USD/MMBtu, down 9.3% on the close before"** (Resend id `01a1aed3-78a5-7c87-befa-16f2019cc23c`): the Digest of 26 October over the same stories as the 01:27 UTC preview, by the code of sessions 1435 to 1450.
- 03:07 UTC, **"[preview, dry run 1451, after] ERW Weekly | Gingerah Energy refers 1,000 MW data centre with 5GWh battery in...; Brent down 6.3% on the week"** (`01a1aed3-79e5-7720-b367-45f454aa5b54`): the Roundup of W44 over the same stories as the 01:33 UTC preview.
- Both to the one fixed recipient of `DIGEST_RECIPIENTS`, never a subscriber; nothing claimed.

## What it did

- **The landing first**: `origin/main` is still red (session 1439's note; `0d0e41e66` unchanged), so the stack was not landed; it is tried at session 1456.
- **The runs** (`runs/periodicals_dryrun/s1451/run.sh`, the worktree's code): the Digest of 26 October (`--now 2026-10-26T15:45Z`, 311 stories, 286 clusters) and the Roundup of W44 (67 stories), run twice: the first time the worktree held no local `policy_reads`, `policy_actions`, `energy_deals` or `datacenter_projects` (the Roundup said "no dated events" and the Digest had no policy actions); the four tables were copied from the main checkout and both run again (the two tracked ones, `energy_deals.csv` and `datacenter_projects.csv`, restored to HEAD after). The emails under `email/`.
- **The reading**: `docs/reviews/periodicals-before-after-2026-11-06.md`, one row a faulted line with the line before and after, for the Digest (24 rows) and the Roundup (12 rows), and the counts; the faults file's new section "State after the second dry runs".
- **The counts** (the Digest of 26 October, before and after): words above the fold 295 and 364; stories under What moved 3 and 5; why lines with "signals" 4 and 0; first links reaching Google 5 and 4 of 10; figures in the block without a key 2 and 0; oil price items in the top ten 2 and 1.

## What a sharp reader sees now

1. The opening number is the day's: Henry Hub down 9.3 percent on 26 October against the 23rd, named by the day's gas story, with its reason; the block's four rows each carry a change, a status and a key.
2. Fault 7 stands: "LNG or gas project faces executive departures and alleged Russian involvement claims; geopolitical risk to US energy sector" (0.36 of its words are the headline's). For chain 150.
3. Three of five What moved items print the headline alone with "One outlet has reported it so far.": the check refuses the old prompt's lines; the new prompt's lines come with Friday's scoring.
4. The Roundup opens with Brent (down 6.3 percent, named by the week's oil stories); the five numbers stand in for the empty deal and datacenter categories with the next price moves, said so; the limitation says the empty fields; next week holds three items of three kinds on three days; the subject is 100 characters.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1451"` | 0 | |
| `brief.py` and `roundup.py` with the model, twice each | 0 | the costs above |
| `email_digest.render` twice; `send_preview` twice | 0 | one recipient each, the character once in each |

## Decisions made without you

- The second runs are of the same days as the first (26 October; W44), not of 5 November: the comparison is the code's, as the chain asks.
- The four local tables were copied into the worktree for the runs (the daily run's steps read `warehouse/output` of their own checkout); the two of them git tracks were restored to HEAD before any commit.
- The runs were made twice; the first pair's cost (USD 0.043) is counted.

## For Samuel's ruling

- None new.
