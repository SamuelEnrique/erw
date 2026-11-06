# The policy monitor's third sample (session 3151, chain 186)

Chain 178's fresh audit measured the rules of chains 166 and 169 on 80 actions never used to write them, then fixed what it found (sessions 3140 to 3142). This third sample measures those fixes the same way: every fifth row of rows 801 to 1200 of the newest actions of the live set (1 April to 4 June 2026), 80 actions never used to write a rule, read against their own documents fetched on 6 November 2026 into the session's scratch folder (80 of 80; the Register answered one request with HTTP 429, which was waited out and asked once more). Their event ids and classes are in `policy-audit-2026-11-06-third-sample.csv`.

Sample: FERC 35, NRC 21, EPA 11, PUCT 4, BLM 4, Interior 2, DOE 1, IRS 1, CPUC 1.

## The count, with the code as chain 178 left it

| # | Class | Right | Faults | The faults |
|---|---|---:|---:|---|
| 1 | A stated date | 43 of 52 rows that state a step | 9 | r15 compliance filings "due on" and a compliance date "required by"; r25 and r45 a final rule that "must be issued no later than"; r32 "requests for hearings must be received on or before"; r38 a hearing "scheduled for Wednesday, May 27, 2026, Thursday, May 28, 2026, and Friday, May 29, 2026"; r42 "The due date to pay additional royalties ... is"; r44, r57 and r68 "EPA will hold a ... public hearing on"; r57 also "requesting a public hearing on or before" |
| 5 | The instrument | 74 of 80 | 6 | r3 and r61 NRC releases of public meetings read as announcements; r47 and r56 releases of an NRC licence renewal and an agreement-state amendment read as announcements, not an order and an approval; r6 FERC's information collection and r78 a revised procedural schedule read as applications |
| 2 | The status | 78 of 80 | 2 | r48 and r80, "Proposed Reinstatement of ... Terminated Oil and Gas Lease", read "issued" for a proposal |
| 3 | A stated figure | 13 of 15 rows with an own figure | 2, and 2 taken wrongly | r26 "$446 to $1,090 million dollars annually" read as 446; r7 a release's grant past its opening; and r48 and r80 take "$20 per acre", a rate, as the action's figure |
| 9 | Out of scope, marked | 78 of 80 | 2 | r32 a pesticide's exemption from a tolerance; r79 a commissioner sworn in |
| 6 | The place | no fault found | 0 | (the rows that name no place state none: Palo Verde's and Gulf South's documents name no county or "located" sentence) |
| 8 | The body | 80 of 80 | 0 | |

**What it says**: the fixes of sessions 3140 to 3142 hold on rows never used to write them (the instrument at 93%, against 89% on the fresh sample before its fixes), but each sample finds kinds of wording the last did not hold: here hearings EPA "will hold", compliance and payment dates, final rules "issued no later than", releases that announce a decision or a meeting, per-acre rates. The dates hold for 83% of the rows that state a step (86% on the fresh sample before its fixes).

## The rows closed by later sessions

(Sessions 3152 to 3156 write their counts here.)

- **Session 3152, class 1 (the dates)**: 52 of 52 rows right (43 before; r38's third hearing day, "and Friday, May 29", is still not taken). The rules: an agency's own deadline for its final rule ("must be issued no later than"); a hearing already scheduled, or one someone "will hold"; objections and "requests for hearings", and "requesting a public hearing", as a party's like interventions; compliance filings, a compliance date and a payment's "due date" as filings due. Two guards: a filing deadline on a date another step holds is that step; a date a party asks, seeks, expects or plans for is no step. On the fresh sample nothing changed; on the first sample four true dates were gained (a compliance deadline, a hearing, a filing deadline; r18's requested 2032 date, which session 3141's rule had added, is gone); on the archive's copy, filings due 8 and meetings 3, each read; `check_policy.py` 303 of 303.
- **Session 3153, classes 5 and 2 (the instrument and the status)**: 80 of 80 each on this sample (74 and 78 before). The rules: an agency's information collection and a revised procedural schedule are notices (after an accepted or tendered application, which keeps its own reading); a release whose title says an agency will brief, discuss, hold or host is a meeting's, one that it extends, renews or grants, or issues a licence, permit, approval, order or authorization, an order's, one that it approves or expands an authority an approval's; a notice titled "Proposed ..." is proposed, one of a schedule scheduled. On the fresh sample three rows change, each to the right reading (two commission approvals, a revised schedule); on the first sample none. On the archive's copy 17 releases leave "announcement" (NRC licence renewals, workshops, commission approvals), each read; a first wording took "NRC Issues Annual Assessments" for an order and was narrowed. `check_policy.py` 303 of 303.
