# License needed: large-load waits, alberta's electric system operator (canada)

Draft `scan-deep-7b2d88672148` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** License needed (large_load_wait_summary, internal): at Alberta's electric system operator (Canada), the median time from entering a stage to leaving it for the 181 large-load requests in its dated lists was at least 3.0 and at most 8.0 months, as of 2026-11-03.

![License needed: large-load waits, alberta's electric system operator (canada)](wait-alberta-electric-system-operat-in-stage.png)

**The tables and rows.** `large_load_wait_summary` (internal: license needed); the rows in `wait-alberta-electric-system-operat-in-stage.csv`.

**Its strength.** At least 20 requests: 181 requests in the interval. At least 5 measured between dated copies: 136 measured. The bounds ordered: at least 3.0, at most 8.0 months. The median bounded on both sides: both bounds held. Requests still waiting counted apart: 124 requests are lower bounds only.

**Its limits.** Bounds, not a figure: a request's wait is known only between the dated copies of the publisher's list that show it, and a request still waiting gives only a lower bound; the publisher's terms keep the table internal.

**Reproduce.** `python wait-alberta-electric-system-operat-in-stage.reproduce.py <large_load_wait_summary.csv>` and `do wait-alberta-electric-system-operat-in-stage.reproduce.do` (Stata) print the figures named at their top.
