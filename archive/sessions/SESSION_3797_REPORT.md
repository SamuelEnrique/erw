# Session 3797 report: the waiting rows, re-checked once each

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 16:50 to 16:53 UTC. Opus 5.5. Model spend USD 0. Requests: 1 (adminrules.utah.gov's robots file).

## Read these first

- **ERCOT's NP9-83-M:** not asked. The file says from 1 December only, and today is 12 November. Chain 212's session 3782 read the pages today: not posted.
- **Utah's R746-318:** not read.
  - adminrules.utah.gov has no robots file (404, a page of its own app). The site is a script-built application ("Utah Office of Administrative Rules", Next.js), and the rule's text is not at an address a single request can read.
  - The rule stays known from the PSC's notice (session 3784) and the statute's clocks, which are held (session 3783).
- **`iso_queue_snapshot_summary`'s live-set load: nothing to load.** Read at 17:45 UTC:
  - the table is in `warehouse/supabase/live_set.yaml` only under `catalogue_hold` (chain 157's "not yet on Redivis's public draft"), and no `full`, `recent` or `select` rule names it, so the live set never held its rows;
  - the data machine's `dm_live_set` loaded its own six tables at 17:00 and named it only among the catalogue's holds;
  - the All grids tab reads it from `site/data/siting/headroom.json`, not from Supabase.
  - Chain 211's carried item ("listed but held 0 rows live") read the catalogue hold as a load rule. The table leaves the hold when it is on Redivis's public draft.
- **The rest wait on a ruling** (chain 212's note): FERC-714's verdict, the PUCT's permission, ERCOT's API key, SPP's license.

## Decisions made without you

- **No second request to a script-built site** to look for a hidden data address. The rule waits until a plain copy is named.

## For Samuel's ruling

- None.
