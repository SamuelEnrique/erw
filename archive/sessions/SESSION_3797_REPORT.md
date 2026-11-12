# Session 3797 report: the waiting rows, re-checked once each

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 16:50 to 16:53 UTC. Opus 5.5. Model spend USD 0. Requests: 1 (adminrules.utah.gov's robots file).

## Read these first

- **ERCOT's NP9-83-M:** not asked. The file says from 1 December only, and today is 12 November. Chain 212's session 3782 read the pages today: not posted.
- **Utah's R746-318:** not read.
  - adminrules.utah.gov has no robots file (404, a page of its own app). The site is a script-built application ("Utah Office of Administrative Rules", Next.js), and the rule's text is not at an address a single request can read.
  - The rule stays known from the PSC's notice (session 3784) and the statute's clocks, which are held (session 3783).
- **`iso_queue_snapshot_summary`'s live-set load:** read after the data machine's own run of 17:00 UTC, whose `dm_live_set` step runs the loader on main's live set. See session 3793's report.
- **The rest wait on a ruling** (chain 212's note): FERC-714's verdict, the PUCT's permission, ERCOT's API key, SPP's license.

## Decisions made without you

- **No second request to a script-built site** to look for a hidden data address. The rule waits until a plain copy is named.

## For Samuel's ruling

- None.
