# Chain of 29 November 2026: sessions 2602 to 2615, data machine (lab-desktop), unattended: the Solomon Islands' electricity (the NSO or Solomon Power), the Cook Islands' (the Statistics Office or Te Aponga Uira), Sierra Leone's (Stats SL, EDSA or EGTC), Djibouti's (INSTAD or EDD), the licenses' fiftieth round

machine: data

Written by session 2588, the first session of `queue/done/128-day-28-november-data-mauritania-mali-papua-new-guinea-curacao.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on every branch, was 129 (128 taken). Sessions 2602 to 2615 were free on origin's main and on every branch when this was written. Session 2601 of chain 128 updates it at chain 128's end. Model: Opus 5.5, high effort.

Chain 128 was taken on 25 October by chain 127's agent when chain 127 landed (the owner's instruction: run the file the queue step prints). Chains 118, 119 and 120 were still unlanded, without an agent. The four sources below were chosen by session 2588 among public ones the ERW does not hold (`sources.csv`, the license record and the queue on main searched for the Solomon Islands, the Cook Islands, Sierra Leone and Djibouti: none appears): four more national grids, each a quantity, never a price in another currency. Djibouti's publishers write in French. Each source session first confirms that the ERW does not hold its source; a source taken first by a chain beside this one, or held, or whose host, robots file (named AI-agent rules included) or terms bar the reader, is replaced by another public one, and the session says why. Chains 118 to 128 hold what their sessions take (chain 127: Samoa and Hawaii; chain 128: Mauritania, Mali, Papua New Guinea and Curacao planned).

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout under the data lock (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c057/write_table.sh`, with `VALIDATOR=branch` for a new unit; `runs/c057/method_cells_locked.sh`, whose run validates with main's validator, so a table with a new unit is set back to pass by hand), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); give each write its own session label; a table written again on the branch leaves its older metadata rows to be replaced by key (`runs/c066/s2066/replace_rows_many.py`);
- a publisher's file that can end with the day in progress keeps only the days ended at its retrieval (chain 098's `ended_days`); a file in local time is checked for its time base (chain 101: ONS's Brasilia time stated nowhere) and its daylight-saving days (chain 101: RTE's fixed 96 quarter hours a day);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/128-day-28-november-data-mauritania-mali-papua-new-guinea-curacao.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/` and any path holding `archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 128's list and any host chains 118 to 128 add to it; among them www.sciencebase.gov (its robots file disallows `/` for every reader), www.phmsa.dot.gov (HTTP 403), odre.opendatasoft.com (its robots file closes `/api/` and every download to all but Google), nemweb.com.au and www.aemo.com.au (a Cloudflare challenge), www.energy.gov.au and www.aer.gov.au (the connection reset at robots.txt), www.mbie.govt.nz (a bot challenge), opendata.cbs.nl's OData paths, api.scb.se's v1, EirGrid's data (written permission), Eskom's Data Portal (its disclaimer: "may not be exploited by the User for any purposes"), data.gov.tw (HTTP 500 at its robots file), opendata.elia.be (its robots file closes `/api/` and downloads to all but Google), transparency.apg.at (no answer), www.nwd-wc.usace.army.mil (its certificate fails verification), cwms-data.usace.army.mil's time series and DART's `/dart/cs/` (their robots files), www.usbr.gov's `/pn-bin` (its robots file), Terna's data (written permission, personal non-commercial use only), www.tepco.co.jp (HTTP 403 at its robots file), Kansai Transmission and Distribution (its terms forbid reposting), OCCTO's area data (only behind its interactive pages) CAMMESA (cammesaweb.cammesa.com and api.cammesa.com reset the connection), dashboard.elering.ee (its robots file disallows `/` for every reader), www.coordinador.cl's generation pages (HTTP 403), www.statssa.gov.za's publication pages (a bot challenge), XM's data (written permission), www.datos.gob.mx (HTTP 403 at its robots file), and grid-india.in and www.grid-india.in (the connection reset at their robots files). JODI (jodidata.org) is not pulled.
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
- **The live site:** from 24 October 2026 (about 02:00 UTC) every page answered HTTP 402 (the Vercel deployment disabled, a question for the owner); by chain 126's landing (25 October, 02:09 UTC) every page answered 200 again and Vercel deployed each push. The snapshots are taken on both sides of a push, and a comparison that cannot run is said so in the report.
- **Session 2602 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from the first fourteen free numbers after 2615, a number found taken skipped upward and said so; look on the running chains' wip branches and the code machine's too), commits it alone and pushes it to main before any other work; session 2615 updates it.

- **Hosts closed by chains 104, 105, 106, 108, 109 and 112, not asked again:** seffaflik.epias.com.tr's API (a TGT login ticket), www.nsmo.vn and nsmo.vn (connection timeouts), web.pln.co.id (does not resolve), data.statistics.sk (a timeout), gendata.pucsl.gov.lk (figures only through scripts), nsong.org (a login behind a CAPTCHA), nerc.gov.ng (statistics by script), www.oc.do's /Portals/ (its robots file), www.nepco.com.jo and www.memr.gov.jo (personal non-commercial use only), dosweb.dos.gov.jo's uploads (its robots file), www.eppo.go.th (its website policy: no redistribution or scripted access without permission), data.go.th (HTTP 403 at its robots file), www.egat.co.th's files (its robots file), www.cenace.gob.ec and www.controlrecursosyenergia.gob.ec (their certificates fail verification), datosabiertos.gob.ec (HTTP 403), www.mbie.govt.nz (an Incapsula challenge), osp.stat.gov.lt (a Cloudflare challenge), www.litgrid.eu (its robots file disallows ClaudeBot, anthropic-ai and Claude-Web by name), donnees.hydroquebec.com (robots closes its API and downloads to all but Google), api.neso.energy (robots disallows every path), Terna's data (personal use only), www.tepco.co.jp (HTTP 403), Kansai Transmission and Distribution (its terms), OCCTO's interactive system, CAMMESA's hosts (connection reset), www.ema.gov.sg (a challenge), IEMOP's data and Noga's (their terms), apis.cbs.gov.il, openstat.psa.gov.ph, whose robots file disallows ClaudeBot, anthropic-ai and Claude-Web by name, and, closed by chains 105 and 109, tso.nbpower.com's archive (POST only; its robots file closes `/Reports` and `/SystemInformation`), api.bls.gov (robots disallows every path), opendata.esett.com (its API only in lazily loaded script chunks), seffaflik.epias.com.tr's API (HTTP 406, a login ticket required), www.nsmo.vn and nsmo.vn (connection timeouts), web.pln.co.id (the name does not resolve), data.statistics.sk (a connection timeout) and podaci.dzs.hr (not PxWeb): **every robots file is read for rules that name AI agents, not only `*`.**

- **Hosts closed by chain 110, not asked again:** nepra.org.pk (a Cloudflare challenge), ntdc.gov.pk (plans and annual PDFs only), www.cppa.gov.pk (down for maintenance), pgcb.gov.bd, www.pgcb.gov.bd and bpdb.gov.bd (their certificates fail verification), www.one.org.ma (a fingerprinting bot check), data.gov.ma (closes the connection), www.hcp.ma's /docs/ and /download/ (its robots file), databaza.instat.gov.al (a timeout), pc-axis.geostat.ge (no energy section) and kegoc.kz's files (its robots file; its figures are charts in Kazakh PDFs). **A PxWeb statistics office answers one POST query** (chain 106's Latvian connector).

- **Hosts closed by chain 114, not asked again:** NamPower's site ("All Rights Reserved", no grant), www.ecb.org.na and cnd.enee.hn, where Honduras's ODS redirects (their certificates fail verification), www.ut.com.sv (HTTP 403 from Akamai, even at its robots file), and CND Panama's figures (loaded only by a key from sitioprivado.cnd.com.pa).

- **Hosts closed by chains 113 and 115, not asked again:** EWURA's reports (www.ewura.go.tz: yearly PDFs behind a menu drawn by script), CNDC Bolivia's figures (www.cndc.bo: a nonce-guarded call), eac.gov.kh (its robots file disallows `/`), www.1212.mn (its certificate fails verification) and opendata.1212.mn (does not resolve); www.hagstofa.is asks a crawl delay of 10 seconds, which is kept.

- **Publishers chain 113 found needing written permission, not asked again:** the Electricity Regulatory Authority of Uganda, ICE and its CENCE (Costa Rica), and Bolivia's CNDC (their verdicts are on record).

- **Hosts closed by chains 114 (later sessions) and 117, not asked again:** comisionenergia-my.sharepoint.com, where Chile's Energia Abierta keeps its files (its robots file disallows `/`), www.steg.com.tn (a connection timeout at its robots file) and data.industrie.gov.tn (HTTP 503, under maintenance); bdl.stat.gov.pl answers HTTP 429 after a few requests (1,000 a day across every reader), so it is not planned on a day another chain used it.

- **Hosts closed by chain 117's later sessions, not asked again:** armstatbank.am (its certificate fails verification), armstat.am and www.armstat.am (HTTP 500 at their robots files), www.nea.org.np (a "Security Access Restricted" page served at its robots file), ben.miem.gub.uy (does not resolve) and catalogodatos.gub.uy (HTTP 500 at its robots file). Statistics Canada's robots file disallows paths ending in `.csv`; its tables' `.zip` downloads are open. stat.gov.kg's open data are CC BY-NC-SA 4.0.

- **Publishers chain 117 found needing written permission, not asked again:** the Egyptian Electricity Holding Company (EEHC) and Tunisia's Ministry of Industry, Mines and Energy (their verdicts are on record).

- **Hosts closed by chain 119, not asked again** (added by its session 2475): www.cienergies.ci (does not resolve), www.jpsco.com's reports (an Incapsula challenge), www.edl.com.la (a script shell with no figures), www.mem.gov.la (a timeout at its robots file), laosis.lsb.gov.la (its certificate fails verification) and www.enecho.meti.go.jp (HTTP 403 at its robots file). Jamaica's OUR gives no generation statistics and STATIN links none. ANARE-CI (Côte d'Ivoire's regulator) states no terms of reuse; its table is internal.

- **Hosts and publishers closed by chain 120, not asked again:** www.statsethiopia.gov.et (does not resolve); Ethiopian Electric Power (www.eep.com.et) needs written permission (its verdict is on record). Bhutan's statistics bureau holds no energy table, and Trinidad and Tobago's regulator gives two years a report in prose. Statistics Canada's archived 25-10-0017-01 holds fuel quantities only, in units the standard lacks.

- **Hosts closed by chain 121, not asked again** (added by its session 2503): www.km.qa and km.qa (a firewall's "Request Rejected" page served at their robots files), www.psa.gov.qa (a connection timeout), www.data.gov.qa (its robots file closes `/api/` and every download to all but Googlebot), www.egenco.mw (its certificate fails verification), statsgrd.com (does not resolve) and ckan.open.nrw (the connection reset at its robots file). www.lucelec.com asks a crawl delay of 10 seconds, which is kept. Publishers chain 121 found needing written permission: EWA (Bahrain), ZIMSTAT, NSO Malawi and LUCELEC (their verdicts are on record). Grenada's CSO links its Open Licence Agreement to a dead name and its own page for it is empty; Saint Lucia's CSO licence excludes third-party data. A PxWeb statbank may eliminate a category dimension from an empty query: select every value (chain 121's Faroe connector).

- **Hosts closed by chain 122, not asked again** (added by its session 2517): www.mew.gov.kw (the TLS handshake fails), statisticsguyana.gov.gy (its robots file disallows ClaudeBot, anthropic-ai and Claude-Web by name), pxweb.stat.si (its robots file disallows ClaudeBot by name), www.ceps.cz (its robots file disallows every path) and UNdata's old download handler on data.un.org (HTTP 404). www.nve.no asks a crawl delay of 20 seconds, which is kept. Publishers chain 122 found needing written permission: Vanuatu's URA (its verdict is on record). Kuwait's statistics bureau publishes behind Arabic form postbacks; CYSTAT's database holds no electricity table; IPTO's data are a file a day. A source session may first check the publisher's llms.txt, as stat.gl's names its API.

- **Hosts closed by chain 123, not asked again** (added by its session 2531): www.electra.cv (its robots file disallows every path to every agent) and www.sec.gov.sc (does not resolve). Publishers chain 123 found needing written permission: NBS Seychelles (its verdict is on record). The Seychelles PUC's publication lists load by script; Belize's Energy Unit draws its annual report's figures as charts; the Barbados Statistical Service and BL&P publish no electricity table; ARME's (Cabo Verde) electricity reports list no file; MONSTAT gives its balance of electricity in a release's prose. ASKdata (Kosovo) is a PxWeb API whose "MWH" figures are thousands of MWh: check a statistics office's scale against EIA's world table.

- **Hosts closed by chain 124, not asked again** (added by its session 2545): www.ceet.tg (its certificate fails verification), stat.gov.lv (HTTP 403 at its robots file) and www.mekh.hu (its robots address serves the site's script shell; every page is drawn by script). instad.bj and direction-energie.gouv.bj answered HTTP 503 for maintenance (not closed: a later chain may ask again); ARE Benin's document lists load by script. Publishers chain 124 found needing written permission: INSTAT (Madagascar), ARSEL (Cameroon), INSEED (Togo), SBEE and ARE (Benin), whose sites state only a copyright line, and NSI Bulgaria, whose licence forbids derivative or collective works (their verdicts are on record). Romania's INS gives its electricity balance as year-to-date totals only. A page may hold its figures' data as base64 CSV links (DfE Northern Ireland's report), and a terms page its text inside a script (SingStat's): read both from the saved page.

- **Hosts closed by chain 125, not asked again** (added by its session 2559): nso.gov.mt (a Cloudflare challenge at its robots file), www.ine.gob.ni (its certificate fails verification), legacy.doe.gov.ph (the name does not resolve), opendata.fcsc.gov.ae (it redirects to bayanat.ae, which does not answer) and www.me.gov.bn (a connection timeout). CNDC Nicaragua draws only the day in progress by script; KSH Hungary draws its STADAT lists by script; doe.gov.ph answers a file's address with its site's page; DEPS Brunei's electricity workbooks answer 404; NBS China's yearbook tables are images. Publishers chain 125 found needing written permission: DERK (Bosnia and Herzegovina), CNDC (Nicaragua), Enemalta (Malta) and DEPS (Brunei) (their verdicts are on record). GASTAT's grant excepts clearly identified third-party material, and its electricity tables name the Ministry of Energy as their source.

- **Hosts closed by chain 126, not asked again** (added by its session 2573): www.sonabel.bf and www.gov.sz (connection timeouts at their robots files), www.esera.co.sz (does not resolve), www.stelco.com.mv (a Cloudflare challenge at its robots file), www.ura.gov.mv (its pages drawn by script), m.inei.gob.pe (its certificate fails verification) and www.gub.uy (the connection reset at its robots file); www.ande.gov.py stays closed (chain 114), and chain 126 asked its robots file again in error. statistics-suriname.org asks a crawl delay of 30 seconds, which is kept (chain 126 missed it once by six seconds: put the wait in the same command as the request). INE Chile's electricity figures are a production index whose files load by script; INE Chile's licence is CC BY-SA 4.0. Publishers chain 126 found needing written permission: EEC (Eswatini), ARSE (Burkina Faso), NBS (the Maldives, no terms stated), EBS (Suriname) and VMME (Paraguay, no terms stated) (their verdicts are on record). INSD (Burkina Faso) gives an open data licence that excludes third parties' data. BCRPData (Peru's central bank) answers ten series a request through its API and allows reproduction with the source cited. A statistics office's workbook may state a unit its cells do not hold (NBS Maldives' table 12.2, kWh under a '000 kWh heading): check it against another table or EIA's.

- **Hosts closed by chain 127, not asked again** (added by its session 2587): www.ons.dz and www.onei.gob.cu (their certificates fail verification), www.creg.dz, www.economie.gouv.ga and www.stats.gov.bs (the names do not resolve), library.sprep.org (a Cloudflare challenge at its robots file) and bcn.gob.ni (a Radware CAPTCHA page; its robots file allows the reader). dbedt.hawaii.gov asks a crawl delay of 10 seconds, which is kept. Algeria's Ministry of Energy no longer serves its 2022 energy balance at the address searches give, and CREG's key figures are images; DGS Gabon's publications end in 2012 and SEEG publishes no figures; URCA's annual report gives generation only as chart labels; TEIAS's report files load by a script route kept in lazily loaded chunks. Publishers chain 127 found needing written permission: SBS (Samoa), Algeria's Ministry of Energy, DGS and SEEG (Gabon), URCA (the Bahamas) and DBEDT (the State of Hawaii) (their verdicts are on record). A WordPress publisher lists its files at `/wp-json/wp/v2/media` (search or mime_type), one request, robots allowing. In a reads spec for `runs/c121/add_reads.py`, quote every outcome: an unquoted comma cuts it (chain 127 restored four).

- **Test 378 allows no table flagged internal where its verdict reads "may be public"** (chain 114's landing): a table whose publisher grants reuse with a citation is public with the citation in its header, and the question goes to the owner.

Read first: chain 128's note (written by session 2615), sessions 2602 to 2615's reports, chain 127's note, `docs/reviews/siting-gaps.md`.

## Session 2602: the Solomon Islands' electricity (the NSO or Solomon Power)

Long end 1:30. Pulls: at most 15 requests. The Solomon Islands National Statistics Office's (NSO) tables, or Solomon Power's published figures (robots and terms first): generation and sales, a year or a month, within the ceiling; a series table in MWh; prices not taken (SBD); cross-check: a year's generation against `eia_world_electricity_annual`'s Solomon Islands.

## Session 2603: the Cook Islands' electricity (the Statistics Office or Te Aponga Uira)

Long end 1:30. Pulls: at most 15 requests. The Cook Islands Statistics Office's tables, or the utility Te Aponga Uira's or the Office of the Prime Minister's renewable energy figures (robots and terms first): generation by source and sales, a quarter, a month or a year, within the ceiling; a series table in MWh; prices not taken (NZD); cross-check: a year's generation against EIA's Cook Islands.

## Session 2604: Sierra Leone's electricity (Stats SL, EDSA or EGTC)

Long end 1:30. Pulls: at most 15 requests. Statistics Sierra Leone's tables, or the distributor EDSA's, the generator EGTC's or the regulator EWRC's published figures (robots and terms first): generation by source and sales, a year or a month, within the ceiling; a series table in MWh; prices not taken (SLE); cross-check: a year's generation against EIA's Sierra Leone.

## Session 2605: Djibouti's electricity (INSTAD or EDD)

Long end 1:30. Pulls: at most 15 requests. The Institut National de la Statistique de Djibouti's (INSTAD) yearbook, or the utility EDD's published figures (robots and terms first): production, imports from Ethiopia and sales, a year or a month, within the ceiling; a series table in MWh; prices not taken (DJF); cross-check: a year's generation against EIA's Djibouti. Its publishers write in French. If the hosts bar the reader, another public grid source, and the session says why.

## Session 2606: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named on a note's `Tables:` line or by a note's file name on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes. Many are described in a note's text already (chain 117's session 2438): a `Tables:` line added to that note serves.

## Session 2607: the licenses' fiftieth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 128 did not reach, those of sessions 2602 to 2605 and 2608 to 2609 first; `license_verdicts.csv` read first; a verdict's read recorded with the outcome exactly `read`; the bound of `tests/test_session205.py` raised if the round needs it.

## Session 2608: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2609: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2608.

## Session 2610: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2611: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first and the branch merged with main. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables and any public table an earlier chain left for the next draft, in a plain upload that refreshes the metadata tables from the branch merged with main; `--reconcile`; the release note extended. Nothing released.

## Session 2612: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2613: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2614: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2608.

## Session 2615: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2602) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
