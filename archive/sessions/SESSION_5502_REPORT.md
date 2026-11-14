# Session 5502 report: chain 269, item 2: the signature pack

Energy Research Warehouse (ERW). Chain 269, portable laptop window P1, 14 November 2026, about 09:05 to 09:45 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5500-closeout`.

- **The pack:** `docs/reviews/five-tools-signature-pack-2026-11-14.md`. Per tool: what Samuel signs (the note's sign-off block and what it accepts and leaves open), five key assumptions with defaults and sources, the cross-checks in one table, the Stata commands (each from its folder, with a log) and what the do-file should print. Then the eight open rulings of chain 243 with their defaults and what this chain built on each, and one new ruling (G1, the Grid page's "Checked against" line).
- **The expected values are today's:** each Python mirror run on main's files at about 09:20 UTC: battery 22 of 22, generator 13 of 13, datacenter 14 of 14, Automated Analysis 66 of 66 computed (10 license needed, 2 not in a download), the Grid 85 of 85 (22 license needed, 81 not held in this laptop's tables). Outputs: `runs/mirror5502_*.out` in the main checkout.
- **What the do-files print** was read from each file's `display` and `list` lines, not run (no Stata here): the Automated Analysis do-file should print "inside the tolerance: 62" (the mirror's 66 less the week's chart's 4, which it leaves to `replicate.py`); the Grid's "met: 85" (every key family of the network and the gravity shape is built by `replicate.do`).
- **Published as a private page** for reading on a phone: https://claude.ai/artifact/9j7g2YiWksNJvDmPfHGkgV (only Samuel can open it unless he shares it). The file in the repository is the record.
- **Test:** `tests/test_session5502.py` (5 tests): each quoted figure is `page_figures.json`'s; the mirror counts; each command; each sign-off block named and still unsigned; the rulings; no dash. 5 passed.
- **Corrected before commit:** two cross-check rows of Automated Analysis were first written from memory of their shape; read again, the solar row's published figure is Potomac's "6.2 GW", and the queue card's counterpart is the owner's thesis, not a publisher (now said as such). The negative coverage words were quoted from `docs/reviews/battery-faults-2026-11-13.md` row 11.

## Decisions made without you

- The pack points at `replication/<tool>/replicate.do` (which ends with each figure beside the page's), not the page's download copies in `site/public/` (which read the CSV from their own folder and compare nothing).
- G1's default is "no line", as the Grid note left it; the pack writes the line you would get on a yes.

## For Samuel's ruling

- **G1. The Grid page's "Checked against" line** (the pack's last section). Default: not added.
