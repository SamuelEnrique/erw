# private/bills: real electricity bills, never shared

Real bills never leave this folder. Everything here except this README is in `.gitignore`: it is not committed, pushed, uploaded, loaded into Supabase or shown on the site.

The bills are Samuel's friends', sent with their permission, for one purpose: checking `/learn/bill`'s arithmetic against real bills.

## What goes here

One CSV per bill, typed or pasted by hand from the bill. One row per line item:

| Column | What it is | Example |
|---|---|---|
| `utility` | the bill's key on `/learn/bill`: `CA` (PG&E), `SCE`, `SDGE`, `TX` (Oncor), `TXC` (CenterPoint) | `TXC` |
| `plan_type` | the rate or plan, in a few words | `fixed-rate 12 months` |
| `period_start`, `period_end` | the billing period, YYYY-MM-DD | `2026-08-14`, `2026-09-13` |
| `kwh` | the bill's total use | `1013` |
| `line` | the charge's name, as printed | `TDU Delivery Charges` |
| `amount` | in USD; credits negative | `-3.21` |
| `energy_rate` (optional, Texas) | the plan's energy charge, USD/kWh, from its Electricity Facts Label | `0.1129` |

## What the intake drops

`site/scripts/bill-intake.mjs` keeps only the columns above. It also drops:
- any column named for a person or place, such as `name`, `address`, `account`, `meter`, `esiid`, `phone` or `email`;
- any line whose name looks like one of those;
- long digit runs inside a line's name.

It writes the rest, de-identified, to `tests/fixtures/bills/`. Read the fixture before committing it.

## Use

```bash
node site/scripts/bill-intake.mjs private/bills/<file>.csv
node site/scripts/test-bill-fixtures.mjs
```
