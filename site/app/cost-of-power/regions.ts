// Energy Research Warehouse (ERW) site, chain 780 (session 11600, 28 November 2026): the pure parts of "Where the next
// gigawatts can go", the section of the All grids tab of /cost-of-power that sets each place's counts side by side
// (Samuel's ruling of 22 October 2026: the siting question lives on that tab, not on a page of its own).
//
// The section reads exactly the files and fields of docs/state/page_files_siting_regions.md, which the data machine's
// builder writes (warehouse/derived/siting_regions.py): site/data/siting/regions/index.json (the places and the ten
// sections), table.json (one value a place and a column) and <id>.json (one file a place). Nothing here computes a
// count: a figure is the file's own, or it is not drawn. No score, no rank, no advice: the reader sorts and filters.
//
// No import of Next.js, of React or of the disk: the server's section, the browser's choices and downloads, and node's
// tests all read this file as it is.

// ---- the files' shapes (the contract's own words) -------------------------------------------------------------------

/** A count's last 24 whole months, where the warehouse holds it by month (the contract's dated line of 28 November
 *  2026, data request 585): in the count's unit and from its source; a month not held is null. */
export type Trend = { months: string[]; period: string | null; v: (number | null)[] };
/** A count as every file writes it. `v` is null exactly when `held` gives the reason. */
export type Cell = { v: number | string | null; unit: string; period: string | null; src: string | null; held: string | null; trend?: Trend | null };
/** `url` (the same dated line) is the address of the table's first row's document: for a table of many publishers it
 *  is not the place's own, so the section draws no link from it (data request 586). */
export type Source = { table: string | null; publisher: string | null; license: string; retrieved: string | null; report: string | null; url?: string | null; held?: string | null };
export type Kind = "region" | "operator" | "ba";
export type Place = {
  id: string; kind: Kind; code: string; name: string; region: string | null; regions: string[]; operator: string | null;
  members: string[]; tz: string; peak_mw: number | null; ref_hub: string | null; file: string;
};
export type SectionHead = { id: string; title: string; counts: { key: string; label: string; unit: string }[] };
export type IndexFile = {
  built: string; example?: boolean; contract?: string; method?: string; license?: string;
  ba_floor_mw: number | null; ba_floor_period: string | null; places: Place[]; sections: SectionHead[];
};
export type Column = { key: string; section: string; label: string; unit: string; period: string | null; src: string | null };
export type RowCell = { period: string | null; src: string | null; held: string | null };
export type TableRow = { id: string; kind: Kind; name: string; v: (number | string | null)[]; cell?: Record<string, RowCell> };
export type TableFile = { built: string; example?: boolean; method?: string; sources: Record<string, Source>; columns: Column[]; rows: TableRow[] };
/** A place's file. A section's own shape is the contract's; the section's drawer reads each by name. */
export type PlaceFile = {
  built: string; example?: boolean; method?: string; id: string; kind: Kind; code: string; name: string; tz: string; members: string[];
  sources: Record<string, Source>; sections: Record<string, Record<string, unknown> & { status?: string }>;
};

export const FOLDER = "siting/regions";
export const INDEX_FILE = `${FOLDER}/index.json`, TABLE_FILE = `${FOLDER}/table.json`;
/** A place's file under site/data, by the name the index gives it; null when the name is not a plain file name. */
export const placeFile = (file: string): string | null => (/^[a-z0-9][a-z0-9-]{0,40}\.json$/.test(file) ? `${FOLDER}/${file}` : null);

export const KINDS: Kind[] = ["region", "operator", "ba"];
export const KIND_WORDS: Record<Kind, string> = { region: "Region", operator: "Market operator", ba: "Balancing authority" };
export const KIND_PLURAL: Record<Kind, string> = { region: "regions", operator: "market operators", ba: "balancing authorities" };
export const KIND_TIP: Record<Kind, string> = {
  region: "One of the 13 regions the Energy Information Administration (EIA) groups the balancing authorities into; its counts are its member authorities', summed where a count is a sum.",
  operator: "One of the seven market operators (CAISO, ERCOT, SPP, MISO, PJM, NYISO, ISO-NE), by its own authority and its own published tables.",
  ba: "A balancing authority that is not itself a market operator and whose highest hourly demand in the last 12 whole months is at least the floor the file names.",
};

// ---- the address ----------------------------------------------------------------------------------------------------

/** The section's own names in the tab's address. Every other name there is the tab's (lib/siting.ts) and is kept as it
 *  came: sort, dir, a, b, grid, kind and the rest are the hub table's, so these carry a prefix of their own. */
export const PARAMS = ["srsort", "srdir", "srcols", "srkind", "sropen", "sra", "srb"] as const;
export type Param = (typeof PARAMS)[number];
export const ANCHOR = "regions", PLACE_ANCHOR = "regions-place", AB_ANCHOR = "regions-ab";
export const NAME_SORT = "name";
export const MAX_COLS = 40;

export type Choice = {
  sort: string; dir: "asc" | "desc"; cols: string[]; colsChosen: boolean; kind: Kind | "all";
  open: string | null; a: string | null; b: string | null;
};
type Raw = Record<string, string | undefined>;

/** The columns the table opens on: the first column of each section, in the file's order. A reader's own choice
 *  (srcols) replaces it; no count is ranked above another by being here. */
export function defaultCols(columns: Column[]): string[] {
  const seen = new Set<string>(), out: string[] = [];
  for (const c of columns) if (!seen.has(c.section)) { seen.add(c.section); out.push(c.key); }
  return out;
}

/** What the address asks of the section, held to what the files offer. */
export function choiceOf(q: Raw, table: TableFile | null, index: IndexFile | null): Choice {
  const columns = table?.columns ?? [];
  const has = (k: string | undefined) => !!k && columns.some((c) => c.key === k);
  const asked = (q.srcols ?? "").slice(0, 1600).split(",").map((s) => s.trim()).filter((k, i, all) => has(k) && all.indexOf(k) === i).slice(0, MAX_COLS);
  // in the file's order, whatever order the address names them in: a column keeps its place beside its section's others
  const cols = asked.length ? columns.filter((c) => asked.includes(c.key)).map((c) => c.key) : defaultCols(columns);
  const sort = has(q.srsort) ? (q.srsort as string) : NAME_SORT;
  const dir: "asc" | "desc" = q.srdir === "asc" ? "asc" : q.srdir === "desc" ? "desc" : sort === NAME_SORT ? "asc" : "desc";
  const kind = (KINDS as string[]).includes(q.srkind ?? "") ? (q.srkind as Kind) : "all";
  const place = (id: string | undefined) => (id && (index?.places ?? []).some((p) => p.id === id) ? id : null);
  const a = place(q.sra), bRaw = place(q.srb);
  return { sort, dir, cols, colsChosen: asked.length > 0, kind, open: place(q.sropen), a, b: bRaw && bRaw !== a ? bRaw : null };
}

const KEY_OK = /^[a-z][a-z0-9_]{0,23}$/;
/** The tab's address with a change to the section's own names: every name the address came with is kept (the tab's
 *  load, its hub table's sort, its rules' filters), bounded so an address cannot grow without end; `null` takes a name
 *  out. `hash` scrolls to a part of the section. */
export function srHref(q: Raw, change: Partial<Record<Param, string | null>> = {}, hash: string | null = ANCHOR, tab: Record<string, string> = {}): string {
  const out = new URLSearchParams();
  out.set("view", "allgrids");
  let n = 0;
  for (const [k, v] of Object.entries(q)) {
    if (k === "view" || typeof v !== "string" || !KEY_OK.test(k) || v.length > 1600 || (k in change) || (k in tab)) continue;
    if ((n += 1) > 48) break;
    out.set(k, v);
  }
  // `tab`: a name of the tab's own that a link of the section sets (rule: the large-load rule the tab opens)
  for (const [k, v] of Object.entries(tab)) if (KEY_OK.test(k) && v) out.set(k, v.slice(0, 200));
  for (const k of PARAMS) { const v = change[k]; if (typeof v === "string" && v !== "") out.set(k, v); }
  return `/cost-of-power?${out.toString()}${hash ? `#${hash}` : ""}`;
}
/** The tab's own anchor and name for a large-load rule (app/cost-of-power/LargeLoadSection.tsx, lib/largeloadrules.ts):
 *  a rule of a place's list opens the tab's rule of the same id, with its document and its cites. */
export const RULES_ANCHOR = "large-load-rules";
export const ruleHref = (q: Raw, id: string): string => srHref(q, {}, RULES_ANCHOR, { rule: id });
/** The change that sorts by a column: a second press turns the order round; the name sort is the address without one. */
export function sortChange(c: Choice, key: string): Partial<Record<Param, string | null>> {
  if (key === NAME_SORT) return c.sort === NAME_SORT && c.dir === "asc" ? { srsort: null, srdir: "desc" } : { srsort: null, srdir: null };
  if (c.sort === key) return { srsort: key, srdir: c.dir === "desc" ? "asc" : null };
  return { srsort: key, srdir: null };
}
/** The change that sets the columns shown: none named when they are the default ones. */
export function colsChange(keys: string[], columns: Column[]): Partial<Record<Param, string | null>> {
  const inOrder = columns.filter((c) => keys.includes(c.key)).map((c) => c.key);
  const def = defaultCols(columns);
  return { srcols: inOrder.length === 0 || (inOrder.length === def.length && inOrder.every((k, i) => k === def[i])) ? null : inOrder.join(",") };
}

// ---- a figure as the section writes it ------------------------------------------------------------------------------

/** A number as the page writes it: whole with commas when the file's value is whole, else two decimals. This is the
 *  form scripts/check-values.mjs expects of a figure it has no rule for (its `shown`), so the section adds none. */
export const figure = (v: number): string => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
/** A unit as a reader reads it beside a figure or in a column's head. */
export const unitWords = (unit: string | null | undefined): string => (!unit || unit === "count" ? "" : unit === "pct" ? "%" : unit === "kgCO2/MWh" ? "kg CO2/MWh" : unit);
/** A time the file gives in UTC ("2026-08-20T21:00:00Z") as the site writes one. */
export const utcWords = (s: string): string => (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(s) ? `${s.slice(0, 10)} ${s.slice(11, 16)} UTC` : s);
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const dayWords = (d: string): string => { const m = d.match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? `${Number(m[3])} ${MONTHS[Number(m[2]) - 1] ?? m[2]} ${m[1]}` : d; };
/** The span a figure covers, in words: "1 Nov 2025 to 31 Oct 2026", a single day, a year. The builder also writes a
 *  period in words of its own ("summer 2027 (...)", "the 730 days to 2026-11-25", "as read to 2026-11-20"): those are
 *  kept as written, with any day in them written as the site writes a day. */
export function periodWords(period: string | null | undefined): string {
  if (!period) return "";
  return period
    .replace(/(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})/g, (_m, a: string, b: string) => `${dayWords(a)} to ${dayWords(b)}`)
    .replace(/\b(\d{4})\.\.(\d{4})\b/g, "$1 to $2")
    .replace(/(^|[^\d-])(\d{4}-\d{2}-\d{2})(?![\d-])/g, (_m, pre: string, d: string) => `${pre}${dayWords(d)}`);
}
/** A month the file names ("2026-10") as words. */
export const monthWords = (m: string): string => { const x = m.match(/^(\d{4})-(\d{2})$/); return x ? `${MONTHS[Number(x[2]) - 1] ?? x[2]} ${x[1]}` : m; };
/** A trend's months that hold a figure, in order: what the small chart draws. Fewer than two: no line. */
export function trendPoints(t: Trend | null | undefined): { t: string; v: number }[] {
  if (!t || !Array.isArray(t.months) || !Array.isArray(t.v)) return [];
  return t.months.map((m, i) => ({ t: `${m}-01`, v: t.v[i] })).filter((p): p is { t: string; v: number } => typeof p.v === "number" && Number.isFinite(p.v));
}

/** The reasons the contract lets a count be held by, each the first words of `held`. */
export const HELD_KINDS = ["license needed", "paused", "not published", "not held", "not a market", "too few"] as const;
export type HeldKind = (typeof HELD_KINDS)[number];
export const LICENSE_NEEDED: HeldKind = "license needed";
/** The kind of a reason, and the whole reason as the hover gives it. A reason that begins with none of the contract's
 *  kinds is "not held", with the file's words kept. */
export function heldKind(held: string | null | undefined): HeldKind {
  const h = (held ?? "").trim().toLowerCase();
  return HELD_KINDS.find((k) => h === k || h.startsWith(`${k}:`)) ?? "not held";
}
export const heldWhy = (held: string | null | undefined): string => (held && held.trim() ? held.trim() : "not held: the file gives no reason");

/** Where a figure comes from, for its hover: the publisher's report in words, the ERW table, when it was retrieved. */
export function sourceWords(sources: Record<string, Source> | undefined, key: string | null | undefined): string {
  const s = key ? sources?.[key] : undefined;
  if (!s) return key ? `Source: ${key}.` : "";
  const parts = [s.report, s.publisher ? `Publisher: ${s.publisher}` : null, s.table ? `ERW table ${s.table}` : null, s.retrieved ? `retrieved ${utcWords(s.retrieved)}` : null].filter(Boolean);
  return parts.length ? `Source: ${parts.join("; ")}.` : "";
}

// ---- the table ------------------------------------------------------------------------------------------------------

/** One cell of table.json, read: the figure, or the reason it is not shown, with the period and the source that
 *  apply (the row's own where it names them, else the column's). */
export type Read = { v: number | null; words: string | null; held: string | null; period: string | null; src: string | null };
export function readCell(table: TableFile, row: TableRow, ci: number): Read {
  const col = table.columns[ci], own = row.cell?.[String(ci)], raw = row.v?.[ci];
  const period = own?.period ?? col?.period ?? null, src = own?.src ?? col?.src ?? null;
  if (own?.held) return { v: null, words: null, held: heldWhy(own.held), period, src };
  if (typeof raw === "number" && Number.isFinite(raw)) return { v: raw, words: null, held: null, period, src };
  if (typeof raw === "string" && raw.trim()) return { v: null, words: raw, held: null, period, src };
  return { v: null, words: null, held: heldWhy(null), period, src };
}
export const colIndex = (table: TableFile, key: string): number => table.columns.findIndex((c) => c.key === key);
/** The period and the source a column's hover gives: the column's own where the file names them (the contract's first
 *  form), else those most of its shown cells share (the builder writes every cell's own and none on the column). A
 *  cell says its own in a hover of its own only where it differs from these. */
export type About = { period: string | null; src: string | null };
export function columnAbout(table: TableFile, ci: number): About {
  const col = table.columns[ci];
  if (col?.period || col?.src) return { period: col.period ?? null, src: col.src ?? null };
  const seen = new Map<string, About & { n: number }>();
  for (const r of table.rows) {
    const own = r.cell?.[String(ci)];
    if (!own || own.held) continue;
    const k = `${own.period ?? ""}|${own.src ?? ""}`;
    const t = seen.get(k) ?? { n: 0, period: own.period ?? null, src: own.src ?? null };
    t.n += 1;
    seen.set(k, t);
  }
  let best: (About & { n: number }) | null = null;
  for (const t of seen.values()) if (!best || t.n > best.n) best = t;
  return best ? { period: best.period, src: best.src } : { period: null, src: null };
}
export const sameAbout = (a: About, b: About): boolean => (a.period ?? "") === (b.period ?? "") && (a.src ?? "") === (b.src ?? "");

/** The rows shown: of the kind asked for, in the file's order, or by a column's figures. A place with no figure in the
 *  column is last in either direction, in the file's order: the order is the column's, never a ranking of places. */
export function rowsShown(table: TableFile, c: Pick<Choice, "sort" | "dir" | "kind">): TableRow[] {
  const rows = table.rows.filter((r) => c.kind === "all" || r.kind === c.kind);
  if (c.sort === NAME_SORT) {
    if (c.dir === "asc") return rows;
    return [...rows].reverse();
  }
  const ci = colIndex(table, c.sort);
  if (ci < 0) return rows;
  const val = (r: TableRow) => readCell(table, r, ci).v;
  const have = rows.filter((r) => val(r) !== null), none = rows.filter((r) => val(r) === null);
  const order = new Map(rows.map((r, i) => [r.id, i]));
  have.sort((x, y) => ((val(x) as number) - (val(y) as number)) * (c.dir === "asc" ? 1 : -1) || (order.get(x.id) as number) - (order.get(y.id) as number));
  return [...have, ...none];
}
/** The columns drawn, in order: the one the table is sorted by first (as the hub table draws its own), then the
 *  chosen ones in the file's order. */
export function colsDrawn(table: TableFile, c: Pick<Choice, "sort" | "cols">): Column[] {
  const chosen = table.columns.filter((x) => c.cols.includes(x.key));
  if (c.sort === NAME_SORT) return chosen;
  const first = table.columns.find((x) => x.key === c.sort);
  return first ? [first, ...chosen.filter((x) => x.key !== c.sort)] : chosen;
}
export const sortWords = (c: Pick<Choice, "sort" | "dir">, table: TableFile): string => {
  if (c.sort === NAME_SORT) return c.dir === "asc" ? "in the file's order: the regions, the market operators, then the balancing authorities" : "in the file's order, turned round";
  const col = table.columns.find((x) => x.key === c.sort);
  return `by ${col ? col.label.toLowerCase() : c.sort}, ${c.dir === "desc" ? "largest first" : "smallest first"}; a place with no figure there last`;
};

// ---- the downloads --------------------------------------------------------------------------------------------------

export const CSV_NAME = "erw-regions-side-by-side.csv";
const csvCell = (v: string | number | null): string => (v === null ? "" : typeof v === "number" ? String(v) : /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);
/** The header of the table's CSV: two columns a count, the figure and, where it is not shown, the reason's kind. */
export const csvColumns = (cols: Column[]): string[] => ["place_id", "kind", "name", ...cols.flatMap((c) => [c.key, `${c.key}.not_shown`])];
/** The rows shown as a CSV in the page's own figures: a count that is not shown is an empty cell and its reason's kind
 *  beside it (never a number). The lines above the header say what the file is, and each column's unit, period and source. */
export function tableCsv(table: TableFile, rows: TableRow[], cols: Column[], address: string): string {
  const head = [
    `# Energy Research Warehouse (ERW): "Where the next gigawatts can go", the places side by side, the rows and columns shown on ${address}`,
    `# Page files built ${table.built}; contract docs/state/page_files_siting_regions.md${table.method ? `; method ${table.method}` : ""}. Each count is as its publisher printed it, or a plain arithmetic of it; nothing is scored or ranked.`,
    ...cols.map((c) => { const a = columnAbout(table, colIndex(table, c.key)); return `# ${c.key}: ${c.label}${unitWords(c.unit) ? `, ${unitWords(c.unit)}` : ""}${a.period ? `; ${periodWords(a.period)}` : ""}${a.src && table.sources[a.src]?.table ? `; ERW table ${table.sources[a.src].table}` : ""}`; }),
  ];
  const body = rows.map((r) => [r.id, r.kind, r.name, ...cols.flatMap((c) => {
    const x = readCell(table, r, colIndex(table, c.key));
    return x.v !== null ? [x.v, ""] : x.words !== null ? [x.words, ""] : ["", heldKind(x.held)];
  })].map(csvCell).join(","));
  return [...head, csvColumns(cols).join(","), ...body].join("\n") + "\n";
}
/** A Python (pandas) and a Stata reader of that CSV: the lines above the header skipped. */
export function pythonReader(nHead: number): string {
  return [`# Energy Research Warehouse (ERW): a reader of ${CSV_NAME}, the places side by side as shown on /cost-of-power?view=allgrids.`,
    "# A count that is not shown is empty, and the column beside it (<count>.not_shown) says why.",
    "import pandas as pd", "", `df = pd.read_csv("${CSV_NAME}", skiprows=${nHead})`, "print(df.shape)", "print(df.head())", ""].join("\n");
}
export function stataReader(nHead: number): string {
  return [`* Energy Research Warehouse (ERW): a reader of ${CSV_NAME}, the places side by side as shown on /cost-of-power?view=allgrids.`,
    "* A count that is not shown is empty, and the column beside it (<count>.not_shown) says why.",
    `import delimited using "${CSV_NAME}", varnames(${nHead + 1}) rowrange(${nHead + 2}) bindquote(strict) clear`, "describe", ""].join("\n");
}
