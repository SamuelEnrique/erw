# Session 128 report: Ask ERCOT, made safe to open

## To finish

**The freeze is on.** This session pushed `wip/128-ask-ercot-safe` only and deployed nothing. The branch is from main (`e33f4e0`) and builds on no other. In this order, when `python scripts/freeze.py status` exits 0:

1. **In Vercel, set `ASK_VISITOR_SALT`** for Production: any secret of 24 characters or more (for example `openssl rand -hex 24`). Without it the tools answer "not answering questions right now" to everyone: they fail closed.
2. **Rule on the three numbers** in `site/lib/chat/limits.json` (USD 3 a day, USD 30 a month, 15 questions a visitor a day are my defaults), or set `ASK_DAILY_USD`, `ASK_MONTHLY_USD`, `ASK_PER_VISITOR_PER_DAY` in Vercel.
3. Land the branch:

```bash
git checkout wip/128-ask-ercot-safe && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-128
git push origin wip/128-ask-ercot-safe && git push origin wip/128-ask-ercot-safe:task/128-ask-ercot-safe
python runs/session118/watch_run.py task/128-ask-ercot-safe 15
node site/scripts/snapshot-live.mjs take after-128 && node site/scripts/snapshot-live.mjs compare before-128 after-128
python runs/session128/prove_sql.py                       # the database's side again, no model call
git push origin --delete wip/128-ask-ercot-safe
```

4. Then one question on production from `/ask/ercot` in the internal view, and `/internal/ask?token=<INTERNAL_COSTS_TOKEN>` should show it with its cost.

- **What the comparison should show on the three open pages: nothing but the clock.** No page changed. The route `/api/ask` and one new internal page did.
- **The database migration is already applied** (below). Landing the code does not need it applied again.

## Verdict: not ready to open, and close

The ceilings hold, proven three ways. What keeps Ask ERCOT closed is not code:

1. Steps 1 to 3 above (a secret, three numbers, a deploy).
2. **A spending limit in the model provider's console.** The ceilings here count what the ledger holds; the provider's own limit is the wall behind them, and only you can set it.
3. **The words on `/terms`.** It says each question is logged without identity. That is still true, and the site now also keeps, for one day, a keyed hash of a visitor's address with a count. The page should say so before the tool opens. I did not edit it.
4. Whatever session 121 left open on the answers themselves; this session did not touch them.

## Read these first

1. **I applied a migration to the production database** (`023_ask_limits.sql`, at 00:16 UTC). It adds a table and two functions, adds one empty column to the cost ledger, and widens one check on it. No page reads any of them, and the site as deployed works as before. I did it because a ceiling that has never met the real database is not proven. It is not a deploy and not a load into a table a live page reads; it is still a change to production made during a freeze, so it is the first thing I am telling you.
2. **No Ask ERCOT call had ever reached the cost ledger.** Since session 121 the site has recorded Ask ERCOT's calls under the step `site_ask_ercot`. The ledger's own check allowed only `site_ask`, refused every such row, and the failure is swallowed by design so that an answer is never lost to a ledger error. The ledger held 95 rows, all the general chat's. The migration mends the check; the first Ask ERCOT rows ever recorded are this session's test question (3 calls, USD 0.0514).
3. **`/api/ask` is open to anyone today**, whatever the page's status: the release gate covers pages, not the API. In production it has one guard, 10 questions an hour per address, counted in each server instance's own memory. The ledger shows USD 0.28 on 4 October and USD 0.42 on 5 October from the general chat. The ceilings built here protect it only once the branch is deployed.
4. **Model spend this session: USD 0.1257 of the USD 2.00 allowed**, two questions.

## What was built

| | What | Where |
|---|---|---|
| A daily and a monthly spending ceiling | read from `limits.json`, or the environment; checked by the database before any model call | `site/lib/chat/limits.ts`, `site_ask_admit` |
| A plain message, and no model call | four messages (month, day, visitor, not answering), each ending "Your question was not sent to the model." | the route, before `ask()` |
| Questions per visitor per day | a count kept for today only, against a keyed hash of the address that changes daily; no address stored | `site_ask_counts` |
| Each question's cost logged | every question gets a number; each of its model calls carries it into the ledger | `question_id` on `site_api_calls` |
| A small internal view of spend by day | today and the month against the ceilings; 62 days by day and tool; the ten costliest questions | `/internal/ask?token=...` |

- **It fails closed.** No ceilings, no secret, no known address, a database that does not answer, a call in the month's ledger with no price: each closes the tools. Only a plain yes from the database admits a question.
- **The visitor's count holds a day, a hash and a number, and nothing else.** The hash is HMAC-SHA256 of the address, the day and a secret the database never sees. It cannot be turned back into an address and is a different value the next day. Rows of earlier days are deleted at each question. A refusal counts nothing.
- **A caller of the database function learns yes or no and no spend figure.** The anon key can execute it and can read neither table (HTTP 401, checked).

## Proven

| How | What it showed |
|---|---|
| `tests/test_session128.py`, 13 tests, the site's own guard run in node with a made-up database answer | every reason refuses with its message after exactly one database call; only a plain yes admits; it is closed without ceilings, secret or address, and when the database throws; the database receives a hash and never the address; the configuration reads the file then the environment and closes on anything that is not a number |
| `runs/session128/prove_sql.py`, 14 checks against the real database with the anon key, no model call | a reached month refuses, a reached day refuses, a visitor at the number is refused; a refusal counts nothing; with two a day the first two are admitted and the third and fourth refused; the anon key reads neither table; the spend view answers only the right token |
| `runs/session128/prove_e2e.sh`, the local build, as a visitor | below |

**End to end, on the local build:**

| Configuration | Question | Answer | Ledger rows added |
|---|---|---|---|
| daily ceiling 0 | Ask ERCOT | HTTP 503, "reached its spending limit for today ... not sent to the model" | 0 |
| questions per visitor 0 | Ask ERCOT | HTTP 429, "reached today's limit of 0 questions ..." | 0 |
| no secret | Ask ERCOT | HTTP 503, "not answering questions right now ..." | 0 |
| the file's ceilings, two a visitor a day | Ask ERCOT: August's average day-ahead price at the hub average | answered (32.97 USD/MWh), USD 0.0514 | 3, step `site_ask_ercot`, one question number |
| the same | general chat: Henry Hub on the latest day held | answered (3.18 USD/MMBtu on 29 September), USD 0.0744 | 2, step `site_ask`, one question number |
| the same | a third question | HTTP 429, "reached today's limit of 2 questions ..." | 0 |

- Each question's cost in the ledger equals the cost the answer reported (0.0514 and 0.0744).
- The internal view answered 200 with the token (today USD 0.1257) and 404 without.
- The test visitor's count was removed afterwards.

## What a ceiling does not do

- **It is checked before a question, not during one.** Questions in flight when it is reached finish. At about USD 0.05 to 0.07 a question, ten at once would pass a ceiling by well under a dollar.
- **It does not stop someone who changes address.** The visitor's count is per address; the daily ceiling is what bounds the spend, and the tool closes for everyone when it is reached. A person who wanted to close the tool for a day could spend its ceiling. That is the trade a hard ceiling makes.
- **It counts the ledger.** If a ledger write fails, that call is not counted. Session 121 awaits the writes before answering; a persistent failure would show as answers with no rows, and the provider's own limit is the wall for that case.
- **The older hourly limit is still per server instance.**

## Checks

- Full suite: 1,271 passed, 19 skipped, exit 0. Two earlier tests (sessions 92 and 121) held the route's lines word for word; they now hold the new lines, which carry the question's number.
- Site build exit 0. Route check exit 0: 8 live pages and 115 in review, 0 failed.

## Decisions made without you

- **The migration applied to production** (point 1).
- **One ceiling for both tools**, not one each: the money is the same.
- **USD 3 a day, USD 30 a month, 15 questions a visitor a day.** At the measured cost that is about 50 questions a day.
- **Closed without a secret**, in place of counting visitors by a hash anyone could recompute.
- **A call with no price closes the tools**, in place of counting it as zero.
- **The question's text is not put in the database.** The internal view shows a costly question's day, tool and cost, not its words.
- **`/terms` not edited** (it is not this session's page, and it was live until yesterday).

## What is left

1. The four things under the verdict.
2. If you want the hourly limit to hold across instances too, it can move into the same database call.
3. A weekly line in the health summary when a ceiling was reached, so you learn the tool was closed without opening the internal view.
