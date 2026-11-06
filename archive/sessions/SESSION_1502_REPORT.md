# Session 1502 report: security, what a visitor can spend and fetch

Energy Research Warehouse (ERW), session 1502, chain 158, samueloldlaptop, 6 November 2026, 10:10 to 10:12 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1501-security`.

## What it found, and held by a test (`d6d0cb149`, `tests/test_session1502.py`)

- **Ask cannot spend the owner's key for a visitor beyond its limits.** The route answers only the site's own pages (403 otherwise). It counts each visitor's questions by the hour in the database (`limited(req, "ask_hour", ...)`), and asks the database before every model call whether the day's and the month's ceilings and the visitor's daily number hold (`lib/chat/limits.ts`, session 128). A refusal carries its reason, and the route stops at 120 seconds.
- **The service key is server-only.** `SUPABASE_SERVICE_KEY` is read by the site's writes alone (`lib/supabase.ts`'s `writeConfig`, `import "server-only"`), and nothing names it for a browser (`NEXT_PUBLIC_`). On the main copy's build of 09:55 UTC its value appears in none of the 4,169 built files, and no client chunk carries a `service_role` claim. The test reads the built files where a copy holds a build (the value never printed).
- **The downloads refuse what they must**: every download outside the internal view until you rule whether it is public (403), a held table by name ("license needed", 403), a table not public in the catalogue (404).
- My first test asserted the key appeared nowhere in the site's code, which is wrong: the server's writes use it. It was corrected to "server-only, in no built file" before the commit.

## Decisions made without you

- None.

## For Samuel's ruling

- Whether the downloads open to visitors (the route's own words: "until the owner rules whether it is public").
