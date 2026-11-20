// Energy Research Warehouse (ERW) site, chain 507 (session 8900): the findings audit of 19 November 2026 beside each
// draft at /internal/findings. Chain 506 audited every draft of docs/findings/ (four checks, "is it already known?", a
// second route for the forty on the sheet); warehouse/analysis/findings/audit_page.py writes what it found into
// data/findings_audit.json, read here at build. Words and states only: nothing here approves a draft. A draft whose
// figure was not reproduced, did not reproduce, or rests on a table that is not public cannot be approved (blockedReason,
// used by the page's control and by the state route). Server code only: the file is about a megabyte.
import "server-only";
import file from "@/data/findings_audit.json";
import type { AuditVerdict, CheckState, KnownState } from "@/lib/findingauditwords";

export type AuditCheck = { name: string; state: CheckState; why: string };
export type SheetPlace = { rank: number; reader: string; figure: string; compared: string; risk: string; why: string; do_text: string };
export type AuditRow = {
  slug: string; family: string; title: string; sentence: string;
  files: { do: string; py: string; md: string; png: string };
  verdict: AuditVerdict; day: string; checks: AuditCheck[]; changed: string;
  known: { state: KnownState; detail: string };
  route2: { state: string; detail: string } | null;
  tables: { name: string; license: string }[];
  blocked: string;
  sheet?: SheetPlace;
};
export type AuditFile = {
  made_by: string; audit: string; sheet_doc: string; gh: string; raw: string; readers: string[]; sheet: string[];
  counts: Record<string, number>; known_counts: Record<string, number>; drafts: Record<string, AuditRow>;
};

export const AUDIT = file as unknown as AuditFile;

/** The audit's row for a draft of the review list, or null for a draft the findings hunt did not write (the scanner's own). */
export const auditOf = (id: string): AuditRow | null => AUDIT.drafts[id] ?? null;

/** Why a draft cannot be approved, or "" when the audit does not stop it. A draft with no row (the daily scanner's, the
 * weekly hunt's) is approved as before: the audit covered docs/findings/ only. */
export const blockedReason = (id: string): string => AUDIT.drafts[id]?.blocked ?? "";

/** The forty of the sheet, in the sheet's order, with their ids. */
export const SHEET: { id: string; row: AuditRow }[] = AUDIT.sheet.map((id) => ({ id, row: AUDIT.drafts[id] }));

/** The address of a repository file on GitHub, to read, and its raw address, to save. */
export const ghRead = (p: string) => AUDIT.gh + p;
export const ghRaw = (p: string) => AUDIT.raw + p;
