# Sessions 1896 and 1897: the W45 Roundup's rows 74, 75, 76 and 65 (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, sessions 1896 and 1897, samueloldlaptop, unattended, Opus 5.5. Run by one agent in `erw-1896` on `wip/1896-periodicals`, cut from `wip/1894-periodicals` (`fb29d58e3`). About 01:15 to 01:40 UTC. All in `warehouse/news/roundup.py`; no table or Supabase write, no model call.

## What it did, with commits (branch head `c1e3d7ed9`, pushed)

- **Row 74 (1896), the Chart of the Week's source line**, which named the ERW three times and California ISO for a Lower 48 series: W45 now reads "Source: EIA-930, Hourly Electric Grid Monitor, hourly net generation by energy source, via the ERW's derived table storage_daily_cycle; data retrieved to 2026-11-05." Worked out when the Roundup writes; `common.source_line` and the stored chart records are unchanged, so `/research` keeps the old line (the data machine's). `15b78ecaa`.
- **Row 75 (1896), the chart pointer:** W45 prints no pointer, since no story of the week names exports; when one does, the sentence ends with the record's figure (": 3,675 kbbl/d in the week of 2026-10-26 to 2026-11-01, down 1,179 from 4,854 the week before."). `68a308011`.
- **Row 76 (1897), Next week:** "- **9 November 2026**: Corpus Christi Liquefaction Stage IV (FERC): comments on the draft EIS due 17:00 Eastern. ([source](...))". The NRC and BLM items of the same day stay (other agencies). Two expected lines in `tests/test_periodicals.py` changed from the two-sentence form. `ce7dd8b48`.
- **Row 65 (1897), why lines that name nothing the headline lacks: left open.** Over the six stored Roundups (W39 to W45) 30 of 41 why lines name nothing their headline lacks, all four of W45's among them; a Roundup-only rule would remove three lines in four, the decision session 1458 left to the owner for the Digest (560 of 784). Tests record the count (`5000d29ed`).
- Faults file states: `d50b80c46`, `c1e3d7ed9`.

## Tests

- `test_session1896`, `test_session1897`, 1882, 1894, 1895, `test_periodicals` and the 34 test files that load `roundup.py` or `brief.py`: 750 tests OK, 7 skipped (`runs/s1896/`).

## Decisions made without you

- Row 75 keeps the sentence's opening words, which `test_session806` pins.

## For Samuel's ruling

- Row 65: whether a why line that names nothing its headline lacks is dropped (three in four of the Roundup's would go), the same question as the Digest's of session 1458. Default kept: the lines stay.
