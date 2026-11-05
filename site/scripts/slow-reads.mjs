// Energy Research Warehouse (ERW) site, session 580: the slowest reads of a build, from its log.
//
//   ERW_READ_TIMING=1 npm run build > ../runs/s580_build.out 2>&1
//   node scripts/slow-reads.mjs ../runs/s580_build.out [N] [--json out.json]
//
// Reads the "[erw-read] {...}" lines lib/supabase.ts prints when ERW_READ_TIMING=1 (session 580), groups the requests
// by kind, table and query (a page asked for twice, by two pages of the site or by a retry, is one read: its slowest
// time is kept, and how often it was asked), and prints the N slowest (20 by default) as a Markdown table: the table,
// the filter (every parameter but select, order, limit and offset), the order, the rows answered (or counted, for a
// count), the status and the time in milliseconds. --json also writes every grouped read, slowest first. Reads a file
// only; sends nothing. Exit 0, or 2 when the log holds no timing line (the build was not started with the switch on).
import { readFileSync, writeFileSync } from "node:fs";

export function parseLines(text) {
  const out = [];
  for (const line of text.split(/\r?\n/)) {
    const i = line.indexOf("[erw-read] ");
    if (i < 0) continue;
    try {
      out.push(JSON.parse(line.slice(i + "[erw-read] ".length)));
    } catch {
      // a line cut by another worker's output is skipped, not guessed at
    }
  }
  return out;
}

/** Rows a request answered, from PostgREST's Content-Range: "0-999/*" is 1,000 rows, "*\/0" none; a count's total. */
export function rowsOf(kind, range) {
  const [span, total] = String(range ?? "").split("/");
  if (kind === "count") return Number.isFinite(Number(total)) && total !== "" && total !== "*" ? Number(total) : null;
  if (span === "*") return 0;
  const m = /^(\d+)-(\d+)$/.exec(span ?? "");
  return m ? Number(m[2]) - Number(m[1]) + 1 : null;
}

export function describe(query) {
  const p = new URLSearchParams(query);
  const filter = [];
  for (const [k, v] of p) if (!["select", "order", "limit", "offset"].includes(k)) filter.push(`${k}=${v}`);
  return { filter: filter.join("&"), order: p.get("order") ?? "", select: p.get("select") ?? "*", offset: Number(p.get("offset") ?? 0) };
}

export function group(lines) {
  const by = new Map();
  for (const l of lines) {
    const key = `${l.kind}|${l.table}|${l.query}`;
    const g = by.get(key) ?? { kind: l.kind, table: l.table, query: l.query, ms: -1, asked: 0, statuses: new Set(), rows: null };
    g.asked++;
    g.statuses.add(l.status);
    if (l.ms > g.ms) {
      g.ms = l.ms;
      const r = rowsOf(l.kind, l.range);
      if (r !== null) g.rows = r;
    } else if (g.rows === null) g.rows = rowsOf(l.kind, l.range);
    by.set(key, g);
  }
  return [...by.values()].map((g) => ({ ...g, statuses: [...g.statuses].join(","), ...describe(g.query) })).sort((a, b) => b.ms - a.ms);
}

const cell = (s) => String(s).replace(/\|/g, "\\|");

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, "/").split("/").pop())) {
  const [file, nArg, ...rest] = process.argv.slice(2);
  if (!file) {
    console.log("usage: slow-reads.mjs <build log> [N] [--json out.json]");
    process.exit(2);
  }
  const lines = parseLines(readFileSync(file, "utf8"));
  if (!lines.length) {
    console.log(`no [erw-read] line in ${file}: was the build started with ERW_READ_TIMING=1?`);
    process.exit(2);
  }
  const n = Number(nArg) > 0 ? Number(nArg) : 20;
  const groups = group(lines);
  const j = rest.indexOf("--json");
  if (j >= 0 && rest[j + 1]) writeFileSync(rest[j + 1], JSON.stringify(groups, null, 1));
  const total = lines.reduce((s, l) => s + l.ms, 0);
  console.log(`${lines.length} requests, ${groups.length} distinct reads, ${Math.round(total / 1000)} s of request time in all`);
  console.log("");
  console.log("| # | ms | kind | table | filter | order | offset | rows | asked | status |");
  console.log("|---|---|---|---|---|---|---|---|---|---|");
  groups.slice(0, n).forEach((g, i) => {
    console.log(`| ${i + 1} | ${g.ms} | ${g.kind} | ${cell(g.table)} | ${cell(g.filter)} | ${cell(g.order)} | ${g.offset} | ${g.rows ?? "?"} | ${g.asked} | ${g.statuses} |`);
  });
}
