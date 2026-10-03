// Energy Research Warehouse (ERW) site: committed markdown (digests, the data standard,
// method documents) rendered to HTML. Links between repository files become site pages
// where the site has one, and GitHub links otherwise.
import "server-only";
import path from "node:path";
import { Marked, type Tokens } from "marked";
import docs from "@/content/docs.json";
import site from "@/data/site.json";
import { gated } from "@/lib/release";

export type Docs = {
  built_at: string;
  digests: Record<string, string>;
  // session 17: the weekly briefs, by ISO week (YYYY-Www); session 23: the Energy Roundup where a week
  // has one (docs/roundup/), else the week's Energy Week (docs/weekly/)
  weeklies: Record<string, string>;
  weekly_source: Record<string, string>;
  latest: string;
  datastandard: string;
  methods: Record<string, string>;
  // session 15: warehouse/metadata/run_status.csv rows for EIA-930 that are not ok (gaps, failures)
  run_status_eia930: { run_id: string; table: string; market: string; status: string; detail: string }[];
  // session 23: Automated Analysis (docs/analysis/): each week's chart of the week and results, the templates, the gallery
  analysis: Analysis;
  // session 24: the tool counts by status, from docs/platform-tools.md
  platform: { total: number; yes: number; partial: number; no: number; planned: number };
  // session 21: warehouse/metadata/sources.csv, for /terms
  sources: { source: string; publisher: string; report: string; report_url: string; license: string; tables: string }[];
  // session 35: the grid pages' config (docs/grids/grids.json) and written layer (docs/grids/<slug>.md)
  grid_config: GridConfig[];
  grids: Record<string, string>;
};
export type GridConfig = {
  slug: string; iso: string; name: string; ba: string; entity: string; tz: string; tz_label: string;
  market_prefix: string | null; hub: { entity: string; label: string } | null;
  prices_public: boolean; prices_note?: string; prices_url?: string;
  queue_table: string | null; queue_url?: string;
  storage_entity: string | null; storage_source: "eia930" | "caiso" | null;
  states: Record<string, string>; names: string[]; tables: string[];
  utilities: string[]; // session 36A: utility names that place a datacenter facility in this grid
};
export type ChartOfWeek = {
  week: string; template: string; title: string; subtitle: string; note: string; caption: string; note_by: string;
  source_line: string; citations: string[]; tables: string[]; params: Record<string, unknown>;
  headline: { label: string; value: number; unit: string; period: string };
  notability_z: number; percentile: number; history_n: number; files: Record<string, string>; option: unknown; rule: string;
};
export type AnalysisResult = {
  template: string; params: Record<string, unknown>; title: string; subtitle: string;
  headline: { label: string; value: number; unit: string; period: string };
  history_n: number; notability_z: number | null; percentile: number | null; source_line: string; tables: string[];
  citations: string[]; option: unknown;
};
export type Analysis = {
  weeks: Record<string, ChartOfWeek>;
  results: Record<string, { week: string; picked: string; results: AnalysisResult[]; skipped: { template: string; reason: string }[] }>;
  templates: { template: string; title: string; public: boolean; method: string; params: Record<string, { default: unknown; choices: unknown }>; tables: string[] }[];
  gallery: { computed_at?: string; templates: { template: string; title: string; default: string; combos: Record<string, { params: Record<string, unknown>; file: string | null; reason?: string }> }[] };
};
export const DOCS = docs as unknown as Docs;

/** The weeks with a chart of the week, newest first (session 23). */
export function analysisWeeks(): string[] {
  return Object.keys(DOCS.analysis?.weeks ?? {}).sort().reverse();
}

function sitePath(repoPath: string): string {
  const p = repoPath.split("\\").join("/");
  const [file, hash] = p.split("#");
  const tail = hash ? `#${hash}` : "";
  if (file === "docs/datastandard.md") return `/data/standard${tail}`;
  let m = file.match(/^docs\/methods\/([\w-]+)\.md$/);
  if (m) return `/data/methods/${m[1]}${tail}`;
  m = file.match(/^docs\/digest\/(\d{4}-\d{2}-\d{2})\.md$/);
  if (m) return `/digest/${m[1]}${tail}`;
  m = file.match(/^docs\/(?:weekly|roundup)\/(\d{4}-W\d{2})\.md$/);
  if (m) return `/roundup/${m[1]}${tail}`;
  // session 23: images of the analysis (the chart of the week), copied into public/analysis-files at build
  m = file.match(/^docs\/analysis\/(.+\.(?:png|svg|json))$/);
  if (m) return `/analysis-files/${m[1]}${tail}`;
  return `${site.repository}/blob/main/${p}`;
}

/** Render markdown that lives at `repoPath` (for example "docs/digest/2026-09-26.md"). */
export function render(md: string, repoPath: string): string {
  const dir = path.posix.dirname(repoPath);
  const marked = new Marked({
    gfm: true,
    walkTokens(token) {
      if (token.type !== "link" && token.type !== "image") return;
      const t = token as Tokens.Link;
      if (/^([a-z]+:|#|\/)/i.test(t.href)) return;
      t.href = sitePath(path.posix.normalize(path.posix.join(dir, t.href)));
    },
  });
  return gateLinks(marked.parse(md, { async: false }) as string);
}

/** Session 67, the release gate (lib/release.ts): in rendered markdown a link to a page in review becomes greyed text
 * with the "in review" label, keeping its address in data-gate-href so the internal view can make it a link again
 * (components/GateRestore.tsx). */
export function gateLinks(html: string): string {
  return html.replace(/<a href="(\/[^"]*)"([^>]*)>([\s\S]*?)<\/a>/g, (all, href: string, _rest: string, text: string) =>
    gated(href) ? `<span class="gate-review" aria-disabled="true" data-gate-href="${href}">${text}<span class="gate-label">in review</span></span>` : all);
}

/** The weekly briefs' ISO weeks, newest first (session 17; the Energy Roundup since session 23). */
export function weeklyWeeks(): string[] {
  return Object.keys(DOCS.weeklies ?? {}).sort().reverse();
}

/** The dated digests, newest first. */
export function digestDates(): string[] {
  return Object.keys(DOCS.digests).sort().reverse();
}

/**
 * The first `n` items under "## Top of the industry" in a digest, each as markdown.
 * Returns null when the digest has no such section, so the page can say so.
 */
export function topItems(md: string, n: number): string[] | null {
  const start = md.indexOf("\n## Top of the industry");
  if (start < 0) return null;
  const rest = md.slice(start + 1);
  const next = rest.indexOf("\n## ", 3);
  const section = next < 0 ? rest : rest.slice(0, next);
  const items: string[] = [];
  let cur: string[] | null = null;
  for (const line of section.split("\n").slice(1)) {
    if (/^\d+\.\s/.test(line)) {
      if (cur) items.push(cur.join("\n"));
      cur = [line.replace(/^\d+\.\s/, "")];
    } else if (cur && line.trim() !== "") {
      cur.push(line.trim());
    }
  }
  if (cur) items.push(cur.join("\n"));
  return items.slice(0, n);
}

/** The digest's title line ("Energy Digest, 2026-09-26") and its first paragraph. */
export function digestTitle(md: string): string {
  const m = md.match(/^#\s+(.+)$/m);
  return m ? m[1].trim() : "";
}

/** Session 23: is a YYYY-MM-DD date a Saturday or Sunday (the digest has no weekend issue)? */
export function isWeekend(date: string): boolean {
  const d = new Date(`${date}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && (d.getUTCDay() === 0 || d.getUTCDay() === 6);
}

/** The ISO week (YYYY-Www) that holds a date: the Roundup that carries a weekend's stories. */
export function isoWeek(date: string): string {
  const d = new Date(`${date}T00:00:00Z`);
  const day = (d.getUTCDay() + 6) % 7; // Monday 0
  d.setUTCDate(d.getUTCDate() - day + 3); // the week's Thursday
  const year = d.getUTCFullYear();
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const week = 1 + Math.round(((d.getTime() - jan4.getTime()) / 86400000 - 3 + ((jan4.getUTCDay() + 6) % 7)) / 7);
  return `${year}-W${String(week).padStart(2, "0")}`;
}

/**
 * Session 23: the digest archive by day, newest first: every dated digest, plus each Saturday and Sunday
 * between the first digest and today (UTC) that has none, marked as having no weekend issue.
 */
export function archiveDays(): { date: string; has: boolean }[] {
  const have = new Set(digestDates());
  const first = [...have].sort()[0];
  const out: { date: string; has: boolean }[] = [];
  const today = new Date().toISOString().slice(0, 10);
  for (let d = new Date(`${first}T00:00:00Z`); d.toISOString().slice(0, 10) <= today; d.setUTCDate(d.getUTCDate() + 1)) {
    const s = d.toISOString().slice(0, 10);
    if (have.has(s)) out.push({ date: s, has: true });
    else if (isWeekend(s)) out.push({ date: s, has: false });
  }
  return out.reverse();
}
