# Session 2272 (chain 174, deals and datacenters) report: facilities' state

6 November 2026, about 13:36 to 13:41 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2272-deals`, cut from `wip/2271-deals`. Model spend **USD 0** (code; the facility answers replayed). Nothing deployed; no warehouse data written.

- **The class**: facilities' state missed, 2 of 60 on the second read (F034 "Hutto, Texas", F015 "Western Kentucky").
- **The fix**: `facility_state` (`warehouse/datacenters/extract.py`) reads the one US state a cluster of one facility names by its full name with a capital, for a facility with no country or the United States; longer names first; "Washington" alone not read. Logged.
- **Before and after**: **2 to 0**; the only other fill across both fixtures is F028 of the 2236 fixture ("Columbus, Georgia", GA as its written answer says).
- **Tests**: `tests/test_session2272_deals.py`, 3 passed; the datacenter tests, 54 passed.
- **Docs**: `docs/methods/datacenter_facilities.md` ("A facility's state from the words"), the audit file's section.

## Decisions made without you

1. **One facility a cluster only**: a story about several sites names several states, and no word rule says which is whose.

## For Samuel's ruling

- None new.
