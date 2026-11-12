// Energy Research Warehouse (ERW) site, sessions 3304 to 3306 (chain 200): the company database's pages (/companies and
// /companies/<id>), the pure part: the files' types, the index's filters, its order and its pages, a company's MW by
// year in spans, its rows as a CSV, and the Python and Stata readers of that CSV. No file is read here and nothing is
// fetched (lib/companydata.ts reads the files); scripts/test-companies.mjs tests this on rows written for the test.
// The files: site/data/companies/ (warehouse/derived/companies_page.py); the method: docs/methods/companies.md.

export type CompanyIndex = {
  built: string; method: string; tables: string[]; held_tables: string[]; held_links: Record<string, number>;
  held_only: number; n_directory: number; n_listed: number; sources: Record<string, string>;
  columns: string[]; link_columns: string[]; rules: string[]; confidence: Record<string, number>;
  kinds: Record<string, number>; segments: Record<string, number>; states: Record<string, number>; grids: Record<string, number>;
  rows: (string | number)[][];
};
/** One listed company, as the index holds it (a figure the hold leaves out is undefined). */
export type IndexRow = {
  id: string; name: string; kind: string; segment: string; hq_state: string; states: string; grids: string;
  n_plants: number; plants_mw: number; planned_mw: number; n_queue: number; queue_mw: number; n_reactors: number;
  n_policy_actions: number; n_deals?: number; deals_mw?: number; n_facilities?: number; facilities_mw?: number;
  footprint_mw: number; n_links: number; aka: string; first_seen: string; last_seen: string;
};
export type Figures = Record<string, number>;
/** A link as a shard holds it: [link id, table position, row, role, name as written ("" = the company's own), rule
 *  position, mw, usd, date, fuel, state, grid, detail]. */
export type ShardLink = [string, number, string, string, string, number, string, string, string, string, string, string, string];
export type Company = {
  id: string; entity_id: string; name: string; kind: string; kind_basis: string; segment: string; segment_basis: string;
  parent: string; parent_id: string; parent_basis: string; eia_utility_id: string; hq_state: string; hq_basis: string;
  states: string[]; grids: string[]; first_seen: string; last_seen: string; figures: Figures; fuel: Record<string, number>;
  years: [string, number, number, number][]; quarters: [string, number, number, number][]; held: Record<string, number>;
  min_confidence: number; names: [string, string, string, number, string][]; links: ShardLink[];
};
/** A link with its table and rule named. */
export type Link = {
  link: string; table: string; row: string; role: string; name: string; rule: string; confidence: number; mw: string;
  usd: string; date: string; fuel: string; state: string; grid: string; detail: string;
};

export const KIND_ORDER = ["regulator", "lab or hyperscaler", "OEM", "utility", "IPP", "lender or investor", "developer", "operator", "other"];
export const PAGE_SIZE = 50;
/** The tables' names as a reader knows them. */
export const TABLE_WORDS: Record<string, string> = {
  energy_deals: "Deals (energy_deals)", datacenter_projects: "Datacenter projects", datacenter_facilities: "Datacenter facilities",
  eia860m_operating_generators: "EIA-860M operating generators", eia860m_planned_generators: "EIA-860M planned generators",
  eia860_plants_annual: "EIA-860 plants", eia860_generator_owners: "EIA-860 generator owners", eia861_utility_data: "EIA-861 utility data",
  utility_service_territories: "EIA-861 service territories", ercot_interconnection_queue: "ERCOT interconnection queue",
  nyiso_interconnection_queue: "NYISO interconnection queue", policy_actions: "Policy actions", nrc_power_reactors: "NRC power reactors",
};
export const ROLE_WORDS: Record<string, string> = {
  buyer: "buyer", seller: "seller", party: "party", operator: "operator", developer: "developer", utility: "utility",
  owner: "owner", service_territory: "service territory", interconnection_customer: "interconnection customer",
  agency: "agency", licensee: "licensee", parent: "parent",
};
/** Session 1878 (companies faults row 4): the builder's match rules (index.rules) as a reader knows them. */
export const RULE_WORDS: Record<string, string> = {
  eia_id: "EIA utility id", reviewed_alias: "reviewed alias", anchored_name: "name of an EIA company", name: "same name",
  company_word: "a company word added",
};
export const ruleWords = (rule: string): string => RULE_WORDS[rule] ?? rule;

/** Session 1878 (companies faults row 3): a count with its noun, one or many ("1 row", "2 rows"). */
export function plural(n: number, one: string, many: string): string {
  return `${count(n)} ${Math.round(n) === 1 ? one : many}`;
}

export function indexRows(ix: CompanyIndex): IndexRow[] {
  return ix.rows.map((r) => Object.fromEntries(ix.columns.map((c, i) => [c, r[i]])) as unknown as IndexRow);
}

export function linksOf(c: Company, ix: Pick<CompanyIndex, "tables" | "rules" | "confidence">): Link[] {
  return c.links.map(([link, t, row, role, name, rule, mw, usd, date, fuel, state, grid, detail]) => {
    const r = ix.rules[rule] ?? "";
    return { link, table: ix.tables[t] ?? "", row, role, name: name || c.name, rule: r, confidence: ix.confidence[r] ?? 0, mw, usd, date, fuel, state, grid, detail };
  });
}

// ---- the index's query, kept in the address so a view can be shared and works without script

export type Sort = "footprint" | "operating" | "planned" | "queue" | "policy" | "name";
export type Query = {
  q: string; kind: string; segment: string; state: string; grid: string;
  has: "" | "plants" | "queue" | "reactors" | "policy" | "deals" | "facilities"; sort: Sort; page: number;
};
export const NO_QUERY: Query = { q: "", kind: "", segment: "", state: "", grid: "", has: "", sort: "footprint", page: 1 };
const HAS = ["plants", "queue", "reactors", "policy", "deals", "facilities"] as const;
/** Session 1878 (companies faults row 11): the index's orders, each a column of the index; `footprint` is the file's own
 *  order and is left out of an address; `name` is A to Z, every other largest first. */
export const SORTS: Record<Sort, { col: keyof IndexRow; words: string }> = {
  footprint: { col: "footprint_mw", words: "the largest footprint first" },
  operating: { col: "plants_mw", words: "the most operating MW first" },
  planned: { col: "planned_mw", words: "the most planned MW first" },
  queue: { col: "queue_mw", words: "the most ERCOT queue MW first" },
  policy: { col: "n_policy_actions", words: "the most policy actions first" },
  name: { col: "name", words: "by name, A to Z" },
};

/** The query an address asks for; a value the index does not hold is no filter. `deals` and `facilities` are
 *  filters only while their tables are not held (index.columns names their figures). */
export function queryOf(sp: Record<string, string | string[] | undefined>, ix: Pick<CompanyIndex, "kinds" | "segments" | "states" | "grids" | "columns">): Query {
  const one = (k: string) => { const v = sp[k]; return (Array.isArray(v) ? v[0] : v ?? "").trim(); };
  const pick = (v: string, have: Record<string, number>) => (v in have ? v : "");
  const has = one("has");
  const hasOk = (HAS as readonly string[]).includes(has) && (has === "deals" ? ix.columns.includes("n_deals") : has === "facilities" ? ix.columns.includes("n_facilities") : true);
  const page = Math.max(1, Math.floor(Number(one("page")) || 1));
  const sort = one("sort");
  return {
    q: one("q").slice(0, 80), kind: pick(one("kind"), ix.kinds), segment: pick(one("segment"), ix.segments),
    state: pick(one("state").toUpperCase(), ix.states), grid: pick(one("grid"), ix.grids),
    has: hasOk ? (has as Query["has"]) : "", sort: sort in SORTS ? (sort as Sort) : "footprint", page,
  };
}

/** The address of a query (only what differs from no query); `page` 1 is left out. */
export function hrefOf(base: string, q: Query, over: Partial<Query> = {}): string {
  const v = { ...q, ...over };
  const p = new URLSearchParams();
  for (const k of ["q", "kind", "segment", "state", "grid", "has"] as const) if (v[k]) p.set(k, String(v[k]));
  if (v.sort && v.sort !== "footprint") p.set("sort", v.sort);
  if (v.page > 1) p.set("page", String(v.page));
  const s = p.toString();
  return s ? `${base}?${s}` : base;
}

const fold = (s: string) => s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

/** The rows a query keeps, in the query's order (the index's own, the footprint largest first, when none is asked; a
 *  tie keeps the index's order). The search reads the name and the other names; every word typed must be in one of them. */
export function filterRows(rows: IndexRow[], q: Query): IndexRow[] {
  const words = fold(q.q).split(/[^a-z0-9&]+/).filter(Boolean);
  const kept = rows.filter((r) => {
    if (q.kind && r.kind !== q.kind) return false;
    if (q.segment && r.segment !== q.segment) return false;
    if (q.state && !r.states.split(";").includes(q.state)) return false;
    if (q.grid && !r.grids.split(";").includes(q.grid)) return false;
    if (q.has === "plants" && !(r.n_plants > 0)) return false;
    if (q.has === "queue" && !(r.n_queue > 0)) return false;
    if (q.has === "reactors" && !(r.n_reactors > 0)) return false;
    if (q.has === "policy" && !(r.n_policy_actions > 0)) return false;
    if (q.has === "deals" && !((r.n_deals ?? 0) > 0)) return false;
    if (q.has === "facilities" && !((r.n_facilities ?? 0) > 0)) return false;
    if (words.length) {
      const hay = fold(`${r.name} | ${r.aka}`);
      if (!words.every((w) => hay.includes(w))) return false;
    }
    return true;
  });
  const sort = q.sort ?? "footprint";
  if (sort === "footprint") return kept;
  if (sort === "name") return kept.sort((a, b) => fold(a.name).localeCompare(fold(b.name), "en-US"));
  const col = SORTS[sort].col;
  return kept.sort((a, b) => Number(b[col] ?? 0) - Number(a[col] ?? 0));
}

/** Session 1878 (companies faults row 5): the names that more than one listed row carries; such a row's cell adds its id. */
export function sharedNames(rows: Pick<IndexRow, "name">[]): Set<string> {
  const seen = new Set<string>(), twice = new Set<string>();
  for (const r of rows) (seen.has(r.name) ? twice : seen).add(r.name);
  return twice;
}
/** The words that tell a row from another of the same name: its EIA utility id, or its id when it has none. */
export function idTag(id: string): { text: string; title: string } {
  const m = /^eia-(\d+)$/.exec(id);
  return m ? { text: `EIA ${m[1]}`, title: `EIA utility id ${m[1]}` } : { text: id, title: `The company database's id ${id}` };
}

/** Session 1878 (companies faults row 6): what EIA-861 writes as a state that is not one. */
export const NOT_STATES: Record<string, string> = { CN: "Canada, as EIA-861 writes it" };
export const stateLabel = (code: string, n: number): string => `${code}${NOT_STATES[code] ? ` (${NOT_STATES[code]})` : ""} (${count(n)})`;
/** The States cell: the first `most`, and every state in the hover, the count first. */
export function statesCell(states: string, most = 3): { text: string; title: string } {
  const all = states.split(";").filter(Boolean);
  return {
    text: `${all.slice(0, most).join(", ")}${all.length > most ? " ..." : ""}`,
    title: all.length ? `${plural(all.length, "state", "states")}: ${all.map((s) => (NOT_STATES[s] ? `${s} (${NOT_STATES[s]})` : s)).join(", ")}` : "",
  };
}

/** One page of rows, and the page shown (a page past the last is the last). */
export function pageOf<T>(rows: T[], page: number, size = PAGE_SIZE): { rows: T[]; page: number; pages: number } {
  const pages = Math.max(1, Math.ceil(rows.length / size));
  const p = Math.min(Math.max(1, page), pages);
  return { rows: rows.slice((p - 1) * size, p * size), page: p, pages };
}

// ---- a company's MW by year, in spans when its years are many

export type YearGroup = { label: string; sub?: string; operating: number; planned: number; queue: number; years: string[] };
/** The years of a company's MW (operating generators by the month they began, planned by the month planned, queue
 *  positions by the date they entered), one group a year; past `most` years (15 since session 3307), one group a span of `span` years (the
 *  first span starts at a multiple of `span`). Sums, not rounded. */
export function yearGroups(years: [string, number, number, number][], most = 15, span = 5): YearGroup[] {
  if (!years.length) return [];
  const first = Number(years[0][0]), last = Number(years[years.length - 1][0]);
  const by = new Map(years.map((y) => [y[0], y]));
  const width = last - first + 1 > most ? span : 1;
  const start = width > 1 ? Math.floor(first / width) * width : first;
  const out: YearGroup[] = [];
  for (let a = start; a <= last; a += width) {
    const ys: string[] = [];
    let o = 0, p = 0, q = 0;
    for (let y = a; y < a + width && y <= last; y++) {
      const v = by.get(String(y));
      if (!v) continue;
      ys.push(String(y)); o += v[1]; p += v[2]; q += v[3];
    }
    const b = Math.min(a + width - 1, last);
    // session 3307: a span is its first year with "to" and the last year's two digits under it ("1990", "to 94"), so the
    // labels of sixteen spans fit a phone's chart; one year is its own label
    out.push({ label: String(a), sub: width > 1 ? `to ${String(b).slice(2)}` : undefined, operating: o, planned: p, queue: q, years: ys });
  }
  return out;
}

// ---- a company page's words (session 1878, companies faults rows 2, 3 and 7 to 10)

/** The lead's count of rows: "143 public rows of 6 tables name it; 2 held rows do too." (one is one: "1 public row of
 *  1 table names it"). */
export function leadRows(nLinks: number, nTables: number, nHeld: number): string {
  return `${plural(nLinks, "public row", "public rows")} of ${plural(nTables, "table", "tables")} name${nLinks === 1 ? "s" : ""} it${nHeld ? `; ${plural(nHeld, "held row does", "held rows do")} too` : ""}.`;
}

/** What a company figure sums or counts, from its own rows by the builder's rules (warehouse/derived/companies_page.py,
 *  figures): the hover of the figure says the count actually summed, not the count of the table's rows. */
export function basisOf(col: string, table: string, links: Link[]): string {
  const of = links.filter((l) => l.table === table);
  const rows = (n: number) => plural(n, "row", "rows");
  const distinct = (xs: Link[], by: (l: Link) => string = (l) => l.row) => new Set(xs.map(by)).size;
  if (col === "queue_mw") {
    const live = of.filter((l) => l.detail !== "withdrawn" && l.detail !== "Completed");
    return `the sum of the ${rows(live.length)} of ${count(of.length)} neither withdrawn nor completed (${plural(distinct(live), "position", "positions")})`;
  }
  if (col === "n_reactors") {
    const lic = of.filter((l) => l.role === "licensee" || l.role === "operator");
    return `a count of ${plural(distinct(lic), "reactor", "reactors")} it is the licensee or operator of, over ${rows(of.length)} (licensee, operator or parent)`;
  }
  if (col === "n_policy_actions") return `a count of ${plural(distinct(of), "policy action", "policy actions")} over ${rows(of.length)}`;
  if (col === "plants_mw") return `the sum of ${rows(of.length)}, one an operating generator, at ${plural(distinct(of, (l) => l.detail), "plant", "plants")}`;
  if (col === "planned_mw") return `the sum of ${rows(of.length)}, one a planned generator, at ${plural(distinct(of, (l) => l.detail), "plant", "plants")}`;
  if (col === "owned_mw") return `the sum of ${rows(of.length)} of ${plural(distinct(of), "jointly owned generator", "jointly owned generators")}, each its nameplate MW times the percent owned`;
  if (col.startsWith("mw_")) {
    const fuel = col.slice(3);
    return `the sum of ${rows(of.filter((l) => (l.fuel || "other") === fuel).length)} of operating generators whose fuel is ${fuel}`;
  }
  return `from ${rows(of.length)}`;
}

/** The last date seen: a date after the file's build is a planned generator's planned month, and says so. */
export const seenLast = (last: string, built: string): string => (last && last.slice(0, 10) > built.slice(0, 10) ? `${last} (planned)` : last);

/** A fuel's share's hover: the two figures it divides, keyed by their columns. */
export const shareTitle = (fuel: string, v: number, total: number): string => `mw_${fuel} ${mw(v)} of plants_mw ${mw(total)} (company_directory)`;

/** The MW by year chart's series that have a group above zero (a series zero in every group is not drawn or named). */
export const YEAR_SERIES = ["operating", "planned", "queue"] as const;
export function liveSeries(groups: YearGroup[]): (typeof YEAR_SERIES)[number][] {
  return YEAR_SERIES.filter((k) => groups.some((g) => g[k] > 0));
}

/** Whether a company page draws its deals by quarter: while energy_deals is held, only for a company held rows name
 *  (the hold line); once it is not, only for a company with quarters. */
export const showDeals = (c: Pick<Company, "held" | "quarters">, dealsHeld: boolean): boolean =>
  dealsHeld ? (c.held.energy_deals ?? 0) > 0 : c.quarters.length > 0;

// ---- the downloads: a company's public rows, and the index's rows of a query

const CSV_SAFE = /[",\n\r]/;
export const csvCell = (v: unknown): string => {
  const s = v === null || v === undefined ? "" : String(v);
  return CSV_SAFE.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

export const LINK_HEAD = ["company_id", "company_name", "input_table", "input_row", "role", "name_as_written", "match_rule", "confidence", "mw", "usd", "date", "fuel", "state", "grid", "detail", "link_id"];

/** A company's public rows as a CSV, its provenance first on lines that begin with "#". */
export function linksCsv(c: Company, links: Link[], ix: Pick<CompanyIndex, "built" | "held_tables" | "sources">, url: string): string {
  const held = Object.entries(c.held);
  const head = [
    `# Energy Research Warehouse (ERW): ${c.name} (${c.entity_id}), every public row of the company database's links (company_links) that names it.`,
    `# From ${url}, built ${ix.built} by warehouse/derived/companies_page.py; method docs/methods/companies.md.`,
    "# One row a company named in a row of an input table: input_table and input_row name the row; role is what the company is in it; match_rule and confidence how the name was matched; mw, usd, date, fuel, state and grid as the row states them.",
    held.length
      ? `# Held, not in this file (license needed: the publishers ask for permission): ${held.map(([t, n]) => `${plural(n, "row", "rows")} of ${t}`).join(", ")}.`
      : "# No row of this company is held.",
    ...Array.from(new Set(links.map((l) => l.table))).map((t) => `# Source of ${t}: ${ix.sources[t] ?? ""}`),
  ];
  const rows = links.map((l) => [c.entity_id, c.name, l.table, l.row, l.role, l.name, l.rule, l.confidence, l.mw, l.usd, l.date, l.fuel, l.state, l.grid, l.detail, l.link].map(csvCell).join(","));
  return [...head, LINK_HEAD.join(","), ...rows, ""].join("\n");
}

/** The index's rows of a query as a CSV. */
export function indexCsv(rows: IndexRow[], ix: Pick<CompanyIndex, "built" | "columns" | "held_tables" | "held_only">, q: Query, url: string): string {
  const cols = ix.columns;
  const head = [
    "# Energy Research Warehouse (ERW): the company database (company_directory), the companies listed on /companies, as filtered.",
    `# From ${url}, built ${ix.built} by warehouse/derived/companies_page.py; method docs/methods/companies.md.`,
    `# Filters: ${(["q", "kind", "segment", "state", "grid", "has"] as const).map((k) => `${k}=${q[k] || "(any)"}`).join(", ")}.`,
    `# Order: sort=${q.sort ?? "footprint"}, ${SORTS[q.sort ?? "footprint"].words}.`,
    "# Every figure is from public rows alone; MW are nameplate (EIA-860M) or as the queue states them; footprint_mw is a sort key (plants, owned, planned and queue MW summed).",
    ix.held_tables.length
      ? `# Held (license needed): ${ix.held_tables.join(", ")}; ${plural(ix.held_only, "company", "companies")} named only in them ${ix.held_only === 1 ? "is" : "are"} not listed, and their rows add nothing here.`
      : "# No table is held.",
  ];
  return [...head, cols.join(","), ...rows.map((r) => cols.map((c) => csvCell((r as unknown as Record<string, unknown>)[c])).join(",")), ""].join("\n");
}

/** A reader of one of the CSVs above, in Python or in Stata: the "#" lines printed (Python) or counted (Stata) and
 *  skipped, the rows loaded as they are. The Stata reader keeps the owner's rules (no line continuation, one empty line
 *  between commands outside a loop and none inside one, every figure column destrung with force). Pure: the address
 *  and the figure columns are given. */
export function reader(as: "py" | "do", url: string, what: string, figures: string[]): string {
  if (as === "py") {
    return [
      `# Energy Research Warehouse (ERW): read ${what} (site/lib/companydb.ts reader).`,
      "# The CSV opens with its provenance, lines that begin with \"#\"; they are printed and skipped, and the rows are",
      "# loaded as they are. Needs pandas.",
      "import io",
      "import urllib.request",
      "",
      "import pandas as pd",
      "",
      `URL = "${url}"`,
      "text = urllib.request.urlopen(URL, timeout=300).read().decode(\"utf-8\")",
      "lines = text.splitlines()",
      "n = 0",
      "while n < len(lines) and lines[n].startswith(\"#\"):",
      "    n += 1",
      "print(\"\\n\".join(lines[:n]))",
      "rows = pd.read_csv(io.StringIO(\"\\n\".join(lines[n:])), dtype=str, keep_default_na=False)",
      ...figures.map((c) => `rows["${c}"] = pd.to_numeric(rows["${c}"], errors="coerce")`),
      "print(rows.shape)",
      "print(rows.head(20))",
      "",
    ].join("\n");
  }
  return [
    `* Energy Research Warehouse (ERW): read ${what} (site/lib/companydb.ts reader).`,
    "* The CSV opens with its provenance, lines that begin with \"#\"; they are counted and skipped, the column names are",
    "* the first line after them.",
    "clear",
    "",
    "tempfile raw",
    "",
    `copy "${url}" \`raw'`,
    "",
    "tempname fh",
    "",
    "local n 0",
    "",
    "file open `fh' using `raw', read text",
    "",
    "file read `fh' line",
    "",
    "while r(eof) == 0 {",
    "    if substr(`\"`macval(line)'\"', 1, 1) != \"#\" continue, break",
    "    local n = `n' + 1",
    "    file read `fh' line",
    "}",
    "",
    "file close `fh'",
    "",
    "import delimited using `raw', varnames(`=`n' + 1') encoding(\"utf-8\") bindquote(strict) stringcols(_all) clear",
    "",
    ...figures.flatMap((c) => [`destring ${c}, replace force`, ""]),
    "describe",
    "",
  ].join("\n");
}

/** A number as the pages write it: whole MW with thousands commas, a share with one decimal. */
export const mw = (v: number): string => Math.round(v).toLocaleString("en-US");
export const count = (v: number): string => Math.round(v).toLocaleString("en-US");
