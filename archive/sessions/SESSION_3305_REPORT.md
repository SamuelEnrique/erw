# Session 3305 report (chain 200, session 9 of the plan, moved up): the SEC EDGAR Form D probe

lab-desktop, 6 November 2026, 20:14 to 20:20 UTC. Moved before the pages' build and the first landing because both locks were held by other windows; it needs neither.

## What was done

- **One request of ten:** `GET https://www.sec.gov/robots.txt` with the ERW's named user agent: HTTP 403, "Request Rate Threshold Exceeded", automated access must follow SEC.gov's policy and Fair Access guidelines. No further request: the refusal was of the user agent.
- **The fair-access policy and the Form D Data Sets read through a web search** (no request to sec.gov): 10 requests a second at most; a user agent with a company name and a contact email; quarterly ZIPs of structured Form D data; public domain (Data.gov's USA.gov label).
- **The estimate:** about 47 requests (robots, the data sets page, the table-definition PDF, one ZIP a quarter from 2015 Q1 to 2025 Q4), once a contact email is named for the user agent. Written in `docs/reviews/edgar-formd-probe-2026-11-06.md`.
- Nothing pulled; no source registered.

## Decisions made without you

- The owner's email was not put in a user agent (the session's rule): the probe stopped at one request instead.
- The search's words are cited as a search returned them; the table definitions and the earliest quarter are written as not confirmed.

## For Samuel's ruling

- Approve the Form D pull (about 47 requests) and name the contact email for its user agent, or decline.

## Cost

- No model call. Three web searches (Claude Code's own tool, not the owner's API key). USD 0.00 under the owner's key.
