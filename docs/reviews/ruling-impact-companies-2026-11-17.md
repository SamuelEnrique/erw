# Ruling impact: /companies, the company database (17 November 2026)

Session 7596 (samueloldlaptop). The one line marked "Changes a figure" under /companies in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`). No page and no default was changed.

- **Script:** `runs/ruling_impact/companies_impact.py`, its printout `companies_impact.out`. It reads the page's own files, `site/data/companies/c/*.json` (built 16 November 2026: 12,724 companies, each with its figures and, where named, its parent). The MW figures are EIA-860 and EIA-860M's (public); the held figures (deals, facilities) are not summed or printed.
- **No model call** (spend USD 0).

| # | Line (the question) | Page and cells | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | A parent company's page sums its listed subsidiaries' operating and owned MW, each subsidiary listed, once the list of who names whom as parent exists | `/companies/<parent>`: plants operated (MW), owned (MW), the footprint, and a list of subsidiaries | Each legal entity keeps its own figures; none is summed into a parent | Summed, by the list of parents | By the parents the files already name (11 companies name 6 parents), two parents' pages move: Duke Energy from 0 to 38,147.3 MW operated and 543.8 MW owned (2 subsidiaries); Dominion Generation from 0 to 28,681.0 MW operated and 5,821.5 MW owned (3 subsidiaries). The rulings line's example, Constellation Energy Corporation, reads 0 MW: no subsidiary with MW names it as parent yet (the one that does, Constellation Energy Generation, LLC, holds no MW), so it stays 0 until the list exists. Found by name alone, the companies called Constellation operate 32,154.0 MW and own 6,228.3 MW (Constellation Nuclear 23,798.1 and 6,228.3; Constellation Power 7,734.1); a subsidiary not named for its parent (Luminant for Vistra) is not found that way, which is why the list is needed first |
