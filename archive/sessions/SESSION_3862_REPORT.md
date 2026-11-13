# Session 3862 report, with 3863 to 3865: Kansas closed, Pennsylvania's model tariff for large loads

Energy Research Warehouse (ERW). Chain 223, data machine (lab-desktop), 13 November 2026 08:02 to 08:12 UTC. Opus 5.5. Model spend USD 0. Requests: 3 in session 3862 (www.kcc.ks.gov) and 9 in session 3863 (www.puc.pa.gov), each under 25. Kept at `runs/license_reads/s3862/` and `s3863/` (not in git).

## Read these first

- **PJM, time to connect: Pennsylvania's adopted model tariff joined `large_load_connection_rules`** (8 steps; 10 documents and 75 steps in all). It is the Pennsylvania PUC's Final Order at Docket M-2025-3054271, adopted 30 April 2026 and entered 12 May 2026; its ordering paragraph 1 adopts the Model Tariff for customers at or over 50 MW, or 100 MW in the aggregate. Its steps, each with its page and words:
  - two open seasons a year for interconnection studies, studied as clusters;
  - **the studies completed within six months** of a complete application;
  - half the study fee refunded for each 90 days late;
  - a load ramp period of three to five years;
  - an initial term of at least five years;
  - 48 months' notice to end or change the contract;
  - 14 business days to ask for a dispute's escalation.
  - The reconsideration orders were read too: the Energy Association's petition was withdrawn and the docket closed on 16 July 2026, so the model stands.
  - Each Pennsylvania utility files its own tariff on the model, so the rows have grid PJM and no utility.
- **The table** was written under the data lock (75 rows: 8 new, 67 replaced), validated (exit 0), archived (`20261113T080701Z-local`, 8 rows) and given its coverage row. On the tab, `site/data/siting/conn_rules.json`'s `pjm` key moved (12 steps to 20), and only that key. Test 2924 counts 75 steps.
- **SPP (the Kansas row, Kansas Gas & Electric, Evergy Kansas South): closed.** The KCC has no robots file, but its electric pages hold no tariff library. Its docket system (`kcc-connect.kcc.ks.gov`, a script-driven search) names no document address, so it was not searched blindly.
- **PJM, transmission and 4CP (the Allegheny row, FirstEnergy Pennsylvania Electric, EIA 66101): closed.** The PUC's electric tariffs list links each utility's own site, and FirstEnergy's terms bar reuse (session 3783). The PUC hosts no copy of the tariffs.
- **Sessions 3864 and 3865 were not run as separate sessions.** No other open row has a public copy this reader can name:
  - the MISO row's Duke Energy Indiana files with the IURC, whose in.gov terms ask permission and whose docket search names no address;
  - the CAISO row's Southern California Edison keeps its tariff book on its own site, closed by its terms;
  - HUD VL, MHK VL and NORTH need a county before a utility.

## Decisions made without you

- **A commission's model tariff is written as the grid's steps,** not as any one utility's: each Pennsylvania utility files its own on the model.
- **A range and a frequency carry their words and no duration** (the load ramp; the open seasons).
- **No county is chosen for a zone by this chain** (HUD VL, MHK VL, NORTH): a zone's footprint needs its operator's definition, and NYISO's is held for a license.

## For Samuel's ruling

- None new. The PUC's site states no terms; the order is a public record, so the rows are public, under the table's own verdict ("not settled", release_v1.STORAGE_HELD).
