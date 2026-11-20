# The security review's ground, 20 November 2026

Energy Research Warehouse (ERW). Chain 610, part B step 1 (`queue/done/610-night-20-november-oldlaptop-weekend-pack-security.md`), written by session 9813 in the desktop's third window. Every route handler and every page that reads a request, as the code on `origin/main` stood at 20:00 UTC on 20 November 2026 (`26dfe42cc`), with what each trusts. The last review's ground was the 41 route handlers of 13 November (`docs/reviews/security-faults-2026-11-13.md`, "The fresh pass"); this one covers everything since and what that one left open.

How it was made: `runs/c610w3/ground.py` (in this window's worktree, not in git) reads each `route.ts` and each `page.tsx` that reads the address, a cookie or a header, and names the guards it calls, what it reads and what it reaches. Each row was then read by hand. Nothing was sent to the production site, to Supabase or to Vercel.

## What changed since 13 November

- **Four new route handlers**, all made when the site is built, none reading anything a visitor names beyond a path part checked against a fixed list: `/grid/boundaries`, `/grid/authority/[code]`, `/grid/prices-map` and `/map/lines/[name]`. They sit under `/grid` and `/map` without a file extension, so the release gate's curtain covers them as it covers their pages.
- **Eight new pages** that read the address: `/conditions`, `/congestion`, `/states`, `/industry`, `/ai-energy`, `/queues/places`, `/storage/places`, `/curtailment/where-when`. Each reads the address only to choose a view or a row from files the site holds; none asks the database with a visitor's words.
- **Changed:** `/internal/findings` and `POST /internal/findings/state` (the findings audit's block on approval), the chat's tools (`lib/chat/heldrows.ts`, `refused.ts`, `window.ts`, `longtext.ts`), the `outputFileTracingIncludes` of `site/next.config.ts` (files only, no header), and the daily workflow's push (a refused push rebases and runs the guard again).

## Route handlers (45)

| Address | Methods | Made | Reads | Checks | Reaches | What it trusts |
|---|---|---|---|---|---|---|
| `/api/analysis` | POST GET | on request | address, body, cookie | same origin, internal cookie | database functions `analysis_request`, `analysis_request_card`, `analysis_requests_list` | the internal cookie (404 without it); the database function checks the internal token again and counts the day |
| `/api/ask` | POST | on request | body, header | same origin, stock client, JSON, limit | `site_ask_admit` (service key), the model | the hourly limit per address (memory and database), the day's and month's spend ceilings and the visitor's day count in the database, each failing closed; a body of 60,000 characters, a question of 500 |
| `/api/download` | GET | on request | address, cookie | limit, internal cookie | the live set (anon key) | the internal cookie (403 without it, until Samuel rules the downloads public); a table name by pattern; a held table refused by name; a non-public verdict refused; 60 an hour; 500,000 rows |
| `/api/entity` | GET | on request | address | limit | the live set (anon key) | a table from a list of two, an id of at most 200 characters, 600 an hour |
| `/api/play/finish` | POST | on request | body, header | same origin, limit | inserts a play (service key) | 30 an hour, 20,000 characters; the score is computed on the server from the level's real prices |
| `/api/play/score` | POST | on request | body, header | same origin, limit | inserts a score (service key) | as above |
| `/api/play/top` | GET | on request | address | limit | the live set | a preset by its parser, 240 an hour |
| `/api/subscribe/confirm` | GET | on request | address | limit | `subscribe_confirm` | the address's signed token, compared in the database; 60 an hour |
| `/api/subscribe` | POST | on request | body, header | same origin, stock client, limit | inserts a subscriber, sends one mail | 5 an hour per address and 200 a day for everybody, a hidden field |
| `/api/thesis/pitchbook` | POST | on request | body | limit | `thesis_pitchbook_accept` | the run's one-time key (43 random characters, erased when used), 400 KB read no further, 60 an hour |
| `/api/thesis/provider` | POST | on request | body, cookie | same origin, internal cookie | nothing of a visitor's | the internal cookie |
| `/api/thesis/run` | POST GET | on request | address, body, cookie | same origin, internal cookie | the thesis functions | the internal cookie; a run id by pattern |
| `/api/unsubscribe` | GET POST | on request | address, body | limit | `subscribe_unsubscribe` | the signed token; 120 an hour |
| `/api/usage` | POST | on request | body, cookie, header | same origin, stock client, JSON, limit, page status | `site_usage_record` | 600 an hour; a path checked against the menu; no cookie set |
| `/board/rows`, `/python`, `/stata` | GET | when built, or on request | nothing | none | a file the site holds | nothing a visitor names; under `/board`, so the curtain covers them |
| `/companies/rows`, `/python`, `/stata`; `/companies/[id]/rows`, `/python`, `/stata` | GET | on request | address or path part | none | files the site holds | the query parsed against the index (`queryOf`); the id looked up in the index; under `/companies`, curtained |
| `/cost-of-power/*.csv` (five) | GET | on request | address | internal cookie, page status | the price files | an address with an extension passes the proxy, so each applies its page's status itself (404 in review without the cookie); the tool's own parsers |
| `/grid/authority/[code]` | GET | when built | path part | none | a file the site holds | new: `dynamicParams = false`, so only the codes of `data/regions/authority/` exist; under `/grid`, curtained; every table in the 85 files is public in the ERW's verdicts (checked on 20 November) |
| `/grid/boundaries` | GET | when built | nothing | none | a file the site holds | new: `ba_boundaries` is public; curtained |
| `/grid/prices-map` | GET | when built | nothing | none | a file the site holds | new: the held grids (ISO-NE, NYISO, PJM) and the paused one (MISO) carry a state and a reason and no figure (read on 20 November); curtained |
| `/internal/findings/approved` | GET | on request | cookie | internal cookie | a file | the internal cookie |
| `/internal/findings/file` | GET | on request | address, cookie | internal cookie | a file of `docs/findings/` | the internal cookie; an id and a file name by pattern, the name beginning with the id |
| `/internal/findings/state` | POST | on request | body, cookie | same origin, JSON, limit, internal cookie | `scanner_draft_set_state`, `analysis_request` | the internal cookie; 500 characters; an id by pattern; a state from a list; the audit's block and the publisher's figure before an approval; the database function checks the token again |
| `/internal/lock` | GET | on request | nothing | same site | clears two cookies | refuses a request the browser marks cross-site |
| `/internal/unlock` | GET POST | on request | address (GET), body (POST) | same origin (POST), limit | sets the internal cookies | the token, in the address (the old link) or the form; **row 8 of the landing file** (finding T1) |
| `/learn/problems/[slug]/data.csv` | GET | on request | path part, cookie | internal cookie, page status | the problem sets' files | a slug from the list of sets; the page's status applied here |
| `/llms.txt` | GET | on request | cookie | internal cookie | a file | the internal cookie while every page is in review |
| `/map/card` | GET | when built | nothing | none | a file | curtained |
| `/map/lines/[name]` | GET | when built | path part | none | two files | new: a name from a list of two (`transmission`, `hgl`), both public tables; curtained |
| `/resources/layer/[name]`, `/resources/overlay/*` (three) | GET | when built | path part | none | files | names from the build's list; curtained |
| `/severance/finder/download` | GET | on request | address, cookie | token or internal cookie | a file | the internal token in the address or the cookie; **row 8** |

## Pages that read the request (61)

Every page outside `/internal` is in review today and is behind the curtain (`site/proxy.ts`): a visitor without the internal cookie is shown the in-review page. What follows is what each would trust once it opens.

| Pages | What they read | What they trust |
|---|---|---|
| The 53 tool, data and news pages that read the address (`/grid`, `/map`, `/prices`, `/prices/compare`, `/cost-of-power` and its tabs, `/datacenters`, `/deals`, `/policy`, `/companies`, `/storage`, `/queues`, `/curtailment`, `/demand`, `/supply`, `/events/*`, `/explore/*`, `/impact`, `/industry`, `/ai-energy`, `/states`, `/conditions`, `/congestion`, the two `/places` pages, `/research/card/[id]` and the rest) | a view, a grid, a hub, a row, a sort | each value is looked up in a list the site holds, or bounded by a pattern, before it is used; a value that reaches the database goes through `lib/supabase.ts`, whose license hold applies to every read; React escapes what it draws, and the 14 places that draw markup go through `lib/markdown.ts` |
| `/in-review` | `path` | a pattern (`^/[A-Za-z0-9_\-./%:]*$`), drawn as text, looked up in the menu for a name |
| `/ask` | `grid`, `q` | a redirect to the grid page with the question cut to 500 characters; the question is put in the box, never asked by itself |
| `/play/battery` | the address | a redirect to a path the code names |
| `/cost-of-power/battery` | the address, the internal cookie | the cookie compared in constant time (S1) |
| `/internal/ask`, `/internal/costs`, `/internal/usage`, `/reports/draft/ai-gigawatts`, `/reports/draft/shape-premium` | `token`, the internal cookie | the token compared with `!==` (L5, open with H1), or the cookie; **row 8** counts every try of the token |
| `/severance/finder`, `/severance/lease/real` | `token`, the internal cookie | as above; **row 8** for the finder |
| `/internal/findings`, `/internal/health`, `/internal/holds`, `/internal/siting-gaps`, `/internal/waits`, `/thesis` | the internal cookie | 404 without it (`tests/test_session5159.py` holds every `/internal` address) |
| `/internal/open` | `state` | a word from a list, for the form's message |

## What the site writes, and who may make it write

| Write | Route | Who may |
|---|---|---|
| A game play, a score | `/api/play/finish`, `/api/play/score` | anyone, 30 an hour from one address; the server computes the score |
| A subscriber, a confirmation, an unsubscription | `/api/subscribe`, `/confirm`, `/api/unsubscribe` | anyone, with the limits above; a confirmation and an unsubscription need the address's signed token |
| A usage count | `/api/usage` | anyone, 600 an hour; no cookie, no address kept (session 5154) |
| A question in the cost ledger | `/api/ask` | anyone, within the ceilings |
| A finding's state, an analysis request, a reader's question | `/internal/findings/state`, `/api/analysis` | the internal cookie only, and the database checks the token again |
| A thesis run, a PitchBook answer | `/api/thesis/*` | the internal cookie; the answer by the run's one-time key |
| A count of a limit | every limited route | the server, under the internal token (`site_rate_admit`) |

## The workflows and their secrets

The nine workflows under `.github/workflows/` are as session 5169 read them on 13 November (`tests/test_session5169.py` holds their permissions, actions and triggers, and passes on 20 November). One changed since: the daily run's push now rebases onto a moved main and runs the guard again (session 7020), which adds no secret and no trigger.

## The tests that hold this ground

The standing tests of the last review pass on `origin/main` at `26dfe42cc` (128 tests in 18 s, 19:49 UTC on 20 November): `tests/test_session5102.py`, `5153`, `5154`, `5159`, `5160`, `5161`, `5162`, `5169`, `5170`, `5171` and `177`. Rows 7 and 8 add `tests/test_session9811.py` and `tests/test_session9812.py`.
