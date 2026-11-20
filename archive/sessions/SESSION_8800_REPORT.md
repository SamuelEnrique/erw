# Session 8800 report: the findings audit, parts A and B and the start of C (chain 506)

Energy Research Warehouse (ERW). 19 November 2026, samueloldlaptop (code role), unattended, from about 11:07 PST. Chain file: https://github.com/SamuelEnrique/erw/blob/main/queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md. Model spend: USD 0.00, no model call. Commits straight to main (documents and drafts only; no site page, no table).

## At the top

- **No public download exists to reproduce from.** The site's download (https://erw-flame.vercel.app/api/download?table=eia_fuel_spot_prices) answered HTTP 403 on 19 November 2026. Every reproduction ran on the ERW's own copy of the table: `warehouse/output` on this machine, or the table rebuilt from the ERW's archive bucket. The audit says so in each row. Every draft's "Reproduce" line still promises "the public downloads".
- **The archive cannot rebuild one table.** `ferc714_planning_area_forecasts` comes back with 11,934 of its 67,215 rows (one filing a forecast year instead of every filing). Its 47 drafts (forecasts and cross_family) are "not checked". Data request 30: https://github.com/SamuelEnrique/erw/blob/main/docs/state/data_requests_large_load.md
- **One draft withdrawn:** `tariff-min-contract-years` says 13 filings; the table, one run later than the draft, holds 14.

## What was done

- **Part A:** every draft listed (549 in 20 families; 364 of 19 November), with its tables and their license: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-audit-2026-11-19.md and its data folder https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/findings-audit-2026-11-19
- **Check 1, the sentence:** 56 sentences mended for the template's "was" after a plural and two lost words; 22 sentences whose "first year this measure counts" was untrue of the table (the script's own year window; the table holds earlier years) now say what is true. Six such mends were wrong (the earlier years were not full) and were put back in the next commit. Every printed figure was set against the sentence as rounded: all agree but two battery fleet drafts, where this machine's older EIA-860M copy differs within the draft's tolerance.
- **Check 2, the figure:** each `reproduce.py` run here; tables rebuilt from the archive bucket (37 whole, row counts equal to the warehouse's), or, for the hourly EIA-930 tables too large for this machine's memory, rebuilt for each draft with only the rows its script names. A split table that held no row, or a short rebuild, is "not checked", never a pass or a fail.
- **Check 3, the Stata file:** every do-file read against its Python (172 shapes, by three readers); all keep Samuel's three rules; 12 mended where their steps differed (empty years not printed as zero, a missing magnitude counted, two reshape names over Stata's 32 characters, a real zero dropped). The trade drafts whose do-file takes a percentile by Stata's rule were run again in Python with Stata's rule: the same figures in every year.
- **Check 4, the chart:** one template for all (`warehouse/analysis/findings/deep/builder.py`): the title names the subject, the finding is the line under it; the y axis carries the unit only. Looks not seen.
- **Part C begun:** about 57 drafts read against publishers by web search; hosts whose pages were opened: www.eia.gov and www.census.gov, robots files and terms read first (`hosts.csv` in the data folder).
- **Part E begun:** three second routes agree (US crude exports and the Netherlands from EIA's own table; data center construction from Census's adjusted rates).

## Decisions made without you

- Check 2 counts a run on the ERW's own copy of a table as a pass (the download refuses), and each row says which copy.
- A per-draft rebuild keeps the rows whose entity, region, node or ba the script names; a script that reads every row (the heat rates) was run on the whole table.
- Part C reads search results and cites the page they name; "seen in search results, page not opened" says where a page was not opened.

## For Samuel's ruling

- **The chart's title** names the subject, not the finding, on all 549 charts. Default: left as drawn.
- **The PNGs keep the old words** of the 78 mended sentences (the line under the title is drawn into the image). Default: not redrawn.
- **"Reproduce" promises a public download** that answers 403, in every draft. Default: left.

## Needs the key

- Nothing.
