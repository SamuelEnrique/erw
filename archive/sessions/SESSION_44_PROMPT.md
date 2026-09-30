# SESSION 44: Gate check, then problem sets v0

## Part 0 (first, 2 minutes)
Read daily-prices run 12 (workflow_dispatch, commit 9fb7d93).
- Passed: read SESSION_42_PROMPT.md and execute it end to end (its rules, its
  approved pull, its report). Then stop; do not do Part B.
- Failed: read its log through the GitHub API, fix the failing step on main if the fix
  takes under 15 minutes, trigger one workflow_dispatch run (approved), and do not
  wait for it. Then Part B.
- Still running: say so in the report and do Part B.

## Part B: problem sets v0 (education)
Read first: /grid/<iso>, /learn/bill, /events/*, /cost-of-power, /storage,
/emissions, their lib files and tables.

Rules: USD 0, no model calls, no data pulls, no Supabase table. Pull and merge if the
daily job lands, never force push.

1. Three sets at /learn/problems/<slug>, listed on the Learn menu:
   a. "Know your grid" (ERCOT and CAISO side by side): peak demand, generation mix,
      battery cycle, carbon intensity.
   b. "Prices and your bill": load-weighted versus simple price, the shape premium,
      the wholesale share of the default PG&E and Oncor bills, the cheapest and
      dearest hour.
   c. "When the grid broke": Uri, CAISO 2020, Elliott, ERCOT 2023, one question each
      plus one comparing two events.
2. Five questions per set, undergraduate level. Each has: the question; the tables a
   student would use (linked to /data); the answer computed server-side from those
   tables at build, never typed in; a worked solution showing the steps with the
   actual numbers; one sentence on why it matters. A "show answer" toggle so a
   teacher can assign it. Questions must stay answerable as data updates (use "the
   latest complete month" style wording and let the numbers move).
3. A one-paragraph note for teachers on each set: time needed, prerequisites, the
   pages students should open.
4. check-values covers every computed answer; check-routes covers the pages; tests/;
   deploy; live check.

## Do not
No pulls beyond an approved Part 0 path, no model calls, no Supabase table, no typed
numbers in answers, no force push.

## Report: archive/sessions/SESSION_44_REPORT.md
Part 0 outcome; if Part B ran, every question with its computed answer and source
table; wall time; spend confirmed; open questions. Commit. Push. Stop.