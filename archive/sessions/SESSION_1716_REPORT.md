# Session 1716 report: AccessLint on the last of the route check's pages

Energy Research Warehouse (ERW), session 1716, chain 191, samueloldlaptop, 6 November 2026, 18:06 to 18:12 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. The gate's kept build (`cfe6575dc`), in the internal view.

## What it did

- **16 more pages**: three hub price pages (MISO, SPP, NYISO), one more event page (`/events/ercot-heat-2023`), and twelve methods pages. With sessions 1504, 1524, 1586 and 1687, AccessLint has read about 115 pages of the 225 in the route check. The rest are other addresses of the same pages and further methods pages.
- **No real fault.** The findings are scrolling regions: the event page's shared section, and `article > pre` on four methods pages. One methods page's `pre`, read 7 seconds after load, is a focusable region named "Code", marked by `ScrollRegions` as chain 189 found for the rest.
- The browser and the server were stopped.

## Decisions made without you

- The AccessLint read stops here: the remaining pages share layouts already read, and AccessLint's only finding on them is the timing artifact.

## For Samuel's ruling

- None.
