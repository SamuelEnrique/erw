// Energy Research Warehouse (ERW) site, chain 780 (session 11600, 28 November 2026): "Where the next gigawatts can
// go", a section of the All grids tab of /cost-of-power (Samuel's ruling of 22 October 2026: the siting question lives
// on this tab). One table of every place, a row a place and a column a count; a place opened shows its own file; two
// places stand side by side as A and B; the rows shown download as a CSV. It reads exactly the files of
// docs/state/page_files_siting_regions.md (app/cost-of-power/regionsdata.ts) and computes nothing: every figure is
// the file's own and carries its key into the file (pf|..., lib/pagefile.ts), which scripts/check-values.mjs
// recomputes from the same file.
//
// No score, no rank, no advice, and no colour that says good or bad: the reader sorts and filters, and the order is
// the column's. A count's period and source are in its hover (the column's head, or the cell's own where it differs).
// A count held for a license is drawn blank with "license needed" on hover; one not shown for another reason says
// the reason's kind in a word, with the reason on hover. A count whose source table the site itself holds for a
// license is drawn blank whatever the file carries (lib/license.ts), so no held figure reaches the page through
// these files. The tab's own parts are untouched: this file is mounted by one line of AllGridsView.tsx.
import type { ReactNode } from "react";
import { InlineSpark } from "@/components/InlineSpark";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { Blank, Tip } from "@/components/largeload/parts";
import { licenseByGrid, licenseByRow, licenseHeldRow } from "@/lib/license";
import { pfKey, type Segment } from "@/lib/pagefile";
import { loadPlace, loadRegions, placePath } from "./regionsdata";
import { AB_ANCHOR, ANCHOR, KINDS, KIND_PLURAL, KIND_SHORT, KIND_TIP, KIND_WORDS, LICENSE_NEEDED, NAME_SORT, PLACE_ANCHOR, TABLE_FILE, choiceOf, colIndex, colsDrawn, columnAbout, defaultCols, figure, heldKind, heldWhy,
  monthWords, periodWords, readCell, rowsShown, ruleHref, sameAbout, sortChange, sortWords, sourceWords, srHref, tableCsv, trendPoints, unitWords, utcWords, withUnit,
  type About, type Cell, type Choice, type IndexFile, type Kind, type Place, type PlaceFile, type Source, type TableFile, type TableRow } from "./regions";
import { RegionsChoices } from "./RegionsChoices";
import { RegionsDownload } from "./RegionsDownload";

export const REGIONS_TITLE = "Where the next gigawatts can go";
type Q = Record<string, string | undefined>;
type Sources = Record<string, Source>;

/** Whether the site holds a count's source table for a license, whatever the file says of the count. A table held by
 *  row reaches a file through its public rows only; one held by grid is asked for the place's own hub. */
function siteHolds(table: string | null | undefined, entity: string | null): boolean {
  if (!table) return false;
  if (licenseByRow(table)) return false;
  if (licenseByGrid(table)) return entity ? licenseHeldRow(table, entity) : false;
  return licenseHeldRow(table, null);
}
const siteHoldWords = (table: string) => `${LICENSE_NEEDED}: the site holds ${table} for a license (docs/licenses.md), so the figure this file carries is not drawn`;
const isCell = (x: unknown): x is Cell => !!x && typeof x === "object" && !Array.isArray(x) && "v" in (x as object) && "held" in (x as object);
const safeUrl = (u: unknown): string | null => (typeof u === "string" && /^https?:\/\/[^\s"<>]+$/.test(u) ? u : null);
const text = (x: unknown): string => (typeof x === "string" ? x : typeof x === "number" ? String(x) : "");
const list = (x: unknown): Record<string, unknown>[] => (Array.isArray(x) ? x.filter((r): r is Record<string, unknown> => !!r && typeof r === "object") : []);

/** A count that is not shown: blank with "license needed" on hover, or the reason's kind in a word with the reason on hover. */
function Held({ held, what, table }: { held: string | null; what: string; table?: string | null }) {
  const kind = heldKind(held);
  if (kind === LICENSE_NEEDED) return <Blank tip={heldWhy(held)} table={table || "siting_regions"} what={what} />;
  return <Tip tip={heldWhy(held)} data={{ "sr-held": kind }}>{kind}</Tip>;
}
/** A figure with its key into its file, written as its unit is written (regions.ts, `figure`). */
const Fig = ({ file, path, v, unit }: { file: string; path: Segment[]; v: number; unit?: string | null }) => <Num check={pfKey(file, path)} raw={v}>{figure(v, unit)}</Num>;

/** A count's small trend: its last 24 whole months as the file holds them (the shared inline chart; a month's figure
 *  under the mouse). Fewer than two months held: nothing is drawn. */
function TrendLine({ c, what }: { c: Cell; what: string }) {
  const pts = trendPoints(c.trend);
  if (pts.length < 2) return null;
  const u = unitWords(c.unit);
  const month = (p: { t: string }) => monthWords(p.t.slice(0, 7));
  const first = pts[0], last = pts[pts.length - 1];
  const lo = pts.reduce((a, p) => (p.v < a.v ? p : a), first), hi = pts.reduce((a, p) => (p.v > a.v ? p : a), first);
  // the line answers the mouse a month at a time (the shared chart's own titles); a finger and the keyboard open
  // these words: the first and the last month and the lowest and the highest, each as the file holds it
  const said = `${what} by month${u ? `, ${u}` : ""}: ${figure(first.v, c.unit)} in ${month(first)}, ${figure(last.v, c.unit)} in ${month(last)}; the lowest month ${figure(lo.v, c.unit)} (${month(lo)}), the highest ${figure(hi.v, c.unit)} (${month(hi)}). ${pts.length} of ${c.trend?.months.length ?? pts.length} months held.`;
  return (
    // its own least width (the line's 96 px and its edge): the shared hover's wrapper is "no wider than its cell", which
    // a table reads as no width at all, and the line then ran over the next column's figure (seen at 390 px)
    <span className="ml-2 inline-block min-w-[100px] align-middle" data-sr-trend="months" data-sr-trend-points={pts.length}>
      <Tip tip={said} plain>
        <span className="inline-block bg-white p-0.5">
          <InlineSpark values={pts} label={`${what} by month${u ? `, ${u}` : ""}, ${month(first)} to ${month(last)}`} width={96} height={22} />
        </span>
      </Tip>
    </span>
  );
}
/** A count of a place's file, as the contract writes one: the figure with its unit and its small trend where the file
 *  carries one, or why it is not shown. `otherwise`: the reason when the file holds no cell here at all. */
function CellView({ c, file, path, what, sources, entity, unit = true, otherwise = null }: { c: unknown; file: string; path: Segment[]; what: string; sources: Sources; entity: string | null; unit?: boolean; otherwise?: string | null }) {
  if (!isCell(c)) return <Held held={otherwise} what={what} />;
  const table = c.src ? sources[c.src]?.table ?? null : null;
  const held = c.held ?? (c.v === null || c.v === "" ? heldWhy(null) : siteHolds(table, entity) ? siteHoldWords(table as string) : null);
  if (held) return <Held held={held} what={what} table={table} />;
  const u = unit ? unitWords(c.unit) : "";
  if (typeof c.v === "number" && Number.isFinite(c.v)) return <><Fig file={file} path={[...path, "v"]} v={c.v} unit={c.unit} />{u ? <span className="ml-1 font-sans text-xs">{u}</span> : null}<TrendLine c={c} what={what} /></>;
  return <span>{utcWords(String(c.v))}</span>;
}
/** The words of a count's hover: what it is, the span it covers, and where it comes from. */
const about = (label: string, unit: string | null | undefined, period: string | null | undefined, sources: Sources, src: string | null | undefined): string =>
  [`${withUnit(label, unit)}.`, period ? `Period: ${periodWords(period)}.` : "", sourceWords(sources, src)].filter(Boolean).join(" ");
/** A hover's words with the way to their source: a link to the publisher's own report where the file gives its address
 *  (one a source; for a table of several publishers, the place's own operator's), then anything said after it. */
const withLink = (said: string, sources: Sources, src: string | null | undefined, more?: string): ReactNode => {
  const u = safeUrl(src ? sources[src]?.url : null);
  return <>{said}{u ? <> <a href={u} rel="noopener" className="underline" data-sr-source-url={src ?? ""}>Open its source</a>.</> : null}{more ? <> {more}</> : null}</>;
};

// ---- the table of every place ---------------------------------------------------------------------------------------

function TableCell({ table, row, ci, place, of }: { table: TableFile; row: TableRow; ci: number; place: Place | undefined; of: About }) {
  const col = table.columns[ci], r = readCell(table, row, ci);
  const source = r.src ? table.sources[r.src]?.table ?? null : null;
  const what = `${col.label}, ${row.name}`;
  const held = r.held ?? (siteHolds(source, place?.ref_hub ?? null) ? siteHoldWords(source as string) : null);
  if (held) return <Held held={held} what={what} table={source} />;
  const body = r.v !== null ? <Fig file={TABLE_FILE} path={["rows", { id: row.id }, "v", ci]} v={r.v} unit={col.unit} /> : <span>{utcWords(r.words ?? "")}</span>;
  // a cell whose period or source is not the one its column's hover gives says its own in a hover of its own
  return sameAbout({ period: r.period, src: r.src }, of) ? body : <Tip tip={withLink(about(what, col.unit, r.period, table.sources, r.src), table.sources, r.src)} plain data={{ "sr-own": "1" }}>{body}</Tip>;
}

function PlacesTable({ q, c, table, index }: { q: Q; c: Choice; table: TableFile; index: IndexFile }) {
  const rows = rowsShown(table, c), cols = colsDrawn(table, c);
  const sectionTitle = (id: string) => index.sections.find((s) => s.id === id)?.title ?? id;
  const placeOf = (id: string) => index.places.find((p) => p.id === id);
  const ofCol = new Map(cols.map((col) => [col.key, columnAbout(table, colIndex(table, col.key))]));
  return (
    <div className="overflow-x-auto" role="region" aria-label={`${REGIONS_TITLE}: every place`} tabIndex={0} data-sr-table={`${rows.length}|${cols.length}`}>
      <table className="w-full border-collapse text-left text-sm tabular-nums">
        <caption className="sr-only">Every place side by side, a row a place and a column a count, each as its publisher printed it</caption>
        <thead>
          <tr className="border-b border-ink align-bottom text-xs">
            {/* the first column stays in place while the rest scrolls (app/tokens.css): on a phone it is kept narrow, so a
                column of figures can be read beside it (seen at 390 px: at 13rem it took 208 of the frame's 358 px) */}
            <th scope="col" className="min-w-36 px-2 py-1.5 font-normal sm:min-w-52" aria-sort={c.sort === NAME_SORT ? (c.dir === "asc" ? "ascending" : "descending") : "none"}>
              <SiteLink href={srHref(q, sortChange(c, NAME_SORT), null)} scroll={false} gate="plain" className="inline-block py-1 underline decoration-dotted" data-sr-sort={NAME_SORT}>Place{c.sort === NAME_SORT && c.dir === "desc" ? " (turned round)" : ""}</SiteLink>
            </th>
            {cols.map((col) => {
              const on = c.sort === col.key;
              return (
                <th key={col.key} scope="col" className="px-2 py-1.5 text-right font-normal" aria-sort={on ? (c.dir === "asc" ? "ascending" : "descending") : "none"} data-sr-col={col.key}>
                  <span className="block">{sectionTitle(col.section)}</span>
                  <SiteLink href={srHref(q, sortChange(c, col.key), null)} scroll={false} gate="plain" className="inline-block py-1 font-semibold underline decoration-dotted" data-sr-sort={col.key}>
                    {col.label}{on ? (c.dir === "desc" ? " (largest first)" : " (smallest first)") : ""}
                  </SiteLink>
                  <span className="block"><Tip tip={withLink(about(col.label, col.unit, ofCol.get(col.key)?.period, table.sources, ofCol.get(col.key)?.src), table.sources, ofCol.get(col.key)?.src, "Press the column's name to sort by it; again to turn the order round.")} data={{ "sr-about": col.key }}>{unitWords(col.unit) || "count"}</Tip></span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className={`border-b border-rule align-top ${c.open === r.id ? "bg-paper" : ""}`} data-sr-row={r.id} data-sr-kind-of={r.kind}>
              <th scope="row" className="px-2 py-1 text-left font-normal">
                {/* one line a place where the name is short: its name (opens its file), its kind in a word, and A and B */}
                <span className="flex flex-wrap items-center gap-x-2">
                  <SiteLink href={srHref(q, { sropen: c.open === r.id ? null : r.id }, c.open === r.id ? ANCHOR : PLACE_ANCHOR)} gate="plain" className="inline-block py-0.5 underline decoration-dotted" aria-expanded={c.open === r.id} data-sr-open={r.id}>{r.name}</SiteLink>
                  <span className="whitespace-nowrap text-xs">
                    {KIND_SHORT[r.kind] ?? r.kind}
                    <SiteLink href={srHref(q, { sra: c.a === r.id ? null : r.id, ...(c.b === r.id ? { srb: null } : {}) }, AB_ANCHOR)} gate="plain" aria-label={`${c.a === r.id ? "Take" : "Set"} ${r.name} as A`} aria-current={c.a === r.id ? "true" : undefined}
                      className={`ml-2 inline-block min-w-6 border px-1 py-1 text-center no-underline ${c.a === r.id ? "border-ink font-semibold" : "border-rule"}`} data-sr-set="a">A</SiteLink>
                    <SiteLink href={srHref(q, { srb: c.b === r.id ? null : r.id, ...(c.a === r.id ? { sra: null } : {}) }, AB_ANCHOR)} gate="plain" aria-label={`${c.b === r.id ? "Take" : "Set"} ${r.name} as B`} aria-current={c.b === r.id ? "true" : undefined}
                      className={`ml-1 inline-block min-w-6 border px-1 py-1 text-center no-underline ${c.b === r.id ? "border-ink font-semibold" : "border-rule"}`} data-sr-set="b">B</SiteLink>
                  </span>
                </span>
              </th>
              {cols.map((col) => <td key={col.key} className="px-2 py-1.5 text-right" data-sr-cell={col.key}><TableCell table={table} row={r} ci={colIndex(table, col.key)} place={placeOf(r.id)} of={ofCol.get(col.key) as About} /></td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ---- A and B, side by side ------------------------------------------------------------------------------------------

function AbPanel({ q, c, table, index }: { q: Q; c: Choice; table: TableFile; index: IndexFile }) {
  const slots = ([["a", c.a], ["b", c.b]] as const).map(([k, id]) => ({ k, row: id ? table.rows.find((r) => r.id === id) : undefined, place: id ? index.places.find((p) => p.id === id) : undefined }));
  const name = (s: (typeof slots)[number]) => s.row?.name ?? "none chosen";
  return (
    <section id={AB_ANCHOR} className="mb-6 max-w-4xl border border-rule bg-white px-4 py-3 text-sm" aria-label="A and B, side by side" data-sr-ab={`${c.a ?? ""}|${c.b ?? ""}`}>
      <h3 className="font-serif text-lg">A and B, side by side: {name(slots[0])} and {name(slots[1])}
        <SiteLink href={srHref(q, { sra: null, srb: null })} gate="plain" className="ml-2 inline-block py-1 font-sans text-xs underline">Clear A and B</SiteLink></h3>
      <div className="mt-2 overflow-x-auto" role="region" aria-label="A and B, every count" tabIndex={0}>
        <table className="w-full border-collapse text-left text-sm tabular-nums">
          <caption className="sr-only">Every count of the table for the two places chosen, A beside B</caption>
          <thead>
            <tr className="border-b border-ink text-xs">
              <th scope="col" className="px-2 py-1.5 font-normal">Count</th>
              {slots.map((s) => (
                <th key={s.k} scope="col" className="px-2 py-1.5 text-right font-normal" data-sr-ab-head={s.k}>
                  {s.k.toUpperCase()}: {s.row ? <SiteLink href={srHref(q, { sropen: s.row.id }, PLACE_ANCHOR)} gate="plain" className="inline-block py-1 underline decoration-dotted">{s.row.name}</SiteLink> : "none chosen"}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {index.sections.flatMap((sec) => table.columns.map((col, ci) => ({ col, ci, of: columnAbout(table, ci) })).filter((x) => x.col.section === sec.id).map(({ col, ci, of }, i) => (
              <tr key={col.key} className="border-b border-rule align-top" data-sr-ab-row={col.key}>
                <th scope="row" className="px-2 py-1.5 text-left font-normal">
                  {i === 0 ? <span className="block text-xs font-semibold">{sec.title}</span> : null}
                  <Tip tip={withLink(about(col.label, col.unit, of.period, table.sources, of.src), table.sources, of.src)}>{withUnit(col.label, col.unit)}</Tip>
                </th>
                {slots.map((s) => <td key={s.k} className="px-2 py-1.5 text-right" data-sr-ab-cell={s.k}>{s.row ? <TableCell table={table} row={s.row} ci={ci} place={s.place} of={of} /> : null}</td>)}
              </tr>
            )))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ---- a place opened: its own file ------------------------------------------------------------------------------------

const th = "px-2 py-1 font-normal", td = "px-2 py-1";
/** A small table of one of a place's lists. `cols`: a head and what a row draws under it. */
function Rows({ caption, head, rows, mark, about: source }: { caption: string; head: { label: string; right?: boolean; tip?: ReactNode }[]; rows: { key: string; cells: ReactNode[] }[]; mark: string; about?: ReactNode }) {
  if (!rows.length) return null;
  return (
    <div className="mt-2 overflow-x-auto" role="region" aria-label={caption} tabIndex={0} data-sr-list={mark} data-sr-list-rows={rows.length}>
      <table className="w-full border-collapse text-left text-sm tabular-nums">
        <caption className="pb-1 text-left text-xs font-semibold">{caption}{source ? <span className="ml-2 font-normal"><Tip tip={source} data={{ "sr-list-source": mark }}>source</Tip></span> : null}</caption>
        <thead><tr className="border-b border-ink text-xs">{head.map((h) => <th key={h.label} scope="col" className={`${th} ${h.right ? "text-right" : ""}`}>{h.tip ? <Tip tip={h.tip}>{h.label}</Tip> : h.label}</th>)}</tr></thead>
        {/* a figure's cell keeps to one line, so a figure and its small trend stand side by side and the table scrolls
            inside its frame on a phone (seen at 390 px: a trend ran over the next column) */}
        <tbody>{rows.map((r) => <tr key={r.key} className="border-b border-rule align-top">{r.cells.map((cell, i) => <td key={i} className={`${td} ${head[i]?.right ? "whitespace-nowrap text-right" : ""}`}>{cell}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
const num = (file: string, path: Segment[], v: unknown, unit?: string): ReactNode => (typeof v === "number" && Number.isFinite(v) ? <Fig file={file} path={path} v={v} unit={unit} /> : null);
const words = (v: unknown): ReactNode => (text(v) ? text(v) : null);
/** A fuel as a reader reads it: the builder names some by their key ("natural_gas"). */
const fuelWords = (v: unknown): ReactNode => { const s = text(v).replace(/_/g, " "); return s ? s.charAt(0).toUpperCase() + s.slice(1) : null; };
const link = (label: unknown, url: unknown, mark: string): ReactNode => { const u = safeUrl(url); return u ? <a href={u} rel="noopener" className="inline-block py-0.5" data-sr-source={mark}>{text(label) || "the source"}</a> : words(label); };
/** A document's words in a table's cell: cut at a word when long, the whole on hover (as the tab's rules table cuts them). */
const cut = (v: unknown): ReactNode => { const s = text(v); if (!s) return null; return s.length > 96 ? <Tip tip={s} plain>{`${s.slice(0, 94).replace(/\s+\S*$/, "")}...`}</Tip> : s; };

function PlaceSection({ q, id, title, place, file, counts, entity }: { q: Q; id: string; title: string; place: PlaceFile; file: string; counts: { key: string; label: string; unit: string }[]; entity: string | null }) {
  const sec = place.sections[id];
  const S = place.sources ?? {};
  const base: Segment[] = ["sections", id];
  if (!sec) return null;
  const head = <h4 className="font-semibold">{title}</h4>;
  if (sec.status && sec.status !== "shown") {
    return <div className="border-t border-rule py-2" data-sr-section={id} data-sr-section-state="not-shown">{head}<p className="mt-1"><Held held={sec.status} what={title} /></p></div>;
  }
  const label = (key: string) => counts.find((x) => x.key === key)?.label ?? key.replace(/_/g, " ");
  // every count the section holds as a cell of its own, the index's counts first and in its order
  const own = [...counts.map((x) => x.key), ...Object.keys(sec)].filter((k, i, all) => all.indexOf(k) === i && isCell(sec[k]));
  const tipOf = (c: Cell, what: string): ReactNode => withLink(about(what, c.unit, c.period, S, c.src), S, c.src);
  const cellAt = (c: unknown, path: Segment[], what: string, unit = true, otherwise: string | null = null) => <CellView c={c} file={file} path={path} what={what} sources={S} entity={entity} unit={unit} otherwise={otherwise} />;
  const srcOf = (key: string): ReactNode => { const k = text(sec[key]) || null, said = sourceWords(S, k); return said ? withLink(said, S, k) : undefined; };
  let extra: ReactNode = null;
  if (id === "price") {
    const hubs = list(sec.hubs);
    // a hub the file lists with a status of its own and no figures (an operator held whole) gives that status as each cell's reason
    const why = (h: Record<string, unknown>) => (text(h.status) && h.status !== "shown" ? text(h.status) : null);
    extra = <Rows mark="price.hubs" caption="Each hub's hourly prices"
      head={[{ label: "Hub" }, { label: "Market" }, { label: "Mean, USD/MWh", right: true }, { label: "95th percentile, USD/MWh", right: true }, { label: "Hours above USD 100", right: true }, { label: "Hours below zero", right: true }, { label: "Hours held", right: true, tip: isCell(hubs[0]?.hours) ? tipOf(hubs[0].hours as Cell, "Hours held") : undefined }]}
      rows={hubs.map((h, i) => ({ key: `${text(h.hub_id)}|${text(h.market)}|${i}`, cells: [words(h.hub) ?? words(h.hub_id), words(h.market),
        ...(["mean", "p95", "hours_over_100", "hours_below_0", "hours"] as const).map((k) => cellAt(h[k], [...base, "hubs", i, k], `${text(h.hub) || "the hub"}, ${text(h.market)}, ${label(k)}`, false, why(h)))] }))} />;
  } else if (id === "congestion") {
    const hubs = list(sec.hubs);
    const top = (key: "top_by_hours" | "top_by_cost", caption: string) => {
      const rows = list(sec[key]);
      return <Rows mark={`congestion.${key}`} caption={caption}
        head={[{ label: "Constraint, as the operator names it", tip: withLink([sec.top_period ? `Period: ${periodWords(text(sec.top_period))}.` : "", sourceWords(S, text(sec.top_src) || null)].filter(Boolean).join(" ") || "The operator's own name of the constraint.", S, text(sec.top_src) || null) }, { label: "Contingency" }, { label: "Hours bound", right: true }, { label: "Cost, USD/MWh times hours", right: true }, { label: "Mean, USD/MWh", right: true }]}
        rows={rows.map((r, i) => ({ key: `${i}`, cells: [words(r.name), words(r.contingency), num(file, [...base, key, i, "hours"], r.hours, "hours"), num(file, [...base, key, i, "cost"], r.cost, "USD/MWh"), num(file, [...base, key, i, "abs_mean"], r.abs_mean, "USD/MWh")] }))} />;
    };
    extra = <>
      <Rows mark="congestion.hubs" caption="Congestion in each hub's price" head={[{ label: "Hub" }, { label: "Share of the price, %", right: true }, { label: "Mean congestion part, USD/MWh", right: true }]}
        rows={hubs.map((h, i) => ({ key: `${text(h.hub_id)}|${i}`, cells: [words(h.hub) ?? words(h.hub_id), cellAt(h.congestion_share_pct, [...base, "hubs", i, "congestion_share_pct"], `${text(h.hub)}, share of the price that was congestion`, false), cellAt(h.congestion_mean, [...base, "hubs", i, "congestion_mean"], `${text(h.hub)}, mean congestion part of the price`, false)] }))} />
      {typeof sec.top_held === "string" && sec.top_held ? <p className="mt-1">The constraints that bound most: <Held held={sec.top_held} what="The constraints that bound most" /></p> : <>{top("top_by_hours", "The ten constraints that bound for the most hours")}{top("top_by_cost", "The ten constraints with the highest cost")}</>}
    </>;
  } else if (id === "queue") {
    const fuels = list(sec.by_fuel);
    extra = <Rows mark="queue.by_fuel" caption="Active requests by fuel" head={[{ label: "Fuel, as Berkeley Lab names it" }, { label: "Active, MW", right: true }, { label: "Active requests", right: true }]}
      rows={fuels.map((f, i) => ({ key: `${text(f.fuel)}|${i}`, cells: [fuelWords(f.fuel), cellAt(f.active_mw, [...base, "by_fuel", i, "active_mw"], `${text(f.fuel)}, active megawatts`, false), cellAt(f.active_projects, [...base, "by_fuel", i, "active_projects"], `${text(f.fuel)}, active requests`, false)] }))} />;
  } else if (id === "large_load") {
    const rules = list(sec.rules), totals = list(sec.queue_totals), laws = list(sec.laws);
    const states = Array.isArray(sec.states) ? (sec.states as unknown[]).filter((s): s is string => typeof s === "string") : [];
    // a rule opens its source: its own document where the row carries an address, else the tab's own rule of the same
    // id (the rules table under this section draws it whole, with its document and each value's cite)
    const ruleName = (r: Record<string, unknown>): ReactNode => (safeUrl(r.source_url) ? link(r.utility, r.source_url, "rule")
      : text(r.id) ? <SiteLink href={ruleHref(q, text(r.id))} gate="plain" className="inline-block py-0.5 underline decoration-dotted" data-sr-rule={text(r.id)}>{text(r.utility) || text(r.id)}</SiteLink> : words(r.utility));
    const threshold = (r: Record<string, unknown>, i: number): ReactNode => {
      const n = num(file, [...base, "rules", i, "threshold_mw"], r.threshold_mw), said = text(r.threshold_text);
      return n && said ? <Tip tip={`As the rule's document prints it: ${said}`} plain data={{ "sr-threshold": "1" }}>{n}</Tip> : n ?? cut(said);
    };
    extra = <>
      {states.length ? <p className="mt-1" data-sr-states={states.length}>The states it reaches: {states.join(", ")}.</p> : null}
      <Rows mark="large_load.rules" caption="The large-load rules of its utilities, each as its document prints it" about={srcOf("rules_src")}
        head={[{ label: "Utility: opens its rule" }, { label: "State" }, { label: "Status" }, { label: "Smallest load, MW", right: true }, { label: "Contract term" }, { label: "Collateral" }, { label: "Exit fee" }, { label: "Study timeline" }]}
        rows={rules.map((r, i) => ({ key: `${text(r.id)}|${i}`, cells: [ruleName(r), words(r.state), words(r.status), threshold(r, i), cut(r.contract_term), cut(r.collateral), cut(r.exit_fee), cut(r.study_timeline)] }))} />
      <Rows mark="large_load.queue_totals" caption="Large-load requests its utilities have stated, each as printed" about={srcOf("queue_totals_src")} head={[{ label: "Utility: opens its document" }, { label: "State" }, { label: "Date" }, { label: "MW", right: true }, { label: "As printed" }]}
        rows={totals.map((r, i) => ({ key: `${i}`, cells: [link(r.utility, r.source_url, "queue-total"), words(r.state), words(r.date), num(file, [...base, "queue_totals", i, "mw"], r.mw), cut(r.figure)] }))} />
      <Rows mark="large_load.laws" caption="State laws and bills on large loads, in the states it reaches" about={srcOf("laws_src")} head={[{ label: "State" }, { label: "Bill" }, { label: "Status" }, { label: "Title" }]}
        rows={laws.map((r, i) => ({ key: `${i}`, cells: [words(r.state), words(r.bill), words(r.status), cut(r.title)] }))} />
    </>;
  } else if (id === "mix_carbon") {
    const mix = list(sec.mix);
    const hours = Array.isArray(sec.intensity_by_hour) ? (sec.intensity_by_hour as unknown[]) : [];
    const pts = hours.map((v, i) => ({ t: `${String(i).padStart(2, "0")}:00`, v })).filter((p): p is { t: string; v: number } => typeof p.v === "number" && Number.isFinite(p.v));
    const hourHeld = typeof sec.intensity_by_hour_held === "string" && sec.intensity_by_hour_held ? sec.intensity_by_hour_held : pts.length < 24 ? "not held: the file holds fewer than 24 hours" : null;
    const hourTip = ["Carbon intensity by hour of day in the place's own clock, kg CO2/MWh, the mean of each hour.", sec.intensity_by_hour_period ? `Period: ${periodWords(text(sec.intensity_by_hour_period))}.` : "", sourceWords(S, text(sec.intensity_by_hour_src) || null), "Put the mouse on the line for an hour's figure."].filter(Boolean).join(" ");
    extra = <>
      <p className="mt-1" data-sr-trend="intensity_by_hour"><Tip tip={withLink(hourTip, S, text(sec.intensity_by_hour_src) || null)}>By hour of day</Tip>:{" "}
        {hourHeld ? <Held held={hourHeld} what="Carbon intensity by hour of day" /> : <span className="inline-block bg-white p-1 align-middle"><InlineSpark values={pts} label={`${place.name}: carbon intensity by hour of day, kg CO2/MWh`} width={168} height={32} /></span>}
        {!hourHeld ? <span className="ml-2 text-xs">lowest <Fig file={file} path={[...base, "intensity_by_hour", pts.reduce((m, p, i) => (p.v < pts[m].v ? i : m), 0)]} v={Math.min(...pts.map((p) => p.v))} unit="kgCO2/MWh" /> at {pts.reduce((m, p) => (p.v < m.v ? p : m), pts[0]).t}, highest <Fig file={file} path={[...base, "intensity_by_hour", pts.reduce((m, p, i) => (p.v > pts[m].v ? i : m), 0)]} v={Math.max(...pts.map((p) => p.v))} unit="kgCO2/MWh" /> at {pts.reduce((m, p) => (p.v > m.v ? p : m), pts[0]).t}</span> : null}
      </p>
      {!mix.length && typeof sec.mix_held === "string" && sec.mix_held ? <p className="mt-1">Each fuel&apos;s share of net generation: <Held held={sec.mix_held} what="Each fuel's share of net generation" /></p> : null}
      <Rows mark="mix_carbon.mix" caption="Each fuel's share of net generation" head={[{ label: "Fuel" }, { label: "Share, %", right: true, tip: isCell(mix[0]?.share_pct) ? tipOf(mix[0].share_pct as Cell, "Share of net generation") : undefined }]}
        rows={mix.map((m, i) => ({ key: `${text(m.fuel)}|${i}`, cells: [fuelWords(m.fuel), cellAt(m.share_pct, [...base, "mix", i, "share_pct"], `${text(m.fuel)}, share of net generation`, false)] }))} />
    </>;
  } else if (id === "imports") {
    const partners = list(sec.partners);
    extra = <Rows mark="imports.partners" caption="The three neighbours it took most from, net" head={[{ label: "Neighbour" }, { label: "Net imports from it, MWh", right: true, tip: isCell(partners[0]?.net_import_mwh) ? tipOf(partners[0].net_import_mwh as Cell, "Net imports from the neighbour") : undefined }]}
      rows={partners.map((p, i) => ({ key: `${text(p.ba)}|${i}`, cells: [<>{words(p.name) ?? words(p.ba)}{text(p.ba) && text(p.name) ? <span className="ml-1 text-xs">({text(p.ba)})</span> : null}</>, cellAt(p.net_import_mwh, [...base, "partners", i, "net_import_mwh"], `Net imports from ${text(p.name) || text(p.ba)}`, false)] }))} />;
  } else if (id === "datacenters") {
    const rows = list(sec.list);
    const heldTable = ["datacenter_facilities", "datacenter_projects"].find((t) => siteHolds(t, null));
    // the file's own reason for an empty list first; then the site's own hold, whatever the file carries
    const listHeld = typeof sec.list_held === "string" && sec.list_held ? sec.list_held : heldTable && rows.length ? siteHoldWords(heldTable) : null;
    extra = listHeld ? <p className="mt-1">The datacenters there: <Held held={listHeld} what="The datacenters there" table={heldTable ?? "datacenter_facilities"} /></p>
      : <Rows mark="datacenters.list" caption="The datacenters there, the largest stated first" head={[{ label: "Name: opens its source" }, { label: "Kind" }, { label: "Operator" }, { label: "State" }, { label: "County" }, { label: "MW stated", right: true }, { label: "Status" }]}
        rows={rows.map((r, i) => ({ key: `${i}`, cells: [link(r.name, r.source_url, "datacenter"), words(r.kind), words(r.operator), words(r.state), words(r.county), num(file, [...base, "list", i, "mw"], r.mw), words(r.status)] }))} />;
  }
  return (
    <div className="border-t border-rule py-2" data-sr-section={id} data-sr-section-state="shown">
      {head}
      {own.length ? (
        <dl className="mt-1 grid gap-x-6 gap-y-1 sm:grid-cols-2 xl:grid-cols-3" data-sr-counts={own.length}>
          {own.map((k) => { const c = sec[k] as Cell; return (
            <div key={k} className="flex items-baseline justify-between gap-3 border-b border-rule/60 py-0.5" data-sr-count={`${id}.${k}`}>
              <dt><Tip tip={tipOf(c, label(k))}>{label(k)}</Tip></dt>
              <dd className="whitespace-nowrap text-right tabular-nums">{cellAt(c, [...base, k], `${label(k)}, ${place.name}`)}</dd>
            </div>
          ); })}
        </dl>
      ) : null}
      {extra}
    </div>
  );
}

function PlacePanel({ q, index, id }: { q: Q; index: IndexFile; id: string }) {
  const p = index.places.find((x) => x.id === id) as Place;
  const place = loadPlace(index, id), file = placePath(index, id);
  const close = <SiteLink href={srHref(q, { sropen: null })} gate="plain" className="ml-2 inline-block py-1 font-sans text-xs underline" data-sr-close={id}>Close</SiteLink>;
  // white, not the paper of the tab's other panels: its lists are tables that scroll inside their frames, and the
  // brand draws a frame's edges and first column on white (app/tokens.css)
  return (
    <section id={PLACE_ANCHOR} className="mb-6 border border-rule bg-white px-4 py-3 text-sm" aria-label={`${p.name}: its counts`} data-sr-place={id} data-sr-place-state={place && file ? "file" : "none"}>
      <h3 className="font-serif text-lg">{p.name}{close}</h3>
      <p className="mt-1 text-xs" data-sr-place-about="1">
        <Tip tip={KIND_TIP[p.kind]}>{KIND_WORDS[p.kind]}</Tip>
        {p.code ? <>, EIA code {p.code}</> : null}
        {p.members.length > 1 ? <>; its authorities: {p.members.join(", ")}</> : null}
        {p.ref_hub ? <>; the hub its prices are read at: {p.ref_hub}</> : null}
        ; its clock: {p.tz}
      </p>
      {!place || !file ? (
        <p className="mt-2"><Held held="not held: this place's own file is not on this build of the site; the table's row is all the page holds of it" what={`${p.name}: its counts`} /></p>
      ) : (
        <div className="mt-2">
          {index.sections.map((s) => <PlaceSection key={s.id} q={q} id={s.id} title={s.title} place={place} file={file} counts={s.counts} entity={p.ref_hub} />)}
        </div>
      )}
    </section>
  );
}

// ---- the section -------------------------------------------------------------------------------------------------------

/** One line near the top of the tab that leads to the section: it stands under the hub table, a long way down. Drawn
 *  only when the regions files are the data machine's (not the contract's examples). */
export function RegionsJump() {
  if (loadRegions().state !== "files") return null;
  return <p className="mb-3 text-sm" data-sr-jump="1">Under the table: <a href={`#${ANCHOR}`} className="inline-block py-0.5 underline">{REGIONS_TITLE.toLowerCase()}, every region side by side</a>.</p>;
}

export function RegionsSection({ q }: { q: Q }) {
  const got = loadRegions();
  const frame = (state: string, body: ReactNode) => (
    // every hover's trigger and every blank is a target 24 px high (WCAG 2.2, target size), as the tab's own cells are
    <section className="mt-4 min-w-0 lg:col-span-2 [&_button[data-tip-trigger]]:min-h-6 [&_button[data-tip-trigger]]:min-w-6 [&_[data-llr-blank]_button]:h-6 [&_[data-sr-downloads]_button]:inline-block [&_[data-sr-downloads]_button]:py-0.5" id={ANCHOR} aria-label={REGIONS_TITLE} data-llr="regions" data-sr="1" data-sr-state={state}>
      <h2 className="mb-2 border-b border-rule pb-1 font-serif text-xl text-accent">{REGIONS_TITLE}</h2>
      {body}
    </section>
  );
  if (got.state !== "files") {
    return frame(got.state, (
      <p className="mb-3 max-w-4xl text-sm" data-sr-not-built="1">
        Every region, market operator and large balancing authority side by side, a count a column: price, congestion, how tight the grid runs, what waits to connect, the large-load rules, carbon, what it leans on its neighbours for, what is spare, how well its demand is forecast, and the datacenters already there.{" "}
        <Tip tip={got.why} data={{ "sr-held": "not built" }}>not built yet</Tip>
      </p>
    ));
  }
  const { index, table } = got;
  const c = choiceOf(q, table, index);
  const rows = rowsShown(table, c), cols = colsDrawn(table, c);
  const counts = Object.fromEntries(KINDS.map((k) => [k, table.rows.filter((r) => r.kind === k).length])) as Record<Kind, number>;
  const address = srHref(q, {}, ANCHOR);
  return frame("files", (
    <>
      <p className="mb-3 max-w-4xl text-sm" data-sr-lead="1">
        {table.rows.length} places side by side, a row a place and a column a count: {KINDS.filter((k) => counts[k]).map((k, i, all) => <span key={k}>{i ? (i === all.length - 1 ? " and " : ", ") : ""}{counts[k]} <Tip tip={k === "ba" && index.ba_floor_mw ? `${KIND_TIP.ba} The floor: ${index.ba_floor_mw.toLocaleString("en-US")} MW${index.ba_floor_period ? `, over ${periodWords(index.ba_floor_period)}` : ""}.` : KIND_TIP[k]}>{KIND_PLURAL[k]}</Tip></span>)}.
        {" "}Each count is <Tip tip={`As its publisher printed it, or a plain arithmetic of it (a share, a sum, a mean, a percentile, a count of hours), from tables the warehouse already holds. A count's period and source are in its column's hover. Files built ${utcWords(table.built)}.`}>its publisher&apos;s own</Tip>; nothing is scored or ranked. Press a place&apos;s name for everything its file holds.
      </p>
      <RegionsChoices key={`${c.cols.join(",")}|${c.kind}|${c.a}|${c.b}`} q={q} columns={table.columns} sections={index.sections.map((s) => ({ id: s.id, title: s.title }))} chosen={c.cols} defaults={defaultCols(table.columns)}
        kind={c.kind} a={c.a} b={c.b} places={table.rows.map((r) => ({ id: r.id, name: r.name, kind: r.kind }))} counts={counts} />
      {c.a || c.b ? <AbPanel q={q} c={c} table={table} index={index} /> : null}
      {c.open ? <PlacePanel q={q} index={index} id={c.open} /> : null}
      <p className="mb-2 text-sm" role="status" data-sr-shown={`${rows.length}|${table.rows.length}`} data-sr-sorted={`${c.sort}|${c.dir}`}>
        {rows.length} of {table.rows.length} places shown{c.kind !== "all" ? ` (the ${KIND_PLURAL[c.kind]})` : ""}, {sortWords(c, table)}. The order is the {c.sort === NAME_SORT ? "file" : "column"}&apos;s, not a ranking of places.{" "}
        <RegionsDownload csv={tableCsv(table, rows, cols, address)} rows={rows.length} cols={cols.length} />
      </p>
      <PlacesTable q={q} c={c} table={table} index={index} />
    </>
  ));
}
