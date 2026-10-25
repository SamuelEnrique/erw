# Public statements of large load waiting for power, each with its exact sentence

Energy Research Warehouse (ERW), method note written in session 2592 (chain 128) for an internal table first written in session 139 and widened in sessions 141 and 151. The method and its history are in [`docs/accelerator/large_load_eighty.md`](../accelerator/large_load_eighty.md) (with [`large_load_pilot.md`](../accelerator/large_load_pilot.md) and [`large_load_forty.md`](../accelerator/large_load_forty.md) before it); this note names the table, gives its shape as held, and points there. How the site uses its figures (aggregates only, no row shown) is in [`datacenter_cost.md`](datacenter_cost.md), "How long a large load waits".

Tables: `large_load_statements`

## Builder and inputs

`warehouse/connectors/large_load_statements.py`. It makes no request and no model call: it reads the research passes' verified statements (each an AI research agent's, under `warehouse/raw/large_load_pilot/` and `warehouse/raw/large_load_statements/`, not in git, with every document as downloaded), checks each again as far as the row allows (a sentence, an address, a figure that stands in the sentence) and writes them. Source id `erw:large_load_pilot`.

## What a row is

Events shape, `event_type` `large_load_statement`: one row per figure as a utility's or grid operator's own document states it. `event_date` is the document's date (a document dated to a month or a year: its first day, `document_date_as_stated` holding what it states; an undated page: the day it was read, `event_date_basis` saying so). `row_kind` is `mw` (a quantity of load) or `wait` (a duration). No number without its sentence (`sentence`, a literal substring of the document's text); nothing is summed, netted, converted or annualized across statements; the stage stays in the document's words (`status`, `stage_as_worded`), with the passes' reading beside it (`stage_class`). `mw` is the figure in MW (gigawatts times 1,000); a range leaves `mw` empty and fills `mw_low` and `mw_high`.

## As held on 25 October 2026

Run `20261019T094207Z`, counted by code from the table read past its header lines: 798 rows, every `event_id` unique, documents dated 2024-05-01 to 2026-10-08; 113 entities in 83 groups; 763 rows from the eighty entities chosen in advance and 35 from bodies outside them that state a figure (`entity_list`); 598 `mw` rows and 200 `wait` rows, 176 of the waits counted as a large load's wait and 171 distinct wait figures (`wait_figure_holder` yes). The document types most cited: commission filings (168), earnings presentations (104), load forecast reports (102), operator reports (100), integrated resource plans (95). `event_date_basis`: the document 778, the day read 20.

## License

Internal: quoted from public documents under each publisher's own terms, not read one by one, and held internal until a person rules. Not on the site, not in the public Redivis dataset, not in the live set. MISO's site was never requested.
