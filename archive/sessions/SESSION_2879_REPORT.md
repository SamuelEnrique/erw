# Session 2879 report: ERCOT's settlement point mapping

5 November 2026, 21:47 UTC, on lab-desktop (the data machine), chain 147, unattended, done while session 2863's landing gate ran. Model spend USD 0. Pulls: www.ercot.com 1 of 10 (the robots file).

## Read these first

- **Step stopped, as the chain says to.** ERCOT's robots file (read at 21:47 UTC) disallows `/misapp` and `/misdownload`, and names no AI agent. The Settlement Points List and Electrical Buses (NP4-160-SG) is posted only through ERCOT's MIS: the document list is `/misapp/servlets/IceDocListJsonWS`, the files `/misdownload/servlets/mirDownload`. ERCOT's public API (`api.ercot.com`) needs a subscription key the machine does not hold.
- **Held already:** `ercot_node_places` gives the load zone and county of 569 of the 873 resource nodes, from ERCOT's CDR (chain 049). `site/data/siting/nodes.json` carries them. No node's hub is held.

## For Samuel's ruling

- **NP4-160 by ERCOT's API with a key, or a ruling on `/misapp`.** This is the same question as session 2863's DAM list.

## Files

- New: this report.
- On the data machine only: `runs/s2879/`, `runs/license_reads/s2879/`.
