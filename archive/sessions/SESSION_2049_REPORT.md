# Session 2049 report: the utilities' capital spending (the SEC's XBRL frames): not taken

23 October 2026, from 19:06 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 1 request of 20 (www.sec.gov's robots file, asked in a call of its own).

## Read these first

- **The SEC refused the ERW's reader at its robots file:** HTTP 403, a "Request Rate Threshold Exceeded" page on the first request of the day: "Automated access to our sites must comply with SEC.gov's Privacy and Security Policy. Please visit www.sec.gov/developer for more developer resources and Fair Access guidelines." The SEC's fair access rule asks every automated reader to declare a company name and a contact email in its User-Agent; the ERW's reader declares the project's address and no email (read 190).
- **Nothing was asked after it:** under the chain's rules a host that refused the ERW's reader is not asked again without a ruling. www.sec.gov and data.sec.gov join that list (data.sec.gov's frames are served under the same policy).
- **No table written.** The owner's email was not put in a request header: it is used only to identify the owner, never sent to another service without the owner asking.
- **No other source was put in its place:** a substitute for the utilities' capital spending would be FERC's Form 1 (FERC's terms are a standing ruling) or a key-gated API, so this session stops here and says so.

## Decisions made without you

- **Stopped at the refusal,** with no second request to the SEC and no other User-Agent tried.

## For Samuel's ruling

- **A contact for the SEC's fair access rule:** an email address (a project or role address) the ERW may declare in its User-Agent to the SEC. With one, a later session can take the XBRL frames as the chain file asked (well under ten requests a second).

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (190), `docs/licenses.md`.
- On the data machine only: `runs/c059/s2049/`, `runs/license_reads/s2049/`.
