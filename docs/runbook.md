# ERW runbook: commands a person runs by hand

Energy Research Warehouse (ERW). The daily run is a GitHub Action (`.github/workflows/daily-prices.yml`, `warehouse/run_daily.sh`). This page holds the few things it cannot do itself, each as the exact commands to run from the repository root, in order. Started in session 29.

Before any of them:

```bash
git pull origin main
pip install -r requirements.txt   # once per machine; .env holds the keys (never committed)
```

After any of them, commit what changed under `warehouse/metadata/` (the upload and archive manifests) and push after merging origin/main (CLAUDE.md, non-negotiable 4).

## Known gaps refreshed from this machine

`warehouse/metadata/known_gaps.csv` lists the tables whose source refuses the GitHub runners. A table there does not close the health gate (`PRIORITIES.md`), but it goes stale unless someone refreshes it from a machine the source answers. Both below have answered GitHub with HTTP 202 and an empty body on every run since 2026-09-27, and download normally from a residential connection. Once a week is enough: CARB auctions are quarterly and the queues are weekly.

### CARB auction prices (`carb_auction_allowance_prices`, internal)

```bash
python warehouse/connectors/carbon_auctions.py --table carb
python warehouse/validate/erw_validate.py warehouse/output/carb_auction_allowance_prices.csv
python warehouse/archive/archive.py write --tables '^carb_auction_allowance_prices$'
python warehouse/redivis/upload.py carb_auction_allowance_prices
```

The table is internal: the upload goes to the private dataset `energy_research_warehouse_internal`, and it is not in the Supabase live set.

### NYISO interconnection queue (`nyiso_interconnection_queue`, public)

```bash
python warehouse/connectors/iso_queues.py nyiso
python warehouse/validate/erw_validate.py warehouse/output/nyiso_interconnection_queue.csv
python warehouse/archive/archive.py write --tables '^nyiso_interconnection_queue$'
python warehouse/supabase/load.py --only '^nyiso_interconnection_queue$'
python warehouse/redivis/upload.py nyiso_interconnection_queue
```

The queue stays its own table (session 29, `docs/migrations/2026-09-29-consolidation.md`): the six ISO queues are snapshots refreshed independently, and this one only from a local machine.

What each step does:

- **Validator.** Exit 0 or stop there.
- **Archive.** Appends the new rows to the durable archive, through the shared index in the bucket, so a local run and the GitHub runs never archive the same rows twice.
- **Upload.** Writes the Redivis draft only. Nothing is released.
## Session 30: the cost page and the shadow scorer

**The internal cost page, `/internal/costs`.**

- It answers 404 unless `?token=` equals the server's `INTERNAL_COSTS_TOKEN`.
- The database function behind it answers nothing unless the same token is in `erw_private.settings`.
- `python warehouse/supabase/apply.py` writes it there from `INTERNAL_COSTS_TOKEN` in `.env`.
- To turn the page on, set `INTERNAL_COSTS_TOKEN` in the Vercel project's environment (the value in `.env`, at least 24 characters) and redeploy.
- To change the token: a new value in `.env`, run `apply.py`, then set it on Vercel.

**The Haiku shadow scorer** (`warehouse/news/shadow.py`):

- **Stop it now:** delete the line `SHADOW_MODEL: claude-haiku-4-5` from `.github/workflows/daily-prices.yml` and `roundup.yml`.
- **It stops by itself** on the `expires` date in `warehouse/config/shadow.yaml`.
- **Recipients:** `SHADOW_RECIPIENT` (a repository secret, optional), else `DIGEST_RECIPIENTS`. Never subscribers.
- **Agreement with the published scores:** `python warehouse/news/shadow_agreement.py`.

**A local session and the two ledger-like tables.** `api_cost_ledger` and `news_scores_shadow` grow on GitHub and locally.

- Before a session's first model call, take the draft's copy, so the session adds to GitHub's rows rather than to an older local file. `--restore` downloads only a table missing locally, so move the local copy aside first:

  ```bash
  mv warehouse/output/api_cost_ledger.csv warehouse/output/api_cost_ledger.csv.bak
  mv warehouse/output/news_scores_shadow.csv warehouse/output/news_scores_shadow.csv.bak
  python warehouse/redivis/upload.py --restore
  ```

  The archive keeps every row either copy ever had.

- A session sets `ERW_SESSION=<n>` and `ERW_SPEND_CAP_USD=<cap>`, so its calls are its own rows and stop at its cap.

## Session 29: removing the migrated tables from Redivis

After the consolidation (`docs/migrations/2026-09-29-consolidation.md`), the old tables stay in both Redivis datasets until a person removes them. The command checks every family first and removes nothing if any count disagrees:

```bash
python warehouse/redivis/upload.py --remove-migrated --dry-run   # what it would remove, and the counts
python warehouse/redivis/upload.py --remove-migrated
```

For each of the six families it checks, in the draft, that the consolidated table holds its old tables' rows:

- either its `count(*)` equals the sum of the old tables' counts;
- or, once the daily run has added days to it, every old row's key is in it (one join per old table).

On any mismatch it removes nothing and says which family failed. It removes only the old tables and prints each one. The manifest (`warehouse/metadata/redivis_uploads.csv`) keeps their lines, marked `migrated_to`, so the history gate keeps their counts.

## Supabase: compacting the database

`warehouse/supabase/load.py` runs a plain `VACUUM (ANALYZE)` on the shape tables after every load and prints their size before and after (session 29; from session 29 to session 44 the code in fact ran `VACUUM (FULL, ANALYZE)`, and in daily run 12 it held the tables for about ten minutes, so session 45 made the plain vacuum the default). A plain vacuum takes no exclusive lock: the space of the rows a load replaced is marked for reuse by the next loads, but `pg_database_size` does not shrink. Only `VACUUM FULL` returns space to the operating system, and it locks each table while it rewrites it (seconds to minutes; the site's reads wait or time out meanwhile), so it stays a person's command, run when the site is quiet:

```bash
python warehouse/supabase/load.py --vacuum-full
```

The loader still warns above `warn_mb` (350 MB) and fails above `max_mb` in `warehouse/supabase/live_set.yaml`. When the warning shows and does not clear, run the command above once, or trim a live window.

**The weekly vacuum (session 49, approved by Samuel).** `.github/workflows/weekly-vacuum.yml` runs `warehouse/supabase/vacuum.py` every Sunday at 10:00 UTC:

- **What it does:** `VACUUM (FULL, ANALYZE)` of the six shape tables, with no load.
- **What it records:** `pg_database_size` before and after, and each table's size, in `warehouse/metadata/run_status.csv` (connector `supabase_vacuum`; the table `supabase` holds the database's two sizes). The workflow commits that file.
- **When:** in the daily run's concurrency group, so it never runs during a daily load, and four hours before the daily run's 14:00 UTC start. The site's reads may wait or time out while `series` is rewritten, a few minutes on a Sunday morning.
- **Run it now:** Actions, "weekly vacuum", Run workflow; or locally, with `SUPABASE_DB_URL` in `.env`: `python warehouse/supabase/vacuum.py` (no load, unlike `load.py --vacuum-full`).
- **Stop it:** delete the `schedule` lines of the workflow.

## The hourly network refresh (session 54)

**Approved by Samuel.** `.github/workflows/hourly-network.yml` runs `warehouse/derived/network_hourly.py --skip-if-busy` on the hour, every hour except 14:00 UTC.

- **What it does:** pulls the last 48 hours of EIA-930 interchange (every BA pair) and demand (the seven ISO BAs), merges them onto the previous network snapshot, and uploads one JSON object to the public Supabase Storage bucket `erw-public` (`network/grid_network.json`). `/network` reads it with a one-hour revalidation.
- **Leaner runs (session 55):** when EIA's interchange `endPeriod` has not moved since the object was built, a run pulls demand only and carries the links over; the object says `"interchange": "unchanged"`, and the job log says "interchange unchanged".
- **What refreshes hourly and what daily:** the links and the ISO demand hourly. Carbon intensity, the nodes and their positions daily, from the committed `site/data/grid_network.json` that the daily run builds (`warehouse/derived/grid_network.py`); that file is also the page's fallback. Details, and why EIA's lag keeps the links more than a day behind the clock while demand is one to two hours behind it: `docs/methods/grid_network.md`.
- **What it never does:**
  - write to the Supabase database, or commit to git;
  - run while the daily or weekly job is queued or running. It has its own concurrency group, so it can never displace their pending runs. The script asks the GitHub API before the pull and again before the upload, and exits 0 without uploading if either is busy.
- **Its record:** the job log only (Actions, "hourly network"). A failed run leaves the object in Storage as it was, and the page keeps showing it, or the committed file when the object is older than that file.
- **Secrets:** `EIA_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (Storage only), and the job's own `GITHUB_TOKEN` (read access to Actions).
- **How often it really runs:** GitHub runs scheduled workflows on a best-effort basis. On 2026-10-01 the 15-minute "latest prices" cron ran five times in 24 hours, so expect hours between refreshes rather than one (archive/sessions/SESSION_54_REPORT.md, open question 1).
- **Run it now:** Actions, "hourly network", Run workflow. Locally, from `.env`, without uploading: `python warehouse/derived/network_hourly.py --dry-run --out network.json`.
- **Stop it:** delete the `schedule` lines of the workflow. The page then falls back to the committed file as soon as that file is newer than the last object.

## An outside trigger for the scheduled jobs (session 58)

**Why.** GitHub runs scheduled workflows on a best-effort basis, and for this repository it runs them rarely.
- On 2026-10-01, "latest prices" (every 15 minutes, 96 runs a day) ran five times in 24 hours.
- The hourly network ran once in the five hours after it was added.
- The daily job's 14:00 UTC run came at 18:00 to 20:00, or not at all.

A free outside scheduler that calls GitHub's `workflow_dispatch` on time fixes this. Samuel sets it up himself: it needs a token, and **no token is ever stored in this repository**.

**Two triggers on one day are safe** for the daily job and the Roundup, the two that send email. A run that is scheduled, or dispatched with `once` set to `1`, stops in its first job (`gate`) when a run of the workflow already succeeded that UTC day. A manual run from the Actions tab (`once` left at `0`) always runs. The other jobs only refresh data, so an extra run costs a minute.

### 1. A fine-grained GitHub token, this repository only

1. GitHub, your picture, **Settings**, **Developer settings**, **Personal access tokens**, **Fine-grained tokens**, **Generate new token**.
2. **Name:** `erw-scheduler`. **Expiration:** 90 days, and put the renewal date in your calendar. **Resource owner:** SamuelEnrique.
3. **Repository access:** "Only select repositories", then `SamuelEnrique/erw`.
4. **Permissions,** Repository permissions: **Actions: Read and write**. Metadata: Read is added by itself. Nothing else.
5. **Generate token** and copy it once (it starts `github_pat_`). Paste it only into the scheduler below; never into a file in this repository, a commit, an issue or a chat.

### 2. The scheduler: cron-job.org (free)

1. Make an account at https://cron-job.org and confirm the email.
2. For each row of the table below: **Create cronjob**.
   - **Title:** the row's name.
   - **URL:** `https://api.github.com/repos/SamuelEnrique/erw/actions/workflows/<file>/dispatches`
   - **Schedule:** "Custom". Set the time zone to **UTC** in your account settings first.
   - **Advanced:**
     - **Request method:** `POST`.
     - **Headers:**
       - `Accept: application/vnd.github+json`
       - `Authorization: Bearer <the token>`
       - `X-GitHub-Api-Version: 2022-11-28`
       - `Content-Type: application/json`
     - **Request body:** the row's body.
   - **Save**, then **Test run** once. GitHub answers **HTTP 204** with an empty body when it accepted the dispatch, and the run appears in the repository's Actions tab within a minute. A 401 means the token is wrong or expired; a 403 or 404 means the token lacks Actions write on this repository; a 422 means the body is wrong.

| Name | `<file>` | When (UTC) | Body |
|---|---|---|---|
| ERW daily | `daily-prices.yml` | every day 14:00 | `{"ref":"main","inputs":{"queues":"0","once":"1"}}` (Mondays pull the ISO queues by themselves) |
| ERW latest prices | `latest-prices.yml` | every 15 minutes | `{"ref":"main"}` |
| ERW hourly network | `hourly-network.yml` | every hour at :05, except 14:05 | `{"ref":"main"}` |
| ERW Roundup | `roundup.yml` | Sundays 23:00 | `{"ref":"main","inputs":{"once":"1"}}` |
| ERW weekly vacuum | `weekly-vacuum.yml` | Sundays 10:00 | `{"ref":"main"}` |

3. **cron-job.org's history** shows each call's HTTP status. The Actions tab shows each run.
4. **Keep the GitHub schedules** in the workflow files as a fallback. The gate stops a late duplicate of the daily job or the Roundup.

### 3. The alternative: Supabase `pg_cron` with `pg_net`

The same calls can come from the project's own database. In Supabase:
1. **Database, Extensions:** enable `pg_cron` and `pg_net`.
2. **Vault:** store the token as a secret named `github_dispatch`. It stays in the database's vault, never in this repository.
3. **SQL editor:** for the daily job, run:

```sql
select cron.schedule('erw-daily', '0 14 * * *', $$
  select net.http_post(
    url := 'https://api.github.com/repos/SamuelEnrique/erw/actions/workflows/daily-prices.yml/dispatches',
    headers := jsonb_build_object('Accept', 'application/vnd.github+json', 'X-GitHub-Api-Version', '2022-11-28',
      'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'github_dispatch'),
      'User-Agent', 'erw-scheduler'),
    body := '{"ref":"main","inputs":{"queues":"0","once":"1"}}'::jsonb);
$$);
```

Repeat with the other rows' files, times and bodies. `select * from net._http_response order by id desc limit 5;` shows GitHub's answers; 204 is accepted. cron-job.org is simpler and keeps the database's resources for the site, so it is the first choice.

### 4. When the token expires

Generate a new one as in step 1. Replace it in each cron job (or the vault secret), then test one run. Delete the old token on GitHub.
