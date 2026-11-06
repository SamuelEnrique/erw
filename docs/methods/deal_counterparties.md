# The deal tracker's counterparties

Energy Research Warehouse (ERW), method note written in session 2234 (chain 156) for the table it adds.

Tables: `deal_counterparties`

## Sources and builder

The ERW builds this table from its own `energy_deals` (`docs/methods/energy_deals.md`), with EIA-861's utility names (`utility_service_territories`, EIA-861 2025) for the utility numbers. The builder is `warehouse/deals/counterparties.py`, run by the daily sequence after the deal extraction as `deal_counterparties`. No model is called and no request is made.

## What a row is

One counterparty of the deals: a name a deal gives as its buyer or seller, once its spellings are joined. A field that names several parties ("Nvidia, Dell", "Apollo and Blackstone") counts for each. A field that holds a description and not a name ("investors", "banks", "a fusion startup", "Leviathan's Israeli owners") is not a row. The folded duplicates of `warehouse/deals/duplicates.csv` are counted once.

## How a name is joined

- **The same words**: two spellings are one name when they have the same words once the suffixes (Inc, Corp, Co, LLC, Ltd, Holdings, Group) and the punctuation are dropped ("AES" and "AES Corp").
- **A company word added**: when one spelling is another with only a company word added ("Constellation" and "Constellation Energy", "NextEra" and "NextEra Energy"). The name kept is the spelling the deals use most; a tie keeps the fuller.
- **An alias with its story**: `warehouse/deals/aliases.yaml` lists the names the rules cannot join, each with the stored story whose words show it ("American Electric Power (AEP)", POWER Magazine, 19 October 2026). An alias no story shows is not added (no story held ties Alphabet to Google, so the two are two names).
- **The US government** is one name, whatever a story calls it (DOE, the Department of Energy, the Pentagon, US), as the deduplication reads it.

## The parent, a second field

A parent is never put in place of a name. It is given only where the name's own words show it ("ADNOC's XRG", "Blackstone's QTS": a possessive; "Amazon data center unit", "OGE Energy unit": a unit, an arm, a subsidiary) or `aliases.yaml` does (Amazon Web Services, Amazon). Two names that begin with the same word ("Related Digital", "Related Companies"; "Golar LNG") are not given a parent: companies share first words.

## The EIA-861 utility number

Only where the name is exactly one utility's name in EIA-861 (both with suffixes dropped), or an alias names the number. On 6 November 2026 no counterparty matches: the deals name holding companies (Duke Energy, Entergy, Dominion Energy, AES, Black Hills), each of which owns several operating utilities in EIA-861 (Duke Energy Indiana, Duke Energy Ohio, ...), and the stories do not say which. A name that begins several utilities' names gets no number.

## Columns

The entities standard columns first (`entity_id` `counterparty:<the name's words>`, `entity_type` company, `name`, `source` erw:energy_deals, `source_url` the earliest deal's first story), then `kind` (utility where an EIA-861 number is matched; ai_buyer for a name of the AI-power rule's party list, `warehouse/deals/fields.py`; government; company), `parent`, `eia861_utility_number`, `spellings`, `deals`, `as_buyer`, `as_seller`, `mw_stated` (the sum of the MW its deals state) with `deals_with_mw` (how many state one), `ai_power_deals`, `first_deal`, `last_deal`, `event_ids`.

The same names are written on every deal of `energy_deals`, beside the buyer and seller as extracted: `buyer_name`, `seller_name`, `buyer_parent`, `seller_parent`, `buyer_eia861`, `seller_eia861` (each a list joined by "; " where the field names several parties).

## License

As `energy_deals`: license needed since 21 October 2026, the names and counts being the ERW's own extraction from the news. Its own row of `warehouse/metadata/license_status.csv` is written once the data machine has built the table and `coverage.csv` holds it (session 410's test holds every row of the file to a table of coverage); until then no live set, page or download reads it.

## What it does not hold

- A company no deal names; a deal's parties that the extraction left empty; an operating utility the stories do not name.
