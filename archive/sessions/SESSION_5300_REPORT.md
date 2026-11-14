# Session 5300 report: US utilities' large-load connection rules, the reader and the first eight groups

13 November 2026, unattended, `portable-laptop` window P4 (Opus 5.5, xhigh). Branch `wip/5300-large-load` in the worktree `erw-p4` (cut from `origin/main` at `739d7279d`). Nothing built, nothing landed, no warehouse data written. Model spend: subagents only, no API key.

## Read these first

- **The dataset:** `docs/research/large_load/utilities_2026-11-13.csv`. 47 rows from 8 utility groups, one row a rule. Every value carries its document, page or section, and the words.
- **The method:** `docs/research/large_load/README.md`. **The hand check:** `docs/research/large_load/spotcheck_2026-11-13.md`.
- **The requests, on main (`1acb5441a`):**
  - `docs/state/data_requests_large_load.md`, 8 rows for window A: the new table; six corrections to window A's registry files; one license question.
  - `docs/state/landing_request_portable.md`, row 26.
- **Window A's table had 84 rows, not 75.** The Redivis draft of 13 November 11:52 UTC holds 84 steps from 12 documents. The prompt's 75 was an earlier draft.

## What was done

- **The ground.** I read `large_load_connection_rules` (84 steps; mostly grid operators' documents, plus PG&E Rule 30 and Utah's two) and `utility_large_load_tariffs` (30 schedules, 95 figures), with their method notes and registries, and the owner's research file of 6 November (leads only).
- **The reader** (`fetch_doc.py`). Robots first: its own agent, `*`, and Anthropic's agents by name. It refuses MISO and the Virginia SCC (paused) and Con Edison, Eversource and Duquesne Light (barred). It spaces requests by host and keeps each copy with its pages, so every quote can be matched again with no second request. Since this session it also:
  - verifies certificates with Windows' verifier;
  - reads .docx and .xlsx files.
- **The checks:**
  - `verify_quotes.py` matches every quote, part by part, on its cited page;
  - `merge_group.py` checks each row's form;
  - `spotcheck.py` prints one row in five, each value beside its words in place;
  - `build_csv.py` and `make_notes.py` write the CSV and one note a utility;
  - `tests/test_session5300_large_load_research.py` checks that every row has a source URL, a date read, and in each field a value with a placed quote, `not published`, or a pointer that resolves.
- **Fifteen reading subagents,** at most eight at once. Eight groups are merged: Dominion and the Virginia co-ops, Southern and Florida, AEP, Entergy and Louisiana, Texas, Duke, the Southwest and California, PJM East. Seven are still reading: the Northwest, Xcel and the Plains, Ameren and Evergy, TVA and the Southeast, the Great Lakes, the Northeast, co-ops and public power. The Texas subagent is re-reading its certificate failures.
- **The quote check:** 633 cites in the 8 groups, every one matched on its cited page.
- **The hand check, one row in five (12 rows), plus one beside the sample:** 11 pass; 2 corrected (Entergy rows 1 and 2, below).
- **Reads:** 610 documents from 150 hosts: 601 read, 3 with no text layer, 6 bot checks (not retried).

## What was found

- **Rules held now that window A lacks**, among them:
  - Dominion GS-5: 25 MW, minimums of 85, 85 and 60 percent, 14 years, 1.5 million USD per MW, read from the Final Order's copy in a Florida PSC filing.
  - PPL LP-6, in effect since 1 July 2026.
  - FPL LLCS-1 and LLCS-2, approved 22 January 2026.
  - Tampa Electric's LLCS, proposed.
  - Kentucky Power: 150 MW and 20 years.
  - I&M's Michigan Tariff LP; APCo and Wheeling's West Virginia terms.
  - El Paso Electric's New Mexico Rates 50 and 51.
  - TEP's 300 MW agreement, with a 40 million USD letter of credit.
  - Louisiana's Lightning Amendment and its large-load guidelines; Maryland's proposed COMAR 20.96.01.
- **Queue sizes** from the utilities' own filings and SEC documents:
  - Oncor: 795 requests, about 293 GW of data centers, at 30 September 2026.
  - Dominion: about 54 GW under contract.
  - PPL: 35.3 GW.
  - Georgia Power: 12,400 MW committed and a 73,100 MW pipeline at 31 March 2026.
  - PG&E: 12,870 MW.
  - AEP Ohio: 15,574 MW signed by 2031.
  - Rappahannock: 22,426 MW requested.
- **Changed since window A read them** (data request rows 2 to 7):
  - NV Energy's LLESA is now a form agreement pending PUCN approval (deadline 2 December 2026).
  - Oncor's docket is 58306.
  - I&M's collateral is due within 10 business days (sheet of 24 June 2026).
  - The GS-5 row can be written.
  - SRP's agreement sets a 15-year minimum term.
  - Duke's settlement terms beyond the held file.
- **Hosts whose terms bar this reader:** Entergy, Dominion, PPL, Exelon, NextEra (fpl.com). Their documents were taken from commission copies or SEC filings, or left unread.

## Decisions made without you

1. **Never duplicating window A.** A value its registries hold unchanged is written `held: <registry>/<file>.yaml`. A changed one is written with its cite, and `erw_overlap` names the old value.
2. **A value only quoted by an intervenor is a note, not a value** (window A's rule for its own registries).
   - Entergy row 1: the ESA's term, minimum charge and exit fee came from an AAE/UCS witness's summary, so they are now "not published", with the words kept in the notes.
   - Entergy row 2: the term came from IEEFA's witness, and is handled the same way.
   - The later briefs say this rule outright.
3. **Robots files that bar Anthropic's agents by name bar this reader,** although it sends its own agent name, because it is driven by Claude. The NCUC's and PUCO's portals are among them.
4. **Certificates are checked by Windows' verifier** (`truststore`), with verification kept: Arizona's name mismatch still fails. The Texas, Florida and Nevada commissions' failures were this machine's. Finished groups re-read those documents once; the Texas group is re-reading now.
5. **Subagents hand over rows as JSON files** in the ignored `runs/s5300/rows/`, so no quote is ever retyped. Only I write repository files.
6. **One CSV for the pass,** named by its first day and rebuilt as groups finish.
7. **Status is one of three.** A date the document prints only to the month is kept as YYYY-MM (two rows).
8. **Statewide commission rules** (Louisiana, Maryland) are rows of their own, with their own notes.
9. **The request rows went to main** from a detached worktree (`erw-p4-row`), as window P2 did for its row 18:
   - documents only;
   - the freeze checked first (none);
   - no snapshot taken, because no page changes.
10. **Sessions 5300 to 5399 are this window's.** Chain 255 (window P1) moved to 5400 to 5419 on seeing this branch.

## For Samuel's ruling

1. **Five of window A's registry files were read from hosts whose terms bar robots or reproduction.**
   - Barring robots: the three Entergy files and Dominion GS-4.
   - Forbidding reproduction: SRP E-67.
   - Also: the two I&M files cite IN.gov, which the method note calls internal, yet they read public.
   - Default: hold them internal until each is re-read from a commission's copy (data request row 8).
2. **Rows read from a party's own posted copy of a docket filing:** an intervenor's site, IEEFA, the SELC (also window A's Duke file), Earthjustice (window A's Xcel file). Default: public, since each is a filing in a public docket, with the host named in the row.
3. **"not published" also covers "not readable here".** The `searched` text gives the reason (a robots file, terms, a paused host). Default: keep one marker. Say if you want a separate `not read` marker in the table.
4. **Duke Energy Progress's row** rests on the settlement's words that the tariff applies to both companies; no Progress leaf is printed. Default: keep it, as written.

## Next

- Merge the six groups reading now, and co-ops and public power when it finishes, each with its check and commit; then the Texas re-read and the certificate retries of the finished groups.
- Then the second pass: what changed in the last 90 days.
- Then the states' large-load legislation.
