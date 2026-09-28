# Session 26 report

Energy Research Warehouse (ERW), session 26, run 2026-09-28 (UTC). **API spend: USD 1.3845** (the re-reads of Task 2), under the USD 3 stop. One further read in the big re-read failed on malformed JSON before its cost was counted (the bug is now fixed); at the run's average it cost under USD 0.03. The Thesis Builder rebuilds made no model call. No key was printed or committed. `origin/main` was merged before the push.

All five rulings are applied. FERC stays via the Federal Register and other state PUCs are deferred, so neither needed code.

## What was built

| Task | Result | API cost (USD) | Commit |
|---|---|---|---|
| 1 | Thesis Builder rulings; both workbooks rebuilt from their saved states with `--resume` | 0 | `a351f05` |
| 2 | Policy date ruling; 70 date-dropped reads and the one malformed read re-read | 1.3845 | `56c5a47` |
| 3 | `energy_companies` in the live set; `/companies`; links from the home page's Investors and from `/deals`, with party names cross-linked | 0 | `e66eada` |
| 4 | A chat-spec check in `run_daily.sh`; validator, coverage, live set, value check, screenshots, this report | 0 | final commit |

## Task 1: the Thesis Builder rulings

- **Public companies:**
  - A company whose stage or raised cell names an exchange listing (public, NASDAQ, NYSE, TSX, LSE, IPO) is kept off Landscape.
  - It is added to Incumbents ("public company (from Landscape)", with its ticker) unless Incumbents already lists it.
  - In `energy_companies` its raised is blank and its confidence note starts "public company".
  - The structure prompt now tells the model that public companies belong on Incumbents.
- **Capital investors and dates:**
  - New runs ask for `investors_spans` and a `date_span`, exact quotes from the cited passages. A field is kept only when its quotes are found there, else it is blank.
  - The saved states predate the ruling and have no spans. There, an investor name is kept only if it appears verbatim in the cited passages of the row's sources (the name is its own quote). A date is kept only if the passages write it in one of its forms ("December 10, 2025", "Dec 10, 2025", "2025-12-10", "12/10/2025", "December 2025" and so on).
  - "not disclosed" is kept as written: it says no investor is named, and it is not a name.
- **Rebuild:** both workbooks were rebuilt with `--resume` from `warehouse/output/thesis_state/`, with no model call, in 0.2 and 1.6 minutes.

What changed in the twenty spot-checked rows (session 25's check):

| Row | Before | After |
|---|---|---|
| Company: Project InnerSpace | on Landscape | unchanged |
| Company: Mantle Reach Power | on Landscape | unchanged |
| Company: Zanskar | on Landscape | unchanged |
| Company: Fervo Energy | on Landscape, raised "$1.89 billion IPO ..." | off Landscape; on Incumbents as "public company (from Landscape)", NASDAQ: FRVO; raised blank, noted public, in `energy_companies` |
| Company: Quaise Energy | on Landscape | unchanged |
| Company: Fluence Energy | on Landscape, Raised held FY2025 revenue (the error session 25 found) | off Landscape; already on Incumbents; raised blank, noted public |
| Company: Tyba | on Landscape | unchanged |
| Company: FlexGen Power Systems | on Landscape | unchanged |
| Company: GridBeyond | on Landscape | unchanged |
| Company: Stem, Inc. | on Landscape, Raised held 2025 hardware revenue (the second error) | off Landscape; already on Incumbents; raised blank, noted public |
| Capital: Sage Geosystems 2026-01 Series B | investors "not disclosed" | unchanged |
| Capital: Fervo Energy 2025-12-10 Series E | "led by B Capital" | investors blank: "B Capital" is in no cited passage (the error session 25 found) |
| Capital: Bedrock Energy 2023-10-11 seed | date 2023-10-11; eight investors | date blank (not in the cited passages); investors: Wireframe Ventures only |
| Capital: Quaise Energy 2026-08-27 Series B final close | "led by Prelude Ventures ..." | investors blank: Prelude is in no cited passage of this row (the second error) |
| Capital: Quaise Energy 2026-07-07 Series B first close | date; Prelude, JERA, Idemitsu | date blank; investors: Prelude Ventures; Idemitsu |
| Capital: FlexGen 2022-07-19 Series C | "Vitol (anchor), existing investors" | Vitol |
| Capital: GridBeyond 2024 Series C | year 2024; four investors | year blank (the third error); investors: Energy Impact Partners; ABB |
| Capital: Tyba 2025-02-06 Series A | Energize Capital lead and others | date kept; Energize Capital dropped (on the fetched page, not in the stored cited passages); Pear VC, Mobilize Climate Capital, Borusan Ventures, Wireframe kept |
| Capital: GridBeyond 2026 Series D | year 2026; four investors | year blank; the four investors kept |
| Capital: Amperon 2023-10-03 Series B | date; four investors | date blank; investors: Energize Capital; Veriten; HSBC Asset Management |

- **All five errors of session 25's check are gone:** two public companies on Landscape, and three capital fields their sources did not state.
- **The ruling is strict with old states.** It also blanks true fields whose words are on a source page but not in the passages the search API returned, such as Tyba's lead investor and most exact dates. Runs from now on ask the model for the quotes, and a re-run of either niche would restore what the pages state.

## Task 2: the policy date ruling

- **The ruling in code:** `accepted_dates()` in `warehouse/policy/reads.py`. A date written in a field in a different format from its spans ("June 22, 2026" for "2026-06-22", or a month and day with a year the text states) is taken out of the number check when the date appears in the source text. Any other number still must be in the spans.
- **Which reads were redone:** from the run logs, 109 fields had been dropped for numbers. The 86 fields whose stray numbers were all date-like (a year, or a day of the month), in 70 actions, were re-read with `reads.py --ids`. Their old rows and evidence spans were replaced.
- **Recovered:** in those 70 actions, 240 kept fields became 283, a net 43 recovered. 44 actions gained fields, 16 kept the same number and 10 lost some: a re-read is a new model answer, so a few fields fall to other checks. 38 fields were still dropped for numbers, now for numbers that are not dates.
- **The malformed read** (`nrc:4cec785a9cad`) had failed twice on unterminated JSON. The output cap was 4,000 tokens; at 8,000 it read with all 5 fields kept.
- **Cost accounting:** `reads.py` now counts every call's cost, failed or not; before, a failed read's cost was lost.
- **Totals:** 227 of 227 actions read, 127 with all five fields kept (97 before). Cost USD 1.3698 plus 0.0147.

## Task 3: `/companies`

- **Live set:** `energy_companies` (17 rows) is loaded.
- **The page:**
  - a scope note: a seed, not a census, growing from Thesis Builder runs and the deal tracker as its counterparties are added;
  - filters for sector, niche tag, stage, state (read from the location) and confidence (any, 50 or more, 80 or more);
  - each row expands to what the company does, founders, raised (or "blank: public company"), website, the confidence and its clause, sources, and first seen;
  - each row has an anchor (`#co-<name>`), and a link to one opens that row.
- **Links:** from Investors on the home page (Companies beside Deals), from `/deals` (in its intro and in the Related line) and from `pages.ts`.
- **Cross-links from `/deals`:** a buyer, seller or other party whose name matches a company links to its row. Names are compared in lower case, without punctuation or a legal suffix. One deal matches today: Fervo Energy as a seller.

## Task 4

- **The chat spec check:** `warehouse/chat/check_spec.py` regenerates the spec from `llms.txt`, `ask.py` and `tools.py` and compares it with the committed `site/lib/chat/spec.json`. It compares content, with line endings normalized, because a fresh checkout gives every file the same time, so an "older than" test on file times cannot work in CI. `run_daily.sh` runs it first and stops on a stale spec. Tested both ways: the current spec passes, and one added line in `llms.txt` fails it.
- **Briefing:** `llms.txt` notes the public-company rule and `/companies`, and the spec was regenerated after it.
- **Validator:** 113 of 113 tables pass.
- **Coverage:** 113 tables.
- **Live set:** catalogue 113, sources 150, `pg_database_size` 334.2 MB.
- **Value check:** 705 of 705 values match Supabase (`/roundup`: 20 of 20).
- **Screenshots:** home, `/deals`, `/policy`, `/companies`, and `/companies#co-fervo-energy` (the row open), at 1280 and 390 px. The script now starts from a blank page before a URL with a fragment. Loading one twice (desktop, then mobile) is a same-document jump with no load event, and it had timed out.

## Decisions made without a human

1. **A public company is detected by rule** (the words "public", an exchange, or IPO in its stage or raised cell). It is moved to Incumbents rather than dropped, so it stays in the map.
2. **For saved states without spans, the name or date itself found in a cited passage stands in for the quote.** It is the strictest test possible without a new model call.
3. **Date-like drops were chosen from the logs by rule:** every stray number is a year or a day of the month.
4. **The spec check compares content rather than file times,** for the reason given under Task 4.

## Open questions for a human

1. **Re-run the two niches?** About USD 2.40 each. The workbooks would carry quoted investors and dates, recovering the true fields that the stored passages do not hold.
2. **Counterparties from `energy_deals`** could seed more of `energy_companies`. Should that be the next step for tool 10?
