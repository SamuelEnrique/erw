# SEC EDGAR Form D: a probe, for the owner's approval (session 3305, chain 200)

6 November 2026, 20:14 UTC, lab-desktop. Asked by chain 200's prompt: whether SEC EDGAR's Form D index files can fill energy issuers' raises by quarter for `/capital` (platform tool 11), their size, their license, and the requests a pull would take, written as an estimate; ten requests at most, robots and the fair-access policy first, a named user agent, nothing pulled beyond the probe.

## What the probe asked, and what it was told

| # | Request | Answer |
|---|---|---|
| 1 | `GET https://www.sec.gov/robots.txt`, user agent `Energy Research Warehouse ERW-connector/0.1 (research probe; +https://github.com/SamuelEnrique/erw)` | **HTTP 403**, a page titled "Request Rate Threshold Exceeded": "Automated access to our sites must comply with SEC.gov's Privacy and Security Policy. Please visit www.sec.gov/developer for more developer resources and Fair Access guidelines." (reference 0.60a7cb17.1793996068.d14ecf26; the body kept under `runs/license_reads/s3305/`, not in git) |

One request of the ten was used. The rest were not made: the refusal was of the user agent, not of a page, and every further request to `www.sec.gov` would have drawn the same answer.

## The fair-access policy (read through a search, not from sec.gov)

- SEC's "Accessing EDGAR Data" page (`https://www.sec.gov/os/accessing-edgar-data`, as a web search returned it on 6 November 2026): "Current max request rate: 10 requests/second", and "Please declare your user agent in request headers", with a sample naming a company and an administrator's contact email. The SEC reserves the right to limit request rates.
- The ERW's user agent names the project and its repository but no email. The session's rules say no person's email goes into a request without being asked, so the probe stopped.

## Form D: what is published (from search results; to be confirmed by the first file a pull reads)

- **Form D Data Sets** (`https://www.sec.gov/dera/data/form-d`): structured data from the XML of the Notices of Exempt Offerings of Securities, one ZIP a quarter, documented by a PDF of table definitions. The SEC's page listed quarters to 2025 Q2 when the search indexed it; Data.gov's record lists files to 2025 Q4. The earliest quarter was not confirmed.
- **License**: Data.gov's record of the Form D Data Sets gives the USA.gov public domain label (`http://www.usa.gov/publicdomain/label/1.0/`), access level public. Public, as the prompt expected.
- **Whether it can fill energy issuers' raises by quarter**: Form D's own text asks each issuer its industry group, with energy groups among them (coal mining, electric utilities, energy conservation, environmental services, oil and gas, other energy), the total offering amount, the amount sold and the date of first sale. If the data sets carry those fields as the form asks them (not confirmed: the table-definition PDF was not read), they give raises by quarter, by energy group and by issuer, disclosed amounts only, with "indefinite" offerings counted apart. They are notices of exempt offerings: private placements, not every financing (no bank loans, no public offerings, no project debt).
- **Size**: not measured (no request reached a file).

## The estimate for a pull (for the owner's approval)

| Step | Requests |
|---|---|
| robots.txt, read alone first | 1 |
| the Form D Data Sets page (the quarters listed) | 1 |
| the table-definition PDF | 1 |
| one ZIP a quarter, 2015 Q1 to the newest (about 44 quarters to 2025 Q4) | about 44 |
| **Total** | **about 47**, at one request a second (a tenth of SEC's ceiling) |

- **Needed first**: a user agent the SEC accepts: a company name and a contact email the owner names. Without it every request answers 403.
- Pulling filings one by one (each Form D's `primary_doc.xml`) instead would take one request a filing, many thousands a year; the quarterly data sets are the route.
- Nothing was pulled. No source was added to the registry.

## For Samuel's ruling

- Approve a pull of the Form D Data Sets (about 47 requests), and name the contact email for the user agent; or decline.

Sources of the policy and data set words above: [Accessing EDGAR Data](https://www.sec.gov/os/accessing-edgar-data), [Form D Data Sets](https://www.sec.gov/dera/data/form-d), [Data.gov: Form D Data Sets](https://catalog.data.gov/dataset/form-d-data-sets) (each as a web search returned it; none was fetched from sec.gov after the 403).
