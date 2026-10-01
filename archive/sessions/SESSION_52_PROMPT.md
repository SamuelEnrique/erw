# SESSION 52: Bill explainer v1 (more utilities, and a private intake for real bills)

## Read first
site/data/bill_rules.json, site/lib/bill.ts, /learn/bill, the quote check from session
43, archive/sessions/SESSION_43_REPORT.md.

## Budget and rules
- USD 0, no model calls, no data pulls. Tariff pages read as text; every rate with its
  quoted passage, checked against the page text. No rate from memory.
- Target about an hour. Pull and merge if the daily job lands, never force push.

## The work
1. Add three bills on the session 43 pattern: Southern California Edison (its standard
   residential time-of-use schedule), San Diego Gas & Electric (the same), and a
   Houston home in CenterPoint's delivery area (CenterPoint's current residential
   delivery charges; the retail energy charge as a labeled, editable default derived
   the way session 43 derived Oncor's). The picker on /learn/bill offers all five.
   Hand-computed test cases at 600 and 1,000 kWh for each.
2. Private intake for real bills (Samuel's friends sent theirs with permission):
   - a folder private/bills/ added to .gitignore, with a README saying real bills
     never leave this folder;
   - a script that, given line items Samuel types or pastes from a bill into a local
     CSV in that folder (charge name, amount, kWh, period), drops anything personal
     and writes a de-identified fixture to tests/fixtures/bills/ (utility, retailer
     plan type, kWh, period, each line's name and amount, no name, address, account or
     meter number);
   - a test that runs every fixture through lib/bill.ts and reports the difference
     between our computed bill and the real one, line by line.
   No real bill is processed tonight; ship the intake with one made-up example fixture
   clearly labeled fictional.
3. check-values, check-routes, tests/, deploy, live check.

## Report: archive/sessions/SESSION_52_REPORT.md
Every new rate with its source, figures left out, the test cases, how to use the
intake in three steps for Samuel, wall time, spend USD 0 confirmed. Push. Stop.