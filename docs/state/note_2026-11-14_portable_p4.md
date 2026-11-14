# Note: US utilities' large-load connection rules, 14 November 2026 (portable laptop, window P4)

Energy Research Warehouse (ERW). Sessions 5300 to 5304, 13 and 14 November 2026, unattended, Opus 5.5 xhigh. Branch `wip/5300-large-load` at `ff0fc7bc9` (landing row 26), worktree `erw-p4`. Research documents only: nothing built, nothing landed, no warehouse data written. Reports: `archive/sessions/SESSION_5300_REPORT.md` to `SESSION_5304_REPORT.md`.

## Rows

- `docs/research/large_load/utilities_2026-11-13.csv`: 122 rows, one a large-load rule, from 17 utility groups: 91 utilities and statewide rules with rows, and one notes file for each of the 166 utilities read (with or without a rule).
- Statuses: 71 in effect, 21 approved, 28 proposed, 1 ordered, 1 denied.
- Licenses: 100 public, 22 internal; 2 public rows name `internal_fields`.
- Fields: 463 values, 36 held by window A's registries (not repeated), 35 pointers to the group's row with the queue figure, 442 not published.
- Cites: 1,699, every one matched on its cited page of the copy read (1,067 documents, 266 hosts).
- New beside window A's registries, among them:
  - Dominion GS-5, PPL LP-6, FPL LLCS, Pacific Power's Schedule 401;
  - 16 TAC 25.194, Santee Cooper L-27-HIL, LG&E and KU's EHLF, We Energies' VLC, IID's Schedule LL;
  - the Louisiana, Maryland, Minnesota, New Jersey and New York statewide rules;
  - queue sizes from the utilities' own filings.

## Changes (the 90 days to 13 November 2026)

- `changes_2026-11-13.csv`: 98 changes from five groups (South 29, East 21, West 19, operators and FERC 15, Midwest 14), 364 cites, all matched.
- Written into rows: Alabama's 33709 procedures approved, Maryland's COMAR 20.96.01 in effect, and Duke Energy Florida's tariff denied on 3 November.

## Laws

- `legislation_2026-11-13.csv`: 28 laws and bills from 26 states, read in the legislatures' own texts, 295 cites, all matched.
- Statuses: 10 in effect, 6 enacted, 4 passed, 3 passed one chamber, 3 introduced, 1 vetoed, 1 died.
- Texas S.B. 6 is withheld: the copy read sits on a path capitol.texas.gov's robots file disallows in capitals.

## Audit corrections

- Five independent auditors read all 122 rows from the cached copies: 677 verdicts, 633 ok, 21 wrong, 23 unclear (`audit_2026-11-14.md`, reports in `audit/`).
- All 21 wrong values were corrected with their quoted sources:
  - wrong pages;
  - dropped words;
  - overstated terms (the 25.194 forfeiture, Tacoma's minimum charge, the $200,000 deposits);
  - missed qualifiers;
  - inferred dates;
  - "not published" fields the documents state.
- 18 unclear findings were resolved; 5 were kept, each with its reason (the Entergy intervenor values, CPS's measures, Tri-State's status).
- Two of my own corrections were wrong (the New York appendix letters, National Grid's printed date). Later batches caught them; both are fixed and logged.

## What waits for window A (`docs/state/data_requests_large_load.md`)

- **Row 1:** load `utilities_2026-11-13.csv` as `utility_large_load_rules`.
- **Row 15:** load the changes as `utility_large_load_rule_changes`.
- **Row 16:** load the laws as `state_large_load_laws`.
- **Rows 2 to 7 and 9 to 14:** corrections and additions to its registry files:
  - NV Energy's LLESA, Oncor's docket, I&M's collateral, Dominion GS-5, SRP's term, Duke's settlement terms;
  - PGE's effective date and Order 26-309, Xcel Colorado's term, AEP Ohio's public copy, Ameren and Evergy's collateral tiers;
  - 16 TAC 25.194, PG&E Rule 30's CPUC copy.
- **Row 17:** window A's operator documents that changed: CAISO's Board approval, FERC on PJM, ERCOT's Batch Zero orders, the PA model tariff docket's closing, Utah's R746-318.
- **Row 8:** the license of twelve registry files, waiting on a ruling.

## Rulings, each with a default

1. **Twelve registry files** were read from hosts whose terms bar robots or ask permission (Entergy, Dominion, CenterPoint, SRP, Georgia Power, Alabama Power, APS, Oncor, PG&E). Default: internal until re-read from a commission's copy.
2. **Party-posted copies of docket filings** (intervenors, SELC, Earthjustice). Default: public, with the host named.
3. **"not published" also covers "not readable here"** (the reason is in `searched`). Default: one marker.
4. **Duke Energy Progress's row** rests on the settlement's words for both companies. Default: keep.
5. **Statuses beyond the three asked** (`ordered`, `denied`, `withdrawn`). Default: keep.
6. **SEC EDGAR asks for a contact in the user agent**; the reader sends a generic one and now gets 403. Default: keep the 153 copies read when allowed; no new EDGAR read until you choose a user agent.
7. **Retries after this machine's own failures** (certificates, the network outage), once each. Default: allowed, as a failure of ours and not the host's refusal.
8. **Lincoln Electric's "may not store".** Default: unread.
9. **The TVA Board resolution** read from TVA's content host, terms unread. Default: public; written as "other", since its text prints it as proposed.
