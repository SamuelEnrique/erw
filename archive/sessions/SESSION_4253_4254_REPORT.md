# Sessions 4253 and 4254 report: fault 19, Illinois's refusal, the fourth and fifth studies (chain 240, window 4)

13 November 2026, about 13:55 to 14:05 UTC. Branch `wip/4250-forecast`. Model spend USD 0.

- **Fault 19** (a sentence printed under the states chart, against "explanations only as hover tips") fixed with a test; built under the lock (13:58) and read: no console error, no sideways scroll, check-values 785 of 785. Landing row 4 moved to `1d43574d3` on main.
- **The page's size**: 92 KB compressed (498 KB raw) for `/impact`, against 61 KB for `/cost-of-power`: no fault.
- **Illinois**: read again with the system's trust store, www.ilga.gov's certificate verifies and the site answers "Access Denied" (HTTP 403) to an automated read, its robots file included: a refusal, honoured; the note and the method say so.
- **The fourth study**: NREL's Indiana's first 1,000 MW of wind (2014; docs.nlr.gov, request 78): the model gives 1.03 of its construction jobs and 0.89 of its operating jobs.
- **The fifth study**: NREL's Rush Creek Wind Farm case study, Colorado (2019; request 80, through OSTI to docs.nlr.gov): 0.51 of its construction jobs, the supply chain the gap (Vestas's Colorado factories against JEDI's default turbine share of 0); 0.71 without the 830 factory jobs; operating jobs 0.69.
- `www.nrel.gov` no longer resolves (the laboratory is NLR now); NREL's reports are read from `docs.nlr.gov`.
- The method note's section 9 holds five studies and the Minnesota tax check; `docs/reviews/forecast-crosscheck-2026-11-13.json` rewritten by `site/scripts/forecast-crosscheck.mjs`.
