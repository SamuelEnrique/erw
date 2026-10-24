# Session 2551 report: the licenses' forty-sixth round (DERK, CNDC, Enemalta and DEPS need written permission)

24 October 2026, about 23:10 to 23:13 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2551.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first:** none of this chain's publishers had a verdict.
- **Four verdicts,** each sentence cut by code from a page sessions 2546 to 2549 saved (`runs/c125/s2551/verdicts.py`); each is a copyright line with no reuse statement, read as ZIMSTAT's (session 2495): **needs written permission**, sold or not.
  - **DERK (Bosnia and Herzegovina)** (read 1022, its English home page): "All Rights Reserved", after "DERK (c) 2004-2026". `derk_bih_electricity_annual` stays internal.
  - **CNDC (Nicaragua)** (read 1026, its home page): "Copyright (c) 2026 CNDC". The ERW holds no table of it.
  - **Enemalta (Malta)** (read 1018, its fuel mix disclosure): "All rights reserved". The ERW holds no table of it.
  - **DEPS (Brunei)** (read 1033, its eData Library page): "Copyright Goverment of Brunei Darussalam. All Right Reserved." (as the page spells it). The ERW holds no table of it.
- **The verdicts' reads now have the outcome exactly `read`** (test 205). Their earlier notes: read 1018 "shares of energy distributed and an emission factor only; All rights reserved"; 1022 "DERK 2004-2026. All Rights Reserved; no terms of reuse"; 1026 "Copyright 2026 CNDC; no statistics files linked"; 1033 "its electricity workbooks listed; Copyright Government of Brunei Darussalam. All Right Reserved".
- **Not given a verdict:** NSO Malta (a Cloudflare challenge), REWS, BHAS and NOS BiH (no terms page read; the ERW holds no table of theirs), INIDE, INE Nicaragua (its certificate fails), the Brunei Department of Electrical Services and Ministry of Energy. Statistics Greenland's terms page could not be found by search, so its table stays unsettled.
- **The record:** 556 tables, 184 publishers with a verdict, 1,031 requests, 0 problems. Tests 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the chain's publishers' pages were already saved; the one unsettled publisher looked for (Statistics Greenland) has no terms page a search finds.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (four rows), `warehouse/metadata/license_reads.csv` (four outcomes), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c125/s2551/`.
