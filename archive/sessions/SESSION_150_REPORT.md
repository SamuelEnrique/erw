# Session 150 report: Thesis Builder, second and third data providers

Run on 8 October 2026 (UTC), unattended, in the chain 150 to 153. An agent built it in a working copy of its own to
a written brief (`runs/session150/BRIEF.md`); I checked the landing and applied the migration myself. `/thesis`
stays `review` and internal.

## Five things to know first

- **Both formats are built from the providers' own public documentation, and no field is invented.** 113 fields are
  mapped (67 of Harmonic's, 46 of Crunchbase's), each found by a test in its provider's saved page. **What is not
  verified, for either: that the connector's actual output carries those names in that nesting.** No connector was
  called, by any means. Only a real pasted answer can show it; whatever does not match is kept as given under "not
  mapped" and feeds no figure.
- **PitchBook is unchanged, byte for byte.** The request text is the same 2,628 characters with the same hash, and
  session 135's fixtures read to the same bytes. **Run `20261006T193517Z-50a8be` and its pending request were not
  read, written or migrated.**
- **One new internal table, by a migration I applied after the landing** (`thesis_provider_results`, two
  functions). The runs table is not altered: no column, no row, no function of the earlier migration replaced.
- **Two terms questions are yours.** Crunchbase's license has an "expunged" clause, and two of its documents could
  govern a connector seat. Harmonic's terms forbid "bulk downloading or automatic scraping": the session asked
  Harmonic's hosts for nine public documentation pages, once each. Say if even that should not be repeated.
- **One saved Harmonic page is a prompt addressed to an assistant** (its "MCP Onboarding Prompt", asking the reader
  to start calling Harmonic's tools). It was read as documentation; nothing in it was acted on.

## Verdict: not ready to open. What is left, exactly

1. **No real answer of any provider has passed through**, PitchBook's included. Paste one of each and read the
   "not mapped" count: that is where documentation and connector will differ, each unmatched field named on hover.
2. **Your ruling on Crunchbase's terms** before a Crunchbase answer is kept, and whether a way to expunge one
   provider's answer from a run is wanted first.
3. **Harmonic's daily limit.** Its guide gives a connector user without API access 100 requests a day, and says
   deal data needs an add-on. The pending run asks for 25 companies: a lookup, an enrichment and the people of
   each may not fit one day.
4. The list of runs shows PitchBook's state only; the other providers' state is in the run's own panel.
5. An answer once accepted cannot be corrected from the page (one answer a provider and run, as PitchBook's).

## What was built

- **One interface** (`site/lib/thesis/providers.ts`; `warehouse/thesis/providers.py`): a provider has an id and
  label, the request text it makes from a run, the format it expects back, a reader for what is pasted, a mapping
  from its fields to the run's facts, and its terms line. PitchBook is the first provider of it.
- **`erw-harmonic-1`**: companies (31 fields), funding rounds (9) and their investors (4), people (7) and their
  experience (6), investors of a saved search (10); saved searches of companies and of investors.
- **`erw-crunchbase-1`**: organizations (29 fields), funding rounds (10), founders (7).
- **A record of who supplied what**: every fact carries the provider, the format, the time pasted and the hash of
  the pasted text. The report shows `Fact: value [Provider]`, the terms line on the label's hover.
- **Disagreement is shown, not settled**: where two providers give a fact differently, every value is kept and
  each line is marked "DIFFERS". Nothing is averaged, preferred or dropped.
- **On `/thesis`**: a row "Data provider" (PitchBook chosen first, Harmonic, Crunchbase); the request text changes
  with the choice; an answer in another provider's format is refused with both formats named. Every element of the
  PitchBook panel is kept. A run with PitchBook alone is drawn exactly as before.
- The two new request texts are made by the page from what a finished run saved, so every finished run works with
  all three providers, with no new run.
- `docs/methods/thesis_builder.md` (internal) and the readers' note are brought up to date.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| The two providers' public documentation and terms pages | 60 requests, 40 MB (set before the first request) | **19 requests**, 1.98 MB |

- data.crunchbase.com 9, support.harmonic.ai 6, console.harmonic.ai 2 (an empty shell), harmonic.ai 1 (terms),
  pitchbook.com 1 (**403, a browser check: left**; PitchBook's terms line says the page was not read).
- **Contact string: exactly "ERW research project, github.com/SamuelEnrique/erw". No address sent.**
- No request to a connector's address, to any API, to MISO or to PJM. No data pull.
- **Terms quoted** (each checked against its saved page, with its hash, in the method note):
  - Harmonic, Terms of Service, last updated 9 December 2025: "You will not (and will not allow anyone else to):
    [...] provide, sell, transfer, sublicense, lend, distribute, or otherwise allow others to access or use the
    Services or the data obtained through the Services;" and, in the same list, the words "bulk downloading or
    automatic scraping".
  - Crunchbase, License Agreement: "Except as otherwise expressly set forth herein, Licensee may not license,
    sublicense, sell, offer to sell, distribute or otherwise provide any Crunchbase data to any third parties."
- Each provider's line on the page says the data is the person's own licensed copy, brought by them, shown to
  them, not published, redistributed or kept in the public warehouse.

## Model spend: none

- No model call, no API call, no connector call. No cap was set for this session.

## The landing

- **Added after the landing.** Landed with session 152 in one push (`task/150-152`, commit `e705393`): checks
  passed (run 37711233439), merged as `b7684f6`. The whole suite in a clean copy: 2,077 tests, passed.
- **Vercel built it:** "Deployment has completed" for `b7684f6` at 01:15:32 UTC on 8 October.
- **Snapshot before** (`150_before`, 01:06:08 UTC) **and after** (`150_after`, 01:15:53 UTC): **6 differences, all on
  `/network`, all its own hourly refresh at 01:05 UTC** (the refresh stamp, the newest demand hour from 22:00 to
  23:00 UTC, the source line's build stamp): expected, and not this deploy. **No checked number moved** (3,357
  keys). Nothing was reverted.
- **The migration** (`025_thesis_providers.sql`) applied at 01:16 UTC, exit 0. Snapshot after it
  (`150_after_migration`) against `150_after`: **0 differences.**
- **On production, in the internal view, the page's check passes 29 of 29**; it stores nothing and queues nothing.
- `site/lib/pages.ts` and everything the three live pages render or read are untouched.

## Checks

- `tests/test_session150.py` 32; `test-thesis-providers.mjs` 19; `test-thesis-pitchbook.mjs` 15;
  `test-thesis-paste.mjs` passes; the page's browser check against the stand-in 93 of 93 (68 before, unchanged).
- The whole suite in the working copy: 1,996 tests, passed. The clean-copy run is made at the landing.

## Decisions made without you

1. A table of its own for the new providers' answers, not a column on the runs table.
2. No one-time key in the two new requests: the answers are pasted on the internal page.
3. A record's content never refuses an answer of the two new providers: what does not fit is kept and counted.
4. Harmonic's amounts are compared as numbers although their currency is not documented; a currency difference
   then shows as a disagreement.
5. A founder is a person whose title holds the word "founder"; the last round is the round with the latest date.
6. I applied the migration (a new internal table) after the landing, with the live pages snapshotted.

## The five most interesting numbers

1. **113 fields mapped, 0 invented**: 67 of Harmonic's and 46 of Crunchbase's.
2. **0 against 14**: Harmonic's connector guide names no tool one by one (seven categories); Crunchbase's names 14.
3. **2,628 characters, one hash**: the PitchBook request text before and after.
4. **100 requests a day**: Harmonic's cap for a connector user without API access, against 25 companies in the
   pending run's request.
5. **4 of Crunchbase's own dictionary entries describe another field** (none of the four is mapped).
