# Session 10821 report (chain 740, lab-desktop window 3): window F's findings on the landed page

- **Row 14's first head landed** (`34904f82b`, landing 2, 14:16 UTC), found from window F's browser read (`docs/reviews/browser-read-2026-11-26.md`, "`/impact` with Datacenter"), which read it on production and filed five findings for this window. The row now shows it landed and asks for the newer head (`6352fb2e4`).
- **The five findings, fixed on the branch:**
  - I1: each default's hover now links its document (JLARC's report for the build, split and refresh; Census CBP's file for the wages; the Tax Foundation's table for the sales rate; the state's cited source for the exemption, property and electricity rules). The discount rate's (OMB Circular A-94) has no address in the ERW's files, so it has none.
  - I2: "Taxes, present value" says in its cell ("without property or electricity tax") and in its hover what this run leaves out.
  - I3: relief held as words (Nevada, Illinois, Massachusetts, Ohio, Nebraska, Alabama, Mississippi, Indiana, Washington) reads "not held", as a state with none read; "none" stays for a rule the project falls short of.
  - I4: picking Paducah, Starwood or Vantage says the document's figure not taken and why (the row's own note).
  - I5: an address naming a project alone (`dcproj`) takes the project's figures, as a pick does; a figure the address gives is kept.
- **One fault of mine, caught before commit to the landing:** the I2 line did not wrap and pushed the page to 501 px at 390; it wraps now (the read found it, a probe named the element).
- **Tests:** `site/scripts/test-datacenter-ui.test.mjs` (I4, I5), run by `tests/test_session10802_datacenter.py`; 22 node tests; 10 Python tests; seventeen addresses read clean at both widths; check-values 1,680 of 1,680.
- **The Stata download** now computes the electricity tax too (the monthly blocks, and Ohio's elective schedule), as the Python one does; its lines are checked by the Python test (Stata is not on this machine).
- **Instructions slip:** one command this session used a heredoc (against "no heredocs") and hung waiting on input; it was stopped, nothing ran.
- **Needs the key:** nothing.
- **Decisions made without you:** a project named alone in an address is read as a pick (its figures set), rather than showing the list on "None".
- **For Samuel's ruling:** nothing new.
