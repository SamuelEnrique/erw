// Energy Research Warehouse (ERW) site: committed markdown (digests, the data standard,
// method documents) rendered to HTML. Links between repository files become site pages
// where the site has one, and GitHub links otherwise.
import "server-only";
import path from "node:path";
import { Marked, type Tokens } from "marked";
import docs from "@/content/docs.json";
import site from "@/data/site.json";

export type Docs = {
  built_at: string;
  digests: Record<string, string>;
  // session 17: the weekly briefs, by ISO week (YYYY-Www)
  weeklies: Record<string, string>;
  latest: string;
  datastandard: string;
  methods: Record<string, string>;
  // session 15: warehouse/metadata/run_status.csv rows for EIA-930 that are not ok (gaps, failures)
  run_status_eia930: { run_id: string; table: string; market: string; status: string; detail: string }[];
  // session 21: warehouse/metadata/sources.csv, for /terms
  sources: { source: string; publisher: string; report: string; report_url: string; license: string; tables: string }[];
};
export const DOCS = docs as Docs;

function sitePath(repoPath: string): string {
  const p = repoPath.split("\\").join("/");
  const [file, hash] = p.split("#");
  const tail = hash ? `#${hash}` : "";
  if (file === "docs/datastandard.md") return `/data/standard${tail}`;
  let m = file.match(/^docs\/methods\/([\w-]+)\.md$/);
  if (m) return `/data/methods/${m[1]}${tail}`;
  m = file.match(/^docs\/digest\/(\d{4}-\d{2}-\d{2})\.md$/);
  if (m) return `/digest/${m[1]}${tail}`;
  m = file.match(/^docs\/weekly\/(\d{4}-W\d{2})\.md$/);
  if (m) return `/weekly/${m[1]}${tail}`;
  return `${site.repository}/blob/main/${p}`;
}

/** Render markdown that lives at `repoPath` (for example "docs/digest/2026-09-26.md"). */
export function render(md: string, repoPath: string): string {
  const dir = path.posix.dirname(repoPath);
  const marked = new Marked({
    gfm: true,
    walkTokens(token) {
      if (token.type !== "link") return;
      const t = token as Tokens.Link;
      if (/^([a-z]+:|#|\/)/i.test(t.href)) return;
      t.href = sitePath(path.posix.normalize(path.posix.join(dir, t.href)));
    },
  });
  return marked.parse(md, { async: false }) as string;
}

/** The weekly briefs' ISO weeks, newest first (session 17). */
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
