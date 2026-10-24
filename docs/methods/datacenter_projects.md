# Datacenter facilities named in the news (the datacenter power tracker's extraction)

Energy Research Warehouse (ERW), method note written in session 2550 (chain 125) for a table first written in session 16 (the datacenter power tracker, platform tool 4).

Tables: `datacenter_projects`

## Sources and builder

The ERW builds this table. Its input is the ERW's own `news_stories`: scored stories with sector `datacenter_power`, at any significance. The builder is `warehouse/datacenters/extract.py` (session 16), run by the daily sequence as the model step `datacenters`. One run writes two tables: this one (entities, public) and `datacenter_projects_evidence` (events, internal, one row a facility and story with the evidence sentence; its own note describes the model call, the schema and the cost). The stories sent are recorded in `warehouse/datacenters/checked.csv` (in git), so a story is sent once.

## What a row is

One datacenter facility that a story names: a named site, or a named operator or developer at a stated place. Market commentary, sponsored content and company-wide plans without a site are not facilities.

## Columns

The entities standard columns come first (`entity_id` `datacenter:<16 hex>`, `entity_type` datacenter, `name`, `geo`, `lat`, `lon`, `capacity_mw`, `status`, `status_date`, `operator`, `source`, `source_url`, `retrieved_at`, `vintage`), then the extractor's: `kind`, `developer`, `site_name`, `state`, `county`, `city`, `mw`, `phase`, `project_status`, `planned_year`, `power_source`, `utility`, `ai_power`, `confidence`, `geo_precision`, `geo_note`, `first_story_at`, `n_stories`, `story_ids`, `story_urls`, `model_id`, `extracted_at`.

- **`capacity_mw` is `mw`, as stated** in a story; 43 of the 156 rows on 24 October 2026 state one.
- **`status`** is the entities vocabulary: announced, applied and permitted become planned; cancelled becomes withdrawn; under_construction and operating stay. The extractor's own word is in `project_status`. On 24 October 2026: planned 56, under_construction 13, withdrawn 7, operating 5, the rest empty (a status without its span is left empty, session 17's ruling).
- **`ai_power`** is true on every row: the table is the platform's AI and datacenter power subset.
- **Place:** with a state and county, the county's internal point (the Census county gazetteer, `geo_precision` county); with a state and city only, the city's internal point (the Census places gazetteer, 2025, `geo_precision` place); else not placed (`geo_precision` none). On 24 October 2026: county 7, place 16, none 133.
- **`model_id`:** the model of each facility's first extraction (claude-sonnet-5-5 for 125 rows, claude-sonnet-5 for 31 on 24 October 2026).

## The checks (session 16's ruling: nothing inferred beyond the stated words)

Every value is checked against the story's own title and summary, and a value that fails is left empty, the run log naming it:

- `mw`: the exact span it was read from is in the story and parses to the same value (GW and MW applied), as in the deal extractor, whose checks the builder imports;
- `state` and `status`: the span each was read from is in the story; a state's span names it (name or postal code);
- `county` and `city`: the span (`location_text`) is in the story and contains the name;
- `planned_year`: its span is in the story and contains the year;
- `operator`, `developer`, `site_name`, `power_source` and `utility`: the name appears in the story.

## Deduplication

Each call carries the facilities already extracted (id, operator, developer, site, place, MW); the model marks a facility that is one of them (`same_as`), and that story's links are added to it, with any field the facility still lacks filled from the new story. Since session 166 a `same_as` is accepted only when the two name the same operator or developer, the same site, or the same county or city in the same state; a state alone joins nothing. `--reextract` rebuilds the tables from every story already checked, the earlier tables kept in `warehouse/datacenters/history/`.

## Vintage

The whole table is rewritten each run from the facilities already extracted and the new stories. On 24 October 2026 it held 156 rows (154 the run before), written by run `20261024T150143Z`.

## License

Public: the model's checked fields and the story links only, no outlet text. The evidence sentences, which are outlet text, are in the internal `datacenter_projects_evidence`. `datacenter_facilities`, which joins this table with the operators' lists and the queues, is held whole for its own reasons (its note).

## What it does not hold

- Facilities no scored story names; the outlets' text; any value a story does not state in words the checks find.
