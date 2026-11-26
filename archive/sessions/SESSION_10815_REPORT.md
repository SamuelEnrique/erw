# Session 10815 report (chain 740, lab-desktop window 3): Georgia's and Nevada's announced projects, a partial-investment flag

- **What a reader will see once landed:** 42 announced projects (Facebook's Stanton Springs in Georgia, Google and Vantage in Storey County, Nevada, added); the construction default 338.9 workers a USD billion (12 rows; 277.8 without GOED's estimate for Google, named in decision 3); permanent jobs a USD billion 51.2 (32 rows); Nevada's hover names GOED's 2 percent sales tax and 75 percent property abatement, still not applied (a Board vote).
- **Read** (requests 272 to 281): Georgia's 2018 release on Facebook in Stanton Springs (USD 750 million, at least 100 jobs); GOED's releases on Google (16 September 2020: USD 600 million, at least 50 people at USD 31.29 an hour, more than 2,500 construction jobs by GOED's estimate) and Vantage (14 November 2024: USD 254 million of capital equipment, about 10 jobs), and its abatement sheet.
- **A new flag:** `investment_partial` on a row whose investment is not the whole datacenter (Vantage's is equipment only): kept with its words, left out of every ratio and not offered as the project's investment in the picker, as Paducah's (power plants included) already was. Builder and picker both read it.
- **Refused, honoured:** commerce.idaho.gov (HTTP 403 to its robots file). **Waiting:** mn.gov (its robots file sets `Visit-time: 0000-1200`; the probe's parser ignores the directive, so the session read the printed rules and did not fetch; noted in memory). Utah's 2018 Facebook announcement was not found on a state site.
- **Tests:** 22 node tests; replication 8,700 of 8,700; the datacenter's Python tests; 57 quotes of 26 states.
- **Commits:** two on the branch; `forecast.md` 13.2 and decision 3, the note, the ground document, the progress file (main).
- **Waiting:** the build of the newest head (the lock held by window A's gate since 13:15 UTC).
- **Needs the key:** nothing.
- **Decisions made without you:** GOED's construction estimate counts as an announced figure (a state agency's own number), with the median without it written beside; Vantage's equipment-only investment gives no ratio.
- **For Samuel's ruling:** nothing new.
