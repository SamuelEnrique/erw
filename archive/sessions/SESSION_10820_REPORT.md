# Session 10820 report (chain 740, lab-desktop window 3): Illinois's and Tennessee's property

The commits carry "Session 10819"; this report covers the work after that session's last update.

- **What a reader will see once landed:** an Illinois building at one third of its cost (Cook County's 25 percent named in the hover, with how to type it) and a Tennessee datacenter at 40 percent for the building and 30 percent for the equipment. Tennessee is a new state in the rules (property only): 35 states.
- **Read** (requests 338 to 346): Illinois' Department of Revenue answer on assessment levels; Tennessee's Comptroller of the Treasury's 2025 Tax Aggregate Report (comptroller.tn.gov answers where www.tn.gov does not); tnecd.com's robots file (a 10-second delay, no page asked). Connecticut's assessment pages answered 404 (two addresses) and a moved PDF, so its ratio is not held.
- **More:** West Virginia's property at 60 percent (the Tax Commissioner's 2025 ratio study, W. Va. Code 11-3-1(d); request 350), so West Virginia joins the rules (property only: 36 states); AWS in Central Ohio (JobsOhio with the Governor, 2023: USD 7.8 billion by 2029, jobs "hundreds"; request 349) as an investment-only row (44 rows, no default moved).
- **Window A's answers:** data request 6 landed at 14:16 (22 rows; grows when row 14 lands), 7 landed (read by the tool), 9 built on `wip/c701-tax` (54 rows of 34 states from an earlier copy of the rules file), 8 (JEDI's coal and CSP trough) in its gate 6, which also takes the newest heads of requested rows.
- **Illinois's equipment:** whether a datacenter's equipment is taxed is not on the pages read, so it keeps the reader's rate on cost, and the hover says to leave it blank unless the county taxes it.
- **Tests:** 22 node tests; 9 Python tests; replication 16,010 of 16,010 figures of 79 cases; 106 quotes of 36 states. The 482-file set under the build lock (14:57 to 15:11 UTC, two halves): 5,245 passed, 15 failed, the 10 of the clean-main run and 5 in other pages' data checks (the board's held grids, `/ask`'s keys against this machine's tables, the events pages' pins), none reading the datacenter's code; noted on row 14.
- **Readers:** three more cases in `docs/reviews/impact-datacenter-readers-2026-11-26.md` (a budget analyst, a utility planner, a county assessor), no fault found.
- **Needs the key:** nothing.
- **Decisions made without you:** Illinois's ratio outside Cook County is applied, the reader adjusting for Cook County by the rate.
- **For Samuel's ruling:** nothing new.
