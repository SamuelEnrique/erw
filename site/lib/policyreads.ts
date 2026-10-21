// Session 469: what an impact read of the policy monitor cites. A read (policy_reads) is written by a model from the
// action's own text, and reads.py keeps a field only when every number in it stands in that text. So a figure in a read
// is the action document's, never an ERW table's: this file says, for each read, which figures it states and that their
// source is the action's own text, or marks it "no figure" when it states none. It also looks for the name of an ERW
// table in the read's words, so that a read citing one would be shown with it (none does on 21 October 2026:
// docs/reviews/policy-impact-reads-2026-10-21.md). No request, no model: a pure function of the read's three text
// fields. The stored text is the warehouse's and is not changed here.
import type { PolicyRead } from "@/lib/data";

/** The fields of a read that are sentences, in the order the page prints them. */
export const READ_FIELDS = ["plain_read", "what_changes", "timeline"] as const;

/** What a read cites: the figures it states (each the action text's), and any ERW table it names. */
export type ReadCite = { kind: "text" | "table" | "none"; figures: string[]; tables: string[] };

export const CITE_WORDS = {
  none: "No figure: this read states no number.",
  text: "Each figure stands in the action's own text (reads.py keeps a field only when its numbers are there); no ERW table is cited.",
  table: "Names an ERW table:",
} as const;

// The units a figure may carry, as the reads write them.
const UNIT = String.raw`(?:percent|per cent|%|MW|GW|kW|TW|MWh|GWh|kWh|TWh|MMBtu|Btu|Dth/day|Dth/d|Dth|MMcf/d|Bcf/d|Bcf|b/d|Tcf|MMcf|million|billion|trillion|thousand|acres|miles|mile|feet|days|day|years|year|months|month|hours|hour|tons|tonnes|barrels|cents|homes|jobs|units|turbines|wells|megawatts|gigawatts|kilowatts)\b`;
const MONTH = String.raw`(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?`;
const LABEL = String.raw`(?:No|Nos|Order|Orders|Section|Sections|Sec|Part|Parts|Docket|Dockets|Unit|Units|Rule|Title|Form|Phase|Tier|Chapter|Article|Subpart|Schedule|Bill|Case|Project|Item|Appendix|Volume|Vol|Exhibit|Table|Figure|Step|Category|Class|Group|Level|Zone|Region|District|Block|Lot|Tract|Lease|Leases|Sale|Sales|Area|Route|Highway|Interstate|Station|Stations|EEA|Alert|Watch|Mile Marker|Exit|Gate|Pad|Well|Line|Train|Trains|Reactor|Reactors)`;

// Dates and identifiers carry digits but are not figures: a date, a year, a docket, an order, a section of a law, a
// part of the Code of Federal Regulations, a unit's number. They are taken out before the figures are read.
const NOT_FIGURES: RegExp[] = [
  new RegExp(String.raw`\b${MONTH}\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*|\s+)\d{4}\b`, "g"),
  new RegExp(String.raw`\b\d{1,2}\s+${MONTH}\s+\d{4}\b`, "g"),
  new RegExp(String.raw`\b${MONTH}\s+\d{4}\b`, "g"),
  new RegExp(String.raw`\b${MONTH}\s+\d{1,2}(?:st|nd|rd|th)?\b`, "g"),
  /\b\d{4}-\d{2}-\d{2}\b/g,
  /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/g,
  /\b\d+\s+(?:CFR|C\.F\.R\.|U\.S\.C\.|USC|FR)\s+[\d.]+(?:\([a-z0-9]+\))*/g,
  new RegExp(String.raw`\b${LABEL}\.?\s*(?:No\.?\s*)?\d[\w.\-]*(?:\s*(?:,|and|to|through|or)\s*\d[\w.\-]*)*`, "gi"),
  /\b\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.|am|pm|AM|PM)?/g, // a time of day
  /§+\s*[\d.]+[\w.\-()]*/g,
  /\b[A-Z]{2,}-\d[\d\-]*\b/g, // WAPA-211, P-2232
  /\b[A-Za-z]+\d[\w\-]*\b/g, // EL26-67, RM26-4, CO2, H2
  /\b[A-Za-z]+-\d[\w\-]*\b/g, // Xe-100, a model's name
  /\b\d+[A-Z]\b/g, // 45Y, 48C
  /\b\d+(?:st|nd|rd|th)\b/g, // 1st, 2nd
  new RegExp(String.raw`\b(?:19|20)\d{2}s?\b(?!\s*${UNIT})`, "g"), // a year standing alone (not "1900 acres")
];

const FIGURE = new RegExp(String.raw`(?:USD\s*|US\$\s*|\$\s*)?\d[\d,]*(?:\.\d+)?(?:(?:\s*|-)${UNIT}(?:\s+(?:million|billion))?)?`, "g");

/** The figures a sentence states: numbers with their unit where one follows, after dates and identifiers are taken out.
 * A number written in words ("two") is not read. */
export function figuresOf(text: string | null | undefined): string[] {
  let s = ` ${String(text ?? "")} `;
  for (const r of NOT_FIGURES) s = s.replace(r, " ");
  const out: string[] = [];
  for (const m of s.matchAll(FIGURE)) {
    const f = m[0].trim().replace(/[,.]$/, "");
    if (/\d/.test(f)) out.push(f);
  }
  return out;
}

/** The ERW tables a read names in its words (a snake_case name that is one of `tables`). */
export function tablesOf(text: string | null | undefined, tables: Iterable<string>): string[] {
  const known = new Set(tables);
  const found = (String(text ?? "").match(/\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g) ?? []).filter((t) => known.has(t));
  return Array.from(new Set(found));
}

/** What a read cites, from its three sentence fields. A read with no figure is marked "none"; with figures, their source
 * is the action's own text ("text"), unless the read names an ERW table ("table"). */
export function citeOf(read: Pick<PolicyRead, "plain_read" | "what_changes" | "timeline"> | null | undefined, tables: Iterable<string> = []): ReadCite {
  if (!read) return { kind: "none", figures: [], tables: [] };
  const words = READ_FIELDS.map((k) => read[k] ?? "").join(" \n ");
  const figures = Array.from(new Set(READ_FIELDS.flatMap((k) => figuresOf(read[k]))));
  const named = tablesOf(words, tables);
  return { kind: named.length ? "table" : figures.length ? "text" : "none", figures, tables: named };
}
