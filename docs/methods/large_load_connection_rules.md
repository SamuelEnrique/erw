# Large loads' connection rules

Energy Research Warehouse (ERW), method note written in session 2924 (chain 153, 6 November 2026) for the table first
written that day.

Table: `large_load_connection_rules` (events, public). Connector: `warehouse/connectors/large_load_connection_rules.py`.
Registry: `warehouse/sources/large_load_connection_rules/` (one file a document; its README gives the form).

## What a row is

One step a grid operator's or a utility's document states for connecting a large load: who acts (`parties`), what the
step is (`x_step`), and what the document states of its time: a number and its unit (`x_duration`, `x_duration_unit`:
business days, calendar days, days, months or years), a date (`event_date`, `x_date_kind` "stated date"), or neither.
Each row carries the words the step is printed in (`x_printed`) and where (`x_section`, `x_page` where the document has
pages). A load size the step prints is `mw`.

A step that states no time is a row too, with its words and no duration: the siting gaps' "the faster path for a
controllable load" is such a row (ERCOT Planning Guide 9.6.1(1): a PCLR is energized with its consumption capped, and
no duration is stated for the conditions that lift the cap).

## What is not done

- No step is summed into a "time to connect": the steps run in parallel, in sequence or only on a condition, as each
  document says, and a sum would be an inference.
- Business days are never converted to calendar days.
- No duration is read from a chart, a slide or a summary: only from the document's own text.
- A document whose terms or robots file bar the reader is not read (Con Edison, Eversource and Duquesne Light, session
  2921; MISO is paused; the Virginia SCC is paused).

## The documents held (6 November 2026, session 2938)

| Document | Body | Date | Steps | Read |
|---|---|---|---|---|
| ERCOT Planning Guide, Section 9 (`09-071126.docx`) | ERCOT | 2026-07-11 | 22 (Batch Zero 9.2 to 9.6; the legacy study 9.8 and 9.9) | session 2905's fetch, read again by 2919 |
| PG&E Electric Rule No. 30 (interim, Advice 7772-E) | PG&E | 2025-12-04 | 4 | session 2921's fetch |
| FERC's order on SPP's HILL and HILLGA processes (ER26-247-000, 194 FERC 61,031) | SPP, as the order states its Tariff | 2026-01-14 | 13 | the copy saved on 8 October 2026 (`large_load_statements`, reused by `large_load_rules`), no new request; added by session 2938 |

## License

Public, row by row. ERCOT's terms let raw data in public portions of its site be reproduced in compilations (licenses.md
#2); PG&E's Rule 30 is its CPUC-filed tariff sheet, and PG&E's site states no terms on its tariff pages (a question for
the owner, session 2921).
