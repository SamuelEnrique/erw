# Session 52 report: bill explainer v1 (more utilities, and a private intake for real bills)

Energy Research Warehouse (ERW), session 52, run 2026-10-01 from 11:25 to about 11:50 UTC. **Wall time about 25 minutes,** against an hour's target.

**API spend: USD 0.00, confirmed.** No model call, no data pull: tariff pages were read as text. No force push.

## What was built

1. **Three more bills on `/learn/bill`,** on the session 43 pattern: each line gives what it is, why it exists, its rate, its source, the quoted passage and the effective date. The picker offers all five; the default bills section shows all five.
   - **Southern California Edison:** Schedule TOU-D, Option 4-9 PM, bundled service.
   - **San Diego Gas & Electric:** Schedule TOU-DR1, SDG&E's standard residential schedule, bundled.
   - **A Houston home in CenterPoint's delivery area,** with the retail energy charge a labelled, editable default.
2. **Every passage was checked against the tariff text,** whitespace ignored, by the script that wrote them (31 passages; none missing). `site/data/bill_rules.json` is now version `2026-10-01.1`. PG&E's and Oncor's entries are unchanged, byte for byte.
3. **`lib/bill.ts`:**
   - `billTOU` is a three-period time-of-use bill for SCE and SDG&E, by each utility's own period definitions.
   - `billTDSP` is a Texas bill for any wires company (`billTX` is Oncor's).
   - `defaultBill` gives each of the five defaults.
   - check-values recomputes each default its own way: by period, from the rates, outside `lib/bill.ts`.
4. **The private intake for real bills:**
   - `private/bills/` is ignored by git except its README, which says real bills never leave the folder.
   - `site/scripts/bill-intake.mjs` turns a typed-in CSV into a de-identified fixture in `tests/fixtures/bills/`.
   - `site/scripts/test-bill-fixtures.mjs` reports, line by line, our computed bill against the real one.
   - No real bill was processed. One made-up example fixture, `txc-fictional-example.json`, is labelled fictional in its own fields.

## Every new rate, with its source

### SCE: Schedule TOU-D, Option 4-9 PM

**Sources:**
- **Schedule TOU-D:** Cal. P.U.C. Sheet No. 91197-E and following, effective 2026-06-01; from SCE's public tariff book (a SharePoint library linked from sce.com; the old library.sce.com no longer resolves).
- **Baseline allocations:** Preliminary Statement Part H.

| Line | Rate | Passage (short) |
|---|---|---|
| Delivery service, summer on / mid / off-peak | $0.33156 / $0.33156 / $0.27270 per kWh | "Summer Season - On-Peak 0.331 56 (I) 0.25321 (R) ..." |
| Delivery service, winter mid / off / super off-peak | $0.33156 / $0.27270 / $0.25153 | "Winter Season - M id-Peak 0.331 56 (I) 0.1 7956 (R) ..." |
| Generation, summer on / mid / off-peak | $0.25321 / $0.13326 / $0.07396 | the same rows, Generation (UG) column |
| Generation, winter mid / off / super off-peak | $0.17956 / $0.10245 / $0.08452 | the same |
| Fixed Recovery Charge | $0.00619 per kWh | "Fixed Recovery Charge - $/kWh 0.0061 9" |
| Baseline Credit | ($0.10099) per baseline kWh | "Baseline Credit**** - $/kWh (0.1 0099) (I)" |
| Base Services Charge | $0.794 per meter per day | "Base Services Charge (BSC) - $/M eter/Day 0.794" |
| California Climate Credit | ($36.00) | "California Climate Credit1 0 (36.00)" |
| Baseline allocation, basic, by region (summer, winter, kWh a day) | 5: 17.0, 18.4; 6: 11.4, 11.0; 8: 12.8, 10.3; 9: 16.9, 12.0; 10: 19.3, 12.1; 13: 22.2, 12.2; 14: 19.2, 11.9 | Part H, the summer and winter tables |

- **The PDF's text splits some numbers** with stray spaces ("0.331 56"). The quotes keep the text as extracted; the check ignores whitespace, as session 43's did.
- **Time periods** (Special Condition 1):
  - summer: on-peak 4 to 9 p.m. on weekdays, mid-peak 4 to 9 p.m. on weekends and holidays, off-peak all other hours;
  - winter: mid-peak 4 to 9 p.m., off-peak 9 p.m. to 8 a.m., super off-peak 8 a.m. to 4 p.m.;
  - summer runs June 1 to October 1.
- **The baseline credit** applies "up to 100% of the Baseline Allocation, regardless of Time-of-Use time period".

### SDG&E: Schedule TOU-DR1

Source: SDG&E's Total Rates Table, effective 2026-08-01. These are bundled totals (UDC, the DWR and wildfire charges, and the EECC commodity rate).

| Line | Rate | Passage (short) |
|---|---|---|
| Energy, summer on / off / super off-peak | $0.69135 / $0.46421 / $0.37433 per kWh | "On-Peak 0.09096 0.15348 ... 0.35943 0.69135", and the like |
| Energy, winter on / off / super off-peak | $0.61471 / $0.53060 / $0.43719 | the winter rows |
| Baseline adjustment credit | ($0.10702) per kWh, up to 130% of baseline | "Up to 130% of Baseline Adjustment Credit ... (0.10702)" |
| Base Services Charge | $0.79343 per day | "Base Services Charge ($/Day) ... 0.79343" |

**Time periods:**
- on-peak 4 to 9 p.m. every day;
- super off-peak midnight to 6 a.m. on weekdays and midnight to 2 p.m. on weekends;
- off-peak the rest.

These are read from the TOU-DR1 sheet SDG&E posts at sdge.com, which is **dated effective January 1, 2018**. Only its periods are used, not its old rates, and the page says so.

### CenterPoint Energy Houston Electric: Tariff for Retail Delivery Service

Source: CenterPoint's tariff PDF, linked from its Houston Electric rates page.

| Line | Rate | Effective |
|---|---|---|
| Customer Charge | $2.11 per month | 2026-02-26 (6.1.1.1.1 Residential Service) |
| Metering Charge | $2.79 per month | 2026-02-26 |
| Distribution System Charge | $0.023240 per kWh | 2026-02-26 |
| TCRF | $0.030812 | Rider TCRF, 53rd revision, 9/1/26 |
| DCRF | **$0.006137** | meter reads on and after 2026-09-30 (Rider DCRF, 16th revision) |
| EECRF | $0.001576 | Rider EECRF |
| NDC | $0.000013 | 4/28/25 |
| TEEEF | $0.000742 | meter reads on and after 2026-08-15 |
| RCE | $0.000048 | 04/28/25 |
| IRA | $0.000000 | 5/18/2026 |
| SRC II | $0.000636 | 9/1/26 |
| ADFIT Credit II | **($0.000023)** | 9/1/26 |
| SRC III | $0.002848 | 02/26/26 |
| ADFIT Credit III | **($0.000418)** | |
| TC5 Refund | **($0.000278)** | 5/18/2026 |
| Retail energy charge | **input**; default **$0.0853/kWh** | see below |

**Corrections to CenterPoint's own rates page:**
- The page lists an older DCRF, $0.004934.
- It shows the three credits unsigned.
- The tariff, which is what the bill uses, gives the DCRF above and the credits signed.

**The default energy charge:**
- EIA's July 2026 Texas residential average, 158.8 USD/MWh (`eia_retail_electricity_prices`, `eia:retail_price:TX:RES`);
- less CenterPoint's per-kWh charges ($0.065333);
- less its fixed charges over 600 kWh ($4.90 / 600).
- That gives 0.085300, so the default bill at 600 kWh matches the state average, as session 43 derived Oncor's.

## Figures left out

**SCE:**
- **The MCAM charge:** it recovers "system reliability procurement ... on behalf of customers whose generation services are provided by certain Electric Service Providers or Community Choice Aggregators", not bundled customers.
- **Baseline regions 15 and 16:** their rows could not be told apart between the summer and winter tables in the text read.
- **Others:** CARE and FERA discounts, Option 4-9 PM-CPP, all-electric and heat pump allocations.

**SDG&E:**
- **Baseline allowances by climate zone.** SDG&E's calculator computes them in a script and its tariff portal's sheets are not linked as files, so no tariff text was found. The allowance is an input from the customer's bill, and **the default bill has no baseline credit**: at 600 kWh with a 300 kWh allowance it would be $41.74 lower.
- **The California Climate Credit:** the only figure seen was on the 2018 sheet.
- **Others:** CARE, FERA and medical baseline rates; March and April weekday super off-peak middays (ignored in the default split).

**CenterPoint:**
- **Fees a retailer adds:** the gross receipts reimbursement, the PUC assessment, and sales tax where it applies. The fictional fixture shows such a line as "only on the bill".
- **A real plan's energy charge:** the default is derived, as above.

**All three:** city taxes and fees.

## The test cases

`site/scripts/test-bill.mjs`, by hand from the cited rates. All pass.

| Case | Hand result |
|---|---|
| SCE winter, 600 kWh (Region 9, baseline 12.0 x 30 = 360 kWh; 20% 4-9 p.m., 33.33% 8 a.m.-4 p.m.): 120 x (0.33156 + 0.17956) + 199.98 x (0.25153 + 0.08452) + 280.02 x (0.27270 + 0.10245) + 600 x 0.00619 - 360 x 0.10099 + 30 x 0.794 | **$224.7648** |
| SCE winter, 1,000 kWh | **$382.9656** |
| SCE summer, 600 kWh (5/7 of 4-9 p.m. on-peak, the rest mid-peak; baseline 16.9 x 30 = 507 kWh) | $208.7889 |
| SDG&E summer, 600 kWh: 120 x 0.69135 + 207.12 x 0.37433 + 272.88 x 0.46421 + 30 x 0.79343 | **$310.9698** |
| SDG&E summer, 1,000 kWh | **$502.4143** |
| SDG&E summer, 600 kWh with a 300 kWh allowance (credit on 390 kWh) | $269.2320 |
| CenterPoint, 600 kWh: 51.18 + 39.1998 + 4.90 | **$95.2798** |
| CenterPoint, 1,000 kWh: 85.30 + 65.333 + 4.90 | **$155.533** |

Every line of each bill is cited, quoted and dated with an https source.

**The default bills live** (600 kWh), with the wholesale share:

| Bill | Total | Wholesale | Share | Price used |
|---|---|---|---|---|
| PG&E | $262.33 | $28.19 | 10.75% | NP15, 46.99 USD/MWh, 2026-08 |
| SCE (winter) | $224.76 | $34.17 | 15.20% | SP15, 56.94, 2026-08 |
| SDG&E (summer, no baseline credit) | $310.97 | $34.17 | 10.99% | SP15, 56.94, 2026-08 |
| Oncor | $95.27 | $22.02 | 23.11% | ERCOT hub average, 36.70, 2026-08 |
| CenterPoint | $95.28 | $22.02 | 23.11% | the same |

## How Samuel uses the intake, in three steps

1. **Type the bill into a CSV in `private/bills/`.** One row per line item: `utility` (CA, SCE, SDGE, TX or TXC), `plan_type`, `period_start`, `period_end`, `kwh`, `line`, `amount` (credits negative), and for Texas `energy_rate` from the plan's Electricity Facts Label. The README lists the columns. Nothing in that folder but the README is ever committed.
2. **Run `node site/scripts/bill-intake.mjs private/bills/<file>.csv`.**
   - It keeps only those columns.
   - It drops any column or line that names a person, address, account, meter or ESI ID, and long digit runs.
   - It writes a fixture to `tests/fixtures/bills/` and prints what it dropped.
   - Read the fixture before committing it.
3. **Run `node site/scripts/test-bill-fixtures.mjs`.** It prints each fixture line by line: the real amount, ours, the difference, the lines only one side has, and the totals. On the fictional example the DCRF differs by $1.21 (the made-up bill used the older rate) and the made-up gross receipts line is "only on the bill".

A test feeds the intake a made-up bill with a name, an address, an account number, an ESI ID and a meter number. None of them survive.

## Verify and ship

| Check | Result |
|---|---|
| Tests | `tests/test_session52.py` 6 tests and `tests/test_session43.py`: 9 OK |
| test-bill | all cases pass |
| Local | check-values 3,809 of 3,809; check-routes 61 of 61 |
| Pushed | e4dc753..2a39875 |
| Live | check-values 3,577 of 3,577 (the five default bills' keys included); check-routes 61 of 61 |
| After the push | the SDG&E season label was corrected to say only what its page says (a change of season falls in June and October), and committed with this report |

## Decisions made without a human

1. **Defaults:**
   - each California bill is set to its season on 2026-10-01: SCE winter, SDG&E summer (labelled an assumption);
   - 20 percent from 4 to 9 p.m., as PG&E's;
   - super off-peak shares from use spread evenly over the hours;
   - SCE Baseline Region 9 (an assumption; the region is on the bill).
2. **SDG&E's baseline allowance is an input defaulting to 0,** rather than a figure from memory.
3. **CenterPoint's tariff overrides its rates page** where they differ.
4. **The wholesale reference** for SCE and SDG&E is CAISO's SP15 zone (Southern California), weighted by CAISO's demand.

## Open questions

1. **SDG&E's baseline allowances** by climate zone, from a tariff sheet as text: where does SDG&E publish them now?
2. **SDG&E's time-period sheet** on sdge.com is from 2018. A current sheet would replace it.
3. **The first real bills** through the intake will show which lines (retailer fees, city taxes) matter most.
