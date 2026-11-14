# Large loads' connection rules

Energy Research Warehouse (ERW), method note written in session 2924 (chain 153, 6 November 2026) for the table first
written that day.

Table: `large_load_connection_rules` (events, public). Connector: `warehouse/connectors/large_load_connection_rules.py`.
Registry: `warehouse/sources/large_load_connection_rules/` (one file a document; its README gives the form).

## What a row is

One step a grid operator's or a utility's document states for connecting a large load: who acts (`parties`), what the
step is (`x_step`), and what the document states of its time: a number and its unit (`x_duration`, `x_duration_unit`:
business days, calendar days, days, months or years), a date (`event_date`, `x_date_kind` "stated date"), or neither.
Each row carries the words the step is printed in (`x_printed`) and where (`x_section`, `x_page` where the document has
pages). A load size the step prints is `mw`.

A step that states no time is a row too, with its words and no duration: the siting gaps' "the faster path for a
controllable load" is such a row (ERCOT Planning Guide 9.6.1(1): a PCLR is energized with its consumption capped, and
no duration is stated for the conditions that lift the cap).

## What is not done

- No step is summed into a "time to connect": the steps run in parallel, in sequence or only on a condition, as each
  document says, and a sum would be an inference.
- Business days are never converted to calendar days.
- No duration is read from a chart, a slide or a summary: only from the document's own text.
- A document whose terms or robots file bar the reader is not read (Con Edison, Eversource and Duquesne Light, session
  2921; MISO is paused; the Virginia SCC is paused).

## The documents held (6 November 2026, session 2938)

| Document | Body | Date | Steps | Read |
|---|---|---|---|---|
| ERCOT Planning Guide, Section 9 (`09-071126.docx`) | ERCOT | 2026-07-11 | 22 (Batch Zero 9.2 to 9.6; the legacy study 9.8 and 9.9) | session 2905's fetch, read again by 2919 |
| PG&E Electric Rule No. 30 (interim, Advice 7772-E) | PG&E | 2025-12-04 | 4 | session 2921's fetch |
| FERC's order on SPP's HILL and HILLGA processes (ER26-247-000, 194 FERC 61,031) | SPP, as the order states its Tariff | 2026-01-14 | 13 | the copy saved on 8 October 2026 (`large_load_statements`, reused by `large_load_rules`), no new request; added by session 2938 |

## License

Public, row by row. ERCOT's terms let raw data in public portions of its site be reproduced in compilations (licenses.md
#2); PG&E's Rule 30 is its CPUC-filed tariff sheet, and PG&E's site states no terms on its tariff pages (a question for
the owner, session 2921).

## Chain 211: the operators' documents from the owner's research file (session 3762)

The research file of 6 November 2026 (`docs/reviews/research/large-load-tariffs-2026-11-06.md`, its operator table) was
used as leads. Each step was read in the operator's own document: robots first, one GET each (`runs/s3762/probe.py`), each
step written with its page and printed words. The table has no status column of its own, so a document that is a proposal
says so in its name and its steps say "(proposed)".

| Document | Body | Date | Steps | Status |
|---|---|---|---|---|
| Board letter on the CIFP for Large Load Additions, with Appendix C (Expedited Interconnection Track) | PJM | 2026-01-16 | 7 | decided by the Board; FERC's acceptance not read |
| Show Cause for Large Loads Approach, CLLSCO workshop | PJM | 2026-09-30 | 5 | proposal (the deck marks large-load values as estimates) |
| Large Loads Considerations, Straw Proposal | CAISO | 2026-08-11 | 3 | proposal |
| Large Load Update, Board hearing (the batch study framework) | ERCOT | 2026-04-01 | 2 (one a statistic) | deck |
| Project No. 58000, Proposal for Publication (16 TAC 25.252) | PUCT | 2026-07-09 | 3 | proposed rule |

**Waiting.** None of these is written:
- **PUCT 16 TAC 25.194** (Project No. 58481): now read in the PUCT's own documents by window P4's research pass (13 November
  2026, rows `texas-01` and `texas-04` of `docs/research/large_load/utilities_2026-11-13.csv`): the Order Adopting New 16 TAC
  §25.194, filed 18 September 2026 (item 218), effective 8 October 2026 (the Texas Register's receipt, item 219). Its steps:
  a $100,000 study fee at the intermediate agreement; the TSP or DSP contacts ERCOT within 60 days after that agreement is
  executed and funded, and tells the customer within five working days; the SLLIA executed and funded within 60 days after
  ERCOT's study report; $50,000 per MW of security at each agreement (the SLLIA's the greater of that or the allocated
  upgrade costs), returned 20 percent at energization and in 20 percent steps after; non-utilized capacity reported within
  30 days of a schedule missed by 24 months. Not written to this registry: the documents sit on interchange.puc.texas.gov,
  and the licensing sweep holds the PUCT's tables for its link policy (session 4102) pending the owner's ruling.
  Project No. 58000 (16 TAC 25.252) is still pending: its latest filing, of 1 October 2026, is comments.
- **MISO's ERAS guide:** the research file names only a news site's copy.
- **MISO's large-load definition:** known only secondhand.
- **FERC's six orders to show cause of 18 June 2026:** known only from law-firm summaries.
- **SPP's CHILLS:** known only secondhand.

## Chain 223: Pennsylvania's model tariff (session 3863)

The Pennsylvania Public Utility Commission's Final Order at Docket M-2025-3054271 (adopted 30 April 2026, entered 12 May
2026) adopts a Model Tariff for customers at or over 50 MW individually or 100 MW in the aggregate (its Appendix, pages 119
to 129). Each Pennsylvania electric distribution company files its own tariff on the model. The rows are therefore the
model's steps under grid PJM, with no utility.

The steps written (8):
- the threshold;
- two open seasons a year for interconnection studies, studied as clusters;
- the studies completed within six months of a complete application;
- half the study fee refunded for each 90 days late;
- a load ramp period of three to five years;
- an initial term of at least five years;
- 48 months' notice to end or change the contract after it;
- 14 business days to ask for a dispute's escalation.

A range (the load ramp) and a frequency (the open seasons) are written with their words and no duration. The orders on
reconsideration were read: the Energy Association of Pennsylvania's petition was withdrawn, and the order of 16 July
2026 closed the docket, so the model stands as adopted.

## Chain 227: Utah's rule R746-318 (session 3888)

The Public Service Commission of Utah's rule R746-318, "Large Scale Electric Requirements", implements S.B. 132 of 2025
(Utah Code Title 54 Chapter 26, whose own steps chain 212 wrote in session 3783). It was read from the Commission's
filing of 31 October 2025 at rulemaking Docket 25-R318-01, which prints the rule's full text and its date of enactment,
1 January 2026; the docket lists the Commission's notice of that effective date. The Office of Administrative Rules'
portal, where the code itself is published, is built by script and names no address for a rule (session 3878), so the
Commission's own filing is the copy read. The rows are under grid PACE with Rocky Mountain Power (PacifiCorp), Utah's
qualified electric utility, as in the statute's rows.

The steps written (5):
- the executed contract filed with the Commission within 15 days;
- a redacted copy served on the utility the same day, where the utility is not a party;
- the Commission's approval or disapproval within 60 days;
- 90 days for a registered generation provider to remedy a notice of deficiency;
- a limited and expedited review of a closed private generation contract for a load reaching 100 MW within five years.

The rule prints the filing window as "15 days" where the statute prints "15 business days"; each is kept as printed, in
its own document's rows. A same-day step prints no number and has no duration.

## Chain 227: the CAISO's draft final proposal (session 3888)

The CAISO's Large Load Enhancements Draft Final Proposal of 24 September 2026, the step after the straw proposal of 11
August (session 3762), on the same stakeholder center. It keeps the 50 MW definition (which it says may shift to align
with NERC's), keeps the PTOs' study procedures within 60 to 90 days as its minimum standard, adds a monthly review by
the CAISO of out-of-cycle transmission additions for large loads, and puts the Board of Governors' decision on 28 October
2026. The steps written (4). The range and the monthly review are written with their words and no duration, as
Pennsylvania's are; the straw proposal's row written in session 3762 carries the range's upper end, 90 days, as its
duration, and is left as it was written. The draft tariff language of 30 October 2026 was read and states no other
clock for a connection. The Board's decision and the FERC compliance filing were not read.

## Chain 267: the CAISO Board's decision (session 3927)

The CAISO Board of Governors approved the Large Load Enhancements on 28 October 2026 (General Session, vote 5-0), as
Management's memorandum of 22 October 2026 describes them, and authorized the filings with FERC. The motion and the
memorandum were read on www.caiso.com (robots read first; the governance page links both). The memorandum keeps the draft
final proposal's 50 MW definition and its monthly review within the PTOs' 60 to 90 days. The steps written (3): the
Board's approval with its stated date, the definition, and the monthly review with its words and no duration. None prints
a single duration, so the CAISO rows' hover reads as before, with the decision now named. The FERC filing it authorizes
(due 16 November 2026) was not read.
