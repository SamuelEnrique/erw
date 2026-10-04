# Session 100 report: New York and SPP

**Done, on `wip/100-reserves`, nothing deployed and no page changed.** The approved pull was made for SPP (159,768 rows of the 300,000 ceiling, USD 0). New York publishes no hourly reserve quantity, so nothing was pulled for it and I say what it does publish. Each product's duration rule is now read from the operator's own document, with sections cited. The fleet-limited estimate was run for both. **SPP is fit to open on the model's side; New York is not yet.**

## To make it live

```bash
# Nothing below was run. No preview address: this session changed no page.

# 1. THE TABLE into the warehouse's records. It exists only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/100-reserves && git merge origin/main
python warehouse/validate/erw_validate.py warehouse/output/spp_as_quantities.csv          # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "spp_as_quantities" write
python warehouse/redivis/upload.py --tables spp_as_quantities               # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold (as spp_as_prices is):
#      - spp_as_quantities
#    then commit coverage.csv, sources.csv, docs/coverage.md and the live set.

# 2. THE VERIFIED RULES onto the battery page's notes (after the freeze: the live battery page shows these notes in
#    its internal view). In warehouse/derived/battery_stack.py replace SPP_ASSUMED and NYISO_ASSUMED with the
#    citations of docs/methods/reserve_quantities_nyiso_spp.md, then:
python warehouse/lock.py run --task "battery stack review" --minutes 30 -- <the venv's python> warehouse/derived/battery_stack.py --review-only --snapshot
#    and commit site/data/battery_stack_review.json.

# 3. TO OPEN SPP on the battery page, after your ruling on SPP's terms (point 2 below): in site/lib/batterystack.ts
#    set spp's `ready` to true and take off `review` and `why`; a deploy with its snapshots.

# 4. TO KEEP THE QUANTITIES CURRENT: one line for spp_as_quantities.py beside spp_as_prices.py wherever that runs
#    (it is run by hand today). One request a day.
```

**Read these five first:**

1. **Both duration assumptions of session 86 are now the operators' own rules, with one exception.**
   - **SPP: 60 minutes for all four modeled products.** Integrated Marketplace Protocols, Revision 119 (latest revision 7/17/2026), section 4.2.2, Offer Submittal: a regulation resource must be "capable of deploying 100% of cleared Regulation-Up or cleared Regulation-Down within the Regulation Response Time for a continuous duration of 60 minutes" (item (a)(ii)); a spin qualified resource, "100% of cleared Spinning Reserve and/or cleared online Supplemental Reserve within the Contingency Reserve Deployment Period for a continuous duration of 60 minutes" (item (b)(i)); supplemental from off line the same (item (c)(i)). Session 86 had found only the 2016 and 2017 copies; the active version is in SPP's document library.
   - **New York, operating reserves: one hour.** NYISO's Market Administration and Control Area Services Tariff, section 4.4.2.1 (Real-Time Dispatch, Overview), effective 9/16/2026: "The Beginning Energy Level of an Energy Storage Resource ... will be used to ensure that Operating Reserves scheduled from the Resource can be sustained for one hour if the Operating Reserves are converted to Energy."
   - **New York, regulation: the tariff states no time.** Rate Schedule 3, section 15.3.2.1(e): "The ISO may reduce the real-time Regulation Capacity (in MW) from an Energy Storage Resource ... to account for the Energy Level of such Resource." A discretion, not a number. The model's one hour for New York's regulation stays an assumption.
2. **SPP is fit to open as far as the model goes; its terms are the open question, and it is yours.** The fleet limit takes nothing off 2024, a tenth of a percent off 2025 and 2 to 3 percent off 2026, when SPP's battery fleet (490 MW) reached the size of its regulation market (about 480 MW each way). What I cannot settle: SPP's terms give permission to copy "EXCEPT when such materials will be used, in whole or in part, within a commercial publication". The reserve prices from session 85 carry the same sentence. Whether the ERW's site is a commercial publication is a person's ruling.
3. **New York is not fit to open yet.** Regulation is 28 to 73 percent of the model's New York figure. Its duration is the assumption the tariff does not settle, and its quantity is not held: the tariff says NYISO "shall establish and post a target level of Regulation Service for each hour" (section 15.3.7), and I did not find where. Four addresses under nyiso.com answered "not found", and its ancillary services page lists its documents by script. With that one document the estimate can be finished; a person with a browser will find it in minutes.
4. **New York publishes no hourly reserve quantity, so there is no New York table.** I read every report in its public market data menu (59). There are prices for day-ahead ancillary services and no report of the MW scheduled; the daily energy report has none; the bid data hold offers, not awards, three months late and masked. What NYISO publishes is its requirement: 655 MW of 10-minute spinning reserve for the control area, and the rest in the method note. I used that one figure, as a constant and named as a requirement, for the spinning reserve cap, and wrote no hourly rows: a requirement repeated 18,000 times would look like data.
5. **In New York the spinning reserve cap never binds.** The fleet is 213.5 to 268.7 MW against a requirement of 655 MW. So for New York the fleet-limited figure depends only on regulation. I give two bounds and call neither the estimate: regulation not capped (the page's price-taker), and no regulation sold. At 4 hours, day-ahead: USD 138.43 and 112.50 per kW in 2025; 159.14 and 105.34 in 2026 to 4 October.

Energy Research Warehouse (ERW), session 100, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 11:23 to 12:00 UTC, unattended. **Model spend: USD 0.00.** One pull, the one named, at USD 0: for SPP, 646 requests to `portal.spp.org` for the table (three folder lists, the 2024 archive, 642 daily files) and about 65 more while finding the report (most of them names that do not exist), and its document library on `spp.org`; for New York, about 20 requests to `mis.nyiso.com`, `nyiso.com` and NYISO's tariff viewer, which ended in documents and no table. No model call, no force push, no deploy. The data lock was held for the pull (15 minutes) and is free.

## The licenses

- **SPP: public, with citation.** Its terms (`https://www.spp.org/terms-conditions/`, as session 85 read and recorded them today): "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication". The table is public as `spp_as_prices` is, under the same sentence and the same open question (point 2).
- **NYISO: nothing was written.** The two documents read (its tariff and its locational reserve requirements) are quoted in the method note with their addresses; a few sentences of a public tariff, cited, are not a table.

## The pull: `spp_as_quantities`

159,768 rows; passes the validator (exit 0). `warehouse/connectors/spp_as_quantities.py`, on the framework the reserve price connectors share (`iso_as_common.py`: the pause is asked before any request; whole days only; the raw files and their manifest kept). The framework now takes a table's own unit and ceiling; the other reserve connectors pass neither and keep USD per MW-hour and 500,000, and a test holds that.

- **Source:** SPP's "Day-Ahead Market Clearing" files, one a day: the MW cleared of Regulation-Up, Regulation-Down, Spinning, Supplemental, Ramp-Up, Ramp-Down and Uncertainty reserve, by hour.
- **Rows:** `spp:SPP` from 2024-09-01 (128,352 rows) and `spp:SWPW` from 2026-04-01 (31,416), the same two rows the price table holds. No day was left out.
- **An older layout:** the files before April 2026 have no BAA column and one row an hour, the system's. My first run stopped on it (the connector refuses a layout it does not know and writes nothing); the connector now reads those rows as `spp:SPP` and stops if such a file has more than one row an hour.

Means of the system row, MW: Regulation-Up 459, 489, 485 (2024, 2025, 2026); Regulation-Down 408, 436, 470; Spinning 686, 665, 680; Supplemental 720, 702, 698.

## The fleet-limited estimate

`warehouse/analysis/battery_fleet_limited_review.py`, session 74's method: in each hour one battery's award of a product, per MW of its power, is at most the MW procured over the grid's operating battery MW of the month, and never above 1. The prices and the program are the page's. It writes daily files under `warehouse/output/analysis_internal/` (not in git) and no table. A day on which no cap is under 1 is not solved twice.

**SPP,** 763 days (two left out for a price not held):

| | 2024, from September | 2025 | 2026, to 3 October |
|---|---|---|---|
| Days with a cap under 1 in some hour | 0 of 122 | 31 of 365 | 267 of 275 |
| Fleet-limited over price-taker, day-ahead, at 2, 4, 8 hours | 100.00 percent | 99.85, 99.86, 99.88 | 97.33, 97.78, 97.98 |
| The same with perfect foresight | 100.00 | 99.88, 99.89, 99.90 | 97.88, 98.20, 98.39 |
| 4 hours, day-ahead, USD per kW: price-taker, fleet-limited | 47.77, 47.77 | 162.59, 162.37 | 123.69, 120.94 |

The cap that binds is regulation's (its daily mean falls as low as 0.60). Spinning and supplemental reserve are bought in larger quantities than the fleet.

**New York,** 764 days:

| 4 hours, USD per kW | 2024, from September | 2025 | 2026, to 4 October |
|---|---|---|---|
| Day-ahead: regulation not capped, no regulation sold | 26.15, 21.82 | 138.43, 112.50 | 159.14, 105.34 |
| Perfect foresight: the same two | 30.73, 26.82 | 172.82, 150.22 | 177.17, 127.92 |

With no regulation sold the battery keeps 63 to 89 percent of the price-taker's figure across years, strategies and durations: the freed power goes to spinning reserve and energy.

## One more rule worth knowing, from SPP's protocols

For a storage resource, SPP's clearing counts "cleared Regulation-Up, Regulation-Down and cleared Contingency Reserve" against its state of charge "by 50% of the cleared product" (section 4.2.2.1, items (58)(a) and (59)(a)). The model holds a full hour of energy behind each MW, which is the qualification rule and stricter than the clearing's. So for SPP the model errs on the low side there.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session100.py` | 10 tests pass. The connector with no request, on files made for the test: a day with the BAA column; the older layout as the system's rows; an empty cell gives no row and its day is not written; a renamed column or hours of another day stop the run; the ceiling of 300,000, the unit, and that the other reserve connectors keep theirs. The caps: a quantity over the fleet, never above 1; no quantity held leaves the product uncapped and named; an hour without a quantity leaves the day out. The method note quotes each document with its section; and each quotation is in the document as saved on this machine. The table as built: under its ceiling, whole days, no negative quantity, the citation in its header |
| Sessions 85's and 89's tests (the reserve connectors, the pause) with it | 71 tests pass |
| The validator on the table | exit 0 |
| The analysis's own checks | every solution passes the page's `check_day`, and no award passes its cap, on every day, strategy and duration |

No site build this session: no file of the site changed.

## Errors and decisions

- **Error, mine:** the first run of the pull stopped on the 2024 files' layout. Nothing had been written. Fixed and run again; the 2024 archive was read from the saved copy, not requested twice.
- **Error, mine, caught before the commit:** the method note first said regulation was "11 to 36 percent" of New York's figure. That is what the battery loses when it sells none; regulation's own share is 28 to 73 percent. Corrected from the daily file.
- **Decision: no hourly rows for New York.** Above, point 4.
- **Decision: a separate method note,** not a section of `battery_stack.md`: that note is one of the four methods pages a live tool links to, and changing it would change a live page at the next deploy.
- **Decision: the page's notes are not updated tonight.** The review grids' notes are in a file the live battery page reads in its internal view. The exact edit is in "To make it live", step 2.

## For Samuel

1. **SPP's terms and "a commercial publication"** (point 2): the ruling that decides whether SPP opens, and whether its two reserve tables stay public.
2. **NYISO's posted regulation targets** (point 3): the one document that finishes New York.
3. **Not in any cloud:** the table is only in `warehouse/output` on this machine until step 1 is run; the tariff, the protocols and the requirements document are saved under `runs/session100/` on this machine only.
