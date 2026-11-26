# Session 10820 report (chain 740, lab-desktop window 3): Illinois's and Tennessee's property

The commits carry "Session 10819"; this report covers the work after that session's last update.

- **What a reader will see once landed:** an Illinois building at one third of its cost (Cook County's 25 percent named in the hover, with how to type it) and a Tennessee datacenter at 40 percent for the building and 30 percent for the equipment. Tennessee is a new state in the rules (property only): 35 states.
- **Read** (requests 338 to 346): Illinois' Department of Revenue answer on assessment levels; Tennessee's Comptroller of the Treasury's 2025 Tax Aggregate Report (comptroller.tn.gov answers where www.tn.gov does not); tnecd.com's robots file (a 10-second delay, no page asked). Connecticut's assessment pages answered 404 (two addresses) and a moved PDF, so its ratio is not held.
- **Illinois's equipment:** whether a datacenter's equipment is taxed is not on the pages read, so it keeps the reader's rate on cost, and the hover says to leave it blank unless the county taxes it.
- **Tests:** 22 node tests; 9 Python tests; replication 15,770 of 15,770 figures of 78 cases; 105 quotes of 35 states.
- **Needs the key:** nothing.
- **Decisions made without you:** Illinois's ratio outside Cook County is applied, the reader adjusting for Cook County by the rate.
- **For Samuel's ruling:** nothing new.
