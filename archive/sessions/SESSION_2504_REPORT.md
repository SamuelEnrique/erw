# Session 2504 report: the next file first; Kuwait not reachable, Oman's electricity taken instead (NCSI's Energy Statistics 2026), public

24 October 2026, from 17:28 UTC (chain 122's start) to about 17:41 UTC for the reads and the connector; the table written under the data lock at 18:19 UTC. On lab-desktop (the data machine), the first session of `queue/done/122-day-22-november-data-kuwait-cyprus-guyana-lesotho.md`, unattended. Precheck passed (`runs/c122/pre2504.out`). Model spend USD 0. Pulls: 9 requests of 15 (8 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Chain 122 was taken at 17:28 UTC by chain 121's agent** when chain 121 landed (`9998f2db`), under the owner's instruction for this run (run the file the queue step prints; stop only when it exits 3). The queue step ran in the detached queue worktree, since this machine's daily task held the data lock and was working in the main checkout.
- **The next file first:** `queue/next/123-day-23-november-data-barbados-belize-seychelles-cabo-verde.md`, sessions 2518 to 2531, machine data, committed alone in the queue worktree and pushed to main as `748c93ac` between two snapshots (both 402 on all 25 pages). Number 123 and sessions 2518 to 2531 were free on main and on every branch. Its rules are file 122's word for word. Its sources: Barbados, Belize, Seychelles and Cabo Verde, none in `sources.csv`, the connectors or the queue.
- **Kuwait is not taken:**
  - the ministry's www.mew.gov.kw fails the TLS handshake (unsafe legacy renegotiation, read 867);
  - the Central Statistical Bureau's robots file allows every path (read 868), but its site is Arabic only and its publications sit behind form postbacks (reads 869, 870).
- **Oman replaced it** (the ERW held no Omani source): the National Centre for Statistics and Information (NCSI), whose two hosts have no robots file (reads 871, 872). Its "Energy Statistics 2026, Fifth Edition - data 2025" (8.1 MB, last modified 8 July 2026) was fetched once; the fetch took over two minutes.
- **A new table, `ncsi_oman_electricity_annual`** (series, 126 rows, `power`), 2023 to 2025:
  - table 11: each governorate's production and distribution (GWh to MWh) and connections (thousands to a count);
  - table 12: production by source (diesel, gas, solar, wind, other), TWh to one decimal.
  - The bulletin prints table 11 twice; the second print must equal the first. Each year's production total must equal table 12's within 0.1 TWh, which also proves the columns' order. The governorates sum to the total within 0.1 GWh.
  - Written by run `20261024T181930Z`, validated (0 errors, 0 warnings), archived, held from the live set; public, so in the release package and the next draft.
- **Public, with the source named.** NCSI's home page: "The contents of this website are licensed under the Open Government Licence" of the Sultanate of Oman (read 873); the licence (read 874, in Arabic) allows use and redistribution for any purpose with the source named and states its compatibility with CC BY 4.0. Verdict: may be public.

## Cross-checks

- Production over `owid_ember_electricity_annual`'s demand for Oman: 1.00 in 2023, 1.00 in 2024, 0.965 in 2025. Production, TWh: 44.97, 49.13, 50.97; gas 41.2, 44.8, 44.5; solar 2.1, 2.3, 4.4.
- As printed: Al Batinah North's and South's distribution in 2023 (9,343.8 and 4,491.6 GWh) look swapped against 2024 and 2025 (4,837.3 and 10,291.5; 4,985.7 and 11,428.0). The table writes them as printed.

## Requests (9 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.mew.gov.kw/robots.txt | TLS handshake fails |
| 2 | www.csb.gov.kw/robots.txt | 200: every path allowed |
| 3 | the bureau's sitemap | 200: seven pages |
| 4 | the bureau's statistics page | 200: Arabic, postbacks |
| 5 | api.ncsi.gov.om/robots.txt | 404 |
| 6 | www.ncsi.gov.om/robots.txt | 404 |
| 7 | NCSI's home page | 200: the licence line |
| 8 | the Open Government Licence | 200 |
| 9 | the bulletin (the fetch) | 200, 8.1 MB |

Reads recorded: 867 to 874 (on this branch, after chain 121's landed 810 to 866). Three web searches found Kuwait's figures only in the press and NCSI's bulletin; they reached no publisher's host.

## Decisions made without you

- **Oman for Kuwait,** a Gulf grid the ERW did not hold.
- **Public** under the Open Government Licence, the bulletin's figures being the Public Services Regulatory Authority's, a government unit under the same licence.
- **The swapped-looking 2023 figures kept as printed.**

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/ncsi_oman_electricity.py`, `tests/test_session2504.py`, this report; `queue/next/123-...md` (on main).
- Changed: the registration; the metadata files; `docs/redivis/release-v1/`; the license record (reads 867 to 874, one verdict).
- On the data machine only: `runs/c122/s2504/`, `runs/c122/write_123.py`, `warehouse/raw/ncsi_oman_energy/`, `warehouse/output/ncsi_oman_electricity_annual.csv`.
