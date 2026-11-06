# Session 2273 (chain 174, deals and datacenters) report: facilities' power source

6 November 2026, about 13:39 to 13:44 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2273-deals`, cut from `wip/2272-deals`. Model spend **USD 0** (code; the facility answers replayed). Nothing deployed; no warehouse data written.

- **The class**: facilities' power source missed, 2 of 60 on the second read (F060, F032).
- **The fix**: `facility_fields.power_from_words` (`POWER_WORDS`), used by `extract.py` for a one-facility cluster with no power source; the kind follows from `power_kind`. Logged.
- **Before and after**: **2 to 0**; only the two filled across both facility fixtures.
- **Tests**: `tests/test_session2273_deals.py`, 3 passed; the datacenter tests, 60 passed.
- **Docs**: `docs/methods/datacenter_facilities.md` ("A facility's power source from the words"), the audit file's section.
- **Sessions 2269 to 2273 (chain 159's unfinished steps) are done**: the landing waits on the desktop; no ruling answered; the open classes taken in order (place by decision; AI tag, a figure of another thing, facilities' state and power in code). Left for sessions 2274 to 2277: MW basis (1) and a party wrong (1).

## Decisions made without you

1. **The words must say how the facility itself is powered**: a company's line of business or a utility's rates are not read.

## For Samuel's ruling

- None new.
