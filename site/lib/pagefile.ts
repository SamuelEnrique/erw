// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): a figure read from a committed page file, and
// its check key, so scripts/check-values.mjs can recompute it from the same file on its own.
//
//   pf|<path under site/data>|<path into the JSON>
//
// The JSON path is segments joined by "/". Each segment is an object key, an array index, or a selector "@field=value"
// (the one element of an array whose `field` equals `value`, compared as text); a selector may name several fields joined
// by "+" ("@a=MIDA+b=TEN+year=2025"), and it matches only when exactly one element has them all, so a file that comes to
// hold two such elements gives no figure rather than the first. Inside a segment the characters % / | ~ + = @ & are
// written as %XX (encodeURIComponent's form), so a key or a value that holds one stays one segment.
//
// The resolver imports nothing of Next.js: node runs this file as it is (scripts/check-values.mjs imports it, and
// scripts/test-pagefile.mjs tests it). Nothing is filled: a path that does not lead to a finite number gives undefined, and
// the problem sets throw on it rather than print a figure.
import fs from "node:fs";
import path from "node:path";

export type Selector = Record<string, string | number>;
export type Segment = string | number | Selector;

const SPECIAL = /[%/|~+=@&]/g;
/** One segment's text with the characters the key gives a meaning to written as %XX. */
export const escapeSegment = (s: string | number): string =>
  String(s).replace(SPECIAL, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase().padStart(2, "0")}`);
const unescape = (s: string): string | null => {
  try { return decodeURIComponent(s); } catch { return null; }
};

/** A segment as the key writes it: a key or an index as text, a selector as "@field=value+field=value". */
export function segmentText(s: Segment): string {
  if (typeof s === "object") return `@${Object.entries(s).map(([f, v]) => `${escapeSegment(f)}=${escapeSegment(v)}`).join("+")}`;
  return escapeSegment(s);
}

/** The check key of a figure: the page file (its path under site/data) and the segments into it. */
export function pfKey(file: string, segments: Segment[]): string {
  return `pf|${file}|${segments.map(segmentText).join("/")}`;
}

/** A key's two parts, or null when it is not a well-formed pf key (a file outside site/data, or not a .json, is not). */
export function parsePf(key: string): { file: string; path: string } | null {
  const p = key.split("|");
  if (p.length !== 3 || p[0] !== "pf") return null;
  const [, file, jsonPath] = p;
  if (!file.endsWith(".json") || file.startsWith("/") || file.split("/").some((x) => x === ".." || x === "." || x === "")) return null;
  return { file, path: jsonPath };
}

/** Where the path leads in a parsed document, or undefined when any step does not exist. Pure: no file is read. */
export function resolvePath(doc: unknown, jsonPath: string): unknown {
  if (jsonPath === "") return doc;
  let cur: unknown = doc;
  for (const raw of jsonPath.split("/")) {
    if (cur === null || cur === undefined) return undefined;
    if (raw.startsWith("@")) {
      if (!Array.isArray(cur)) return undefined;
      const conds: [string, string][] = [];
      for (const c of raw.slice(1).split("+")) {
        const i = c.indexOf("=");
        const f = i > 0 ? unescape(c.slice(0, i)) : null, v = i > 0 ? unescape(c.slice(i + 1)) : null;
        if (f === null || v === null) return undefined;
        conds.push([f, v]);
      }
      const hits = cur.filter((el) => el !== null && typeof el === "object" && !Array.isArray(el)
        && conds.every(([f, v]) => Object.prototype.hasOwnProperty.call(el, f) && String((el as Record<string, unknown>)[f]) === v));
      if (hits.length !== 1) return undefined;
      cur = hits[0];
      continue;
    }
    const k = unescape(raw);
    if (k === null) return undefined;
    if (Array.isArray(cur)) {
      if (!/^\d+$/.test(k)) return undefined;
      cur = cur[Number(k)];
    } else if (typeof cur === "object") {
      if (!Object.prototype.hasOwnProperty.call(cur, k)) return undefined;
      cur = (cur as Record<string, unknown>)[k];
    } else return undefined;
  }
  return cur;
}

/** A finite number where the path leads, else undefined. */
export function resolveNumber(doc: unknown, jsonPath: string): number | undefined {
  const v = resolvePath(doc, jsonPath);
  return typeof v === "number" && Number.isFinite(v) ? v : undefined;
}

// ---------------------------------------------------------------- the files themselves

/** The site's data folder: site/data when the process runs in site/ (Next.js, the scripts and the tests all do). */
export const DATA_DIR = () => path.join(process.cwd(), "data");
const cache = new Map<string, unknown>();

/** A page file read and parsed, once a process. Throws when the file is missing or is not JSON. */
export function readPageFile(file: string, dataDir: string = DATA_DIR()): unknown {
  if (!parsePf(`pf|${file}|`)) throw new Error(`not a page file under site/data: ${file}`);
  const full = path.join(dataDir, ...file.split("/"));
  if (!cache.has(full)) cache.set(full, JSON.parse(fs.readFileSync(full, "utf-8")));
  return cache.get(full);
}

/** The figure a key names, read from its file: what scripts/check-values.mjs compares with the page's data-raw. */
export function pfValue(key: string, dataDir: string = DATA_DIR()): number | undefined {
  const k = parsePf(key);
  if (!k) return undefined;
  return resolveNumber(readPageFile(k.file, dataDir), k.path);
}

/** The header fields a page file carries about itself, where it has them. */
export type FileHead = { built?: string; tables: string[]; license?: string; method?: string };
export function fileHead(file: string, dataDir: string = DATA_DIR()): FileHead {
  const d = readPageFile(file, dataDir) as Record<string, unknown>;
  const s = (x: unknown) => (typeof x === "string" ? x : undefined);
  return {
    built: s(d.built) ?? s(d.built_at_utc), license: s(d.license), method: s(d.method),
    tables: Array.isArray(d.tables) ? d.tables.filter((t): t is string => typeof t === "string") : [],
  };
}
