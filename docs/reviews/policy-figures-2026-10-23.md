# The policy monitor's figures: each one, its key and its hover (23 October 2026)

Energy Research Warehouse (ERW), session 2400 (chain 088, `queue/done/088-day-23-october-portable-policy-games.md`), written on portable-laptop on 23 October 2026 at about 20:40 UTC. Both views of `/policy` read for every figure a visitor sees, in the page's files (`site/app/policy/page.tsx`, `PolicyTable.tsx`, `WeekView.tsx`, `site/lib/policyweek.ts`, `policyweekdata.ts`). For each: where it stands, whether it is a value of the live set that `check-values` can read again (then it carries a `Num` with its key), or a count this page makes of the rows it was given (then it carries a hover that says so and no key, since the checker reads the server's page and the count changes with every click), and its hover before and after this session. No figure's value changed; one line of the week view's foot changed its form (below).

## The first view, `/policy` (every action, scored)

| Figure | Where | Key | Hover before | Hover after |
|---|---|---|---|---|
| The significance score of each action | the table's last column | `event\|policy_actions\|<id>\|significance` (session 332), kept | none (the column head says what it is) | unchanged; the Method note's section 3 says how it is scored |
| "N of M actions": M, the total | beside the filters | **new** `event_count\|policy_actions\|all`: the checker counts the live table's rows | none | "Every action of the live table policy_actions, as this page read it (the count is checked against the table)." |
| "N of M actions": N, the filtered count | beside the filters | none: counted on the page from the rows the server gave it, changes with every filter | none | "The actions the filters above leave, counted on this page." |
| "Any tag (N)" | the Tag filter's option | none: an option's text carries no hover in a `select`; the count is the rule's, on the page | none | unchanged; the chips on each row carry the rule's matched term and field |
| "since 2025-10-01" | the lead | a date in the words, not a figure | the three hovers of the lead (session 164) | unchanged |
| "No action scored 5 or more since <day>" | "This week in policy" when empty | a date in the words | none | unchanged |
| "The first 400 are shown" | under the table | a constant of the page | none | unchanged |
| "Figures: ..." under a read | the opened row | none by design (section 11 of the Method note: the figures are the read's own words, computed by nothing) | none | unchanged |

The cards of "This week in policy" show no figure: the agency, the type and the date are words.

## The second view, `/policy?view=week` (what changed this week)

| Figure | Where | Key | Hover before | Hover after |
|---|---|---|---|---|
| "N actions" | beside the window chips | none: counted on the page, changes with every click | the window's days, both ends | the same, then "Counted on this page from the rows read: the actions the window and the filters leave." |
| "of M" | beside it, when an agency or a topic is chosen | none: counted on the page | none | "The M actions of the window, the grid and the large-load choice, before the agency and the topic are chosen. Counted on this page from the rows read." |
| The chart's cell counts, "No topic" and "All" | the table of counts | none: counted on the page | each cell's `data-tip` (the agency, the count, the topic, the window; session 157) | unchanged |
| The count beside each agency's heading | the groups | none: counted on the page | none | "N actions of <agency> in the last D days that the filters leave; counted on this page from the rows read." |
| "N held for thirty days" | the foot | **new** `event_count\|policy_actions\|since\|<first day>` on the actions read: the checker counts the live table's rows dated the window's first day or later | "Read for this page: A actions of the live table policy_actions and D proceedings and orders of the site's file of dockets, all dated in the thirty days to <today>." | "Read for this page: R actions of the live table policy_actions dated <first day> or later (the count is checked against the table), of which A are shown and R minus A are not, and D proceedings and orders of the site's file of dockets, all dated in the thirty days to <today>." |
| "dockets held <day>" | the foot | none: a date of the site's file (`state_rules.json`, `built_at_utc`) | the file's build day and its row count | unchanged |
| "tag rule version V" | the foot | none: the rule file's version | what a tag is | unchanged |
| "K held, not shown" | the foot | none: counted on the page (the municipal rule and the rows without a sentence) | each dropped row's reason | unchanged |

**The one line whose form changed.** The foot said "N held for thirty days" where N was the shown actions plus the dockets, one sum of a table's rows after the page's own drop and a file's rows. It says now "R actions and D dockets held for thirty days": R is every action read from `policy_actions` for the window, before the drop, and carries the key, so that the checker can count the same rows; the dropped count stands beside it as before, so the shown count is R minus the dropped actions. The sum N is not shown any more: a sum of a table's count and a file's count has no key the checker can recompute, and the two parts say more than the sum did. This is a change of the foot's words, not of any figure of the data.

## What the checker reads

- `site/scripts/check-values.mjs` holds a new kind, `event_count|<table>|all` and `event_count|<table>|since|<YYYY-MM-DD>`: the count of an events table's rows, every row or those dated the day or later, read with `Prefer: count=exact` as the other counts are. The page's `since` is the window's first day as the page computed it, so a page cached before midnight carries its own day in the key and the checker counts the same rows.
- `/policy?view=week` is in the checker's page list since this session (`/policy` since session 332). It carries one key; the page has no floor in `check-values-floor.json`, so no floor is judged until a passing full run writes one.
- A count can differ between the page and the checker by the rows the daily run loaded between the page's hourly cache and the check; the same holds for every count key of the site (the datacenter and project counts) and the gate's run reads the page fresh from its own build.

## Not keyed, and why

- The page's own counts (the filtered count, the week view's counts, the chart's cells, the group counts): the checker reads the HTML the server wrote; these change in the browser with every filter and have no row of their own in the live set. Each carries a hover that says it is counted on this page from the rows read.
- The read's "Figures" line: the read's own words (section 11 of the Method note).
- The dockets' count and build day: the site's file, not the live set.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-policy-week.mjs` in the worktree: 83 passed, exit 0 (two new assertions: the key's form, the foot's hover).
- `node scripts/check-values.mjs --list`: exit 0, the week view listed.
- `npx tsc --noEmit`: 15 errors in the worktree against 2 in the main checkout, every one a generated file the build writes (`PageProps`, `content/*.json`), none in the policy files.
