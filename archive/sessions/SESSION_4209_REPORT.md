# Session 4209 report: the cross-check (chain 239, window 4)

13 November 2026, about 10:48 to 10:52 UTC. Model spend USD 0.

- **Three published studies read** (robots first; requests 49, 50, 54): Jayhawk Wind, Kansas (economic development report, November 2019); Glendive Wind, Montana (NextEra's summary of a 2024 Strategic Economic Research study); Ohio University's 2020 study of utility-scale solar in Ohio (low scenario). Refused or missing: the Kentucky PSC filing (its robots file names Python clients), the Center for Rural Affairs' Nebraska tax paper (403), Lava Run Wind's report (404).
- **`site/scripts/forecast-crosscheck.mjs`** runs each study's own project through the model. Jayhawk: 0.82 of its construction jobs (supply chain 0.96, induced 1.07, onsite 0.40: the developer's own in-state spending), 0.79 of its operating jobs. Ohio: 1.10 of its construction jobs, 1.16 of its direct jobs, 3.5 times its operating jobs (JEDI's 2010 PV operating costs). Glendive: the summary's "approx. 400" sits nearer the model's onsite construction jobs (272) than its total (1,730); kept with that caveat.
- The table and the reasons are in the method note, section 9; the run's numbers in `docs/reviews/forecast-crosscheck-2026-11-13.json`.
