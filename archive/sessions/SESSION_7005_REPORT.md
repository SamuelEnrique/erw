# Session 7005 report: the company database's replication mirror (goal 4)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0. No request made.

- **`replication/companies/replicate.py`**, written from `docs/methods/companies.md` and the tables alone, not from the page builder: for each of the 12,724 listed companies, every figure of its shard and its index row recomputed from its public rows of `company_links`, each MW, county and status read from the input table's own row (EIA-860M's nameplate, EIA-860's percent owned, the ERCOT queue's capacity and status, the NRC's capacity, EIA-861's territories). **381,721 of 381,721 figures equal** on the files of the branch (built 09:04 UTC) and the tables of main's checkout. A changed figure in a copy of the index is caught (exit 1, the one difference printed).
- **`replication/companies/replicate.do`**: five headline figures from `company_links.csv` (12,724 companies listed; 6,060 that operate a generator; 1,423,491.7 operating MW; the largest, Florida Power & Light, 40,818.1 MW; 95 NRC reactors linked), expected values at its top. Not run: Stata is not on this machine.
- **The method note** gains a "Replication" section, with the warning below.
- **No mismatch, so no new faults row.**

## Decisions made without you

- **The replication takes the company each link names as given** (the resolution is the method's rules 1 to 7, which the builder applies; replicating the name resolution itself would be the builder again). What it checks independently is every figure from the input rows, the listing (every company with a public row is listed, and only those), and that each shard's links are exactly the company's public rows.
- **A reader's trap, written into the do-file and the method note:** pandas' `comment="#"` drops rows whose names hold a "#" (12,714 companies instead of 12,724).

## For Samuel's ruling

- None new.
