# Session 2938 report: the connection rules and the interruptible riders, continued

6 November 2026, about 07:13 to 07:16 UTC, on lab-desktop (the data machine), chain 155, unattended. Model spend USD 0. Pulls: none of the 25 allowed. The document was already on this machine.

## Read these first

- **SPP's High Impact Large Load process joins `large_load_connection_rules`: 13 steps, the table now 39 rows** (commit `ce6b8b948`). The document is FERC's order accepting SPP's Tariff revisions (Docket ER26-247-000, 194 FERC 61,031, issued 14 January 2026, effective 15 January 2026), a federal work, as SPP posts it. It was saved on 8 October 2026 and reused, with no new request. It states:
  - a HILL is 10 MW or more at 69 kV or below, or 50 MW or more above 69 kV (page 5);
  - 30 calendar days to return the HILL Delivery Point Study Agreement with a USD 10,000 fee and a USD 100,000 deposit, and 90 calendar days for SPP to complete that study (page 8);
  - for the HILL Generation Assessment (page 14): 15 calendar days to validate a request; 10 business days to cure; 90 calendar days for the system impact study; 30 days to notice a restudy and 60 to complete it; 45 calendar days to negotiate the agreement; 10 business days to tender it; 10 business days to execute it;
  - **150 days for the whole HILLGA process, against 12 months for SPP's standard DISIS cluster** (page 29). This is the first stated faster path for a large load's generation in the table.
- **The write** (`runs/c147/write_table.sh`, under the data lock): validator PASS, coverage, archive run `20261106T071516Z-local` (13 rows). The method note lists the document; test 2924 now pins 39 rows of three grids (6 passed).
- **Not reached:** PJM (non-members may not republish, licenses.md #15), NYISO (no license conferred) and ISO-NE (permission), whose documents are those publishers' own; MISO (paused); CAISO (it connects no load; the utilities do, and of them only PG&E's site was open, session 2921).
- **Interruptible riders:** none. The utilities under the row's grids are closed to this reader (sessions 2921 and 2937).

## Decisions made without you

- **A FERC order read as the statement of SPP's Tariff.** It is the Commission's own text, in the public domain, and it cites each Tariff section it restates. SPP's own terms (licenses.md #6, "except ... within a commercial publication") are not relied on.
- **The registry's state for SPP is AR**, its seat (the registry needs one; SPP spans fourteen states).

## For Samuel's ruling

- None new.
