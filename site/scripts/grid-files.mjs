// Energy Research Warehouse (ERW) site, session 1182 (chain 091): the Grid tool's panel files, read from a page's HTML.
// Each panel chains 077 and 078 added offers its table as a CSV written into its link (components/grid/PanelFile.tsx:
// <a href="data:text/csv;charset=utf-8,..." download="erw_<panel>[_<part>].csv" data-grid-file="<id>">). Shared by
// scripts/check-table-downloads.mjs (the line: each panel offers its file, which opens with its provenance) and
// scripts/check-download.mjs --grid (the file whole: its rows, its cells, its figures the page's), and tested offline by
// scripts/test-grid-files.mjs on pages drawn from committed fixtures. Reads only; sends nothing.

/** The Grid pages the two checks read by default, each with the files it must offer (an id, or a prefix ending in "_"
 *  for an id that carries a year). The Gravity tab's address carries shape=gravity, as lib/gridtool.ts gridHref writes it. */
export const GRID_FILE_PAGES = [
  ["/grid?grid=ercot&view=network", ["grid_network_ercot", "grid_network_ercot_balance"]],
  ["/grid?grid=us48&view=network", ["grid_network_us48"]],
  ["/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO", ["grid_replay_ERCO", "grid_network_ercot", "grid_network_ercot_balance"]],
  ["/grid?grid=ercot&view=gravity&shape=gravity", ["grid_gravity_ercot", "grid_exchange_ercot_ties", "grid_exchange_ercot_twelve_months"]],
  ["/grid?grid=us48&view=gravity&shape=gravity", ["grid_gravity_us48", "grid_exchange_us48"]],
  ["/grid?grid=ercot&view=clean", ["grid_clean24_ercot"]],
  ["/grid?grid=ercot", ["grid_mix_ercot_hourly", "grid_scarcity_ercot", "grid_ercotnotice_ercot"]],
  ["/grid?grid=ercot&mixp=month", ["grid_mix_ercot_monthly"]],
  ["/grid?grid=caiso", ["grid_scarcity_caiso", "grid_caisoalert_caiso"]],
  ["/grid?grid=caiso&mixp=month", ["grid_mix_caiso_monthly"]],
  ["/grid?grid=us48&mixp=month", ["grid_mix_us48_monthly"]],   // session 1185: the Lower 48 by month, the sum of the states
  ["/grid?grid=ercot&mix=stress", ["grid_stress_ercot_ramp", "grid_stress_ercot_tight_", "grid_stress_ercot_calm", "grid_stress_all_"]],
];

const PREFIX = "data:text/csv;charset=utf-8,";
/** An HTML attribute's text as the browser reads it (React writes &amp;, &quot;, &#x27;, &lt; and &gt;). */
export const unescapeAttr = (s) => s.replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const attr = (tag, name) => { const m = new RegExp(`\\s${name}="([^"]*)"`).exec(tag); return m ? unescapeAttr(m[1]) : null; };

/** Every panel file of a page: its id, its link's attributes and the CSV its data: address holds. */
export function gridFilesOf(html) {
  return [...html.matchAll(/<a\b[^>]*\sdata-grid-file="[^"]*"[^>]*>/g)].map(([tag]) => {
    const href = attr(tag, "href") ?? "";
    let csv = null;
    try { csv = href.startsWith(PREFIX) ? decodeURIComponent(href.slice(PREFIX.length)) : null; } catch { csv = null; }
    return { id: attr(tag, "data-grid-file"), href, download: attr(tag, "download"), rows: Number(attr(tag, "data-grid-file-rows")),
      figures: Number(attr(tag, "data-grid-file-figures")), held: Number(attr(tag, "data-grid-file-held") ?? 0), csv };
  });
}

/** Every figure's value on a page (data-raw), as the page's own figures. */
export const rawsOf = (html) => new Set([...html.matchAll(/\sdata-raw="([^"]*)"/g)].map((m) => unescapeAttr(m[1])));

/** A CSV text to its rows of cells (quoted cells read as CSV). */
export function parseCsv(text) {
  const rows = [];
  let row = [], cur = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; continue; }
    if (c === '"') { q = true; continue; }
    if (c === ",") { row.push(cur); cur = ""; continue; }
    if (c === "\n") { row.push(cur); rows.push(row); row = []; cur = ""; continue; }
    cur += c;
  }
  if (cur !== "" || row.length) { row.push(cur); rows.push(row); }
  return rows;
}

const NUMBER = /^-?\d+(\.\d+)?(e[+-]?\d+)?$/i;
/** The problems of one file (none: it is whole). `raws`: the page's figures (rawsOf). Checked: the link (a CSV data:
 *  address, an attachment named for its id); the top (the provenance lines, then the columns); the rows (as many as the
 *  link says, each with as many cells as there are columns); the figures (every number past the first column, and every
 *  "Figure:" line's number, is a figure the page draws; the link says how many it holds, at least one). */
export function gridFileProblems(f, raws) {
  const out = [];
  if (!f.href.startsWith(PREFIX)) out.push("the link is not a CSV data: address");
  if (f.csv === null) { out.push("its data: address does not decode"); return out; }
  if (f.download !== `erw_${f.id}.csv`) out.push(`it downloads as ${f.download}, not erw_${f.id}.csv`);
  const lines = f.csv.split("\n");
  const k = lines.findIndex((l) => !l.startsWith("# "));
  const top = lines.slice(0, k);
  const want = [["the tool's line", /^# ERW \(Energy Research Warehouse\), the Grid tool: \S/], ["the panel and its page", /^# Panel: grid_[A-Za-z0-9_]+.*, on the page \/grid\?/],
    ["the tables", /^# Tables: [a-z0-9_]+/], ["the filter", /^# Filter: \S/], ["the hour or window", /^# (Hour|Window): \S/], ["the time drawn", /^# Drawn: \d{4}-\d\d-\d\dT\d\d:\d\d/]];
  for (const [what, r] of want) if (!top.some((l) => r.test(l))) out.push(`its header does not give ${what}`);
  if (k < 0 || !lines[k]) { out.push("no columns after the header"); return out; }
  const body = parseCsv(lines.slice(k).join("\n").replace(/\n$/, ""));
  const width = body[0].length;
  if (body.length - 1 !== f.rows) out.push(`${body.length - 1} rows, the link says ${f.rows}`);
  const bad = body.filter((r) => r.length !== width).length;
  if (bad) out.push(`${bad} rows do not have its ${width} columns`);
  const nums = [...body.slice(1).flatMap((r) => r.slice(1)).filter((c) => NUMBER.test(c)),
    ...top.filter((l) => l.startsWith("# Figure: ")).map((l) => /: (-?[\d.e+-]+)(?: \(key [^)]*\))?$/i.exec(l)?.[1]).filter((x) => x && NUMBER.test(x))];
  const stray = nums.filter((n) => !raws.has(n));
  if (stray.length) out.push(`${stray.length} number(s) of the file are no figure of the page: ${stray.slice(0, 3).join(", ")}`);
  if (!(f.figures > 0)) out.push("the link says it holds no figure");
  return out;
}

/** The files a page must offer and does not: `ids` the page's file ids, `want` the expected ids or prefixes. */
export const missingFiles = (ids, want) => want.filter((w) => !ids.some((id) => (w.endsWith("_") ? id.startsWith(w) : id === w)));
