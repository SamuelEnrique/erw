# SESSION 33: Four small fixes, 45 minutes

## Read first
CLAUDE.md, archive/sessions/SESSION_32_REPORT.md (question 5 and the skipped tests),
archive/sessions/SESSION_30_REPORT.md (questions 6 and 7, the chat eval q27), the
package tests, warehouse/supabase/load.py, warehouse/archive/restore.py.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls, no re-pulls, no backfills, no schema changes, no deletions from Redivis,
  no force push. Target 45 minutes: do the four items in order; if the fourth does not
  fit, leave it and say so.
- Today's daily job is running on GitHub and will commit: git pull and merge before
  pushing.

## The four items
1. Package tests on large tables. Any per-table test that loads a table over 200,000
   rows whole now tests by partition (the `ba`, `market` or `year` column, as session
   29 did for the ERCOT history), so `eia930_all_emissions` and the ERCOT history never
   load whole in a test. Give the workflow's test step a 20-minute timeout so a slow
   test fails visibly instead of hanging the run. Run the package suite once to the
   end and report the count and the time.
2. The 47 news stories left out by session 29's merge: restore from the archive run
   20260929T012526Z and add the missing keys to the working news_stories. They stay
   unscored; the daily run scores them. Report the count added.
3. The Supabase loader's reachability probe: replace the exact count with a cheap
   check, three retries with backoff before failing.
4. The chat eval's q27: the count on a growing table becomes a tolerance or a
   date-fixed count. No eval run.

## Report: archive/sessions/SESSION_33_REPORT.md
Each item done or not, test count and time, rows added, spend USD 0 confirmed, wall
time, whether the daily job landed and merged. Commit after every item. Push at the
end. Stop.