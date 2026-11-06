# Session 3061: chain 166's eighth session (its 2267): the monitor's calendar, keyed and traced

Personal laptop, second window, 6 November 2026, 13:05 to 13:25 UTC. Opus 5.5. Branch `wip/3061-policy` cut from `wip/3060-policy`.

## What it did

- `warehouse/policy/monitor_site.py`: each record carries `steps`, every dated step its documents state, each with its words and its document; `site/data/policy/monitor.json` rebuilt (1,495 records).
- `site/lib/policymonitor.ts`: `calendarOf` (the past week's actions; the month ahead's steps, soonest first), the keys `policycal|<record>|<document>|<kind>|<date>` and `policyfig|<record>|<document>|<value>|<unit>`, and `keysOf`.
- `site/app/policy/MonitorCalendar.tsx` (new): the two lists above the monitor's table, of the records the filters leave (any date); each date with its words as hover and its key as `data-check`; each figure of the table keyed the same way.
- `site/scripts/policy-figures.mjs` (new): every key as the page makes them; `scripts/check_policy.py` (new), in `check_digest.py`'s form: each key found in its document's row of `policy_actions` (the connector's columns, or what `fields.derive` reads from a row's summary where the copy holds no text), ok, FAIL or "not here", exit 1 on a FAIL or when nothing could be checked.
- Tests: `tests/test_check_policy.py` (3), `test-policy-monitor.mjs` (45, 8 new).

## What it found

- `python scripts/check_policy.py` on this laptop's tables: 262 keys (steps and figures), 262 ok, 0 FAIL, 0 not here. On this copy both sides read the rows' summaries, so the run proves the keys and their tracing, not the texts; the data machine's copy, with the fields read from the printed texts, is the real trace (its first run after the landing).

- **The dash checks of five files are now written by code point** (chr(0x2014) in Python, String.fromCharCode(0x2014) in JavaScript): session 3060 wrote their escapes back as text, and this session's edit of monitor_site.py turned them into the characters again (the editing tool decodes the escape). A code point survives any edit. The 71 files this chain changed hold no dash character.

## Decisions made without you

- **The calendar is of the records the filters leave**, with the date filters set aside (the calendar has its own window: seven days back, thirty ahead, from the page's day).
- **`data-check`, not `<Num check>`.** The site's `check-values.mjs` knows only its own key families; a new family there is the gate's, and this window does not run the gate. The keys are traced by `check_policy.py` instead, as the chain asks; adding the family to `check-values.mjs` is left for the landing, written in the request.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
