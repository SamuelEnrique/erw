# Energy equities: the sources, their robots files and terms (chain 701, part D1)

Energy Research Warehouse (ERW). Written by session 10000 (chain 701) on 26 November 2026, data machine (lab-desktop), before any pull. Every request below is a row of `runs/c701/probe/probe.csv` or `runs/c701/probe/probe_ruled.csv` (copied to `docs/reviews/equities-sources-2026-11-26/`; bodies kept under `runs/license_reads/c701/`, not in git). License codes are those of `docs/price-sources.md` ("License shorthand"); a code that page lacks is spelled out. Nothing was bought and no paid service or key was used.

## What the warehouse and the site held before this chain

- No equity table: `coverage.csv` held no table of share prices, share counts, filings or index levels (the six rows matching "equit" are the sector tag `equities` on `frb_treasury_yields` and the like).
- `docs/price-sources.md`, section 10 (25 September 2026): 34 tickers checked once by Nasdaq's quote endpoint (undocumented, terms unknown, used as a check only); Yahoo ruled out (Yahoo-personal: no automated collection, no redistribution); Tiingo's free plan internal only.
- `company_directory` (14,033 companies, model-extracted from the deals and news): names and roles, no tickers or SEC numbers.
- FRED's tables were retired: its terms forbid storing or redistributing its content without written consent (`warehouse/metadata/license_verdicts.csv`, key FRED, read 12).

## The sources

| Source | What it would give | Address | How far back | Robots file | Terms | License | Verdict |
|---|---|---|---|---|---|---|---|
| SEC EDGAR | the list of companies with SIC codes and tickers (`company_tickers_exchange.json`, each company's `submissions`), every filing, the XBRL company facts (revenue, net income, capital spending, debt, shares outstanding as filed) | https://www.sec.gov/ and https://data.sec.gov/ | XBRL facts from 2009; filings from 1993 | not read: both hosts answered HTTP 403 at `/robots.txt` to the ERW's connector string (requests 1 and 2 of `probe.csv`, 11:37 UTC) and to the owner's ruled contact string "ERW research project, github.com/SamuelEnrique/erw" (`probe_ruled.csv`, 11:38 UTC). The 403 page: "Your Request Originates from an Undeclared Automated Tool ... Please declare your traffic by updating your user agent to include company specific information" (data.sec.gov) and "Request Rate Threshold Exceeded ... Automated access to our sites must comply with SEC.gov's Privacy and Security Policy" (www.sec.gov). `docs/accelerator/large_load_eighty.md` records the same refusal of the ruled string in every earlier pass | US government work, public domain (not read this time: the site refused) | public domain (US government), once readable | **not pulled.** It refuses the ruled contact string. The SEC asks for a user agent naming a company and a contact; no address of a person is sent by the ERW without the owner's word. One line under "For Samuel's ruling". Everything of part D that needs a company's industry code, share count or statements waits on it |
| Nasdaq Trader symbol directory | every US-listed security: ticker, name, listing exchange, ETF flag (no industry code) | https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs (`nasdaqlisted.txt`, `otherlisted.txt`) | today's list only | no robots file (the address answers a "Page Not Available" page, request 3) | "Copyright and Disclaimer" (request 20): the content "may not be copied, reproduced, transmitted, displayed, performed, distributed, rented, sublicensed, altered, stored for subsequent use or otherwise used in whole or in part in any manner without the prior written consent of Nasdaq, except ... one unaltered permanent copy to be used by the viewer for personal and non-commercial use only" | needs written permission (Nasdaq) | **not pulled**: storing is forbidden; and without an industry code the list could not give a segment by a written rule |
| Nasdaq quote pages (nasdaq.com) | daily prices | https://www.nasdaq.com/ | | not read: the connection was reset at `/robots.txt` (request 4) | not read | | **not pulled** (no robots file could be read) |
| NYSE | listed companies, exchange notices | https://www.nyse.com/ | | read (request 5): `Disallow: /cgi-bin/`, `/partial/` only | not read: the NYSE sells its market data (no free end-of-day file was found on the pages read) | | **not pulled** this time; part F reads its terms |
| Stooq | daily prices (CSV) | https://stooq.com/ | decades | read (request 6): `User-agent: *` `Disallow: /` (only Bingbot and Googlebot are allowed) | not read | | **not pulled**: its robots file refuses every other reader |
| Tiingo | end-of-day prices, 30 years and more | https://api.tiingo.com/ | 30+ years | read (requests 7, 8): `Disallow: /admin` only | free plan "Internal Use Only" (`docs/price-sources.md`); the pricing page is drawn by a script and gave 37 characters of text (request 19), so no price was read | internal at most | **not pulled**: it needs an account key the repository does not hold, and even then internal only |
| Alpha Vantage | end-of-day prices | https://www.alphavantage.co/ | 20+ years | none (HTTP 404, request 9) | not read (`docs/price-sources.md`: its terms PDF was not parsed) | not settled | **not pulled**: it needs a key the repository does not hold |
| S&P Dow Jones Indices | the S&P 500 Energy and Utilities sectors and the other energy indices | https://www.spglobal.com/spdji/ | decades | not read: HTTP 403 at `/robots.txt` (request 10) | not read | | **not pulled** |
| State Street (SPDR funds XLE, XOP, XLU) | each fund's NAV by day, a published proxy for its index | https://www.ssga.com/ | from each fund's start | read (request 11): its list does not disallow the fund pages or `/library-content/` | read in part F (request 48, the XLE fund page, 26 November 2026, 14:10 UTC): "The whole or any part of this work may not be reproduced, copied or transmitted or any of its contents disclosed to third parties without State Street Investment Management's express written consent." | needs written permission | **not pulled**: the NAVs may not be copied or passed on without written consent |
| IEX (the exchange) | IEX's own trades only, not a consolidated close | https://iextrading.com/ | from 2016 | read (request 12): nothing disallowed | the market data page links its terms (request 18), not read: IEX's own trades are about a few percent of a stock's volume and give no closing price, so the source does not meet the need; read again in part F (26 November, the same page): its HIST section says "Historical PCAP data is not currently available for direct download." | | **not pulled** (no close, and no download) |
| Cboe | market statistics | https://www.cboe.com/ | | read (request 13): `/book/` and `/*market_statistics/volume_reports/` disallowed | not read | | **not pulled** (the volume reports are disallowed) |
| FRED | a few equity indexes (third party, for example NASDAQCOM) | https://fred.stlouisfed.org/ | | read (request 14): crawl delay 1 | `license_verdicts.csv`, FRED, read 12: no storing or redistribution without the Bank's written consent | FRED-3P | **not pulled** (its tables were retired for these terms) |
| Yahoo | prices of all of them | | | | Yahoo-personal | Yahoo-personal | **not pulled** (`docs/price-sources.md`) |

## What part D can build today

- **Nothing that needs the SEC**: the universe's industry codes (the segment rule is written on SIC codes, so no company is put in a segment by judgment), the share counts, the statements, and so the value-weighted lines.
- **No daily price of any company or index from a source whose terms allow the ERW to keep it.** The price columns of every file of `docs/state/page_files_equities.md` stay null with `held` "license needed" (or "source needed"), as the contract allows.
- The energy prices set beside them (WTI, Brent, Henry Hub, the public power hubs, uranium, carbon) are the warehouse's own and need no new source: `site/data/equities/energy_prices.json` can be written from them now.

## Paid routes (also in `docs/licenses_costs.md`)

- Tiingo's redistribution tier: no price could be read (the pricing page is drawn by a script).
- S&P Dow Jones Indices: its site refused the robots request; no price read.
- Nasdaq's symbol directory and indexes: written permission; no price stated on the terms page.

## For Samuel's ruling

- **The SEC refuses the ERW's contact string.** EDGAR (company list with industry codes, filings, statements, share counts; public domain) answers 403 to "ERW research project, github.com/SamuelEnrique/erw" and asks for "company specific information" in the user agent, which in the SEC's own examples is a name and an e-mail address. With a contact address you choose (a project address would do), every company, share count and statement line of part D can be read. Default: not pulled, and the equities files carry the energy prices and blanks.
- **No free daily share price may be kept.** Every free source read either refuses automated readers (Stooq, Yahoo), forbids storing (Nasdaq), or needs a key and is internal only (Tiingo, Alpha Vantage). Default: prices drawn blank with "license needed".

## Read again in part F (26 November 2026)

- State Street's fund pages: written consent needed (request 48; the row above).
- IEX: no historical download at all (the HIST section of the market data page, request 18).
- Nasdaq: its robots file was not asked again: the probe asks an address once a chain (request 4 was reset); left for the next chain.
- Alpha Vantage: still needs a key the repository does not hold; its terms were not read.

## Read again (part F, 26 November 2026, 22:53 to 22:57 UTC)

The sources whose robots file or terms were not read the first time, read once more through `docs/research/large_load/fetch_doc.py` (robots first, each host's own robots file, Nasdaq's 30-second crawl delay kept between its requests). The answers are cached under `runs/s5300/docs/` on lab-desktop (not in git).

| Source | Robots file | Terms | Verdict |
|---|---|---|---|
| Nasdaq (nasdaq.com) | read: `Crawl-delay: 30` for every agent; `/api/v1/*` and the option chains disallowed; no AI agent named | read at `/legal` (`/terms-of-use` answers 404): "Not access or use the Service, or any process, whether automated or manual, to capture data or content from the Service"; the license is "solely for your personal, non-commercial use"; no content shared or copied "without Nasdaq's prior written approval" | **closed**: automated capture is barred |
| S&P Dow Jones Indices (spglobal.com) | read: the index exports and factsheets disallowed (`/spdji/*/idsexport*/`, `/spdji/*/idsfactsheet*/`, `/spdji/*/idsenhancedfactsheet*/`); GPTBot given a crawl delay, no Anthropic agent named | not read: `/en/terms-of-use` answers HTTP 403 | **closed**: the paths that carry index levels are disallowed |
| NYSE (ICE's terms) | nyse.com read the first time (nothing relevant disallowed); www.ice.com's read now (the terms page allowed) | read at `ice.com/privacy-security-center/terms-of-use` (the link nyse.com gives): a licence "only for your own personal, non-commercial use"; "spiders, robots, avatars, agents, tools or other devices or mechanisms to navigate, search or determine this Website is strictly prohibited, unless expressly permitted by ICE" | **closed** |
| IEX | read the first time (nothing disallowed) | not read: the market data page's "Terms of Use" link is malformed (`www.iexexchange.io/https://iex.io/legal/terms/index`) and `iex.io/legal/terms/index` answers 404 | unchanged: not pulled (IEX's own trades are not a consolidated close) |

Nothing here changes D2 and D3: the equity tables still wait on the SEC ruling and on a price source whose licence allows it. Stooq (robots refuse every reader but two search engines) and Alpha Vantage (a key the repository does not hold) were not asked again.
