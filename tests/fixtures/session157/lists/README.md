# Saved real list pages for tests/test_session157_refresh.py

Five responses of the regulators' own open lists, exactly as the trial of the daily refresh step saved them on
8 October 2026 (UTC), whole and not trimmed (the largest is 30 KB). Nothing here is made up. Each was a plain request
with the contact string "ERW research project, github.com/SamuelEnrique/erw" as the User-Agent.

| File | The list | Asked at (UTC) |
|---|---|---|
| `tx_dockets_large_load.html` | Public Utility Commission of Texas, the Interchange docket search by case style, "large load": `https://interchange.puc.texas.gov/search/dockets/?UtilityType=A&Description=large%20load&ItemsPerPage=200` | 2026-10-08T08:55:38Z |
| `tx_filings_60332.html` | The Interchange filing list of docket 60332: `https://interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber=60332&ItemMatch=Equal&DocumentType=ALL&SortOrder=Ascending` | 2026-10-08T08:55:37Z |
| `ca_decisions_A2411007.html` | California Public Utilities Commission, the decisions list of Application 24-11-007: `https://apps.cpuc.ca.gov/apex/f?p=401:59::::RP,57,RIR:P5_PROCEEDING_SELECT:A2411007` | 2026-10-08T08:55:57Z |
| `va_cases_large-load.json` | Virginia State Corporation Commission, the docket search's case list, caption holding "large-load" (the lower-case path of `GetCasesEstDate`) | 2026-10-08T08:57:16Z |
| `va_docs_PUR-2026-00131.json` | The docket search's document list of case PUR-2026-00131 (matter 147127; the lower-case path of `GetDocuments`) | 2026-10-08T08:57:40Z |

The trial's own copies, with the manifest (status, bytes, sha256 and time of every request), are under
`runs/session157/refresh_trial/raw/policy_monitor_refresh/` on the data machine (not in git). Git may change a
file's line endings on checkout; the readers do not depend on them.

Terms, as `warehouse/config/policy_monitor_feeds.json` quotes them: Texas, "all PUCT content is protected by federal
copyright laws" (its rows are internal; these two pages hold a docket search and a filing list, facts of the public
record, kept here only so that the readers are tested on the real markup); California, "It may be distributed or
copied as permitted by law."; Virginia, "Permission is granted to make fair use of the contents of the SCC website."
