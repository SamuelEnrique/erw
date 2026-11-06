# Session 2270 (chain 174, deals and datacenters) report: deals' AI-power tag

6 November 2026, about 13:29 to 13:32 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2270-deals`, cut from `wip/2269-deals`. Model spend **USD 0** (code; the answers replayed). Nothing deployed; no warehouse data written.

- **The class**: AI-power tag wrong, 2 of 106 on the second read (D005 a motive, D104 a market).
- **The fix**: `fields.DATACENTER_GENERIC` (a datacenter, hyperscale or AI word followed by buildout, boom, demand, market, growth, sector, industry, race, frenzy or spending) is taken out of the words before `DATACENTER_WORDS` reads a load; a named AI party is read first, as before.
- **Before and after**: **2 to 0**; every replayed row's tag diffed: only the two changed (37 to 35 tagged).
- **A fixture answer changed**: the 2232 fixture's written answer for D005 (chain 156) said AI power; it now accepts either reading, with the reason in its `why`, since the later read quotes the prompt's own rule on motives.
- **Tests**: `tests/test_session2270_deals.py`, 3 passed; the deals and datacenter tests, 258 passed, 1 skipped.
- **Docs**: `docs/methods/energy_deals.md` ("A datacenter word that is a motive or a market"), the audit file's section.

## Decisions made without you

1. **The later read over the earlier answer** for D005, since it quotes the prompt's rule; the fixture accepts both rather than flipping one read's answer.

## For Samuel's ruling

- None new.
