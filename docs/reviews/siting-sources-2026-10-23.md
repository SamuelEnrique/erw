# The siting gap sources, probed (session 666)

Energy Research Warehouse (ERW), session 666 (chain 043, run on 22 October 2026 UTC), for Samuel and the code machine's All grids tab. Five publishers' robots files and terms read, with 15 of the 16 requests the session allowed; nothing pulled, no table written. The code machine's `docs/reviews/siting-gaps.md` was on no branch when this was written, so the gaps are the chain file's: large-load tariffs by utility, utility service territories, substations and transmission lines, connection durations, reserve margins.

Every request is in `runs/s666/probe.csv` on the data machine, and each body under `runs/license_reads/s666/` (not in git). The terms reads are in `warehouse/metadata/license_reads.csv` (records 88 to 90).

## The verdicts

| Gap | Publisher and file | Robots file | Terms, as read | ERW verdict | Shape | Next session's ceiling |
|---|---|---|---|---|---|---|
| Utility service territories | EIA, Form EIA-861, `Service_Territory_2025.xlsx` in `f8612025.zip` (4,756,816 bytes) | allows `/electricity/data/eia861/`; disallows every `/archive/` path | public (record 1, EIA's copyright page) | public | entities | 0: the 2025 zip was saved on 21 October (`warehouse/raw/eia861/`) |
| Substations | HIFLD (DHS), Electric Substations | the hub's robots file answers (crawl delay 60 s) | not read: the HIFLD Open hub's front page answers HTTP 404 | not settled | (entities) | none: not pulled |
| Transmission lines | HIFLD (DHS), Electric Power Transmission Lines | as above | as above | not settled | (entities) | none: not pulled |
| Large-load tariffs | OpenEI, the Utility Rate Database (API `api.openei.org/utility_rates`) | allows the wiki; disallows the bulk file `/apps/USURDB/download/usurdb.csv` | "Content is available under Creative Commons Zero unless otherwise noted." | public | series | 400, with an API key (`OPENEI_API_KEY` is not in this machine's `.env`) |
| Reserve margins | NERC, the Long-Term Reliability Assessment | allows every path; content signals `search=yes, ai-train=no, use=reference` | not read: `/terms-of-use-policy` (linked from the home page) loads its text by script; the page served holds only "Copyright 2026 North American Electric Reliability Corporation. All rights reserved." | not settled | (series) | none: not pulled |
| Connection durations | Berkeley Lab, Queued Up 2026 data file (15,571,236 bytes by its headers) | allows `/sites/default/files/` | CC BY 4.0 (the table's header, record 14) | public | derived from the table held | 0: `lbnl_interconnection_queue` is held |

## What each finding means

- **EIA-861's service territories** are ready to write from the saved zip, with no request. EIA's robots file disallows `/archive/`, the folder of EIA-861's earlier years' zips (`archive/zip/f861<year>.zip`), which `eia861_sales.py --year` and `eia861m_sales.py` may ask for: a question for the owner, not changed here.
- **HIFLD Open no longer answers** at `hifld-geoplatform.hub.arcgis.com` (its front page: "Not Found. Redirecting to /404"). One search of ArcGIS Online's catalogue (`runs/license_reads/s666/10_*`) found the layers only as copies made by others: an archive of the transmission lines by Esri's Federal User Community, "Electric Retail Service Territories" copies carrying HIFLD's own line "None (Public Use)" (NBAM_Org; a 2025 HIFLD Open copy by `layermanager`), and substations clipped by states, counties and private users. None is the publisher's own, so the ERW has no source it can cite for substations or transmission lines, and sessions 668 and 669 write nothing. A guess at EIA's own ArcGIS organization found no layer (record 13 of the probe); whether EIA's Energy Atlas republishes these layers was not read.
- **OpenEI's rates are public (CC0)**, by the API only: its robots file refuses the bulk CSV. The API needs a key from the NREL (now NLR) developer network, which this machine does not hold.
- **NERC's terms could not be read**, so the reserve margins are not pulled; session 672 does its second half only.
- **Queued Up** needs no request: the table is held, and its derived durations are session 671's.

## For Samuel

- **An OpenEI API key** (`OPENEI_API_KEY` in this machine's `.env`), for session 670's pull.
- **HIFLD's successor**, if there is one the owner knows of (a DHS or DOE page that publishes substations and transmission lines today), or a ruling on the Esri archive copy of the transmission lines.
- **NERC's terms**, read in a browser: whether the LTRA's tables may be stored and republished.
- **EIA's `/archive/` rule** against the two EIA-861 connectors' earlier years.
