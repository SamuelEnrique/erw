# Queues outside the seven grids (`/queues/places`)

Session 8014, chain 581 (part F2), 20 November 2026. Builder: `warehouse/derived/queue_places.py`, a step of the data machine's daily run (`dm_queue_places`, after the states' files). Page file: `site/data/queue_places.json`. Page: `site/app/queues/places/page.tsx`. License: public.

## What exists, read first

The warehouse holds the queues of the seven grid operators (their own tables) and one compilation of every public queue in the country: Lawrence Berkeley National Laboratory's "Queued Up" (`lbnl_interconnection_queue`, the 2026 edition, through 2025), whose regions "West" (8,097 entries) and "Southeast" (4,334) are the queues of the utilities and federal power marketers outside the ISOs. `/queues` draws them as two regions, "West, outside the ISOs" and "Southeast, outside the ISOs". No table of the warehouse holds a utility's own queue outside the ISOs beside LBNL's compilation, and none was pulled here: the compilation is the public record the warehouse has of them, kept under LBNL's names.

## Rules

- Each queue owner keeps LBNL's own name (`lbnl_entity`, for example PacifiCorp, SOCO, Duke, BPA, TVA); nothing is matched to an EIA-930 code by name.
- MW is LBNL's capacity of the entry; entries are counted and summed by LBNL's status (active, suspended, operational, withdrawn, unknown) and type.
- A state is listed when some of its people live outside the seven grids (by county, `eia_county_region` with the Census Bureau's county estimates, as `/states` computes); Connecticut, whose counties do not match between the two sources, has no share and is not listed. A state no entry of LBNL's West or Southeast names is listed as "no public queue in the compilation". On the edition of 2026: 49 owners and 25 states, every one of them named by at least one entry.

### Decisions (session 8014)

| Key | Decision | Default |
|---|---|---|
| `lbnl-names` | Each owner under LBNL's name, nothing matched by name | LBNL's names |
| `states-by-people` | A state listed by its people outside the seven grids | by county population |
| `first-two` | Opens on the two owners with the most active MW | BPA and the next |

## A row as the publisher files it (session 9000, data request 562)

One entry of Arizona Public Service (APS, queue id Q362, a 275 MW solar and battery request of 30 September 2020 at the Milligan to Casa Grande 230 kV point) is filed by LBNL with the state `NC`, while the same row's county is Pinal and its FIPS code 4021, both Arizona. Read again on 20 November 2026 in LBNL's own workbook (`lbnl_ix_queue_data_file_thru2025.xlsx`, sheet "03. Complete Queue Data", row of `q_id` Q362, entity APS): the workbook writes NC. The connector copies the state as written, so the row stays as LBNL filed it, and North Carolina's list of owners names APS with this one entry. No state is changed here; a correction belongs to the publisher.
