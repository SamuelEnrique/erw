# License needed: large-load waits, the bonneville power administration

Draft `scan-deep-f03fb0f0b061` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** License needed (large_load_wait_summary, internal): at the Bonneville Power Administration, the median time from request to withdrawal for the 167 large-load requests in its dated lists was at least 20.3 and at most 32.9 months, as of 2026-11-15.

![License needed: large-load waits, the bonneville power administration](wait-bonneville-power-administratio-request-to-withdrawal.png)

**The tables and rows.** `large_load_wait_summary` (internal: license needed); the rows in `wait-bonneville-power-administratio-request-to-withdrawal.csv`.

**Its strength.** At least 20 requests: 167 requests in the interval. At least 5 measured between dated copies: 90 measured. The bounds ordered: at least 20.3, at most 32.9 months. The median bounded on both sides: both bounds held. Requests still waiting counted apart: 0 requests are lower bounds only.

**Its limits.** Bounds, not a figure: a request's wait is known only between the dated copies of the publisher's list that show it, and a request still waiting gives only a lower bound; the publisher's terms keep the table internal.

**Reproduce.** `python wait-bonneville-power-administratio-request-to-withdrawal.reproduce.py <large_load_wait_summary.csv>` and `do wait-bonneville-power-administratio-request-to-withdrawal.reproduce.do` (Stata) print the figures named at their top.
