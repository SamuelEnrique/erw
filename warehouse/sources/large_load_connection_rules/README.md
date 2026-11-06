# Large loads' connection rules: the registry

Energy Research Warehouse (ERW), session 2924 (chain 153). One file a document, `<body>_<document>.yaml`, read by
`warehouse/connectors/large_load_connection_rules.py` into `large_load_connection_rules` (events, one row a step).
Method: `docs/methods/large_load_connection_rules.md`.

A session fills a file by reading the document itself (the grid operator's guide or protocols, the utility's filed rule),
after the host's robots file and terms. Each step is written with the words it is printed in and where (its section, and
its page where the document has pages). A step that states no number of days or months is written with its words and no
duration; a date the document states is written as it states it. Nothing is estimated, summed or inferred.

```yaml
body: Electric Reliability Council of Texas (ERCOT)   # who states the rule
grid: ERCOT
utility: ""                                           # a utility's rule: its name, and eia_id
eia_id: ""
state: TX
document: ERCOT Planning Guide, Section 9, Large Load Interconnection or Modification
document_date: 2026-07-11                             # the document's own date
document_url: https://...
retrieved_at: 2026-11-05T20:18:00Z
license: public
steps:
  - section: "9.3.1(2)(a)(ii)"
    page: ""                                          # the PDF's page, where it has pages
    step: the ILLE posts its financial security
    party: ILLE
    duration: 7                                       # a number the step prints, or left out
    unit: business days                               # business days, calendar days, days, months or years
    date: ""                                          # a date the step prints, YYYY-MM-DD
    mw: ""                                            # a load size the step prints, MW
    printed: "The ILLE shall have seven Business Days from the date of notification to post the financial security ..."
```
