# Session 10807 report (chain 740, lab-desktop window 3): part F, more announced projects

- **What a reader will see once landed:** the datacenter's defaults rest on 25 announced projects (was 22): MW 1,000 (was 1,800), investment USD 11.0 million a MW (was 8.33), 0.306 permanent jobs a MW (was 0.208), 250 construction jobs a USD billion (was 325); each hover says the count, the lowest, the highest and the date computed (26 November 2026).
- **Read** (requests 192 to 194, Louisiana Economic Development): Hut 8's River Bend, West Feliciana Parish (17 December 2025: up to USD 10 billion, 245 MW of critical IT load on 330 MW of utility capacity, at least 75 direct jobs, about 1,000 construction workers at peak); Amazon in Caddo and Bossier Parishes (23 February 2026: USD 12 billion, 540 direct jobs, up to 1,500 construction jobs); Applied Digital's Delta Forge 1, Rapides Parish (26 May 2026: USD 3.6 billion, 300 MW of critical IT load, 200 on-site jobs, over 1,000 construction jobs at peak). Every quote verified.
- **Request 8** for window A: the JEDI models the table lacks (coal, hydropower, CSP, transmission line), evaluated as `jedi_recalc.py` evaluates the four held.
- **Waiting:** the local build; window A's gate `land-21574e2f` held the build lock from 11:47 UTC (its checks passed by 12:11).
- **Commits:** the rows, defaults and tests (branch); the hover date (branch); `forecast.md` 13.2 and 13.4 with the new medians (main); request 8 (main).
- **Needs the key:** nothing.
- **Decisions made without you:** the tests read the medians from the file (they move with each row, by design); the CleanArc test fixes its construction workers at 975 so its hand sums stay fixed.
- **For Samuel's ruling:** nothing new.
