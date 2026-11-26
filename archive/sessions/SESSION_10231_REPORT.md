# Session 10231 report (chain 710, part D, the old laptop, 26 November 2026)

The signature explorers (platform tool 5) audited as a hostile expert would: `docs/reviews/explore-model-audit-2026-11-26.md` and its folder of evidence.

## What was done

- The arithmetic is right in all three explorers. Peak premium: every row of HB_HUBAVG 2015 to 2025 restated from ERCOT's 15-minute prices (308 of 308 annual, 3,696 of 3,696 monthly) and the default view's 64 figures as drawn by the page's own code, 64 of 64. The ERCOT tab of `/prices` (where `/explorer/ercot-peak-premium` redirects): 30 of 30, and it agrees with `/explore` on the 29 figures they share. Demand growth: 94 of 94. Interconnection: 201 of 212; the 11 others are rows whose input pull this machine does not hold (a data request).
- The peak premium with one rule changed at a time: block hours, midday hours, means, the median of daily gaps, load weighting, day-ahead, weekdays and holidays, the clock-change days, summer, constant dollars, the traded block. The thesis's direction holds under every rule; its 2025 size runs from 9.59 to 22.38.
- Seven findings: three Moderate (the dollars not said; two medians read as a typical day; EIA's estimates on the demand explorer), three Low, one Very low. Seven words branches for landing, one figure branch for ruling.

## Decisions made without you

- The GDP price index the forecast tool already holds (`site/data/forecast/deflator.json`) was used to size constant dollars; no CPI is held.
- Finding 6 was first found on 16 November and left open because the file is shared; no sibling session edits it tonight, so its words fix was made here and credited to that read.
- The demand explorer's two findings (4, 5) carry tonight's consumption audit's findings 1 and 7 onto the explorer, which that audit's branches do not touch; their figures stay that audit's rulings, not repeated.
- The seven words branches merge without a conflict, so no `wip/audit-explore-words` was pushed.
- The importer tests (sessions 1496, 2200 to 2204, 7507, 7508, 7517) were run once, on a local merge of the seven words branches (87 passed, none skipped), not per branch.

## For Samuel's ruling

- Finding 1, `wip/audit-explore-2` (`90dcef513`), not for landing: write the peak premium's earlier years in 2025 dollars. 2015's figures move by x1.3251 (peak-block IQR 7.64 to 10.12, median 20.49 to 27.15, 99.9th percentile 583.96 to 773.82); ratios and counts do not move. Default: left as it is.

## Landing (words only)

- `wip/audit-explore-1` (`14b2fa2d0`), `-3` (`0588a2d65`), `-4` (`118957ed5`), `-5` (`37239e2d7`), `-6` (`d6565b9a7`), `-7` (`c1cd7bc6d`), `-8` (`15f76f034`): each from origin/main `e9e70cf12`, each drawn and read (pass; branch 8 is a note only); they merge together cleanly.

## Data request

- From the CAISO, ERCOT and SPP pulls the 16 November build of `iso_queue_statistics` read: the interconnection default view's figures beside the table's rows, and which CAISO position of entry year 2019 changed status since the pull of 26 September.

## Needs the key

- Nothing.

## Problems

- None of the hard rules was broken to my knowledge. No heredoc, no inline code, every script under `runs/c10231/` run by name; TMP and TEMP set under `runs/`; no build, no server, no browser, no live service, no web read, spend USD 0.
