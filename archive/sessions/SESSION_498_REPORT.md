# Session 498 report: DOE's OE-417 disturbance reports, probed, not pulled

21 October 2026, from 18:16 UTC, on lab-desktop (the data machine), a public source probed while the daily run held the data lock (the owner's instruction of 21 October: "probe another public source rather than idle"). Model spend USD 0.

## Read these first

- **Not pulled: no file to pull.** DOE's Form OE-417 (electric emergency incidents and disturbances: major outages by event) was published as annual summaries at `www.oe.netl.doe.gov`, which no longer resolves (a name error).
  - DOE's page on energy.gov (`/ceser/electric-disturbance-events-oe-417`) answers 404; energy.gov's robots file allows it.
  - The form's new site, `doe417.pnnl.gov`, is a JavaScript application (its robots address returns the application's page), with no published file found.
  - A web search found no current address for the summaries.
- Nothing was written, and no terms page was read: there was nothing to pull.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.oe.netl.doe.gov | 1 | robots file (the name does not resolve) |
| doe417.pnnl.gov | 1 | robots file (the application's page) |
| www.energy.gov | 2 | robots file (200), the OE-417 page (404) |

## For a later session

- Find OE-417's current public summaries (DOE CESER), by a person's pointer or a later search.

## Files

- New: this report.
