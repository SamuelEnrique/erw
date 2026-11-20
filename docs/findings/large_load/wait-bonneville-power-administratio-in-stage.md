# License needed: large-load waits, the bonneville power administration

Draft `scan-deep-16ffaab139ce` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** License needed (large_load_wait_summary, internal): at the Bonneville Power Administration, the median time from entering a stage to leaving it for the 288 large-load requests in its dated lists was at least 15.0 and at most 39.3 months, as of 2026-11-15.

![License needed: large-load waits, the bonneville power administration](wait-bonneville-power-administratio-in-stage.png)

**The tables and rows.** `large_load_wait_summary` (internal: license needed); the rows in `wait-bonneville-power-administratio-in-stage.csv`.

**Its strength.** At least 20 requests: 288 requests in the interval. At least 5 measured between dated copies: 216 measured. The bounds ordered: at least 15.0, at most 39.3 months. The median bounded on both sides: both bounds held. Requests still waiting counted apart: 200 requests are lower bounds only.

**Its limits.** Bounds, not a figure: a request's wait is known only between the dated copies of the publisher's list that show it, and a request still waiting gives only a lower bound; the publisher's terms keep the table internal.

**Reproduce.** `python wait-bonneville-power-administratio-in-stage.reproduce.py <large_load_wait_summary.csv>` and `do wait-bonneville-power-administratio-in-stage.reproduce.do` (Stata) print the figures named at their top.
