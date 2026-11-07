# Session 2240 (chain 156, deals and datacenters) report: the AI-power view

6 November 2026, from about 09:29 UTC, portable-laptop (code role), unattended. Worktree `erw-2240` on `wip/2240-deals`, cut from `wip/2239-deals`. Model spend **USD 0**. Nothing deployed (`/deals` stays `review`); no warehouse data written.

- **`site/lib/dealsai.ts`** (new, pure): the AI-tagged deals by buyer (one name a company), by the kind of supply (nuclear, gas, renewables and storage, grid supply, compute capacity, capital and acquisitions, other; read from the deal's kind and its stated technology), by grid and by quarter; each group's deals, and its MW and US dollars summed where stated with the count that state each; the ten with the most MW and the ten with the most US dollars; `aiKey` (`deals|ai_<deals|mw|with_mw|usd|with_usd>|<dimension>|<value>`).
- **`site/app/deals/ai/view.tsx`** (new): `/deals?view=ai` (`?aby=buyer|supply|grid|quarter`), under the tracker's tab; the hold drawn as on every deals view; the two lists of ten each with its sources, and the AI tag's basis as the sources' hover.
- **`site/lib/deals2.ts`**: a deal carries its kind of session 2232 (or its type's kind, for an older row), its buyer and seller as one name a company, and its AI tag's basis.
- **`site/app/deals/page.tsx`**: the view's address; session 466's tab line kept as it was, the active tab read beside it.
- **`site/scripts/check-values.mjs`**: every new key recomputed with the page's functions.
- **`tests/test_session2240_deals.py`** (7 tests); with 2239, 466, 465: passed (113's check of committed files passes on the commit). Type check: no error in the deals files.

## Decisions made without you

1. **The buyer of a raise or a loan with no buyer named is the party named first** (the seller), so an AI datacenter firm's own debt is grouped under it rather than under "not stated"; said in the section's note.
2. **The kind of supply** is the deal's kind first (a restart, an SMR, a gas buildout, storage, compute), then its stated technology, then its form; "Grid supply" is a PPA, an offtake or a behind-the-meter deal with no stated fuel.
3. **"The ten largest with their evidence"**: the evidence is the deal's sources and the AI tag's basis, for the reason of session 2238 (the sentence is outlet text the site does not show).

## For Samuel's ruling

- None new.
