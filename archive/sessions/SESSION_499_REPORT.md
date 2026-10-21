# Session 499 report: BLS energy price indexes, probed, refused by the robots file

21 October 2026, from 18:17 UTC, on lab-desktop (the data machine), a public source probed while the daily run held the data lock. Model spend USD 0.

## Read these first

- **Not pulled: the robots file forbids it.** The Bureau of Labor Statistics' consumer price indexes for electricity, utility gas, gasoline, energy and all items would serve as deflators. BLS's API v1 needs no key.
  - But `api.bls.gov/robots.txt` reads `User-agent: * / Disallow: /`: every path closed to every automated agent.
  - `www.bls.gov/robots.txt` answered 403 (Access Denied).
  - No request was made to the API.
- The ERW holds no BLS key, and BLS's API v2 key is a person's sign-up. The robots file would stand either way.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.bls.gov | 1 | robots file (Disallow: /) |
| www.bls.gov | 1 | robots file (403) |

## For Samuel's ruling

- Whether BLS's price indexes are wanted, by another route a person can approve (BLS's own download pages, if their robots file allows a reader), or not at all.

## Files

- New: this report.
