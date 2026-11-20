# License needed: large-load waits, the new york iso

Draft `scan-deep-eb172f7d4510` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** License needed (large_load_wait_summary, internal): at the New York ISO, the median time from request to study for the 58 large-load requests in its dated lists was at least 0.8 and at most 2.8 months, as of 2026-11-05.

![License needed: large-load waits, the new york iso](wait-new-york-iso-request-to-study.png)

**The tables and rows.** `large_load_wait_summary` (internal: license needed); the rows in `wait-new-york-iso-request-to-study.csv`.

**Its strength.** At least 20 requests: 58 requests in the interval. At least 5 measured between dated copies: 21 measured. The bounds ordered: at least 0.8, at most 2.8 months. The median bounded on both sides: both bounds held. Requests still waiting counted apart: 3 requests are lower bounds only.

**Its limits.** Bounds, not a figure: a request's wait is known only between the dated copies of the publisher's list that show it, and a request still waiting gives only a lower bound; the publisher's terms keep the table internal.

**Reproduce.** `python wait-new-york-iso-request-to-study.reproduce.py <large_load_wait_summary.csv>` and `do wait-new-york-iso-request-to-study.reproduce.do` (Stata) print the figures named at their top.
