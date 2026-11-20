// Energy Research Warehouse (ERW) site, chain 507 (session 8900): the words and types of the findings audit of 19
// November 2026, with no data, so the filter at /internal/findings (a client component) does not carry the audit's file.
// The file and its readers are in lib/findingaudit.ts.

export type CheckState = "passed" | "fixed" | "not checked" | "withdrawn" | "failed in part";
export type AuditVerdict = "passed" | "passed after a fix" | "not checked" | "held" | "withdrawn" | "not audited";
export type KnownState = "new" | "known" | "known in part" | "not read yet";

export const VERDICT_ORDER: AuditVerdict[] = ["passed", "passed after a fix", "not checked", "held", "withdrawn", "not audited"];
export const KNOWN_ORDER: KnownState[] = ["new", "known in part", "known", "not read yet"];

/** What each verdict means, for the hover tip of its count. */
export const VERDICT_TIPS: Record<AuditVerdict | "none", string> = {
  passed: "Checks 1 to 3 passed: the sentence says only what the figure shows, the figure reproduced on the audit's machine, the Stata file does what the Python does.",
  "passed after a fix": "Checks 1 to 3 passed after the audit mended the sentence's wording or the do-file; no figure was changed.",
  "not checked": "The figure could not be reproduced on the audit's machine (memory, or a table rebuilt short); the reason is in check 2. Cannot be approved until it is.",
  held: "Rests on a table that is internal or held; not reproduced and not for /research. Cannot be approved.",
  withdrawn: "The figure does not reproduce: the audit's run printed another figure than the draft's. Cannot be approved.",
  "not audited": "A draft of docs/findings/ the audit of 19 November 2026 has no row for yet. Cannot be approved until it is audited.",
  none: "A draft of the daily scanner or the weekly hunt, not of docs/findings/: the audit of 19 November 2026 did not cover it, and its approval is as before.",
};

/** What each answer to "is it already known?" means. */
export const KNOWN_TIPS: Record<KnownState, string> = {
  new: "New as far as found: no publisher found printing this figure or this comparison.",
  "known in part": "A publisher printed part of it; the hover on the answer says what, and what this draft adds.",
  known: "A publisher printed it; the hover on the answer says who, when, and their figure beside ours.",
  "not read yet": "Not searched yet: chain 507 reads the rest, strongest first.",
};

/** One draft as the filter sees it. `verdict` is "none" for a draft the audit did not cover; `rank` is 0 off the sheet. */
export type BrowseItem = { id: string; family: string; verdict: AuditVerdict | "none"; known: KnownState | "none"; reader: string; rank: number; text: string; ruling: string };
