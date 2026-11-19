# The events pages' "whole country" views, read as their reader (started 19 November 2026)

Energy Research Warehouse (ERW). Chain 503, part E (session 8440, the old laptop). The form is part B of chain 304: five real cases a named reader would bring, each taken start to finish on the page; every gap a numbered row; every fault fixed at its cause with a test. Then the done line for the new views: the method note, the replication, a cross-check against a published figure, the decisions.

## The reader and the five cases

The reader: **a resource adequacy analyst at a utility in the Southeast**, preparing a note on how much help neighbors gave in recent storms and heat. Real places, real dates:

1. **Winter Storm Elliott, Tennessee, 23 and 24 December 2022** (`/events/elliott-2022#whole-country`): what Tennessee's demand, generation by source and net imports did against the baseline, and which neighbors sent it power.
2. **Winter Storm Elliott, the Carolinas beside Tennessee** (`/events/elliott-2022?region=car&b=ten#whole-country`): the same for the Carolinas, the two side by side, and the pair between them.
3. **Winter Storm Uri, Texas beside the Central region, 14 to 19 February 2021** (`/events/uri-2021?region=tex&b=cent#whole-country`): what crossed Texas's ties and what the Central region (the Southwest Power Pool's ground) sent or took.
4. **The September 2022 heat wave, California beside the Northwest** (`/events/caiso-heat-2022?region=cal&b=nw#whole-country`): California's net imports through 6 September against the baseline, and what the Northwest and the Southwest each sent.
5. **The January 2025 cold, the Mid-Atlantic beside the Southeast** (`/events/cold-2025?region=mida&b=se#whole-country`): each region's highest hour against the baseline at that hour, and the change in gas and coal generation.

For each case the questions are the same: can the reader get the answer without leaving the page, without a figure that contradicts another page, and without a word they would not know?

## State on 19 November 2026

| Part | State |
|---|---|
| The five cases read on the page | waits for the files: `site/data/regions/events/<event>.json` are not on origin/main (the data machine's chain 501, step B7). Nothing was waited on; the parts below that need no file are done. |
| The method note | done: `docs/methods/events.md`, "The whole country" (session 8410), with the replication's lines (session 8440). |
| The replication | written and tested on the fixture: `replication/events/replicate_regions.py`, 203 of 203; it runs on the site as it stands and says no file is there. The count on the real files waits for them. |
| The Stata do-file for the five headline figures | waits for the files: its expected values are real figures and none can be written before a file exists. |
| The cross-check against a published figure | waits for the files. What it will set beside the page: the federal inquiry's account of Winter Storm Elliott for the Tennessee Valley Authority and Duke (already linked on the page), ERCOT's and the Southwest Power Pool's own accounts of February 2021, CAISO's report on September 2022, and EIA's own regional totals on its Hourly Electric Grid Monitor. Each host's robots file and terms are read first; `www.ferc.gov` and `www.nerc.com` refused the reader on 19 November and are not asked again. |
| The decisions | on the page as hovers inside the section (each with its default and source): the baseline, the 5 percent of "reached", the regions drawn first, the 21 days that switch the charts to days. The page's own decisions block is not changed (the pin holds it). |

## Gaps found before any file (from the section as drawn on the fixture)

| # | Where | The gap | What was done |
|---:|---|---|---|
| 1 | "A region hour by hour", the charts | Hours are in UTC, as the file writes them; the reader's storm is in local time. The contract gives each region's time zone only in `index.json`. | Left as it is, said on the hover "How a figure here is formed". When `index.json` is on the site: draw the charts in the region's own time and name the zone under them (one change in `site/app/events/WholeCountry.tsx`, with a test). |
| 2 | "Each region across the event", the highest hour | The baseline beside it is the baseline at that same hour, not the baseline days' own highest hour, which is what the page's older sections use. A reader setting the two side by side sees two different percents for nearly the same ground. | Said on the head's hover. For Samuel's ruling in session 8410's report (the default: the file's hourly baseline). |
| 3 | The pair table | The file gives one flow a pair (the first side's report where held, else the second's); the two sides' reports and their gap are in the trade files, not in the event file. A reader cannot see here how far the two sides disagree during the storm. | Not a fault of the page: the event file does not hold it. One line for the data machine if the first read on real files shows a pair whose direction turns with the side read. |
