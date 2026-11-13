# Session 5154 report: row 23, the usage count's daily code and "no identifier"

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. No pull. Nothing built, nothing landed, no warehouse data written, no migration written or applied.

Clock: precheck 19:01 UTC, the tests by 19:05 UTC. Inside the long end of 1:00.

## Read these first

- **Today, for the day in progress, the database holds a code that stands for one browser.** It is a keyed hash, hashed again under a random salt of the day; the code and the salt are deleted when the day is over. That is what `docs/methods/usage_counts.md` has said since session 177. It is still an identifier, for a day.
- **The roadmap says "no cookie and no identifier".** Whether a one-day code breaks those words is yours to read. Ruling 1.
- **The other choice is built and is one setting away: `USAGE_VISITORS=off`** in the host's environment. Then no value stands for a visitor; the address and the user agent are not read for the count; events are counted as before.
  - What you lose with it: "distinct visitors". The `visitors` numbers then count pages (1 for a page's line).
- **Nothing changes until the variable is set.** The default is the daily code, as since session 177.
- "No cookie" holds either way and now has a standing test.

## What to review

1. `site/lib/guard.ts`, the last 16 lines: `usageVisitorsOff` and `usageNobody`.
2. `site/app/api/usage/route.ts`: one line chooses the value sent.
3. `docs/methods/usage_counts.md`, "Counting with no code at all".
4. `docs/security.md`, the section on the usage counts and "no identifier".

## What was done

- **The read**: the route, `site/components/Usage.tsx`, `site/lib/usage.ts`, the database's function `site_usage_record` and its tables (migration 028), the method note.
- **The switch** (`site/lib/guard.ts`): `USAGE_VISITORS=off`, read on the server.
- **What is sent in the visitor's place** (`usageNobody`): a keyed hash of the page's path alone, in the form the database's function asks for. One value a page, because the database drops lines beyond 400 a "visitor" a day: one constant for the whole site would have met that ceiling on a busy day and lost lines unseen.
- **No migration.** The database's function is used as it is.
- **The tests**: one more in `site/scripts/test-usage.mjs` (15 tests now); `tests/test_session5154.py`, 8 tests (the switch, the route's line, no cookie, nothing kept in the browser, counts only of an earlier day).
- **The records**: the method note's new section, row 23 of the list, a section in `docs/security.md`.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5154 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `node --import ./scripts/alias-register.mjs scripts/test-usage.mjs` | 0 | 15 tests passed |
| `pytest` on `test_session5154`, `5153`, `5152`, `5151`, `5102`, `177`, `371`, `203` | 0 | 103 passed |

- **Not run:** the build; the route against a database (`USAGE_VISITORS=off` was never set anywhere).
- **Not verified:** how `/internal/usage` reads with the switch on. Its numbers would be right as counts of events; its "visitors" columns would count pages, and the page's words do not say so.

## Decisions made without you

- **Built the second choice rather than only describing it**, default unchanged, so the ruling is a setting and not a session.
- **The limit of 600 an hour from one address stays under both choices.** It keeps its own keyed hash of the address for the limit's window, in `site_rate_counts`, as every limit of the site does. Without it the count's door has no limit across the host's instances.
- **`/internal/usage` and `/privacy` not touched**: the words of pages.

## For Samuel's ruling

1. Row 23. Default: (a) the daily code as today. (b) set `USAGE_VISITORS=off` on Vercel (Settings, Environment Variables, Production; then a redeploy): no code at all, and no count of distinct visitors.
2. If (b): the words of `/internal/usage` ("visitors") and of `/privacy` then want a sentence each. Default: a session writes them once (b) is chosen.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 5 of the list session 5150 rebuilt.
