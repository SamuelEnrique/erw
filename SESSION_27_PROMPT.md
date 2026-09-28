Session 27 of the Energy Research Warehouse (ERW). Read CLAUDE.md, warehouse/thesis/build.py, warehouse/deals/extract.py, site/lib/pages.ts and SESSION_26_REPORT.md first. Same non-negotiables; commit after each task; may push after merging origin/main; API spend stop USD 8.

Human rulings on session 26: re-run both niches; seed energy_companies from the deal tracker's counterparties.

TASK 1. Re-run Thesis Builder for "subsurface heat mapping for geothermal" and "grid-scale battery storage software for merchant operators" with the span rules, replacing the two workbooks in docs/thesis/. Report cost, time, the number of Capital rows with a quoted investor and a quoted date, and any row where the new run disagrees with the old one on amount or stage. Commit.

TASK 2. Seed tool 10 from deals. For every buyer, seller and other party in energy_deals, create or merge a row in energy_companies: name, the sector of the deal, niche tags from the deal type and technology, location where a deal states one, sources (the deal's story links), confidence from the same rule (deal-only rows start at the source count), first_seen the deal's date. Do not invent descriptions, founders or stages; leave them blank with "from deals; not yet researched". Merge on normalized name plus website when known. Report the count before and after and the share with a description. Reload the live set and check /companies still renders every row.

TASK 3. Feedback log. Create docs/feedback/README.md with the demo protocol (the five questions, the 20-minute page order, where notes go) and a template file docs/feedback/TEMPLATE.md; add a "Feedback" row to docs/platform-tools.md's status page pointing at the folder. No site changes.

TASK 4. Validator, coverage, live set, briefing if any table changed shape, value check, SESSION_27_REPORT.md. Final commit and push.