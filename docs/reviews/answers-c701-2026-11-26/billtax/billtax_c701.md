# Data request 53: taxes and local fees on the two default bills (chain 701, 26 November 2026)

The bills are the learning pages' defaults as `site/data/bill_rules.json` and `site/lib/bill.ts` build them: **PG&E E-TOU-C**, bundled service, baseline territory T, Income Tier 3, 600 kWh, 20 percent in peak hours, winter, a 30-day bill (229.63 USD); and **Oncor's area of ERCOT**, 600 kWh, the retailer's energy charge as the input plus Oncor's delivery charges (95.27 USD). The page says taxes and local fees are not included.

Every quote is in `billtax_c701.json` (verify_quotes' "changes" shape) and `billtax_c701.csv`. Documents were read through `docs/research/large_load/fetch_doc.py` on the `erw-c701n` copy and cached under its `runs/s5300/docs`. verify_quotes.py: **cites checked: 24; exact 24**.

## 1. PG&E, San Francisco (bundled E-TOU-C)

| Line | Rate | Applies to | On the default bill |
|---|---|---|---|
| Energy Commission tax (Energy Resources Surcharge) | 0.0003 USD per kWh (2026; CDTFA notice L1020, p. 1: "three-tenths mill ($.0003) per kilowatt-hour"); PG&E Preliminary Statement Part K, Sheet 1: "currently fixed at $0.00030 per kilowatthour", effective January 1, 2019 | each kWh bought from an electrical utility; PG&E states it as a separate item on the bill | 600 x 0.0003 = **0.18 USD** |
| San Francisco Utility Users Tax | 7.5 percent of taxable charges (Treasurer's UUT statement, p. 2: "The Utility Users Tax rate is 7.5%") | charges for electrical energy; **residential customers exempt** under BTRC sec. 707.1 (p. 2) | **0.00 USD** |
| Franchise Fee Surcharge, Schedule E-FFS | residential, per kWh: 0.00086 (pre-2009 vintage), 0.00064 (2009), 0.00061 (2010), Sheet 2, effective January 1, 2026; later vintages are on Sheets 2 and 3 but their columns did not read cleanly, so they are not given | direct access and Community Choice Aggregation customers only (Sheet 1) | **0.00 USD** (the default is bundled). A CleanPowerSF home would pay it at its CRS vintage |

So the PG&E default with its taxes is 229.63 + 0.18 = **229.81 USD**. Not found: California sales tax treatment of electricity (not read), and any further line on PG&E's own bill pages (not read; see PG&E's terms below).

## 2. Oncor, Dallas (retailer plus Oncor delivery)

| Line | Rate | Applies to | On the default bill |
|---|---|---|---|
| PUC Assessment | one-sixth of one percent of gross receipts (PURA Sec. 16.001(b), the PUCT's edition effective as of September 1, 2025, p. 87) | the retailer's gross receipts from rates charged to the ultimate consumer; if itemized, labelled "PUC Assessment" (16 TAC 25.479, p. 753) | if passed through on the whole bill: 95.27 / 600 = **0.16 USD** |
| Miscellaneous Gross Receipts Tax Reimbursement | **not found** | retailers operating in a city or town of more than 1,000 people (16 TAC 25.479, p. 753); excluded from the EFL "price" (25.475(b)(8), p. 726) | not computed |
| Sales tax (state; City of Dallas) | **not found** | the line is defined (25.479, p. 753): collected for the state, cities and special purpose districts | not computed |
| Municipal franchise charge | a charge per kWh delivered inside the city (PURA Sec. 33.008(b), p. 116); Dallas's figure **not found** | "included in the nonbypassable delivery charges" the retailer pays the wires utility (Sec. 33.008(c), p. 117); Oncor's tariff has no municipal rider (its DCRF formula reads "not including municipal franchise fees", p. 103) | **0.00 USD added**: already inside the delivery charges the default counts |

So the Oncor default with what could be read is 95.27 + 0.16 = **95.43 USD** if the retailer passes the assessment through, before the gross receipts tax reimbursement and any sales tax, whose rates were not found.

## What could not be read, and why

- **comptroller.texas.gov**: its robots file disallows the reader (and `*`) for `/taxes/sales/utility/cities.php` (the list of cities that tax residential gas and electricity, the record for Dallas) and `/taxes/misc-gross-receipts/`. No other Comptroller page was tried.
- **statutes.capitol.texas.gov**: robots allows the reader, but both `Docs/TX/htm/TX.182.htm` and `Docs/TX/pdf/TX.182.pdf` answer with the site's script-only page (an Angular shell, no statute text), so Tax Code sec. 182.022 (the gross receipts tax rates) and sec. 151.317 (the residential exemption) could not be read. The first try at this host failed on a DNS lookup before any request.
- **pge.com**: robots allows the reader (it names NinjaBot, W3C-checklink, GPTBot and `*`), but PG&E's Terms of Use, read after the two tariff sheets, say under "Mining": "No user or third party is authorized to use any software, bots, spiders, or other information-gathering devices or programming routines to monitor, copy, or otherwise "mine" information displayed on the Website for display on or use with any Website or service, except as authorized by PG&E or by a PG&E customer of record." They also allow use "solely for your own internal lawful purposes" and bar use "in publications, other websites or presentations" without consent. No further pge.com page was requested. **For Samuel's ruling**: pge.com is not in fetch_doc.py's refused list, and the site's bill rules already cite pge.com tariff sheets. The Energy Commission tax rate is also given by the CDTFA, whose terms allow reuse; Schedule E-FFS has no second official copy read here.

## Hosts: robots and terms

| Host | Robots (for ERW-research-reader, `*` and Anthropic's agents) | Terms on reuse |
|---|---|---|
| cdtfa.ca.gov | allowed (`*` named) | Conditions of use ("Ownership"): "information presented on this web site, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." |
| sftreasurer.org | allowed (`*` named) | Disclaimer: the law controls over the site; the City "does not certify the authenticity of information that originates from third parties". No reuse limit read |
| www.pge.com | allowed (NinjaBot, W3C-checklink, GPTBot, `*` named) | bars bots that mine information for use on any website or service; internal use only; see above |
| ftp.puc.texas.gov | no robots file (404) | the PUCT's Link Policy (www.puc.texas.gov, robots allowed): "all PUCT content is protected by federal copyright laws"; "Site owners should contact the PUCT to request permission to use or copy content from the PUCT's website." The PURA and rule texts are state law and rules |
| www.oncor.com | allowed (`*` named) | Terms & Conditions: use "for personal, noncommercial, and, as applicable, educational purposes only"; copies must carry Oncor's copyright notice; no framing or deep-linking. No clause on bots or automated reading |
| comptroller.texas.gov | **disallowed** | not read |
| statutes.capitol.texas.gov | allowed (no agents named) | not read (script-only pages) |

## Request count

**38 requests**, under the 40 allowed: 19 reader calls. Two were refused at the Comptroller's robots file (1 request each). One failed on DNS before any request (counted as 1). The other 16 each took a robots request and a document request (32), and three redirects each took one more robots check (www.puc.texas.gov to its trailing-slash address, www.cdtfa.ca.gov to cdtfa.ca.gov, www.oncor.com to its home page): 2 + 1 + 32 + 3 = 38. Documents: Tax Code ch. 182 htm and pdf (shells), the Oncor tariff, the PUCT's chapter 25 rules, PURA (2025 edition), CDTFA L1020, the SF UUT statement, PG&E E-FFS and Preliminary Statement K, PG&E's terms, the PUCT link policy, CDTFA's conditions of use, the Oncor and SF Treasurer home pages (to find their terms links), Oncor's terms and the SF Treasurer's disclaimer. Web searches (to find addresses only): 14.
