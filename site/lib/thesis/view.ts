// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis). What the page works out from a run:
// its address, which cells of a trend's table are numbers, the series a chart draws, and which company of a PitchBook
// answer is which company of the report. Pure functions, no I/O: scripts/test-thesis-pitchbook.mjs tests them.
import type { Cell, Missing, PbCompany, PitchbookPayload, Trend } from "./types";

// Session 169, the owner's ruling of 8 October 2026: the market research is the ERW's (scope, trends, capital, policy,
// risks, incumbents, timing, references); companies come from a connector (landscape, deal funnel, pipeline, success
// stories, investors), each tab a greyed placeholder until a provider's answer is pasted. Every address of a tab that
// existed before still opens the same tab.
export const TABS = [
  { id: "scope", label: "Scope and definitions" }, { id: "trends", label: "Trends" }, { id: "capital", label: "Capital" },
  { id: "policy", label: "Policy" }, { id: "risks", label: "Risks" }, { id: "incumbents", label: "Incumbents" },
  { id: "timing", label: "Timing" }, { id: "references", label: "References" },
  { id: "landscape", label: "Company landscape" }, { id: "funnel", label: "Deal funnel" }, { id: "pipeline", label: "Pipeline map" },
  { id: "success", label: "Success stories" }, { id: "investors", label: "Investors" },
] as const;
export type TabId = (typeof TABS)[number]["id"];
export const METHOD = "/data/methods/thesis";
export const EMPTY_TAB = "Nothing was found for this tab in this run.";
export const PB_PENDING = "PitchBook pending";
export const PB_PENDING_WHY = "Asked of PitchBook; shown here when the answer is submitted.";
/** A run's id as migration 024 writes it ("20261006T140512Z-a1b2c3"); anything else is not asked of the database. */
export const RUN_ID = /^[A-Za-z0-9_-]{1,80}$/;

type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
export type Choice = { run: string | null; tab: TabId };
/** What an address asks for: the run selected and the tab of its report (the first when none is named). */
export function choiceOf(q: Query): Choice {
  const run = one(q.run) ?? "";
  const tab = one(q.tab);
  return { run: RUN_ID.test(run) ? run : null, tab: TABS.find((t) => t.id === tab)?.id ?? "scope" };
}
export function hrefOf(c: Choice, patch: Partial<Choice> = {}, hash = ""): string {
  const n = { ...c, ...patch };
  const q = new URLSearchParams();
  if (n.run) q.set("run", n.run);
  if (n.run && n.tab !== "scope") q.set("tab", n.tab);
  const s = q.toString();
  return `/thesis${s ? `?${s}` : ""}${hash ? `#${hash}` : ""}`;
}

/** A list that may be absent, as a list. */
export const arr = <T>(v: T[] | null | undefined): T[] => (Array.isArray(v) ? v : []);
/** A field that should be text, as text ("" when it is absent or something else). */
export const str = (v: unknown): string => (typeof v === "string" ? v : typeof v === "number" && Number.isFinite(v) ? String(v) : "");
export const isMissing = (c: unknown): c is Missing => typeof c === "object" && c !== null && typeof (c as Missing).missing === "string";
export const PLACEHOLDER: Record<Missing["missing"], string> = {
  not_disclosed: "not disclosed", not_confirmed: "not confirmed", not_held: "not held", pitchbook_pending: PB_PENDING,
};
/** A link the page may open: http or https only. Anything else is shown as text. */
export function safeUrl(u: unknown): string | null {
  if (typeof u !== "string") return null;
  const s = u.trim();
  if (!/^https?:\/\//i.test(s)) return null;
  try { return new URL(s).href; } catch { return null; }
}

/**
 * The number a table cell holds, or null. A cell is numeric when it reads as a number once the thousands commas, a
 * leading "$" and a trailing "%" or unit are taken away. The unit is the chart's own (or its last words: "billion"
 * for "USD billion"). Anything else ("about 12", "3 to 5", "1.2B" under another unit, a placeholder) is not a number:
 * its row is left out of the chart, never drawn as zero and never drawn at another scale.
 */
export function numeric(cell: unknown, unit = ""): number | null {
  if (typeof cell !== "string") return null;
  let s = cell.trim().replace(/−/g, "-");
  if (!s) return null;
  const words = unit.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const tails = words.map((_, i) => words.slice(i).join(" "));      // the unit, then each shorter run of its last words
  const low = s.toLowerCase();
  const tail = tails.find((t) => low.endsWith(t) && low.length > t.length);
  if (tail) s = s.slice(0, s.length - tail.length).trim();
  else if (s.endsWith("%")) s = s.slice(0, -1).trim();
  const m = /^([+-]?)\$?\s*(\d{1,3}(?:,\d{3})+|\d+)?(\.\d+)?$/.exec(s);
  if (!m || (m[2] === undefined && m[3] === undefined)) return null;
  const v = Number(`${m[1]}${(m[2] ?? "0").replace(/,/g, "")}${m[3] ?? ""}`);
  return Number.isFinite(v) ? v : null;
}

export type ChartData = { kind: "bar" | "line"; title: string; unit: string; categories: string[]; series: { name: string; data: (number | null)[] }[] };
/**
 * What a trend's chart draws, from its own table: the category column along the axis and one series for each value
 * column. A row none of whose value cells is a number is left out; in a chart of several series a cell that is not a
 * number is a gap. Null when the trend names no chart, or no row holds a number.
 */
export function chartOf(t: Trend | null | undefined): ChartData | null {
  const c = t?.chart;
  if (!c || (c.kind !== "bar" && c.kind !== "line")) return null;
  const columns = arr(t?.table?.columns), rows = arr(t?.table?.rows).filter(Array.isArray);
  const cols = arr(c.values).filter((i) => Number.isInteger(i) && i >= 0);
  if (!Number.isInteger(c.category) || c.category < 0 || !cols.length) return null;
  const unit = str(c.unit);
  const kept = rows
    .map((r) => ({ cat: r[c.category], vals: cols.map((i) => numeric(r[i], unit)) }))
    .filter((r) => typeof r.cat === "string" && r.cat.trim() !== "" && r.vals.some((v) => v !== null));
  if (!kept.length) return null;
  return {
    kind: c.kind, title: str(c.title) || str(t?.title), unit,
    categories: kept.map((r) => (r.cat as string).trim()),
    series: cols.map((i, k) => ({ name: str(columns[i]) || `Column ${i + 1}`, data: kept.map((r) => r.vals[k]) })),
  };
}

/** A number as the page writes it: thousands commas, at most two decimals. */
export const num = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** "6 Oct 2026, 14:05 UTC" from a timestamp; "6 Oct 2026" from a day; "Mar 2025" from a month; any other text
 * ("2025", "Q3 2026") as it is. */
export function whenWords(t: string | null | undefined): string {
  if (!t) return "";
  const part = /^(\d{4})-(\d{2})(?:-(\d{2}))?$/.exec(t);
  if (part) return `${part[3] ? `${Number(part[3])} ` : ""}${MON[Number(part[2]) - 1] ?? part[2]} ${part[1]}`;
  if (!/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(t)) return t;
  const d = new Date(t);
  if (Number.isNaN(d.getTime())) return t;
  return `${d.getUTCDate()} ${MON[d.getUTCMonth()]} ${d.getUTCFullYear()}, ${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")} UTC`;
}

const SUFFIX = new Set(["inc", "incorporated", "llc", "ltd", "limited", "corp", "corporation", "co", "company", "plc", "gmbh", "ag", "sa", "bv", "lp"]);
/** A company's name as it is matched: lower case, punctuation as spaces, a closing legal form dropped. */
export function nameKey(name: unknown): string {
  const words = str(name).toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/&/g, " and ").replace(/[^a-z0-9]+/g, " ").trim().split(" ").filter(Boolean);
  while (words.length > 1 && SUFFIX.has(words[words.length - 1])) words.pop();
  return words.join(" ");
}
/** The company of a PitchBook answer that was asked for under this name (the answer's "name" is the name asked). */
export function pitchbookFor(pb: PitchbookPayload | null | undefined, name: unknown): PbCompany | null {
  const k = nameKey(name);
  if (!pb || !k) return null;
  return arr(pb.companies).find((c) => nameKey(c?.name) === k) ?? null;
}
const usdM = (v: number) => `USD ${num(v)} million`;
/** Every figure a PitchBook company holds, each with its own name; the page writes the "PitchBook" tag beside each. */
export function pbFigures(c: PbCompany | null | undefined): { id: string; label: string; value: string }[] {
  if (!c || !c.found) return [];
  const out: { id: string; label: string; value: string }[] = [];
  const add = (id: string, label: string, value: string | undefined | null) => { if (value) out.push({ id, label, value }); };
  const n = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : null);
  if (c.pitchbook_name && nameKey(c.pitchbook_name) !== nameKey(c.name)) add("pitchbook_name", "Listed as", c.pitchbook_name);
  add("total_raised", "Total raised", n(c.total_raised_usd_m) === null ? null : usdM(c.total_raised_usd_m!));
  const r = c.last_round;
  if (r) {
    const parts = [str(r.type), r.date ? whenWords(r.date) : "", n(r.size_usd_m) === null ? "" : usdM(r.size_usd_m!)].filter(Boolean);
    add("last_round", "Last round", parts.join(", "));
    add("post_valuation", "Post-money valuation", n(r.post_valuation_usd_m) === null ? null : usdM(r.post_valuation_usd_m!));
  }
  add("financing_status", "Financing status", str(c.financing_status));
  add("hq", "Headquarters", str(c.hq));
  add("founded_year", "Founded", n(c.founded_year) === null ? null : String(c.founded_year));
  add("employees", "Employees", n(c.employees) === null ? null : num(c.employees!));
  add("founders", "Founders", arr(c.founders).join(", "));
  add("lead_investors", "Lead investors", arr(c.lead_investors).join(", "));
  add("investors", "Investors", arr(c.investors).join(", "));
  add("description", "Description", str(c.description));
  return out;
}
/** The figure of a PitchBook company that answers one cell of the report (a cell that read "PitchBook pending"). */
export const PB_FIELD: Record<string, string> = { founders: "founders", raised: "total_raised", location: "hq", stage: "last_round" };
export function pbFigureFor(c: PbCompany | null | undefined, field: string): { label: string; value: string } | null {
  const id = PB_FIELD[field];
  return (id && pbFigures(c).find((f) => f.id === id)) || null;
}
/** A cell as plain text (for a chart's label or a title): its string, or its placeholder. */
export const cellWords = (c: Cell | null | undefined): string => (isMissing(c) ? PLACEHOLDER[c.missing] ?? "not held" : str(c));

// ------------------------------------------------------------------ session 169: the connector tabs

export type ConnectorId = "landscape" | "funnel" | "pipeline" | "success" | "investors";
export const CONNECTOR_IDS: ConnectorId[] = ["landscape", "funnel", "pipeline", "success", "investors"];
export const CONNECTOR_NOTE = "Connect PitchBook or Harmonic to fill this";
export const CONNECTOR_WHY = "The ERW does not search for companies. This tab is filled from a data provider's answer, pasted in the panel above.";
const COMPANY_COLUMNS = ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"];
/** The columns of each connector tab when a report does not name its own (a report written before session 169). The
 * funnel's stand in for the MCJ workbook's columns until that workbook is read. */
export const CONNECTOR_COLUMNS: Record<ConnectorId, string[]> = {
  landscape: COMPANY_COLUMNS, pipeline: COMPANY_COLUMNS,
  funnel: ["Company", "What it sells", "Stage", "Funnel stage", "Date sourced", "Sourced by", "Next step", "Status", "Notes", "Source"],
  success: ["Company", "What it sells", "Outcome", "Date", "Raised before", "Investors", "Source"],
  investors: ["Investor", "Companies backed in this niche", "Lead in", "Latest round seen", "Source"],
};
/** A report written since session 169: the market research, with the companies left to a connector. */
export const isMarket = (r: { version?: unknown } | null | undefined): boolean => typeof r?.version === "number" && r.version >= 2;
export function columnsOf(r: { connector_tabs?: { columns?: Record<string, string[]> } | null } | null | undefined, tab: ConnectorId): string[] {
  const own = r?.connector_tabs?.columns?.[tab];
  return Array.isArray(own) && own.length && own.every((c) => typeof c === "string") ? own : CONNECTOR_COLUMNS[tab];
}

const EARLY = /\b(pre-?seed|seed|angel|series [ab]\b|grant|accelerator|incubator|early stage)/i;
const EXIT = /\b(acquired|acquisition|merger|merged|publicly (held|traded)|ipo|buyout|spac)\b/i;
const roundWords = (c: PbCompany) => { const r = c.last_round; return r ? [str(r.type), r.date ? whenWords(r.date) : "", typeof r.size_usd_m === "number" ? usdM(r.size_usd_m) : ""].filter(Boolean).join(", ") : ""; };
const join = (v: unknown) => arr(v as string[] | null).map(str).filter(Boolean).join(", ");

/**
 * What a connector tab holds from a PitchBook answer: its rows, every cell a string ("" where the answer holds nothing
 * for it, which the page shows as a placeholder). Null when the run holds no answer, or the answer no company. Every
 * row is labeled PitchBook's in its Source cell. Nothing is computed beyond grouping: the investors' tab counts the
 * companies of the answer each investor is named on.
 */
export function connectorRows(pb: PitchbookPayload | null | undefined, tab: ConnectorId): string[][] | null {
  if (!pb) return null;
  const seen = new Set<string>();
  const all = [...arr(pb.companies), ...arr(pb.additional_companies)].filter((c) => c && c.found).filter((c) => {
    const k = nameKey(c.pitchbook_name || c.name);
    if (!k || seen.has(k)) return false;
    seen.add(k);
    return true;
  }) as (PbCompany & { why?: string })[];
  if (!all.length) return null;
  const source = `PitchBook${pb.pulled_on ? `, pulled ${whenWords(str(pb.pulled_on))}` : ""}`;
  const name = (c: PbCompany) => str(c.pitchbook_name) || str(c.name);
  const stage = (c: PbCompany) => str(c.last_round?.type) || str(c.financing_status);
  const raised = (c: PbCompany) => (typeof c.total_raised_usd_m === "number" ? usdM(c.total_raised_usd_m) : "");
  const company = (c: PbCompany) => [name(c), str(c.description), join(c.founders), stage(c), raised(c), join(c.investors), typeof c.founded_year === "number" ? String(c.founded_year) : "", str(c.hq), roundWords(c), source];
  const latest = (c: PbCompany) => str(c.last_round?.date);
  if (tab === "landscape") return all.map(company);
  if (tab === "pipeline") return all.filter((c) => EARLY.test(`${stage(c)} ${str(c.financing_status)}`) && !EXIT.test(`${stage(c)} ${str(c.financing_status)}`))
    .sort((a, b) => latest(b).localeCompare(latest(a))).map(company);
  if (tab === "funnel") return all.map((c) => [name(c), str(c.description), stage(c), "Sourced", str(pb.pulled_on), "PitchBook", "", "", str((c as { why?: string }).why), source]);
  if (tab === "success") return all.filter((c) => EXIT.test(`${str(c.financing_status)} ${str(c.last_round?.type)}`))
    .map((c) => [name(c), str(c.description), EXIT.test(str(c.last_round?.type)) ? str(c.last_round?.type) : str(c.financing_status), latest(c) ? whenWords(latest(c)) : "", raised(c), join(c.investors), source]);
  const by = new Map<string, { names: string[]; lead: string[]; latest: string }>();
  for (const c of all) {
    const leads = new Set(arr(c.lead_investors).map(nameKey));
    for (const inv of new Set([...arr(c.investors), ...arr(c.lead_investors)].map(str).filter(Boolean))) {
      const k = nameKey(inv);
      const e = by.get(k) ?? { names: [inv], lead: [], latest: "" };
      if (!e.names.includes(name(c))) e.names.push(name(c));
      if (leads.has(k) && !e.lead.includes(name(c))) e.lead.push(name(c));
      if (latest(c) > e.latest) e.latest = latest(c);
      by.set(k, e);
    }
  }
  return [...by.values()].sort((a, b) => b.names.length - a.names.length || a.names[0].localeCompare(b.names[0]))
    .map((e) => [e.names[0], `${e.names.length - 1}: ${e.names.slice(1).join(", ")}`, e.lead.join(", "), e.latest ? whenWords(e.latest) : "", source]);
}
