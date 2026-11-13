# The held grids' prices in files the site serves by address

Energy Research Warehouse (ERW). Chain 245, session 4174, 13 November 2026, for Samuel's ruling. Nothing was deleted or changed: the list below is from `python scripts/held_public_files.py --markdown`, which deletes nothing and has no mode that does.

## What is the matter

- **NYISO and ISO-NE are held "license needed".** Their own terms ask for written permission (reads 1670 and 1672), and none is recorded. The price board's page masks their rows when it draws them (`holdRows` in `site/lib/board.ts` strips the figures).
- **The workbench's files are not masked.** They sit under `site/public/board/s/` (a row's whole history), `site/public/board/h/` (a hub's hourly prices) and `site/public/seller/prices/` (the seller tab's yearly prices).
- **The proxy serves them by address.** `site/proxy.ts` serves any file with an extension past the review curtain (every extension but `.rsc`, since session 5101). A visitor who types an address gets the prices.
- **They are also in the public GitHub repository,** and in its history.
- **Some are still written.** 110 of the files belong to board rows whose status in `site/data/board.json` is "ok". The page keeper marks them held since 4 October ("only the held file has it"), yet their newest point is 5 November, after the hold began on 21 October. `warehouse/derived/board_page.py` blanks a held grid's power-hub rows and its one reserves summary row. Its per-product reserve rows (32 files), battery rows (40), day-ahead/real-time rows (20), peak rows (12) and spark rows (6) still build files for those grids on the data machine.
- **The rest stay because of the keeper.** `warehouse/derived/page_keep.py` keeps a file only the old build has (its rules 4 and 5).

## What a ruling would change (not done)

- **Remove the files below** (a deletion, the owner's to order). Rewriting the repository's history is a further, separate decision.
- **In `board_page.py`:** build no series, hourly or seller file for a row of a held grid, in every group, as its power-hub branch already does (`ls.held_grids()`).
- **In `page_keep.py`:** never keep a file whose board row is of a held grid, so that a removal is not undone by the next run.
- **Or, instead:** bring `/board/`, `/seller/` and `/findings/` files under the curtain in `site/proxy.ts`, which leaves the repository's copies.
- **The test:** `tests/test_session4109_public_site.py` (`HeldGridFiles`) already fails on any new such file. Its fixture, `tests/fixtures/chain229_held_grid_public_files.txt`, lists these 138 and only shrinks.

## Default

- **Left as they are** until you rule (every page is in review).

## The files

138 files, 3,291,851 bytes, of the held grids ISO-NE, MISO, NYISO, PJM

| File | Bytes | Grid | What it is | Its board row |
|---|---:|---|---|---|
| `site/public/board/h/isone-h-internal-hub.json` | 243,263 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-connecticut.json` | 17,214 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-maine.json` | 17,221 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-nemassbost.json` | 17,216 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-newhampshire.json` | 17,252 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-rhodeisland.json` | 17,224 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-semass.json` | 17,233 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-vermont.json` | 17,228 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/isone-z-wcmass.json` | 17,228 | ISO-NE | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-capitl-as-price-dam-nsync10.json` | 105,380 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-capitl-as-price-dam-op30.json` | 100,180 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-capitl-as-price-dam-spin10.json` | 106,974 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-capitl.json` | 17,253 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-centrl.json` | 17,253 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-dunwod.json` | 17,277 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-genese.json` | 17,253 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-hud-vl-as-price-dam-nsync10.json` | 106,033 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-hud-vl-as-price-dam-op30.json` | 100,841 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-hud-vl-as-price-dam-spin10.json` | 107,546 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-hud-vl.json` | 17,233 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-longil-as-price-dam-nsync10.json` | 106,033 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-longil-as-price-dam-op30.json` | 100,841 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-longil-as-price-dam-spin10.json` | 107,546 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-longil.json` | 17,283 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-mhk-vl.json` | 17,235 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-millwd.json` | 17,241 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-n-y-c-as-price-dam-nsync10.json` | 108,152 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-n-y-c-as-price-dam-op30.json` | 101,211 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-n-y-c-as-price-dam-spin10.json` | 109,404 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-n-y-c.json` | 242,900 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-north.json` | 17,234 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/h/nyiso-nyca-as-price-dam-reg.json` | 113,884 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-west-as-price-dam-nsync10.json` | 100,242 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-west-as-price-dam-op30.json` | 100,178 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-west-as-price-dam-spin10.json` | 100,549 | NYISO | board hourly prices (the workbench) | ok |
| `site/public/board/h/nyiso-west.json` | 17,277 | NYISO | board hourly prices (the workbench) | no board row of this id |
| `site/public/board/s/isone-h-internal-hub-da-battery.json` | 7,833 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-da-minus-rt.json` | 8,449 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-da-offpeak.json` | 9,261 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-da-peak-less-off.json` | 6,303 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-da-peak.json` | 6,621 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-dark.json` | 445 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-heat.json` | 9,475 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-rt-battery.json` | 8,650 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-rt-offpeak.json` | 8,745 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-rt-peak-less-off.json` | 5,847 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-rt-peak.json` | 6,081 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-h-internal-hub-spark.json` | 9,528 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-connecticut-da-battery.json` | 635 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-connecticut-da-minus-rt.json` | 671 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-connecticut-rt-battery.json` | 610 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-maine-da-battery.json` | 618 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-maine-da-minus-rt.json` | 658 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-maine-rt-battery.json` | 599 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-nemassbost-da-battery.json` | 653 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-nemassbost-da-minus-rt.json` | 697 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-nemassbost-rt-battery.json` | 634 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-newhampshire-da-battery.json` | 628 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-newhampshire-da-minus-rt.json` | 683 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-newhampshire-rt-battery.json` | 609 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-rhodeisland-da-battery.json` | 634 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-rhodeisland-da-minus-rt.json` | 669 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-rhodeisland-rt-battery.json` | 612 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-semass-da-battery.json` | 636 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-semass-da-minus-rt.json` | 676 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-semass-rt-battery.json` | 609 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-vermont-da-battery.json` | 624 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-vermont-da-minus-rt.json` | 673 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-vermont-rt-battery.json` | 601 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-wcmass-da-battery.json` | 648 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-wcmass-da-minus-rt.json` | 696 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/isone-z-wcmass-rt-battery.json` | 623 | ISO-NE | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-as-price-dam-nsync10.json` | 8,485 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-as-price-dam-op30.json` | 8,437 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-as-price-dam-spin10.json` | 8,491 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-da-battery.json` | 616 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-da-minus-rt.json` | 677 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-capitl-rt-battery.json` | 713 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-centrl-da-battery.json` | 619 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-centrl-da-minus-rt.json` | 676 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-centrl-rt-battery.json` | 705 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-dunwod-da-battery.json` | 623 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-dunwod-da-minus-rt.json` | 682 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-dunwod-rt-battery.json` | 718 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-genese-da-battery.json` | 621 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-genese-da-minus-rt.json` | 678 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-genese-rt-battery.json` | 711 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-as-price-dam-nsync10.json` | 8,514 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-as-price-dam-op30.json` | 8,458 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-as-price-dam-spin10.json` | 8,549 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-da-battery.json` | 624 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-da-minus-rt.json` | 680 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-hud-vl-rt-battery.json` | 714 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-as-price-dam-nsync10.json` | 8,512 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-as-price-dam-op30.json` | 8,456 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-as-price-dam-spin10.json` | 8,545 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-da-battery.json` | 626 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-da-minus-rt.json` | 690 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-longil-rt-battery.json` | 726 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-mhk-vl-da-battery.json` | 625 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-mhk-vl-da-minus-rt.json` | 678 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-mhk-vl-rt-battery.json` | 723 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-millwd-da-battery.json` | 622 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-millwd-da-minus-rt.json` | 681 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-millwd-rt-battery.json` | 722 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-as-price-dam-nsync10.json` | 8,603 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-as-price-dam-op30.json` | 8,473 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-as-price-dam-spin10.json` | 8,634 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-da-battery.json` | 7,820 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-da-minus-rt.json` | 8,680 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-da-offpeak.json` | 9,209 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-da-peak-less-off.json` | 6,425 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-da-peak.json` | 6,568 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-dark.json` | 1,271 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-heat.json` | 35,289 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-rt-battery.json` | 9,031 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-rt-offpeak.json` | 8,986 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-rt-peak-less-off.json` | 6,081 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-rt-peak.json` | 6,270 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-n-y-c-spark.json` | 35,270 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-north-da-battery.json` | 613 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-north-da-minus-rt.json` | 673 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-north-rt-battery.json` | 702 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-nyca-as-price-dam-reg.json` | 8,924 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-as-price-dam-nsync10.json` | 8,445 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-as-price-dam-op30.json` | 8,432 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-as-price-dam-spin10.json` | 8,439 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-da-battery.json` | 615 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-da-minus-rt.json` | 668 | NYISO | board series (the workbench) | ok |
| `site/public/board/s/nyiso-west-rt-battery.json` | 706 | NYISO | board series (the workbench) | ok |
| `site/public/seller/prices/isone_2025.json` | 53,320 | ISO-NE | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2019.json` | 51,930 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2020.json` | 51,872 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2021.json` | 51,940 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2022.json` | 54,008 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2023.json` | 51,930 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2024.json` | 52,348 | NYISO | the seller tab's yearly prices | not a board file |
| `site/public/seller/prices/nyiso_2025.json` | 52,933 | NYISO | the seller tab's yearly prices | not a board file |
