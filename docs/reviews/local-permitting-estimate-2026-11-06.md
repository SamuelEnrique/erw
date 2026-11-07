# Local permitting records for the Friction Index: an estimate for the owner's approval

Session 3409 (chain 202), 6 November 2026, lab-desktop, fourth window. Twelve requests were made across the candidate
hosts, as the prompt allowed: nine robots files first (one host's name did not resolve), then three reads of what a
host publishes. No record was pulled and nothing is proposed to be pulled without the owner's word. Every request is
a row of `runs/c202/permits/probe.csv`; the bodies are under `runs/license_reads/c202_permits/` (not in git).

## The question

The Friction Index counts opposition as the news reports it. The records of the bodies that decide (county and city
planning commissions, boards of supervisors, state siting boards) would give the outcome side: the agenda item, the
vote, the permit granted or denied, the moratorium adopted, dated and placed. The probe asked which such sources
publish machine-readable records, which bar the ERW's reader, and what a first pull would cost.

## What the probe read

| Host | Kind | Robots | What it publishes | For the reader |
|---|---|---|---|---|
| `webapi.legistar.com` (Granicus Legistar, the agenda system of many cities and counties) | the public web API | no robots file (HTTP 404) | JSON of a client's events, agenda and minutes files, matters and votes (`/v1/<client>/events`, `/matters`, `/votes`); the sample call for one client answered HTTP 500, "LegistarConnectionString setting is not set up in InSite for client: chandler": the API answers only for the clients that have switched it on, and no public list of them was found in the probe | machine-readable where a client enabled it; each client is a separate request and a separate check |
| `chandler.legistar.com` (one Legistar client) | the client's own site | no robots file | the web calendar and agenda pages (HTML, PDF agendas) | readable; the API is the better door where it is on |
| `opsb.ohio.gov` (Ohio Power Siting Board) | the board's site | allows, except its search paths | an IBM WebSphere portal; the case list is drawn by script, and the case documents live in the commission's docketing system (`dis.puc.state.oh.us`) | the portal is readable; the documents are not (next row) |
| `dis.puc.state.oh.us` (Ohio's docketing system, the siting board's documents) | the docket | **names forty agents, `anthropic-ai` and `ClaudeBot` among them, with `Disallow: /`;** no wildcard rule | the case documents, filings and orders | **barred for the ERW's reader** by the rule the memory of session 2309 sets: a host that names an AI agent is honoured, whatever user agent the connector sends |
| `apps.psc.wi.gov` (Wisconsin PSC, the ERF docket system and siting cases) | the docket | `*` allowed with `Content-Signal: search=yes, ai-train=no, use=reference`; **`anthropic-ai`, `ClaudeBot` and twenty others `Disallow: /`;** a second `*` block says `Disallow: /` | the dockets of generation and transmission siting (CPCN cases) | **barred for the ERW's reader** by the same rule, and ambiguous for everyone (two `*` blocks) |
| `ores.ny.gov` (New York's Office of Renewable Energy Siting) | the siting office | the name did not resolve | | not reached; the office's documents are on `dps.ny.gov`'s DMM system, not probed |
| `www.datacenterwatch.org` (Data Center Watch) | a tracker of data center opposition | the AI agents are listed in the same block as `*`: the ordinary disallows only (`/config`, `/search`, `/api/`, `/account`) | "a boutique research firm tracking the growing opposition to data center development": quarterly reports (2023 to Q1 2025, Q2 2025, Q3-Q4 2025, Q1 2026, Q2 2026), a weekly newsletter of local moratoria and withdrawals (text, by county and state), media coverage | readable as text; **no machine-readable table** seen; the reports are the firm's product and their terms were not found on the page read: a license question before any use |
| `www.loudoun.gov` (Loudoun County, Virginia, the largest data center county) | the county's site | allows, except admin and search paths | the planning commission's agendas and minutes are on the county's agenda host (Granicus or Laserfiche), not on this host, not probed | the next probe's first stop, with the agenda host's robots |
| `comptroller.texas.gov` (the Texas data center sales tax exemption) | a state list | `Disallow: /*/` with `Allow: /economy/`, `/data/` and others | the list of qualifying data center projects by county (a registry of projects, not of opposition) | readable; a place list for the outcome side, not for friction; not asked in this probe |

## What a first pull would be, and cost

- **The one machine-readable door found is Legistar's web API,** for the clients that switched it on. A first pull
  would: (1) take a list of the counties and cities with data center or energy siting disputes in the ERW's own link
  table (`attention_story_links`, the `place` field: 337 stories name a state and a few dozen name a county or city
  so far); (2) for each, find whether its agenda system is Legistar, and whether the API answers (one request each,
  `GET /v1/<client>/events?$top=1`); (3) for those that answer, read the events of the last twelve months with their
  agenda and minutes file links and the matters whose title holds "data center", "solar", "wind", "battery",
  "pipeline", "substation", "transmission" or "moratorium" (two or three requests a client a month). For thirty
  clients: about ninety requests to set up and about a hundred a month after, a few megabytes of JSON a month, no
  model needed for the agenda items' titles and the votes (a model would read the minutes' PDF only where the vote is
  not in the structured fields: a cost of about USD 0.01 a document on Haiku, a few dollars a month).
- **The state siting boards** that matter most for energy projects (Ohio, Wisconsin) bar AI agents by name in their
  docket systems and are not read. New York's and others' (California's CEC, Minnesota's, Michigan's new siting
  authority) were not probed within the twelve requests; each needs its robots read first.
- **The trackers of data center moratoria** (Data Center Watch) publish text for people, not a table; a use of their
  counts would need their permission and a citation, and would be a secondary source. The ERW's own Friction Index
  already counts the same moratoria as the news reports them.
- **Cost of the first pull, in all:** about two sessions of work, under 300 requests, no model spend beyond a few
  dollars for minutes without structured votes; storage in kilobytes. The output would be a table of agenda items and
  votes on energy and data center matters by county, dated: the outcome side the research memo's paper needs
  (`docs/reviews/attention-paper-notes-2026-11-06.md`).

## What bars the reader, in one list

- `dis.puc.state.oh.us` and `apps.psc.wi.gov`: AI agents named with `Disallow: /`. Not read; a pause row is not needed
  because no connector asks them, but a note in `docs/methods/attention.md`'s limits names them.
- `ores.ny.gov`: no answer to the name.
- Legistar clients without the API switched on (Chandler, Arizona, in the sample).

## For the owner's ruling

1. Start the Legistar first pull (about thirty clients drawn from the link table's places, about 300 requests, no
   model spend of note), as a new source `legistar_agenda_items` with the Granicus terms read first?
2. Ask Data Center Watch for permission to cite their quarterly counts, or leave them aside?
3. Probe the other state siting boards (California, New York's DMM, Minnesota, Michigan) in a later session, twelve
   requests at a time, robots first?

Nothing of this is started. The twelve requests are the probe's whole footprint.
