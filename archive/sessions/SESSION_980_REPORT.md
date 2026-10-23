# Session 980 report: the federal energy loans (not taken)

23 October 2026, from 13:52 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`. Model spend USD 0. Pulls: 4 requests of 15 (www.energy.gov's robots file, asked in a call of its own and read first: it disallows `/search/` and the user pages, not the office's; the portfolio page; the projects page; lpoapps.loanprograms.energy.gov's robots file, which failed before any answer).

## Read these first

- **No table written.** The Loan Programs Office is now the Office of Energy Dominance Financing (EDF): `https://www.energy.gov/lpo/portfolio-projects` and `https://www.energy.gov/edf/edf-projects` carry only the office's note on loan amounts ("Page last updated: October 5, 2026"); the project list itself is an embedded app at `https://lpoapps.loanprograms.energy.gov`.
- **That host fails TLS certificate verification** from this machine (`SSLCertVerificationError`), so even its robots file could not be read. The session did not turn verification off and asked nothing more of the host.

## Decisions made without you

- **Verification kept on:** a request that would need it turned off is not made; the next session that tries can check whether the host's certificate chain has been fixed (or whether this machine's certificate store lacks an intermediate) before anything else.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c055/s980/`, `runs/license_reads/s980/`.
