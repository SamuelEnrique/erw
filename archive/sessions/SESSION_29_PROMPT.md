# SESSION 29: Table consolidation (Ben item 5) and carried rulings

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, docs/feedback/ben-2026-09-28.md (item 5),
archive/sessions/SESSION_28_REPORT.md, warehouse/redivis/upload.py, the archive writer and
restore code from session 28, the erw package, and the site's data queries.

## Budget and stops
- Expected Anthropic API spend: $0.00. Hard cap: $0.00. This session makes no model calls.
  If any script, test or job would call the Anthropic API (digest scoring, extraction, chat
  eval, Thesis Builder), skip it, mark it skipped, and say so in the report.
- No backfills, no source re-runs, no re-pulls. Every table you build comes from data
  already in the archive. If a step needs new data, stop that step and report.
- Time: aim for 60 to 120 minutes. At 150 minutes stop cleanly: commit, push, write the
  report with what shipped and what did not.
- Memory: process one table family at a time, stream with pyarrow, never hold more than
  one family in memory. This laptop has stopped sessions on memory before.

## Health check (first, no changes)
Read the last daily run status. List failures. CARB and NYISO HTTP 202 are now known gaps
(ruling). Anything else failing goes in the report under "run health" with cause if obvious.
This session is structural, not a new source or tool, so the PRIORITIES.md health gate does
not block it; say in the report whether the gate would block a source session tomorrow.

## Part A: carried rulings (small, first, one commit each)
1. Known gaps: add CARB and NYISO 202 to the known-gap list with the exact local command
   that refreshes each, documented in the runbook so Samuel can run it himself.
2. Supabase loader vacuums after every load, and prints size before and after.
3. The daily workflow regenerates sources.csv after its pull, never before.
4. Update the erw package tests to the current schema and add them to the workflow as a
   required step. If a test needs the Anthropic API, mark it skipped in CI.

## Part B: consolidation plan (write it before touching data)
Inventory all 113 tables from the coverage table. Write docs/migrations/2026-09-29-
consolidation.md with an explicit map: old table -> new table + partition column + value.

Rules:
- Consolidate a family only when its members share the same columns and differ by a value
  encoded in the table name (region, BA, ISO, market, year, hub). That value becomes a
  column; if the column already exists with that value in every row, just drop the suffix.
- Required families: ERCOT history (24 tables -> one), EIA-930 (one table per family:
  demand, generation, interchange, or whatever the families actually are, with a ba
  column), trader view (one table). Apply the same rule to any other family of 3 or more.
- Never merge tables with different licenses or different tiers. Flag those in the report.
- Do not touch entities, events, digest or news tables unless they meet the rule exactly.
- Naming follows docs/datastandard.md. Add a rule there: partition keys are columns,
  never name suffixes.
- Sanity target: roughly half the table count or fewer. Report the real number, do not
  force it.

## Part C: build and verify locally
For each family, in order, small families first, ERCOT history last:
- Build the consolidated table from the archive partitions, not from Supabase or the
  Redivis draft.
- Reconcile: row count of new == sum of old, per family and per partition value; column
  set identical; source, retrieved_at, vintage, license, tier carried on every row;
  validator passes. Any mismatch: keep the family unconsolidated, write why, move on.
- Commit per family with counts in the message.

Archive: existing partitions are never rewritten or renamed (append-only stands). From the
next daily run, appends go under the new names. The restore path reads the migration map
so old-named partitions resolve into the new tables. Test: restore of every consolidated
table from the archive equals the local consolidated table row for row. This test is a
hard requirement; without it the session is not done.

## Part D: Redivis draft (layout datapages will copy)
- Upload every consolidated table to the correct dataset by license (public vs internal).
- Do NOT delete the old tables from either dataset. Do not lower or bypass the history-
  loss gate. Update the rolling-table manifest: new entries with count = sum of old, old
  entries marked migrated (kept, not removed, so the gate's history survives).
- Write one guarded deletion command (a flag on upload.py) for Samuel to run tomorrow:
  it verifies per family that the new table's Redivis row count equals the sum of the old
  tables' counts, refuses to remove anything on any mismatch, and prints what it removed.
  Put the exact command at the top of the report.

## Part E: Supabase live set
Load the consolidated tables that belong in the live set, drop the old ones in the same
run, vacuum, report size before and after. Must stay well under 500 MB.

## Part F: package, chat catalogue, site
- erw package: fetch, filter, cite, coverage work on the new names with partition
  filtering. Old names keep working via the migration map with a DeprecationWarning
  through the first monthly release. Tests pass. Regenerate llms.txt and the chat's
  table catalogue.
- Site: update every query that read an old table. Then run a route check that hits
  every live page and fails on non-200, on "undefined", or on an empty table where the
  page showed data before this session. Fix what breaks. No placeholder data anywhere.
- Regenerate the coverage table, update README table count, add a CHANGELOG entry.

## Do not
No new sources, no new tool pages, no digest or rubric changes, no model calls, no
backfills, no rewriting of existing archive partitions, no deletions from Redivis, no
gate changes, no schema changes beyond adding the partition column.

## Report: archive/sessions/SESSION_29_REPORT.md
1. The one deletion command for Samuel, and what it will remove.
2. Table count before and after; the migration map summary; families left
   unconsolidated and why.
3. Reconciliation table: per family, old sum vs new count, restore test result.
4. Redivis: what was uploaded to which dataset; manifest changes.
5. Supabase size before and after.
6. Site route check results; anything fixed.
7. Part A rulings: done or not, with the local refresh commands.
8. Run health and whether the gate blocks tomorrow.
9. API spend: $0.00 confirmed. Wall time. Open questions for Samuel, and anything you
   skipped.
Commit after every working step. Push at the end.

## Chain (optional)
If SESSION_30_PROMPT.md exists in the repo root when you finish and the report is written
and pushed, read it and execute it; when that report is written, do the same for
SESSION_31_PROMPT.md if it exists. If either file is absent, stop.