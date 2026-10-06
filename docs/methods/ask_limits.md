# The ceilings of the question-answering tools

`site/lib/chat/limits.ts`, `site/lib/chat/limits.json`, migration `023_ask_limits.sql`, the route `site/app/api/ask/route.ts`
and the internal view `/internal/ask`. Session 128. They cover both tools that call a model for a visitor: the
general chat (`/ask`) and Ask ERCOT (`/ask/ercot`). Both pages are in review; the route they call is not behind the
release gate, so the ceilings stand on the route.

## What happens to a question

1. The route checks the question's shape, and the older limit of 10 questions an hour per address (kept in one
   server instance's memory, so a floor and not a guarantee).
2. **The route asks the database whether the question may go to a model** (`site_ask_admit`). One call. It says yes,
   or one of the reasons below.
3. On yes the question is given a number (32 hexadecimal characters drawn at random, made from nothing about the
   visitor) and goes to the model. Every model call it makes is one row of `site_api_calls` carrying that number, so a
   question's cost is the sum of its rows.
4. On no, the answer is a plain message and **no model is called**.

| Reason | When | What the visitor reads | HTTP |
|---|---|---|---|
| `month` | the tools' spend this UTC month has reached the monthly ceiling | "This tool has reached its spending limit for the month, so it is not answering questions until next month. Your question was not sent to the model." | 503 |
| `day` | the tools' spend this UTC day has reached the daily ceiling | "This tool has reached its spending limit for today, so it is not answering questions until tomorrow (UTC). Your question was not sent to the model." | 503 |
| `visitor` | this visitor has asked the day's number of questions | "You have reached today's limit of N questions. It starts again at midnight UTC. Your question was not sent to the model." | 429 |
| `closed` | the tool cannot count: no ceilings, no secret for the visitor's hash, no known address, the database did not answer, or a call in this month's ledger has no price | "This tool is not answering questions right now. Your question was not sent to the model." | 503 |

**It fails closed.** Anything that is not a plain yes from the database is a no.

## The configuration

`site/lib/chat/limits.json`, each value overridden by the server's environment where set:

| Value | File | Environment |
|---|---|---|
| Daily ceiling, USD | `daily_usd`: 3 | `ASK_DAILY_USD` |
| Monthly ceiling, USD | `monthly_usd`: 30 | `ASK_MONTHLY_USD` |
| Questions per visitor per day | `per_visitor_per_day`: 15 | `ASK_PER_VISITOR_PER_DAY` |
| The secret of the visitor's hash | none: environment only | `ASK_VISITOR_SALT`, at least 24 characters |

The three numbers are the session's defaults, for a person to rule on. A value that is missing or is not a number
closes the tools. A ceiling of 0 is a ceiling: it admits nothing. Without `ASK_VISITOR_SALT` the tools are closed.

## The visitor, and what is stored

No address is stored anywhere. The server makes a keyed hash (HMAC-SHA256, 32 hexadecimal characters) of the
visitor's address, the UTC day and the secret. The database keeps, **for today only**, that hash and a count
(`site_ask_counts`: a day, a hash, a number). Every question deletes the rows of earlier days.

- The hash cannot be turned back into an address without the secret, which the database never sees.
- It is another value the next day, so a visitor is not followed from one day to the next.
- A refusal counts nothing against a visitor.
- A visitor is an address. People behind one address share a count, and a visitor who changes address is counted
  anew: the daily ceiling, not this count, is what bounds the spend.

A question's text is not stored in the database. As before, the server's log holds a line per question (the time, the
question, the outcome, since session 121 its cost, and now its number), with no address.

## What a ceiling is not

- **It is checked before a question, not during one.** Questions being answered when a ceiling is reached finish, so
  a day can end above its ceiling by the cost of the questions in flight. Measured on 6 October 2026: one Ask ERCOT
  question cost USD 0.05 and one general question USD 0.07.
- **It counts what the ledger holds.** A call that fails to reach the ledger is not counted. Until this session every
  Ask ERCOT call failed to: the ledger's own check allowed only the general chat's step name. Migration 023 mends it.
- **It is not the provider's limit.** A spending limit set in the model provider's console is the outer wall, and a
  person sets it.

## The internal view

`/internal/ask?token=<INTERNAL_COSTS_TOKEN>`: today's and the month's spend against their ceilings, the day's
questions and visitors, spend and questions by day and tool for 62 days, and the ten costliest questions (their day,
tool, calls and cost: no text, no visitor). It answers 404 without the token, and the database answers nothing to a
wrong one.

## Proven

- The guard's logic: `tests/test_session128.py` (13 tests; no model, no database).
- The database's function, against the database: `runs/session128/prove_sql.py` (14 checks; no model).
- End to end on a local build: `runs/session128/prove_e2e.sh`. With the daily ceiling at 0, the visitor's number at
  0, and no secret, three questions were refused and the ledger gained no row. With the file's ceilings, two real
  questions were answered and logged with their numbers, and a third was refused by the visitor's number.
