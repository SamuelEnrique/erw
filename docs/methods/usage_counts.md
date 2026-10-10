# Usage counts: how the site counts use without cookies or personal data

Session 177 (10 October 2026). The site counts how its tools are used. It does so with no cookie, no identifier kept in the browser, and nothing that can follow a person from one day to the next. This note says exactly what is recorded, how the daily code is made, and what the method cannot promise. The reader's page is [`/privacy`](/privacy); the owner's page of counts is `/internal/usage`.

## What one line holds

| Column | What it is | Where it comes from |
|---|---|---|
| `day` | the UTC day | the database's clock |
| `path` | the page's path, without a query or a hash, at most 120 characters | the browser sends `location.pathname`; the server keeps it only if it is a page of the release list (`site/lib/release.ts`) or a page under one |
| `tool` | the tool's name | the server names it from the path through the menu's own list (`site/lib/pages.ts`); the browser cannot send one. A visitor who asked for a page in review is counted with the tool "In review (not opened)" |
| `event` | `tool opened`, `input changed`, `scenario compared` or `download` | the browser |
| `visitor` | a code for one browser for one day (below) | the server and the database, together |
| `n` | how many times that line happened that day | the database |

Never recorded, in a table or in a log: the IP address, the user agent string, the referrer, a query string, the name or the value of any input, a cookie, an identifier from `localStorage`.

## The four events

- **tool opened**: once a page view (`site/components/Usage.tsx`, mounted once in the root layout).
- **input changed**: a form control inside the page's `<main>` changed, at most once a control a page view. Only the fact is sent.
- **scenario compared**: a tool compared two cases. The tool calls `track("scenario compared")` itself (`site/lib/usage.ts`).
- **download**: a click on a link that carries `download`, goes to `/api/download` or a download route, or names a `.csv`, `.do` or `.py` file.

## The daily code, step by step

1. The browser posts `{"event", "path"}` to `/api/usage`. The request carries, as every request does, the visitor's address and user agent.
2. The site's server computes `v1 = HMAC-SHA256(key = ASK_VISITOR_SALT, "erw-usage\n" + address + "\n" + user agent)`, 64 hexadecimal characters. `ASK_VISITOR_SALT` is a secret only the server holds. The address and the user agent go no further than this step: they are not logged and not sent to the database.
3. The server calls the database function `site_usage_record` (migration 028) with `v1`.
4. The database holds one row in `site_usage_salt`: today's salt, 32 bytes from `gen_random_bytes`, drawn the first time it is needed that UTC day. It is derived from nothing: not from a secret, not from the date.
5. The database computes `visitor = first 32 hexadecimal characters of HMAC-SHA256(key = today's salt, v1)` and stores the line with that. `v1` is not stored.
6. **When the day is over**, the first call of any of the functions after 00:00 UTC (a usage count, a rate-limit check, or the owner opening `/internal/usage`) does three things in one transaction: it adds the day's lines up into `site_usage_daily` as counts (events and distinct visitors, per line, per page, per tool and for the whole day); it deletes the day's lines, with their codes, from `site_usage_events`; and it deletes the day's salt.

So what is kept of an earlier day is counts. The codes are gone, and the salt that made them is gone. Because the salt was random and not derived, it cannot be computed again from anything the database or the site keeps. Two days' codes for the same browser share nothing, and "the same browser on two days" is counted as two browser-days: the site cannot tell.

## What this cannot promise

- **Backups.** Supabase keeps its own backups of the database for their retention period. A backup holds whatever the tables held when it ran, which can include a day's codes and that day's salt. Reversing a code would also need the server's secret and a candidate address and user agent to test.
- **A quiet midnight.** The day is closed by the first call after 00:00 UTC. If nothing calls the functions for some hours, yesterday's codes and salt stay until something does.
- **During the day** the codes of that day exist, so the day's own lines can be grouped by browser. That is what makes "distinct visitors today" a number.
- **A shared address.** People behind one address with the same browser version are one code.
- **The hosts.** Vercel and Supabase handle every request and keep their own logs under their own terms. This note is about what the ERW's own code stores.

## When nothing is counted

- The browser sends Do Not Track (`navigator.doNotTrack` of `"1"`) or Global Privacy Control: the page's script sends nothing, and the server drops a request that carries `DNT: 1` or `Sec-GPC: 1`.
- The request comes from another site's page, from a stock command-line client, or names a path that is not a page of this site.
- The page tells the reader that nothing typed there is sent (`/battery/customer`, the contract boxes of the cost-of-power pages, the severance tools, the bill page): the page view is counted and nothing after it, so no request follows what the reader does. `site/scripts/check-no-request.mjs` proves it for `/battery/customer`.
- An element inside `data-no-usage` is never counted.
- More than 400 different lines from one code in a day, or 200,000 lines in a day: the rest are dropped.

## Who can write and read

The four tables have row-level security on and no policy: the site's public key reads and writes none of them. The three functions take the internal token and refuse without it, so a person holding only the public key cannot fill the counts. `/internal/usage` is behind the internal view and shows counts only.

## Files

`site/lib/usage.ts` (`track`), `site/components/Usage.tsx`, `site/app/api/usage/route.ts`, `site/lib/usagepath.ts`, `site/lib/guard.ts` (`usageVisitor`), `site/app/internal/usage/page.tsx`, `warehouse/supabase/migrations/028_security_usage.sql`, `warehouse/supabase/rollbacks/028_security_usage.sql`.
