# Chain of 18 November 2026: sessions 2448 to 2461, data machine (lab-desktop), unattended: Rwanda's grid (REG or the regulator RURA), Senegal's (Senelec or the regulator CRSE), Azerbaijan's (the State Statistical Committee), Uzbekistan's (the statistics agency), the licenses' thirty-ninth round

machine: data

Written by session 2434, the first session of `queue/done/117-day-17-november-data-tunisia-egypt-armenia-nepal.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on every branch, was 118 (116 the code machine's, 117 taken). Sessions 2448 to 2461 were free on origin's main and on every branch when this was written. Session 2447 of chain 117 updates it at chain 117's end. Model: Opus 5.5, high effort.

Chain 117 was taken at 11:06 UTC on 24 October by chain 103's agent when chain 113 landed (the owner's instruction: run the file the queue step prints), beside chains 114 and 115 under other agents. The four sources below were chosen by session 2434 among public ones the ERW does not hold (`sources.csv`, the connectors and the queue on main and on chains 114's and 115's branches searched for Rwanda, Senegal, Azerbaijan and Uzbekistan, none found): four more national grids, each a quantity, never a price in another currency. Each source session first confirms that the ERW does not hold its source; a source taken first by a chain beside this one, or held, or whose host, robots file (named AI-agent rules included) or terms bar the reader, is replaced by another public one, and the session says why. Chain 113 holds Costa Rica's CENCE, Austria's E-Control, Luxembourg's ILR and Statistics Iceland; chain 114 Guatemala's AMM, Panama's Secretaria Nacional de Energia and Statistics Mauritius; chain 115 Zambia's Energy Regulation Board, Statistics Botswana's electricity brief, Mongolia's ERC and Georgia's ESCO balances; chain 117 what its sessions 2434 to 2446 take (Tunisia, Egypt, Armenia and Nepal planned).

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout under the data lock (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c057/write_table.sh`, with `VALIDATOR=branch` for a new unit; `runs/c057/method_cells_locked.sh`, whose run validates with main's validator, so a table with a new unit is set back to pass by hand), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); give each write its own session label; a table written again on the branch leaves its older metadata rows to be replaced by key (`runs/c066/s2066/replace_rows_many.py`);
- a publisher's file that can end with the day in progress keeps only the days ended at its retrieval (chain 098's `ended_days`); a file in local time is checked for its time base (chain 101: ONS's Brasilia time stated nowhere) and its daylight-saving days (chain 101: RTE's fixed 96 quarter hours a day);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/117-day-17-november-data-tunisia-egypt-armenia-nepal.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/` and any path holding `archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 117's list and any host chains 114, 115 and 117 add to it; among them www.sciencebase.gov (its robots file disallows `/` for every reader), www.phmsa.dot.gov (HTTP 403), odre.opendatasoft.com (its robots file closes `/api/` and every download to all but Google), nemweb.com.au and www.aemo.com.au (a Cloudflare challenge), www.energy.gov.au and www.aer.gov.au (the connection reset at robots.txt), www.mbie.govt.nz (a bot challenge), opendata.cbs.nl's OData paths, api.scb.se's v1, EirGrid's data (written permission), Eskom's Data Portal (its disclaimer: "may not be exploited by the User for any purposes"), data.gov.tw (HTTP 500 at its robots file), opendata.elia.be (its robots file closes `/api/` and downloads to all but Google), transparency.apg.at (no answer), www.nwd-wc.usace.army.mil (its certificate fails verification), cwms-data.usace.army.mil's time series and DART's `/dart/cs/` (their robots files), www.usbr.gov's `/pn-bin` (its robots file), Terna's data (written permission, personal non-commercial use only), www.tepco.co.jp (HTTP 403 at its robots file), Kansai Transmission and Distribution (its terms forbid reposting), OCCTO's area data (only behind its interactive pages) CAMMESA (cammesaweb.cammesa.com and api.cammesa.com reset the connection), dashboard.elering.ee (its robots file disallows `/` for every reader), www.coordinador.cl's generation pages (HTTP 403), www.statssa.gov.za's publication pages (a bot challenge), XM's data (written permission), www.datos.gob.mx (HTTP 403 at its robots file), and grid-india.in and www.grid-india.in (the connection reset at their robots files). JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID, FRED's API key; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches (74 on main when this was written: chain 101's 73 and 74), agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is `public` or `internal`**; a table whose license is not settled is `internal` until a ruling. A table registered from a source a held table already uses takes a source id of its own.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write, a trial or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout (trials included), waits for it, puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** agreed with the chains running beside it before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted). `tests/test_session152` requires the reads numbered without a gap.
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape;** every file's em and en dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one,** and leaves room for the whole run (a plain upload of seven tables with the metadata tables took 90 requests in session 2185); a long upload runs as a detached process; the branch is merged with main before the upload.
- **A currency other than USD is a standing question for the owner:** a foreign country's prices are not taken; its quantities are.
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **The live site:** from 24 October 2026 (about 02:00 UTC) every page answered HTTP 402 (the Vercel deployment disabled, a question for the owner); the snapshots are still taken on both sides of a push, and a comparison that cannot run is said so in the report.
- **Session 2448 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from the first fourteen free numbers after 2461, a number found taken skipped upward and said so; look on the running chains' wip branches and the code machine's too), commits it alone and pushes it to main before any other work; session 2461 updates it.

- **Hosts closed by chains 104, 105, 106, 108, 109 and 112, not asked again:** seffaflik.epias.com.tr's API (a TGT login ticket), www.nsmo.vn and nsmo.vn (connection timeouts), web.pln.co.id (does not resolve), data.statistics.sk (a timeout), gendata.pucsl.gov.lk (figures only through scripts), nsong.org (a login behind a CAPTCHA), nerc.gov.ng (statistics by script), www.oc.do's /Portals/ (its robots file), www.nepco.com.jo and www.memr.gov.jo (personal non-commercial use only), dosweb.dos.gov.jo's uploads (its robots file), www.eppo.go.th (its website policy: no redistribution or scripted access without permission), data.go.th (HTTP 403 at its robots file), www.egat.co.th's files (its robots file), www.cenace.gob.ec and www.controlrecursosyenergia.gob.ec (their certificates fail verification), datosabiertos.gob.ec (HTTP 403), www.mbie.govt.nz (an Incapsula challenge), osp.stat.gov.lt (a Cloudflare challenge), www.litgrid.eu (its robots file disallows ClaudeBot, anthropic-ai and Claude-Web by name), donnees.hydroquebec.com (robots closes its API and downloads to all but Google), api.neso.energy (robots disallows every path), Terna's data (personal use only), www.tepco.co.jp (HTTP 403), Kansai Transmission and Distribution (its terms), OCCTO's interactive system, CAMMESA's hosts (connection reset), www.ema.gov.sg (a challenge), IEMOP's data and Noga's (their terms), apis.cbs.gov.il, openstat.psa.gov.ph, whose robots file disallows ClaudeBot, anthropic-ai and Claude-Web by name, and, closed by chains 105 and 109, tso.nbpower.com's archive (POST only; its robots file closes `/Reports` and `/SystemInformation`), api.bls.gov (robots disallows every path), opendata.esett.com (its API only in lazily loaded script chunks), seffaflik.epias.com.tr's API (HTTP 406, a login ticket required), www.nsmo.vn and nsmo.vn (connection timeouts), web.pln.co.id (the name does not resolve), data.statistics.sk (a connection timeout) and podaci.dzs.hr (not PxWeb): **every robots file is read for rules that name AI agents, not only `*`.**

- **Hosts closed by chain 110, not asked again:** nepra.org.pk (a Cloudflare challenge), ntdc.gov.pk (plans and annual PDFs only), www.cppa.gov.pk (down for maintenance), pgcb.gov.bd, www.pgcb.gov.bd and bpdb.gov.bd (their certificates fail verification), www.one.org.ma (a fingerprinting bot check), data.gov.ma (closes the connection), www.hcp.ma's /docs/ and /download/ (its robots file), databaza.instat.gov.al (a timeout), pc-axis.geostat.ge (no energy section) and kegoc.kz's files (its robots file; its figures are charts in Kazakh PDFs). **A PxWeb statistics office answers one POST query** (chain 106's Latvian connector).

- **Hosts closed by chain 114, not asked again:** NamPower's site ("All Rights Reserved", no grant), www.ecb.org.na and cnd.enee.hn, where Honduras's ODS redirects (their certificates fail verification), www.ut.com.sv (HTTP 403 from Akamai, even at its robots file), and CND Panama's figures (loaded only by a key from sitioprivado.cnd.com.pa).

- **Hosts closed by chains 113 and 115, not asked again:** EWURA's reports (www.ewura.go.tz: yearly PDFs behind a menu drawn by script), CNDC Bolivia's figures (www.cndc.bo: a nonce-guarded call), eac.gov.kh (its robots file disallows `/`), www.1212.mn (its certificate fails verification) and opendata.1212.mn (does not resolve); www.hagstofa.is asks a crawl delay of 10 seconds, which is kept.

- **Publishers chain 113 found needing written permission, not asked again:** the Electricity Regulatory Authority of Uganda, ICE and its CENCE (Costa Rica), and Bolivia's CNDC (their verdicts are on record).

Read first: chain 117's note (written by session 2447), sessions 2434 to 2447's reports, chain 115's and chain 114's notes, `docs/reviews/siting-gaps.md`.

## Session 2448: Rwanda's generation and demand (REG or RURA)

Long end 1:30. Pulls: at most 15 requests. Rwanda Energy Group's published statistics or the Rwanda Utilities Regulatory Authority's reports, or the National Institute of Statistics of Rwanda's energy tables (robots and terms first): generation by source, imports and the peak demand, a month or a year, as far back as published within the ceiling; a series table in MWh and MW; prices not taken (RWF); cross-check: a year's generation against `owid_ember_electricity_annual`'s Rwanda.

## Session 2449: Senegal's electricity (Senelec or CRSE)

Long end 1:30. Pulls: at most 15 requests. Senelec's annual reports or the Commission de Regulation du Secteur de l'Energie's published figures, or the national statistics agency's (ANSD) energy tables (robots and terms first): generation by source, purchases from independent producers and the peak demand, a year, as far back as published within the ceiling; a series table in MWh and MW; prices not taken (XOF); cross-check: a year's generation against Ember's Senegal.

## Session 2450: Azerbaijan's electricity balance (the State Statistical Committee)

Long end 1:30. Pulls: at most 15 requests. The State Statistical Committee of the Republic of Azerbaijan's energy tables (robots and terms first): generation by source, exports, imports and consumption, a year or a month, within the ceiling; a series table in MWh; cross-check: a year's generation against Ember's Azerbaijan.

## Session 2451: Uzbekistan's electricity (the statistics agency)

Long end 1:30. Pulls: at most 15 requests. The National Statistics Committee of Uzbekistan's open data (stat.uz, its tables or its open data portal; robots and terms first): generation and consumption of electricity, a year or a month, by region if published, within the ceiling; a series table in MWh; cross-check: a year's generation against Ember's Uzbekistan. If the hosts bar the reader, another public grid source, and the session says why.

## Session 2452: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named on a note's `Tables:` line or by a note's file name on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2453: the licenses' thirty-ninth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 117 did not reach, those of sessions 2448 to 2451 and 2454 to 2455 first; `license_verdicts.csv` read first; a verdict's read recorded with the outcome exactly `read`; the bound of `tests/test_session205.py` raised if the round needs it.

## Session 2454: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2455: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2454.

## Session 2456: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2457: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first and the branch merged with main. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables and any public table an earlier chain left for the next draft (chain 113's note: `hagstofa_iceland_power_annual`; chain 110's: `eurostat_crude_imports_monthly`), in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2458: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2459: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2460: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2454.

## Session 2461: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2448) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
