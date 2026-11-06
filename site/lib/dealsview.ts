// Energy Research Warehouse (ERW) site, session 2238 (chain 156): the deals table's filters, sort and downloads.
//
// Pure functions, no imports, so Node runs this file as it is (tests/test_session2238_deals.py). The fields of
// session 2232 to 2235 (kind, stage, grid, flags, the canonical names) are read where the row has them; a row of the
// live set loaded before the desktop's first run of the new extractor has none, and each field then falls back to what
// the row's own older columns give (the kind from its type, the grid from its state, said so on the page). Nothing is
// estimated: a figure a story does not state is null and "not stated".

/** The kinds of master plan tool 6 (warehouse/deals/fields.py KINDS), in its order, with the page's words. */
export const KINDS: [string, string][] = [
  ["nuclear_restart_uprate", "Nuclear restart or uprate"], ["smr", "Small modular reactor"],
  ["behind_the_meter", "Behind the meter"], ["gas_buildout", "Gas buildout"], ["transmission", "Transmission"],
  ["storage", "Storage"], ["compute_capacity", "Compute capacity"], ["ppa", "PPA"], ["offtake", "Offtake"],
  ["project_finance", "Project finance"], ["m_and_a", "M&A"], ["capital", "Capital"], ["fuel_supply", "Fuel supply"],
  ["other", "Other"],
];
export const KIND_LABEL: Record<string, string> = Object.fromEntries(KINDS);

/** The stages of warehouse/deals/fields.py STAGES, in the order a deal moves. */
export const STAGES = ["rumored", "announced", "signed", "financed", "closed", "under_construction", "operating", "cancelled"];
export const STAGE_LABEL: Record<string, string> = {
  rumored: "Rumored", announced: "Announced", signed: "Signed", financed: "Financed", closed: "Closed",
  under_construction: "Under construction", operating: "Operating", cancelled: "Cancelled",
};

/** The grid operator that serves most of a state (lib/deals2.ts STATE_GRID, the same reading). */
const STATE_GRID: Record<string, string> = {
  TX: "ERCOT", CA: "CAISO", NY: "NYISO", CT: "ISO-NE", ME: "ISO-NE", MA: "ISO-NE", NH: "ISO-NE", RI: "ISO-NE", VT: "ISO-NE",
  PA: "PJM", NJ: "PJM", MD: "PJM", DE: "PJM", VA: "PJM", WV: "PJM", OH: "PJM", DC: "PJM",
  MN: "MISO", IA: "MISO", WI: "MISO", MI: "MISO", LA: "MISO", OK: "SPP", KS: "SPP", NE: "SPP",
};

/** The kind of a row extracted before session 2232, read from its type (fields.kind_of's last step). */
const FORM_KIND: Record<string, string> = {
  ppa: "ppa", offtake: "offtake", project_finance: "project_finance", m_and_a: "m_and_a", debt: "capital",
  equity_raise: "capital", tax_equity: "capital", joint_venture: "capital", fuel_supply: "fuel_supply",
  behind_the_meter: "behind_the_meter", nuclear_restart: "nuclear_restart_uprate", smr: "smr",
};

export type Row = {
  id: string; date: string; type: string; status: string; buyer: string; seller: string; others: string;
  asset: string; technology: string; state: string; country: string;
  mw: number | null; mwh: number | null; dollars: number | null; priceValue: number | null; priceUnit: string;
  usdPerMwh: number | null; termYears: number | null; aiPower: boolean; confidence: number | null;
  storyUrls: string[]; source: string;
  // session 2232 to 2235
  kind: string; kindBasis: string; stage: string; grid: string; gridBasis: string; flags: string[];
  buyerName: string; sellerName: string; statusHistory: string; aiBasis: string; fieldsVersion: string;
};

const num = (v: unknown): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

/** A row of the live set (lib/data.ts DealRow) as the table reads it. */
export function rowOf(r: { event_id: string; event_date: string; status: string | null; mw: unknown; price: unknown;
  source: string; source_url: string; extra: Record<string, string> | null }): Row {
  const x = r.extra ?? {};
  const type = x.deal_type ?? "";
  const state = (x.state ?? "").toUpperCase();
  const named = x.grid ?? "";
  const kind = x.kind || FORM_KIND[type] || "other";
  return {
    id: r.event_id, date: r.event_date, type, status: r.status ?? "", buyer: x.buyer ?? "", seller: x.seller ?? "",
    others: x.other_parties ?? "", asset: x.asset ?? "", technology: x.technology ?? "", state, country: x.country ?? "",
    mw: num(r.mw), mwh: num(x.mwh), dollars: num(x.usd ?? x.dollars), priceValue: num(x.price_value), priceUnit: x.price_unit ?? "",
    usdPerMwh: num(x.usd_per_mwh ?? r.price), termYears: num(x.term_years),
    aiPower: String(x.ai_power ?? "").toLowerCase() === "true", confidence: num(x.confidence),
    storyUrls: (x.story_urls ?? r.source_url ?? "").split(";").filter(Boolean), source: r.source,
    kind, kindBasis: x.kind ? (x.kind_basis ?? "") : `from the deal type (${type || "none"}), extracted before session 2232`,
    stage: x.stage ?? "", grid: named || STATE_GRID[state] || "", gridBasis: named ? "named in a story" : STATE_GRID[state] ? `the main grid of ${state}` : "",
    flags: (x.flags ?? "").split("; ").filter(Boolean), buyerName: x.buyer_name || x.buyer || "", sellerName: x.seller_name || x.seller || "",
    statusHistory: x.status_history ?? "", aiBasis: x.ai_power_basis ?? "", fieldsVersion: x.fields_version ?? "",
  };
}

/** A stated price per MWh (or in another energy unit): the comparables' "price disclosed". */
export const priceDisclosed = (d: Row): boolean => d.usdPerMwh !== null || (d.priceValue !== null && /mwh|kwh|mw-?month|mmbtu/i.test(d.priceUnit));

/** The names a row's parties go by: the canonical names where held, else as extracted. */
export const partiesOf = (d: Row): string[] =>
  [...d.buyerName.split("; "), ...d.sellerName.split("; "), ...d.others.split(";")].map((x) => x.trim()).filter(Boolean);

export type Inputs = { kind: string; grid: string; state: string; party: string; mwMin: string; mwMax: string; year: string;
  ai: string; stage: string; price: string };
export const NO_INPUTS: Inputs = { kind: "", grid: "", state: "", party: "", mwMin: "", mwMax: "", year: "", ai: "", stage: "", price: "" };

/** The stage a row is at: its stage where extracted, else its status (the five words before session 2232). */
export const stageOf = (d: Row): string => d.stage || d.status;

export function filterRows(rows: Row[], f: Inputs): Row[] {
  const lo = f.mwMin === "" ? null : Number(f.mwMin);
  const hi = f.mwMax === "" ? null : Number(f.mwMax);
  const party = f.party.trim().toLowerCase();
  return rows.filter((d) =>
    (!f.kind || d.kind === f.kind) && (!f.grid || (f.grid === "none" ? !d.grid : d.grid === f.grid)) &&
    (!f.state || d.state === f.state) && (!party || partiesOf(d).some((p) => p.toLowerCase().includes(party))) &&
    (lo === null || (d.mw !== null && d.mw >= lo)) && (hi === null || (d.mw !== null && d.mw <= hi)) &&
    (!f.year || d.date.slice(0, 4) === f.year) && (!f.ai || (f.ai === "yes") === d.aiPower) &&
    (!f.stage || (f.stage === "none" ? !stageOf(d) : stageOf(d) === f.stage)) &&
    (!f.price || (f.price === "yes") === priceDisclosed(d)));
}

export type SortKey = "date" | "kind" | "parties" | "asset" | "where" | "grid" | "mw" | "usd" | "price" | "stage" | "ai" | "sources";
const KEY: Record<SortKey, (d: Row) => string | number | null> = {
  date: (d) => d.date, kind: (d) => KIND_LABEL[d.kind] ?? d.kind, parties: (d) => partiesOf(d).join(" / ").toLowerCase(),
  asset: (d) => d.asset.toLowerCase(), where: (d) => [d.state, d.country].filter(Boolean).join(", "), grid: (d) => d.grid,
  mw: (d) => d.mw, usd: (d) => d.dollars, price: (d) => d.usdPerMwh ?? d.priceValue, stage: (d) => STAGES.indexOf(stageOf(d)),
  ai: (d) => (d.aiPower ? 1 : 0), sources: (d) => d.storyUrls.length,
};

/** Sorted by one column; a row with no value for it goes last whichever way, ties by date (newest first) then id. */
export function sortRows(rows: Row[], key: SortKey, dir: "asc" | "desc"): Row[] {
  const k = KEY[key];
  return [...rows].sort((a, b) => {
    const x = k(a), y = k(b);
    const ex = x === null || x === "" || x === -1, ey = y === null || y === "" || y === -1;
    if (ex !== ey) return ex ? 1 : -1;
    if (!ex && x !== y) return (x! < y! ? -1 : 1) * (dir === "asc" ? 1 : -1);
    return a.date < b.date ? 1 : a.date > b.date ? -1 : a.id.localeCompare(b.id);
  });
}

/** The columns of the download, in order: the deal's own fields and its links; no outlet text (no title, no
 * sentence), so a held outlet's story is a link only, as the news index holds it. */
export const CSV_COLUMNS: [string, (d: Row) => string | number | null][] = [
  ["event_id", (d) => d.id], ["date", (d) => d.date.slice(0, 10)], ["kind", (d) => d.kind], ["deal_type", (d) => d.type],
  ["buyer", (d) => d.buyer], ["seller", (d) => d.seller], ["buyer_name", (d) => d.buyerName], ["seller_name", (d) => d.sellerName],
  ["other_parties", (d) => d.others], ["asset", (d) => d.asset], ["technology", (d) => d.technology], ["state", (d) => d.state],
  ["country", (d) => d.country], ["grid", (d) => d.grid], ["grid_basis", (d) => d.gridBasis], ["mw", (d) => d.mw],
  ["mwh", (d) => d.mwh], ["usd", (d) => d.dollars], ["usd_per_mwh", (d) => d.usdPerMwh], ["price_value", (d) => d.priceValue],
  ["price_unit", (d) => d.priceUnit], ["term_years", (d) => d.termYears], ["stage", (d) => stageOf(d)],
  ["ai_power", (d) => (d.aiPower ? "true" : "false")], ["confidence", (d) => d.confidence], ["flags", (d) => d.flags.join("; ")],
  ["story_urls", (d) => d.storyUrls.join(";")],
];

const cell = (v: string | number | null): string => {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

/** The filtered rows as CSV, with the header comment lines the ERW's own files carry. */
export function toCsv(rows: Row[], note: { url: string; when: string; filters: string }): string {
  const head = [
    "# Energy Research Warehouse (ERW): energy deals, the rows of /deals as filtered on the page",
    `# Downloaded: ${note.when} from ${note.url}; filters: ${note.filters || "none"}`,
    "# Source: the ERW's own extraction (energy_deals, docs/methods/energy_deals.md); story_urls links every story; no outlet text",
    `# Rows: ${rows.length}. A figure the stories do not state is empty. flags: the cross-check of each figure against its headlines`,
  ];
  const lines = [CSV_COLUMNS.map(([c]) => c).join(","), ...rows.map((d) => CSV_COLUMNS.map(([, f]) => cell(f(d))).join(","))];
  return [...head, ...lines].join("\n") + "\n";
}

/** A reader of that CSV in Python (pandas), and in Stata, as plain text. */
export const pythonReader = (file: string): string =>
  `# Read the ERW's deals as downloaded from /deals\nimport pandas as pd\n\ndeals = pd.read_csv("${file}", comment="#", dtype={"event_id": str})\n` +
  `deals["date"] = pd.to_datetime(deals["date"])\nprint(deals.groupby("kind")["mw"].agg(["count", "sum"]))\n`;
export const stataReader = (file: string): string =>
  `* Read the ERW's deals as downloaded from /deals\nimport delimited using "${file}", varnames(5) rowrange(6) clear stringcols(1)\n` +
  `generate date_d = date(date, "YMD")\nformat date_d %td\ntabstat mw, by(kind) statistics(count sum)\n`;

/** The filters as words, for the download's header. */
export const filterWords = (f: Inputs): string =>
  Object.entries(f).filter(([, v]) => v !== "").map(([k, v]) => `${k}=${v}`).join(", ");
