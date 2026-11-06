# Smart meters: Illinois

Draft `scan-deep-5d99205b850f` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of meters in Illinois that are advanced (AMI) was 92.8 percent of meters in 2019, against 6.4 percent of meters in 2013, the first year EIA's meter table holds.

![Smart meters, Illinois](ami-share-ami-il.png)

**The figure by full year** (percent of meters): 2013: 6.4, 2014: 16.8, 2015: 38.1, 2016: 60.5, 2017: 78.4, 2018: 90.5, 2019: 92.8.

**The tables and rows.** `eia_meters_state_annual`; the rows for Illinois, region key `ami_IL` (the card's `hunt.region`), years 2013 to 2019. The yearly values: `ami-share-ami-il.csv`.

**Its strength.** The change is 3.88 typical yearly moves (a typical move is 22.3 percent of meters, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2013 lie above 2013's value. Survives a change of window: from 2014 to 2019 the change is 76.0, from 2013 to 2018 it is 84.1. Sample large enough: 2013 holds 1 and 2019 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2014 to 2019 the change is 76.0, 88.0 percent of the change from 2013. At least one typical yearly move: the change is 3.88 typical yearly moves (22.3 percent of meters a year, the median move between full years); the floor is 1.

**Its limits.** EIA's figures as published, nominal dollars where a price; the latest months are preliminary. EIA-861's meter counts by type, as utilities report them; the ERW's table splits out advanced meters by state only to 2019.

**Reproduce.** `python ami-share-ami-il.reproduce.py <the table's CSV>` and `do ami-share-ami-il.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
