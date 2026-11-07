// Energy Research Warehouse (ERW) site, session 3650: what the problem sets (lib/problems.ts) need beyond their figures,
// kept in a file that imports nothing so node can test it alone (scripts/test-problemkit.mjs):
//
//   - GUIDE: for each set, the one line a student should be able to do after it, the grids, the tables and the skills it
//     uses (the index lists them), and the order of its five problems from the easiest to the hardest;
//   - sourceOfKey: the words of where a figure came from, read from its check key, for the hover tip every figure carries
//     (components/Num.tsx, `source`): the table, the entity, the variable and the time, and the table's citation;
//   - figureRows and csvOf: every keyed figure of a set as the rows of its CSV download (app/learn/problems/[slug]/data.csv).
//
// No number is typed here: the figures are lib/problems.ts's, each with its check key.

export type KitV = { v: number; k: string; u?: string };
export type KitPart = string | KitV;
export type KitQuestion = { id: string; answer: KitPart[]; steps: KitPart[][]; line?: KitPart[] };

/** The method note every set's figures follow. */
export const METHOD_NOTE = "docs/methods/problem_sets.md";

export type SetGuide = {
  /** what a student should be able to do after the set: one line, read after "After this set a student can" */
  can: string;
  grids: string[];
  tables: string[];
  skills: string[];
  /** the five question ids, the easiest first: the order the live set asks them in (lib/problems.ts, problemSet) */
  order: string[];
};

export const GUIDE: Record<string, SetGuide> = {
  "know-your-grid": {
    can: "read a grid's hourly demand and generation tables and compare two grids by a difference, a ratio and a share",
    grids: ["ERCOT", "CAISO"],
    tables: ["eia930_all_demand", "eia930_all_generation", "storage_daily_cycle", "carbon_intensity_daily"],
    skills: ["MW against MWh", "a daily peak", "a ratio", "a share of a sum", "a local day in UTC"],
    order: ["a4", "a3", "a1", "a2", "a5"],
  },
  "prices-and-your-bill": {
    can: "tell a load-weighted price from a simple one and find the wholesale share of a real retail bill",
    // the hubs whose rows are public: cost_of_power_monthly's ISO-NE, MISO and NYISO rows are held for a license (lib/license.ts)
    grids: ["ERCOT", "CAISO", "SPP"],
    tables: ["cost_of_power_monthly", "cost_of_power_hourly_profile"],
    skills: ["a weighted average", "USD per MWh against cents per kWh", "a share of a bill", "a complete month", "ranking hubs"],
    order: ["b1", "b3", "b4", "b5", "b2"],
  },
  "when-the-grid-broke": {
    can: "measure an extreme event against a baseline of normal days and compare two events on the same figure",
    grids: ["ERCOT", "CAISO", "PJM"],
    tables: ["event_window_daily"],
    skills: ["a baseline", "percentage points against percent", "the maximum of a window", "a ratio across events"],
    order: ["c3", "c2", "c4", "c1", "c5"],
  },
  "storage-and-taxes": {
    can: "compute a battery's round trip and one cycle's earnings, and a well's production tax in three states",
    grids: ["ERCOT"],
    tables: ["storage_daily_cycle", "cost_of_power_hourly_profile", "cost_of_power_monthly", "eia_fuel_spot_prices"],
    skills: ["MWh against kWh", "a round trip efficiency", "a monthly mean of daily prices", "a percent of value", "a tax credit"],
    order: ["d2", "d1", "d4", "d3", "d5"],
  },
  "networks-and-money": {
    can: "read a grid's ties to its neighbors and judge what a solar plant and a battery earn against their debt",
    grids: ["ERCOT", "every balancing authority of EIA-930"],
    tables: ["eia930_all_interchange", "merchant_revenue_monthly", "event_window_daily"],
    skills: ["the sign of a flow", "a net sum", "a capture rate", "a debt service coverage ratio", "an event against normal days"],
    order: ["e3", "e1", "e2", "e4", "e5"],
  },
};

/** The questions in the set's rising order; a question the order does not name keeps its place after the named ones. */
export function inOrder<Q extends { id: string }>(questions: Q[], order: string[]): Q[] {
  const at = (q: Q) => { const i = order.indexOf(q.id); return i < 0 ? order.length : i; };
  return questions.map((q, i) => ({ q, i })).sort((a, b) => at(a.q) - at(b.q) || a.i - b.i).map((x) => x.q);
}

/** The words for one instructor, for the index's hover: each set's tables (the keys /data and the CSVs name) and the
 *  method note. */
export function instructorNote(): string {
  const sets = Object.entries(GUIDE).map(([slug, g]) => `${slug}: ${g.tables.join(", ")}`).join("; ");
  return `Table keys by set: ${sets}. Every figure carries its check key (series|<table>|<entity>|<variable>|<time>, or the computed forms), recomputed by site/scripts/check-values.mjs. Method note: ${METHOD_NOTE}.`;
}

// ---------------------------------------------------------------- where a figure came from

const OP: Record<string, string> = { ratio: "the ratio", diff: "the difference", pct: "the percentage" };
const FILE_OF: Record<string, string> = {
  bill: "the default bill of /learn/bill (site/lib/bill.ts on site/data/bill_rules.json, each tariff line cited there)",
  battery: "the home battery game's assumed battery (site/lib/battery.ts), an assumption, not a measurement",
  sev: "the production tax as /severance computes it (site/lib/severance.ts on site/data/severance_rules.json, each rate cited to its statute)",
  sevcert: "the Texas Comptroller's certified price for the low-producing well credit (site/data/severance_rules.json)",
  sevcredit: "the low-producing well credit the certified price gives (site/lib/severance.ts on site/data/severance_rules.json)",
  net: "the hourly network snapshot /network draws (site/lib/network.ts)",
  mr: "the seller's tab (site/lib/merchant.ts on site/data/merchant_snapshot.json)",
  mrs: "the seller's tab's storm figures (site/lib/merchant.ts on site/data/merchant_snapshot.json)",
  fullday: "the newest UTC day both tables hold in full, every hour of both grids (site/lib/gridday.ts)",
};
/** The table a computed key is drawn from, where it reads one. */
const TABLE_OF: Record<string, string> = {
  bill: "cost_of_power_monthly", net: "eia930_all_interchange", mr: "merchant_revenue_monthly", mrs: "merchant_revenue_monthly",
  sevcert: "", sevcredit: "", sev: "eia_fuel_spot_prices", battery: "cost_of_power_hourly_profile", fullday: "",
};

/** The table a key reads, or "" for a figure computed from a committed file alone. A calc reads its first part's. */
export function tableOfKey(k: string): string {
  const p = k.split("|");
  if (p[0] === "series") return p[1] ?? "";
  if (p[0] === "series_max" || p[0] === "series_sum") return p[1] ?? "";
  if (p[0] === "spotmean") return "eia_fuel_spot_prices";
  if (p[0] === "calc") return tableOfKey((p[2] ?? "").replaceAll("~", "|"));
  if (p[0] === "battery") return p[1] === "cycle" || p[1] === "cycle_fleet" ? "cost_of_power_hourly_profile" : "";
  if (p[0] === "bill") return p[2] === "wholesale" || p[2] === "share" ? "cost_of_power_monthly" : "";
  return TABLE_OF[p[0]] ?? "";
}

/** The short words of one key: what was read, with no citation. Undefined for a key of a form this file does not know. */
export function keyWords(k: string): string | undefined {
  const p = k.split("|");
  const t = (s: string | undefined) => (s ?? "").slice(0, 16).replace("T", " ").replace(/ 00:00$/, "");
  switch (p[0]) {
    case "series": {
      const [, table, entity, variable, ts, event] = p;
      return `${table}: ${entity}, ${variable}, ${t(ts)}${event ? `, event ${event}` : ""}`;
    }
    case "series_max": return `${p[1]}: the highest ${p[2]} of ${p[5]}, ${t(p[3])} to ${t(p[4])} (UTC)`;
    case "series_sum": return `${p[1]}: the sum of ${p[2]} of ${p[5]}, ${t(p[3])} to ${t(p[4])} (UTC)`;
    case "spotmean": return `eia_fuel_spot_prices: the mean of ${p[1]}'s daily spot_price in ${p[2]}`;
    case "calc": {
      const a = keyWords((p[2] ?? "").replaceAll("~", "|")), b = keyWords((p[3] ?? "").replaceAll("~", "|"));
      if (!OP[p[1]] || !a || !b) return undefined;
      return `${OP[p[1]]} of (${a}) and (${b})`;
    }
    default:
      return FILE_OF[p[0]] ? `${FILE_OF[p[0]]}: ${p.slice(1).join(", ")}` : undefined;
  }
}

/** Every table a key reads, a calc's both parts included, in order and once each. */
export function tablesOfKey(k: string): string[] {
  const p = k.split("|");
  if (p[0] === "calc") return [...new Set([...tablesOfKey((p[2] ?? "").replaceAll("~", "|")), ...tablesOfKey((p[3] ?? "").replaceAll("~", "|"))])];
  const t = tableOfKey(k);
  return t ? [t] : [];
}

/** The hover tip of a figure: what was read, and the citation of each table it reads (`cite`, the site's
 *  data/table_citations.json). Undefined for a key of a form this file does not know. */
export function sourceOfKey(k: string, cite: (table: string) => string | undefined): string | undefined {
  const w = keyWords(k);
  if (!w) return undefined;
  const src = tablesOfKey(k).map((t) => cite(t) ?? t);
  return `${w}.${src.length ? ` Source: ${src.join(" ")}` : ""} Method: ${METHOD_NOTE}.`;
}

// ---------------------------------------------------------------- the set's figures as CSV

export type FigureRow = { question: string; key: string; table: string; value: number; unit: string };

/** Every keyed figure of a set, once each, in the order a reader meets them: the worked example, then each question's
 *  answer, its one-line computation and its steps. `held` drops a figure whose table is not public (Num's heldBy). */
export function figureRows(example: KitQuestion | null, questions: KitQuestion[], held: (key: string) => boolean): FigureRow[] {
  const seen = new Set<string>(), rows: FigureRow[] = [];
  for (const q of [...(example ? [example] : []), ...questions]) {
    for (const part of [...q.answer, ...(q.line ?? []), ...q.steps.flat()]) {
      if (typeof part === "string" || seen.has(part.k) || held(part.k) || !Number.isFinite(part.v)) continue;
      seen.add(part.k);
      rows.push({ question: q.id, key: part.k, table: tablesOfKey(part.k).join(" "), value: part.v, unit: part.u ?? "" });
    }
  }
  return rows;
}

const cell = (v: unknown): string => {
  const s = v === null || v === undefined ? "" : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

/** The CSV of a set's figures, with the ERW's '#' provenance lines. */
export function csvOf(slug: string, title: string, rows: FigureRow[], readAt: string, cite: (table: string) => string | undefined): string {
  const head = [
    `# Energy Research Warehouse (ERW) problem set "${title}" (${slug}): every figure of the live set, as the page computes it.`,
    `# Read from the ERW live set (Supabase) and the site's committed files at ${readAt}. Each row's key is its check key (site/scripts/check-values.mjs recomputes it); a figure of a table that is not public is left out.`,
    `# Method: ${METHOD_NOTE}. The rows each question needs, for a dated edition: /problems/<date>/<set>-<question>.csv.`,
  ];
  const lines = [...head, "question,key,table,value,unit,source"];
  for (const r of rows) lines.push([r.question, r.key, r.table, r.value, r.unit, sourceOfKey(r.key, cite) ?? ""].map(cell).join(","));
  return lines.join("\n") + "\n";
}
