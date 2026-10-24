// Energy Research Warehouse (ERW) site, session 1182 (chain 091): a panel's table of figures, to download. Each panel
// chains 077 and 078 added to the Grid tool offers its table as a CSV made from the page's own figures, as the hub
// table's and the node list's downloads are made (app/cost-of-power/AllGridsDownload.tsx, session 793): no new route
// and no read, so the file holds exactly what the page draws. Here the file is written on the server into the link
// itself (a data: address with the download attribute), so it needs no script and a checker reads it from the HTML.
//
// The file opens with its provenance, as every ERW file does (CLAUDE.md, non-negotiable 5): the panel and the page, the
// tables it is drawn from, the filter, the hour or window, and the time the page was drawn. Then the panel's columns and
// its rows. A cell that holds a figure (a components/Num.tsx figure: its check key and its value as read) is written as
// that value, before the page rounds it for display; a figure of a held grid (lib/license.ts, Num's heldBy) is written
// "license needed", never its value, as the page draws it; a cell the page writes in words ("not held", "could not be
// read", "no tie reported") is written in those words. The cells are the same React nodes the panel draws in its table,
// read here without drawing them (cellOf), so the file and the table cannot say two things.
import type { ReactNode } from "react";
import { Num, heldBy } from "@/components/Num";
import { LICENSE_NEEDED } from "@/lib/license";

/** A figure as a file cell: its check key and its value as read (a Num's two props). */
export type FileFig = { check: string; raw: number | string };
/** A cell of the file: a figure, or any node the panel draws (its figures and words are read from it). */
export type FileCell = FileFig | ReactNode;
/** What the file's header says about the panel. */
export type FileOf = {
  /** the panel's name on the page (data-grid-panel), e.g. grid_network_ercot */
  panel: string;
  /** a part of the panel, where it offers more than one table (e.g. "balance") */
  part?: string;
  /** what the table is, in words */
  title: string;
  /** the page's address, e.g. /grid?grid=ercot&view=network */
  page: string;
  /** the tables the figures are drawn from, each with a note in words where it helps */
  tables: string[];
  /** the rows read: the entity, the variables, the grid */
  filter: string;
  /** the hour or the window, said whole ("Hour: ...", "Window: ...") */
  window: string;
  /** any further line of the header */
  notes?: string[];
  /** the panel's figures that stand beside its table, in its sentences (a net, a count, a day): each one line of the
   *  header, "Figure: <label>: <value> (key <its check key>)" */
  figures?: { label: string; value: FileCell }[];
};

const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const isFig = (x: unknown): x is FileFig =>
  !!x && typeof x === "object" && !ELEMENT.has((x as { $$typeof?: symbol }).$$typeof as symbol) && typeof (x as FileFig).check === "string" && "raw" in (x as object);

type Token = { text: string } | { fig: FileFig } | { held: true };

/** Reads a node as the panel draws it, in order: its words, its figures (each Num, or a host element carrying
 *  data-check) and its held figures. A server component that is not async is called with its props (the panel's small
 *  figure components, Missing); a client component, or one that throws when called outside a render, is read by its
 *  children. */
function read(node: unknown, out: Token[], depth = 0): void {
  if (node === null || node === undefined || typeof node === "boolean" || depth > 40) return;
  if (typeof node === "string" || typeof node === "number") { out.push({ text: String(node) }); return; }
  if (isFig(node)) { out.push(heldBy(node.check) ? { held: true } : { fig: { check: node.check, raw: node.raw } }); return; }
  if (Array.isArray(node)) { for (const x of node) read(x, out, depth + 1); return; }
  if (typeof node !== "object") return;
  const el = node as { $$typeof?: symbol; type?: unknown; props?: Record<string, unknown> };
  if (!ELEMENT.has(el.$$typeof as symbol)) return;
  const props = el.props ?? {};
  const type = el.type as (((p: unknown) => unknown) & { __erwClient?: string; prototype?: { isReactComponent?: unknown } }) | string | undefined;
  if (type === Num) { read({ check: String(props.check), raw: props.raw as number | string }, out, depth + 1); return; }
  if (typeof type === "string") {
    if (props["data-check"] !== undefined) { out.push({ fig: { check: String(props["data-check"]), raw: props["data-raw"] as string } }); return; }
    if (props["data-license-held"] !== undefined) { out.push({ held: true }); return; }
    if (type !== "svg") read(props.children, out, depth + 1);
    return;
  }
  if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
    let drawn: unknown;
    try { drawn = type(props); } catch { read(props.children, out, depth + 1); return; }
    if (drawn && typeof (drawn as { then?: unknown }).then === "function") { read(props.children, out, depth + 1); return; }
    read(drawn, out, depth + 1);
    return;
  }
  read(props.children, out, depth + 1);
}

/** A cell as the file writes it, and the figures in it (held ones not among them, but counted). A cell that holds a
 *  figure is written as its value (two figures in one cell: both, in order, a space between); one without, as its words. */
export function cellOf(cell: FileCell): { text: string; figs: FileFig[]; held: number } {
  const out: Token[] = [];
  read(cell, out);
  const figs = out.flatMap((t) => ("fig" in t ? [t.fig] : []));
  const held = out.filter((t) => "held" in t).length;
  if (figs.length || held) return { text: out.flatMap((t) => ("fig" in t ? [String(t.fig.raw)] : "held" in t ? [LICENSE_NEEDED] : [])).join(" "), figs, held };
  return { text: out.map((t) => ("text" in t ? t.text : "")).join("").replace(/\s+/g, " ").trim(), figs: [], held: 0 };
}

const csvCell = (s: string) => (/[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);

/** The file: its header, its columns and its rows; the figures it holds (held ones not among them) and how many are held. */
export function panelFile(of: FileOf, columns: FileCell[], rows: FileCell[][], drawn: number = Date.now()):
  { name: string; csv: string; figs: FileFig[]; held: number; rows: number } {
  const figs: FileFig[] = [];
  let held = 0;
  const line = (cells: FileCell[]) => cells.map((c) => { const x = cellOf(c); figs.push(...x.figs); held += x.held; return csvCell(x.text); }).join(",");
  const head = columns.map((c) => csvCell(cellOf(c).text)).join(",");
  const beside = (of.figures ?? []).map(({ label, value }) => {
    const x = cellOf(value);
    figs.push(...x.figs); held += x.held;
    return `Figure: ${label}: ${x.text}${x.figs.length === 1 ? ` (key ${x.figs[0].check})` : ""}`;
  });
  const body = rows.map(line);
  const name = `erw_${of.panel}${of.part ? `_${of.part}` : ""}.csv`;
  const top = [
    `ERW (Energy Research Warehouse), the Grid tool: ${of.title}`,
    `Panel: ${of.panel}${of.part ? ` (${of.part})` : ""}, on the page ${of.page}`,
    `Tables: ${of.tables.join("; ")}`,
    `Filter: ${of.filter}`,
    of.window,
    `Drawn: ${new Date(drawn).toISOString()} (the time the page was drawn; these are its figures then)`,
    ...(of.notes ?? []),
    ...beside,
    "Each figure is its value as read, before the page rounds it; a cell the page writes in words (not held, could not be read, license needed) is written in those words, and a held grid's figure is never written.",
    "Every figure's check key, its table and its filter are on the page: hover the figure.",
  ];
  const csv = [...top.map((t) => `# ${t.replace(/[\r\n]+/g, " ")}`), head, ...body].join("\n") + "\n";
  return { name, csv, figs, held, rows: rows.length };
}

/** The link that downloads the panel's table, under it. `id` names the file on the page (data-grid-file). */
export function PanelFile({ of, columns, rows }: { of: FileOf; columns: FileCell[]; rows: FileCell[][] }) {
  const f = panelFile(of, columns, rows);
  const id = `${of.panel}${of.part ? `_${of.part}` : ""}`;
  return (
    <p className="mt-1 text-xs text-muted" data-grid-file-line={id}>
      <a href={`data:text/csv;charset=utf-8,${encodeURIComponent(f.csv)}`} download={f.name} data-grid-file={id} data-grid-file-rows={f.rows}
        data-grid-file-figures={f.figs.length} data-grid-file-held={f.held}>Download this table (CSV)</a>
      {", "}its source, filter and {of.window.toLowerCase().startsWith("hour") ? "hour" : "window"} in the file&apos;s first lines.
    </p>
  );
}
