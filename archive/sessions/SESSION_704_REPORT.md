# Session 704 report: capacity on the All grids tab

22 October 2026, from 09:17 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-704` on `wip/704-allgrids` (cut from `wip/703-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 704. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **The capacity tables are internal, and the repository is public** (GitHub answers its address without a token). So no capacity price is written into the site's files.
  - `site/data/siting/capacity.json` (new) holds each market's newest delivery period, its auction, its unit and the zones it priced, and no price:
    - PJM BRA 2028/2029 (17 zones);
    - ISO-NE FCA 18 (system-wide only);
    - MISO PRA 2026/27 Spring 2027 (11 zones);
    - NYISO spot October 2026 (4 localities).
  - The tab draws "license needed" in place for every PJM, ISO-NE, MISO and NYISO row (session 408's rule). The hover gives the zone, the auction, the delivery period, the unit and the rule of conversion.
- **The figures are computed where the table is held**: `warehouse/derived/siting_page.py --internal FILE --rows ROWS` writes them outside the repository. Tonight's are in `runs/chain_050/capacity_internal.json` on this machine, not in git. For a load that runs every hour, in USD per MWh:
  - PJM RTO 13.54 (USD 325 per MW-day);
  - NYC 17.26, Long Island 13.88, G-J Locality and the rest of the state 8.22 (USD 12.60, 10.13 and 6.00 per kW-month);
  - ISO-NE system-wide 4.90 (USD 3.58 per kW-month);
  - MISO 0.32 in every zone (USD 7.61 per MW-day).
- **ERCOT, CAISO, SPP: "no capacity market"**, one line of why on hover. They count as zero in the all-in figure.
- **The interruptible profile (heavy industry): "not held"** outside those three grids. It pays capacity on its firm demand only, which its utility's interruptible tariff sets, and no such tariff is held.
- **The zone map** (`capacityZone`):
  - NYISO: N.Y.C. to NYC; LONGIL to LI; HUD VL, MILLWD and DUNWOD to the G-J Locality; the rest to NYCA.
  - MISO: the hubs to their local resource zones (Minnesota Z1, Illinois Z4, Indiana Z6, Michigan Z7, Arkansas Z8, Louisiana and Texas Z9, Mississippi Z10).
  - ISO-NE: the zone's own price where the newest auction priced it, else system-wide (FCA 18 priced none).
  - PJM: the one row to the RTO.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view).
2. The Capacity column: CAISO, ERCOT and SPP read "no capacity market"; ISO-NE, MISO, NYISO and PJM read "license needed". Hover "license needed" at "NYISO N.Y.C. (zone)": NYC, Spot 10/2026, 2026-10-01 to 2026-10-31, USD/kW-month, and the rule.
3. Choose Heavy industry: the four held grids read "not held" (the interruptible tariff).
4. On this machine, `runs/chain_050/capacity_internal.json` holds the computed figures.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session704` to `700` | 0 | 38 tests OK, 1 skip (the file holds no price; the conversion on a fixture; the zone map; all-in follows capacity) |
| `siting_page.py --internal` | 0 | 29 rows computed, outside the repository |
| built and checked on 705's branch | 0 | see 705's report |

## The landing

Landed with sessions 700 to 705 in one push at 10:09 UTC (`b25a5c66`); the gate, the snapshots (0 differences) and the deletion of the merged branches are in `SESSION_705_REPORT.md`, "The landing".

## Decisions made without you

1. **No internal price in the public repository.** The prompt's "computed, keyed, drawn as license needed": computed by the builder where the table is held; drawn as "license needed" in place, with no `data-check`, so the value checker passes it by as it passes `Num`'s held figures.
2. **"Latest cleared" is the newest delivery period each market has cleared**, forward where the auction is forward: PJM 2028/29, ISO-NE 2027/28.
3. **A load is taken to run at the grid's peak**: no peak hours of these four grids are held. The rule is in the tip.
4. **The MISO zone map** is the zones' published geography (a hub to the zone it lies in), written in `lib/siting.ts`. It changes no figure on the page while MISO is paused and the table internal.

## For Samuel's ruling

- Whether any capacity figure may be shown. NYISO's spot rows are marked public row by row in the table (`x_license`), but NYISO's prices are license-held since 20 October 2026.
- Whether the computed figures belong in a private place the site can read (the Supabase internal view, say), so a reviewer could see them under the internal cookie.

## Files

- Changed: `site/lib/siting.ts` (`CapFile`, `capacityZone`, `capacityCell`, `CAPACITY_RULE`; `allIn` carries the cell's words), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`CapTd`, `Held`), `site/scripts/siting-files.mjs` (`capzones`), `warehouse/derived/siting_page.py` (`capacity.json`, `--internal`), `tests/test_session702.py` (the all-in words).
- New: `site/data/siting/capacity.json`, `tests/test_session704.py`, this report.
