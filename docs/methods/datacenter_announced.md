# Announced datacenters: what each project's own document said it would bring

Energy Research Warehouse (ERW), method note written in session 10000 (chain 701) for a table first written on 26 November 2026, at data request 6 of `docs/state/data_requests_forecast.md` (chain 740's `/impact`, whose datacenter defaults come from these rows).

Tables: `datacenter_announced`

## What the rows are

One row a named datacenter project and one public document: a state agency's or the company's own release. Chain 740 (lab-desktop, window 3) read each document on 26 November 2026 and transcribed by hand, for each figure the document states, its value, what it counts, the phrase that states it (`says`), any qualifier ("at least", "nearly", "up to") and the sentence it sits in (`quote`), into `warehouse/forecast/datacenter_announced_rows.json`. Its script `warehouse/forecast/datacenter_announced.py --verify-reads` checks every sentence against the text it kept of the document, on the machine that read it. No model API was called; the reading was a chain session's, so the table's tier is `model_extracted`, as the large-load tables' is.

## The table

Builder: `warehouse/derived/datacenter_announced_table.py` (no request). Events shape, 22 rows on 26 November 2026, documents dated 2023-01 to 2026:

- `event_id` `erw_dc_announced:<row id>`; `event_date` the document's date; a document dated by its month only is written on the month's first day, `x_date_precision` `month`, and `x_doc_date` keeps the date as printed (three rows); `event_type` `announcement`; `status` `announced`; `parties` the company; `source_url` the document's address;
- `mw` as stated, and `x_mw_measure` what it measures (IT capacity, grid capacity: they differ and are not converted);
- for investment (`x_investment_usd`, with `x_investment_year`), construction jobs and permanent jobs: the value, its measure (for jobs: workers at peak, direct new jobs and so on), `says`, `qualifier` and `quote`; `x_investment_includes_generation` where the document's figure includes power plants;
- `x_name`, `x_state`, `x_county`, `x_place`, `x_doc_title`, `x_doc_publisher`, `x_doc_request` (the request's row in `runs/c740/probe/probe.csv` on lab-desktop), `x_wage` (as written, JSON), `x_incentive`, `x_years`, `x_note`.

A figure a document does not state is empty: 15 rows state no megawatts, 15 no construction jobs, 4 no permanent jobs. Nothing is computed, summed or filled. Before writing, the builder checks that each figure's phrase sits inside its sentence and that no row id is given twice.

## What it is not

- Not what was built or what happened: what a document said a project would bring, on its date.
- Not comparable figure to figure without the measure: "IT capacity" and "grid capacity", "workers at peak" and "jobs", are each the document's own.
- Not a census of datacenters: 22 projects whose documents chain 740 read.

## License

Internal. The rows quote the documents' sentences, and session 255's rule (which `large_load_public` follows) makes public only facts with a link and no quoted text; the documents' own reuse terms were not read. Whether the facts alone (values, measures and addresses, without the quotes) may be a public selection is a line for Samuel's ruling, default internal.
