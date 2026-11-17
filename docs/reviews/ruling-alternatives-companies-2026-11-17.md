# Ruling alternatives: /companies, the company database (17 November 2026)

Session 7625 (portable-laptop, code role). The one line of `docs/reviews/ruling-impact-companies-2026-11-17.md` (it moves two parents' figures from 0 and adds a list), built on its own branch from origin/main with a test that pins it. **No branch asks to land; no default on main changed; no held figure summed or drawn.** Model spend USD 0.

- **Build:** the worktree `erw-alt` (3,239 MB free before the build), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px.
- **Tests:** the new test and every test file that names a changed file: 38 passed.

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 1 | A parent company's page sums its listed subsidiaries' operating and owned MW, each subsidiary listed | `wip/alt-companies-1` (`9a3ed4789`) | `/companies/duke-energy`: no MW figure (0 operating, 0 owned); `/companies/dominion-generation` the same | Duke Energy: **"Operating, with its subsidiaries" 38,147 MW** (38,147.3) and owned share 544 MW (543.8), with a "Subsidiaries" table: Duke Energy Carolinas, LLC 23,868 and 464; Duke Energy Progress (NC) 14,279 and 80. Dominion Generation: **28,681.0 MW** operating and 5,821.5 owned, 3 subsidiaries (Virginia Electric & Power 20,208.2 and 3,873.3; Dominion Energy South Carolina 6,212.9 and 686.4; Dominion Energy Nuclear Connecticut 2,259.9 and 1,261.8). No other parent's page moves: the other four parents' subsidiaries hold no MW; Constellation Energy Corporation stays 0 | `site/lib/companydata.ts`, `site/app/companies/[id]/page.tsx`, `tests/test_session7625_alt_companies_parents.py` | On `site/data/companies/c/*.json` (built 16 November 2026): only Duke Energy and Dominion Generation have subsidiaries with MW, at 38,147.3 and 543.8, and 28,681.0 and 5,821.5; the page reads every shard and draws the sums and the list | `docs/reviews/ruling-alternatives/companies-1-parent-summed-1280.png` |

## Decisions made without you

- **"The list of who names whom as parent" is the files' own `parent_id`** (11 companies naming 6 parents), as the impact file measured; a fuller list (Luminant for Vistra, the Constellation companies) is the data machine's to build, and the page would then sum it with no change of code.
- **The summed figures stand beside the company's own**, labelled "with its subsidiaries" and carrying no check key of their own (the check keys are each company's own figures).
