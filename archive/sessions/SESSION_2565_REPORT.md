# Session 2565 report: the licenses' forty-seventh round (INSD's open data licence: may be public; EBS needs written permission)

25 October 2026, about 00:48 to 00:50 UTC, on lab-desktop (the data machine), chain 126, unattended. Precheck passed on its second run (`runs/c126/pre2565b.out`; see below). Model spend USD 0. Pulls: 6 requests of 20.

## Read these first

- **The first precheck failed** (`runs/c126/pre2565.out`, 00:48:06 UTC): it was run from the worktree, where this machine's ledger file is not, and Supabase's copy of the cost ledger did not answer, so the day's spend could not be read. The script recorded the line as idle in `erw_health` and says the machine's one email follows 15 minutes later. Run again from the main checkout at 00:48:19 it passed (USD 0.00 spent today). If the email arrives, it is this.
- **`license_verdicts.csv` was read first.** This chain's sources' publishers already had theirs (EEC, ARSE, NBS, ABS, given in sessions 2560 to 2563); this round takes the other publishers the chain met with no verdict.
- **Two verdicts,** each sentence cut by code from the page as saved (`runs/c126/s2565/verdicts.py`):
  - **INSD (Burkina Faso)** (read 1075, its Accord de licence de donnees ouvertes): "L'INSD vous accorde ... une licence mondiale, gratuite et non exclusive vous permettant d'utiliser librement les donnees, de les copier, modifier, traduire, publier, adapter, distribuer, de creer des oeuvres derivees et des produits a valeur ajoutee a des fins commerciales et non commerciales, sous reserve des conditions de la presente licence." (quoted here without its accents; the record holds it as printed). **May be public**, with the attribution the licence words; it does not extend to third parties' data. The ERW holds no table of INSD's.
  - **EBS (Suriname)** (read 1072, its disclaimer, whose footer carries the line): "(c) 2026 - Energie Bedrijven Suriname". The disclaimer limits EBS's liability and grants no reuse; the Algemene voorwaarden page links only a file of supply conditions (read 1071). Read as ZIMSTAT's (session 2495): **needs written permission**. The ERW holds no table of EBS's own; `abs_suriname_electricity_annual` rests on ABS's licence.
- **Not given a verdict:** URA (Maldives; its home page is drawn by scripts, no terms in the bytes, read 1074), STELCO (a Cloudflare challenge, session 2562), SONABEL (no answer, session 2561), ESERA (does not resolve) and the Government of Eswatini (no answer, session 2560). Not asked again.
- **The record:** 561 tables, 191 publishers with a verdict, 1,073 requests, 0 problems. Tests 205, 207 and 378 pass; test 205's bound holds (this chain's reads 1048 to 1075).

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | nvebs.com's robots file | 200 |
| 2, 3 | EBS's Algemene voorwaarden page and disclaimer | 200 |
| 4, 6 | INSD's home page and open data licence | 200 |
| 5 | URA's home page | 200 (drawn by scripts) |

Reads recorded: 1070 to 1075.

## Decisions made without you

- **INSD may be public** under its own open licence; a table of INSD's would still be checked for third parties' data, which the licence excepts.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (two rows), `warehouse/metadata/license_reads.csv` (reads 1070 to 1075), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c126/s2565/`.
