# Session 2276 (chain 174, deals and datacenters) report: stated facilities with no row

6 November 2026, about 13:45 to 13:48 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2276-deals`, cut from `wip/2275-deals`. Model spend **USD 0** (code; the facility answers replayed). Nothing deployed; no warehouse data written.

- **The class**: stated facilities with no row, 2 of 60 on the second read.
- **F017, fixed**: refused for no place; `facility_country` reads the market a company enters with the facility ("to enter US market"). Kept on both facility fixtures (61 and 24 rows, one more each).
- **F028, by the ruling**: the model gave no facility; the prompt's human ruling (session 23) makes a purchase of chips or servers no facility, and the AI cluster bought outright reads as one.
- **Older answers and tests**: the 2236 fixture's answer for F017 (chain 156: "no place stated") now accepts either, with the reason; `tests/test_session2236_deals.py` (the stored rows found wrongly: F057 alone) and `tests/test_session2262_deals.py` (four country fills, the fourth this one) changed with notes.
- **Before and after**: **2 to 1**.
- **Tests**: `tests/test_session2276_deals.py`, 2 passed; the datacenter tests, 60 passed.
- **Docs**: `docs/methods/datacenter_facilities.md` ("The market a company enters with a facility"), the audit file's section.

## Decisions made without you

1. **A country is a place**, as `has_place` already counts it, so a facility named with a company, its MW and only its country is kept.

## For Samuel's ruling

- Whether an AI cluster bought outright (servers in a building another company owns) is a facility or a purchase of servers.
