# Session 512 report: DOE's Loan Programs Office portfolio, probed, not pulled

21 October 2026, from 19:36 UTC, on lab-desktop (the data machine), the third session of `queue/done/026-night-21-october-sources.md`. Model spend USD 0.

## Read these first

- **Not pulled: DOE publishes no file of the portfolio, only a map application.**
  - `www.energy.gov/lpo/portfolio-projects` now redirects to `/edf/edf-projects`: the office is renamed the Office of Energy Dominance Financing (EDF), and the page was last updated on 5 October 2026.
  - The page holds no project in its HTML. It embeds an H5P iframe ("LPO Portfolio Projects Map") of `https://lpoapps.loanprograms.energy.gov`, which is a script application (GraphiteGTC, `LPOProjectMap.min.js`) with an undocumented internal API.
  - As with OE-417 in session 508, no connector was built on an application's internal calls.
- **Robots and terms**:
  - `www.energy.gov/robots.txt` disallows neither `/lpo` nor `/edf`.
  - `lpoapps.loanprograms.energy.gov` has no robots file (404).
  - DOE's terms are already recorded: record 54, "Government information at DOE websites is in the public domain". No new read was needed.
- **A fault of the host, not worked around**: `lpoapps.loanprograms.energy.gov` fails Python's certificate check ("unable to get local issuer certificate": its intermediate certificate is not served). Verification was not turned off. Windows' own trust store (`truststore`, already installed) completes the chain, and the front page was read that way.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.energy.gov | 2 of 10 | robots file; the portfolio page |
| lpoapps.loanprograms.energy.gov | 3 of 10 | robots file (one failed on the certificate, one read with Windows' curl: 404); the front page |

## For Samuel's ruling

- Whether EDF's projects should be read from the map application's own data calls (undocumented, a script application's), or asked of DOE as a file (`LPO` contact), or left.

## Files

- New: this report.
