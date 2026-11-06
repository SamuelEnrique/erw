# Session 2285 (chain 179, deals and datacenters) report: USD missed beside another currency

6 November 2026, about 14:08 to 14:13 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2285-deals`, cut from `wip/2284-deals`. Model spend **USD 0** (code; the answers replayed). Nothing deployed; no warehouse data written.

- **The class** (the third read, session 2284): T024's USD empty though its evidence states "US$938 million" beside the euros.
- **The fix**: `fields.usd_stated`, used by `extract.py` where the model gave no USD: exactly one figure stated explicitly in US dollars in the evidence (US$ or USD), not a contract's funding or an asset's cost. Logged.
- **Before and after**: **1 to 0**; every row's sum and flags diffed on the four deal fixtures (2232, 2249, 2256, 2284): only T024 changed. The sums refused in session 2271 are not filled back (the model had given them).
- **Tests**: `tests/test_session2285_deals.py`, 3 passed; the deals and datacenter tests, 284 passed, 1 skipped.
- **Docs**: `docs/methods/energy_deals.md` ("A figure stated in US dollars beside another currency"), the audit file's section.

## Decisions made without you

1. **Only a figure the story itself states in US dollars**; no conversion, and a bare $ stays the model's to read.

## For Samuel's ruling

- None new.
