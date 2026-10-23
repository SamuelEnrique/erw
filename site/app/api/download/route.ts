// Energy Research Warehouse (ERW) site: GET /api/download?table=<table>, one public table of the live set
// as CSV (session 21, ruling 10). Streams from Supabase with the anon key (public rows only), page by
// page, with the table's provenance header lines at the top (as '#' lines, as in the ERW's own CSVs),
// then the table's columns in their CSV order. A windowed table (for example the last 35 days of prices)
// gives what the live set holds; the full history is on Redivis.
//
// Session 368: pages by key, not by offset, and takes no row count. The count (Prefer: count=exact) and a page deep in
// a table by offset passed the anon role's three-second statement timeout on the largest tables (session 328's finding,
// the night note of 20 October 2026, item 3). Each page now starts after the last row of the one before, on the table's
// primary key in the live set (warehouse/supabase/migrations/001_shapes.sql and 011: series (table_name, entity,
// variable, ts_utc, event), entities (table_name, entity_id), events (table_name, event_id)), so every page is a short
// range read of that key's index; the stream ends when a page comes back short. The rows come in the order they came in
// before (series entity, variable, ts_utc; entities entity_id; events event_id), with event last for the series rows that
// share the first three. The first pages are read before the answer starts: a table that ends within them is counted as
// before (the same line, the same bytes); a larger one is streamed a page at a time as the reader takes it, its line
// saying the count was not taken.
import site from "@/data/site.json";
import citations from "@/data/table_citations.json";
import { downloadFilter, type Shape } from "@/lib/downloadfilter";
import { limited } from "@/lib/guard";
import { licenseNeeded, licensePublishers } from "@/lib/license";
import { refusal, verdictOf } from "@/lib/packages";
import { COOKIE, cookieOpens } from "@/lib/release";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// session 368: the largest table of the live set (ercot_as_prices, about 340,000 rows) is some 340 short reads
export const maxDuration = 300;

// session 368: no count is taken, so the limit is kept as the rows are streamed: a table that passes it ends in an error,
// never in a file that looks whole. 200,000 until session 368; ercot_as_prices, whole in the live set, holds 338,132.
const MAX_ROWS = 500_000;
// session 1009 (chain 070): the cap and the hourly limit may be set lower on the server (ERW_DOWNLOAD_MAX_ROWS,
// ERW_DOWNLOAD_PER_HOUR); never higher than the cap above, and 60 an hour when the variable is not set
const ROW_CAP = Math.min(Number(process.env.ERW_DOWNLOAD_MAX_ROWS) || MAX_ROWS, MAX_ROWS);
const PER_HOUR = Number(process.env.ERW_DOWNLOAD_PER_HOUR) || 60;
const PAGE = 1000;
// the rows read before the answer starts: a table that ends within them carries its count on the "Downloaded" line
const FIRST_ROWS = 50_000;
const STD: Record<string, string[]> = {
  series: ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"],
  entities: ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"],
  events: ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"],
};
// each shape's primary key after table_name, in order: the order of the rows and the page's start
const KEY: Record<string, string[]> = { series: ["entity", "variable", "ts_utc", "event"], entities: ["entity_id"], events: ["event_id"] };

function supa() {
  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL or SUPABASE_ANON_KEY is not set on the server");
  return { base: new URL(url).origin, headers: { apikey: key, Authorization: `Bearer ${key}` } };
}

async function get(path: string, extra: Record<string, string> = {}) {
  const { base, headers } = supa();
  const res = await fetch(`${base}/rest/v1/${path}`, { headers: { ...headers, ...extra }, cache: "no-store" });
  if (!res.ok) throw new Error(`Supabase ${path.split("?")[0]}: HTTP ${res.status}`);
  return res;
}

// the ERW writes UTC times with Z; Supabase returns +00:00
const cell = (v: unknown): string => {
  if (v === null || v === undefined) return "";
  let s = typeof v === "object" ? JSON.stringify(v) : String(v);
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$/.test(s)) s = s.replace("+00:00", "Z");
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

const text = (msg: string, status: number) => new Response(msg + "\n", { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });

/** Session 328: a reader of one table's CSV from this route, in Python or Stata. It fetches the CSV, keeps the lines that
 *  begin with "#" (the table's provenance: the source report, its address, when it was retrieved) and loads the rows that
 *  follow as they are: no number is computed, so what it loads is what the page read. Session 535: and in R (as=r), base R
 *  only, so nothing is installed: readLines and read.csv, as the Python reader does with urllib and pandas. */
function readerText(table: string, as: Reader, origin: string): string {
  const url = `${origin}/api/download?table=${table}`;
  if (as === "r") {
    // an R name begins with a letter: a table name that does not (none does on 21 October 2026) is read into erw_<table>
    const name = /^[a-z]/.test(table) ? table : `erw_${table}`;
    return [
      `# Energy Research Warehouse (ERW): read the table ${table} from the ERW site's live set.`,
      "# The CSV opens with its provenance, lines that begin with \"#\" (the source report, its address, when it was",
      "# retrieved); they are printed and skipped, and the rows are loaded as they are. Base R only: no package to install.",
      "# An empty cell is NA; no comment character is set, so a value that holds \"#\" (an address) is read whole.",
      `URL <- "${url}"`,
      "old <- options(timeout = max(300, getOption(\"timeout\")))",
      "lines <- readLines(URL, warn = FALSE, encoding = \"UTF-8\")",
      "options(old)",
      "n <- 0L",
      "while (n < length(lines) && startsWith(lines[n + 1L], \"#\")) n <- n + 1L",
      "writeLines(lines[seq_len(n)])",
      `${name} <- read.csv(text = lines[seq_along(lines) > n], stringsAsFactors = FALSE, check.names = FALSE,`,
      "  na.strings = \"\", encoding = \"UTF-8\")",
      `print(dim(${name}))`,
      `print(head(${name}))`,
      "",
    ].join("\n");
  }
  if (as === "py") {
    return [
      `# Energy Research Warehouse (ERW): read the table ${table} from the ERW site's live set.`,
      "# The CSV opens with its provenance, lines that begin with \"#\" (the source report, its address, when it was",
      "# retrieved); they are printed and skipped, and the rows are loaded as they are. Needs pandas.",
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
      `${table} = pd.read_csv(io.StringIO("\\n".join(lines[n:])))`,
      `print(${table}.shape)`,
      `print(${table}.head())`,
      "",
    ].join("\n");
  }
  return [
    `* Energy Research Warehouse (ERW): read the table ${table} from the ERW site's live set.`,
    "* The CSV opens with its provenance, lines that begin with \"#\" (the source report, its address, when it was",
    "* retrieved); they are counted and skipped, the column names are the first line after them, and the rows are",
    "* loaded as they are.",
    "clear",
    "tempfile raw",
    `copy "${url}" \`raw'`,
    "tempname fh",
    "local n 0",
    "file open `fh' using `raw', read text",
    "file read `fh' line",
    "while r(eof) == 0 {",
    "    if substr(`\"`macval(line)'\"', 1, 1) != \"#\" continue, break",
    "    local n = `n' + 1",
    "    file read `fh' line",
    "}",
    "file close `fh'",
    "import delimited using `raw', varnames(`=`n' + 1') encoding(\"utf-8\") bindquote(strict) clear",
    "describe",
    "",
  ].join("\n");
}

type Reader = "py" | "do" | "r";

const reader = (table: string, as: Reader, origin: string) => new Response(readerText(table, as, origin), {
  headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_${table}.${as}"`, "Cache-Control": "public, max-age=3600" },
});

/** A filter value in PostgREST's logic syntax (or=(...)): in double quotes, its own quotes and backslashes escaped. */
const quoted = (v: string) => `"${v.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
const enc = (v: unknown) => encodeURIComponent(String(v));

/** Session 368: the table's rows, page by page, in its key's order, each page starting after the last row of the one
 *  before. A series row's key has four parts, so the next rows are read in up to three ranges, each a range of the
 *  primary key's index: the rest of the last row's (entity, variable), then the rest of its entity, then the entities
 *  after it. A single-column key (entities, events) has one. A short page of the last range ends the table. The key's
 *  values are read as k0, k1, ... so that a column the CSV does not carry (event) adds nothing to the row's bytes. */
async function* pages(shape: string, table: string, select: string, filters = ""): AsyncGenerator<Record<string, unknown>[]> {
  const key = KEY[shape];
  const sel = `${select},${key.map((k, i) => `k${i}:${k}`).join(",")}`;
  const order = key.join(",");
  // session 1009: the reader's filters (lib/downloadfilter.ts) hold in every range read below
  const base = `${shape}?select=${sel}&table_name=eq.${table}${filters}&order=${order}&limit=${PAGE}`;
  // with retries: one page is a short read, and a busy database can refuse one now and then
  const read = async (filter: string) => {
    for (let attempt = 1; ; attempt += 1) {
      try {
        return (await (await get(base + filter)).json()) as Record<string, unknown>[];
      } catch (e) {
        if (attempt >= 3) throw e;
        await new Promise((r) => setTimeout(r, 500 * attempt));
      }
    }
  };
  // the ranges after a row's key, the narrowest first: for series [same entity and variable], [same entity], [after]
  const ranges = (last: Record<string, unknown>): string[] => {
    if (key.length === 1) return [`&${key[0]}=gt.${enc(last.k0)}`];
    const [e, v, t, ev] = [String(last.k0), String(last.k1), String(last.k2), String(last.k3)];
    return [
      `&entity=eq.${enc(e)}&variable=eq.${enc(v)}&ts_utc=gte.${enc(t)}&or=${enc(`(ts_utc.gt.${quoted(t)},event.gt.${quoted(ev)})`)}`,
      `&entity=eq.${enc(e)}&variable=gt.${enc(v)}`,
      `&entity=gt.${enc(e)}`,
    ];
  };
  let rows = await read("");
  yield rows;
  if (rows.length < PAGE) return;
  let todo = ranges(rows[rows.length - 1]);
  while (todo.length) {
    rows = await read(todo[0]);
    if (rows.length) yield rows;
    // a full page: the next one starts after its last row, in the narrowest range again; a short one: the next range
    todo = rows.length === PAGE ? ranges(rows[rows.length - 1]) : todo.slice(1);
  }
}

export async function GET(req: Request) {
  const table = new URL(req.url).searchParams.get("table") ?? "";
  if (!/^[a-z0-9_]{3,64}$/.test(table)) return text("table must be an ERW table name", 400);
  // session 1009 (chain 070): whether the downloads are public or the owner's is his to rule (the rule of 12 October
  // 2026); until he does, the route answers only a request that carries the internal view's cookie
  const cookie = (req.headers.get("cookie") ?? "").split(/;\s*/).find((c) => c.startsWith(`${COOKIE}=`))?.slice(COOKIE.length + 1);
  if (!(await cookieOpens(cookie, process.env.INTERNAL_COSTS_TOKEN))) {
    return text("the download is open to the internal view only, until the owner rules whether it is public", 403);
  }
  // session 282: the download refuses what /data holds back, a table marked "license
  // needed" on the day (lib/license.ts, the rule of session 207 from 20 October 2026); until now only the link was hidden
  if (licenseNeeded(table)) return text(`${table} is held: license needed (${licensePublishers(table).join("; ")}). It is not downloaded from this site.`, 403);
  // session 1009: any table whose license verdict is not public is refused with the packages' own words
  const refused = refusal(table);
  if (refused) return text(refused, 403);
  // session 177 (lib/guard.ts): a download reads up to MAX_ROWS rows from the database; sixty an hour a visitor
  const lim = await limited(req, "download", PER_HOUR, 3600);
  if (!lim.ok) return new Response(`limit reached: ${PER_HOUR} downloads per hour; try again later\n`, { status: 429, headers: { "Content-Type": "text/plain; charset=utf-8", "Retry-After": String(lim.retryAfter) } });
  try {
    const cat = (await (await get(`catalogue?select=table_name,in_live_set,columns,license&table_name=eq.${table}`)).json()) as {
      in_live_set: string; columns: string | null; license: string;
    }[];
    if (!cat.length || cat[0].license !== "public") return text(`${table} is not a public ERW table`, 404);
    if (cat[0].in_live_set !== "yes" || !cat[0].columns) {
      return text(`${table} is not in the site's live set. Every table is on Redivis (${site.redivis.url}); version 1 is pending release.`, 404);
    }
    // session 328: ?as=py or ?as=do answers a Python or a Stata reader of this table's CSV, never the rows themselves
    const as = new URL(req.url).searchParams.get("as");
    if (as === "py" || as === "do") return reader(table, as, new URL(req.url).origin);
    // session 535: ?as=r answers an R reader of the same CSV, after the same checks
    if (as === "r") return reader(table, as, new URL(req.url).origin);
    const columns = JSON.parse(cat[0].columns) as string[];
    const shape = columns[0] === "entity_id" ? "entities" : columns[0] === "event_id" ? "events" : "series";
    // session 1009: the reader's filters, checked before any row is read
    const params = new URL(req.url).searchParams;
    const filter = downloadFilter(shape as Shape, { entity: params.get("entity"), variable: params.get("variable"), start: params.get("start"), end: params.get("end") });
    if ("error" in filter) return text(filter.error, 400);
    const hdr = (await (await get(`headers?select=line&table_name=eq.${table}&order=line_no`)).json()) as { line: string }[];
    const std = STD[shape];
    const select = shape === "series" ? std.join(",") : [...std, "extra"].join(",");
    const csv = (rows: Record<string, unknown>[]) => rows.map((r) => columns.map((c) => cell(c in r ? r[c] : (r.extra as Record<string, unknown> | null)?.[c])).join(",") + "\n").join("");
    // the first pages, read before the answer starts: a failure here is a plain 502, as before
    const it = pages(shape, table, select, filter.query);
    const first: string[] = [];
    let n = 0, done = false;
    while (n < FIRST_ROWS) {
      const step = await it.next();
      if (step.done) { done = true; break; }
      n += step.value.length;
      first.push(csv(step.value));
    }
    const at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    const counted = done ? `${n} rows` : `${n} rows or more, read page by page (the count is not taken on a table this large)`;
    // session 1009: the citation in the release's words (the packages' cite), the license verdict, and the filters
    const head = (citations as Record<string, string>)[table];
    const cite = head ? `# Cite: ${head} Via the Energy Research Warehouse (ERW), table \`${table}\`, the live set, fetched ${at}.\n` : "";
    const verdict = `# ERW license verdict: ${verdictOf(table) || "not in the record"}.\n`;
    const only = filter.words.length ? `# Rows: ${filter.words.join("; ")}.\n` : "";
    const top = hdr.map((h) => `# ${h.line}\n`).join("") + cite + verdict + only + `# Downloaded from the ERW site's live set (Supabase) at ${at}: ${counted}.\n` + columns.join(",") + "\n";
    const encoder = new TextEncoder();
    let started = false;
    // pulled: the next page is read only when the reader has taken the last, so no table is held whole in the server
    const stream = new ReadableStream<Uint8Array>({
      async pull(ctl) {
        try {
          if (!started) {
            started = true;
            ctl.enqueue(encoder.encode(top + first.join("")));
            first.length = 0;
            if (done) ctl.close();
            return;
          }
          const step = await it.next();
          if (step.done) { ctl.close(); return; }
          n += step.value.length;
          if (n > ROW_CAP) throw new Error(`${table} holds more than the ${ROW_CAP} rows a download allows; narrow it with entity, variable, start or end, or read it on Redivis (${site.redivis.url})`);
          ctl.enqueue(encoder.encode(csv(step.value)));
        } catch (e) {
          ctl.error(e);
          await it.return(undefined).catch(() => {});
        }
      },
      async cancel() {
        await it.return(undefined).catch(() => {});
      },
    });
    return new Response(stream, {
      headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${table}.csv"`, "Cache-Control": "public, max-age=3600" },
    });
  } catch (e) {
    return text(`the download failed: ${(e as Error).message}`, 502);
  }
}
