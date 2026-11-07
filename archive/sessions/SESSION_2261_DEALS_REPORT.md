# Session 2261 (chain 159, deals and datacenters) report: facilities' operator

6 November 2026, from about 13:00 to 13:03 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2261-deals`, cut from `wip/2260-deals`. Model spend **USD 0** (code; the 2249 and 2236 facility answers replayed). Nothing deployed; no warehouse data written.

- **The class**: facilities' operator missed, 3 of 60 on the second read.
- **F014, fixed**: the model joined two companies in the developer field ("Colt DCS, RMZ"); `checked_fields` refused the joined string. `names_named` (`warehouse/datacenters/extract.py`) keeps an operator or developer when each of its names is in the story. Replayed: F014 keeps "Colt DCS, RMZ"; no company refusal is left on either facility fixture.
- **F050 and F036, by the rule**: a description ("TikTok owner") is not a name; a government named by its place ("Balearic Islands") was left empty by the model, and no word rule makes a place an operator.
- **Before and after**: operator missed **3 to 2**.
- **Found on the way**: the second read's facilities have a country missed three times (F035, F044, F053), counted under no class in the 2249 tally; it is the next class (session 2262).
- **Tests**: `tests/test_session2261_deals.py`, 2 passed; the tests that load the datacenter extractor (166, 176, 2236), 46 passed.
- **Docs**: `docs/methods/datacenter_facilities.md` ("Two companies in one field"), the audit file's section.

## Decisions made without you

1. **Joined names only in the two company fields**: a site, a power source or a utility with two names joined is still refused.

## For Samuel's ruling

- None new.
