# Session 8610 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part C: the region tabs made ready for the form the data machine announced in answer to data request 551. About 16:02 to 16:13 UTC. Branch `wip/8602-grid-regions` at `0e7bc3289` (landing request row 42, its head moved). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant. On today's files a reader sees one more line in the regions' decisions fold and nothing else.
- **A decision of mine you may want to rule on: net load where no solar or wind was ever reported.** Net load is demand less wind and solar. New York's authorities have never reported solar to EIA; the Carolinas', Florida's and the Southeast's have never reported wind. The data machine will now write those as blank, not zero. By the seven grids' rule a blank makes the whole net load blank, so four regions would lose their year-after-year block. I made a region's net load demand less what is reported, and the page says so in a line. The figures are the ones drawn today. The seven grids' rule is not changed.

## What was done

- **The form.** A source no authority of a region has ever printed is `null` all through its mix file, and named in a new key (`sources_not_printed`). It is on the data machine's branch, not on main.
- **The page, made ready:**
  - in the latest hour's table and the table of shares such a source is a blank row ("not held"), with why on hover; it was 0 MW, 0.0 percent and 0 MWh;
  - the charts draw only what is held;
  - net load as above, with its line.
- **Tried end to end** on a copy of New York's real file with coal, solar and storage set to null (never shipped; the real file put back and checked byte for byte): the page, the browser check and the replication.
- **The replication** reads the same form by the same rule, and counts two more checks a region.

## What was checked

- `tests/test_session8610.py` 14 passed; with the six earlier sessions' own, 136 passed. Type check and lint clean.
- On a build of the real files: `check-grid-regions.mjs` 25 of 25. The page read again and the replication rerun: 1,375 of 1,375.
- On the trial file: New York 117 of 117; its three sources "not held" in both tables; "net load here is demand less wind".

## What to review (after row 42 and the data machine's files land; in the internal view)

1. `https://erw-flame.vercel.app/grid?region=ny`: Coal, Solar and Storage read "not held" in the first table; rest the mouse on one.
2. Same page, "Year after year": the line under the table says net load is demand less wind.
3. `https://erw-flame.vercel.app/grid?region=car`: Wind reads "not held"; the line says demand less solar.

## Not as the chain expected

- The new form was not on main, so it was tried on a copy made by hand from a real file. When the real files land, the check has a line that reads them.
- One earlier test of mine counted a phrase twice in a file and now finds it three times; updated with the reason.

## Decisions made without you

- Net load for a region with a never-reported wind or solar: demand less the one that is reported (above).
- A blank source's row stands after the held ones in the table of shares, not among the zeros.
- The words of the hover: "No balancing authority of New York has reported solar to EIA in any hour held since July 2018, so the region's file holds none. It is blank, not zero."

## Needs the key

- Nothing.

## For Samuel's ruling

- **Net load where a source was never reported** (above). Default taken: demand less what is reported, said on the page. The other choice: the block blank for New York, the Carolinas, Florida and the Southeast.
