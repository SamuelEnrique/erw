# Session 2235 (chain 156, deals and datacenters) report: the figures cross-checked

6 November 2026, about 08:23 to 08:29 UTC, portable-laptop (code role), unattended. Worktree `erw-2235` on `wip/2235-deals`, cut from `wip/2234-deals`. Model spend **USD 0**. Nothing deployed; no warehouse data written.

- **`warehouse/deals/crosscheck.py`** (new): the headlines' MW, MWh and US dollars against the record's (valuations, combined values and company-wide investments left out); MW and MWh, USD and USD per MWh never confused; a term in months flagged, not converted; the sanity bounds. `flags()` returns words; the extractor writes them to `flags` on every record on every run and logs the count.
- **`warehouse/deals/fields.py`**: the MWh bound from 200,000 to 50,000,000 (50 TWh: an energy contract of 3.3 TWh is real); `num()` writes a figure in plain digits in every flag.
- **Over the stored 529 deals**: 14 flagged (6 MW and 4 USD the headline states and the record lacks; 2 USD and 1 MW contradicted; 1 above a bound). The table in the audit file.
- **`tests/test_session2235_deals.py`** (12 tests), with 2232 to 2234 and 531: 54 passed.

## Decisions made without you

1. **Flags, never corrections.** A headline's figure the record lacks is named in the flag; the figure is not written into the record, because the record's figures are kept only where their span checks (session 15), and the cross-check reads headlines without the model's span.
2. **A term in months is not converted to years**, by the ruling that no figure is converted; the flag shows that a term exists.
3. **Rounding tolerance 2 percent** between a headline and the record (USD 21.4 and 21.5 billion are one sum).

## For Samuel's ruling

- None new.
