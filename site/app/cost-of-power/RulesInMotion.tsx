import type { ReactNode } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolTable } from "@/components/tool/ToolPage";
import { hrefOf, type Inputs } from "@/lib/datacenter";
import { NO_READ, NONE_WORDS, RULE_GRIDS, blockOf, dayWords, docketTip, docketWords, droppedTip, foldOf, leftOf, linkOf, readOf, rulesGrid, sourcesOf, statusOf, termsTip, type RuleRow } from "@/lib/rules";
import { rulesFile } from "@/lib/rulesdata";

// Session 154: "Rules in motion", in the section "How soon" of "What a datacenter pays" (/cost-of-power, in review):
// the regulatory actions in motion for the grid the address names, newest first, each with its date, its status, the
// regulator and docket number as a link to the source document (the exact sentence, the page and the topic on hover)
// and a one-line read marked as a model's; then the group "Federal, all grids". Eight rows of each group are shown and
// the rest are behind a fold (a details element: it answers the mouse and the keyboard, with no script). Everything is
// read from one site file, data/datacenter/rules.json (lib/rulesdata.ts); what is shown and in what order is
// lib/rules.ts. MISO reads "paused while terms are reviewed" and shows no row. An address that names PJM shows PJM's
// rules here, although the rest of the page does not open PJM. The face carries no method: a thing not held is a short
// placeholder with its reason on hover, and the rest is in the Method note (docs/methods/datacenter_cost.md).

function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
const dotted = "cursor-help border-b border-dotted border-muted";
const longDay = (iso: string) => { const d = new Date(iso); return Number.isNaN(d.getTime()) ? null : d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }); };

function rowCells(r: RuleRow, group: string): { key: string; cells: ReactNode[] } {
  const date = dayWords(r.date), status = statusOf(r), read = readOf(r), href = linkOf(r)!;
  const where = (r.why_here ?? "").trim(), title = (r.title ?? "").trim();
  return {
    key: `${group}-${r.id}`,
    cells: [
      <span key="d" className="whitespace-nowrap" data-rule={r.id} data-rule-group={group} data-rule-date={date ? r.date : ""}>
        {date ?? <Missing words="not stated" why="The document states no date for this row." />}
      </span>,
      <span key="s" data-rule-status={r.id}>
        {status.stated ? <span className={dotted} title={status.why}>{status.words}</span> : <Missing words={status.words} why={status.why} />}
      </span>,
      <span key="l" className="block">
        <a href={href} title={docketTip(r)} className="cursor-help" data-rule-link={r.id}>{docketWords(r)}</a>
        {title ? <span className={`block text-xs text-muted ${where ? "cursor-help" : ""}`} title={where || undefined} data-rule-title={r.id}>{title}</span> : null}
      </span>,
      <span key="r" className="block" data-rule-read={r.id}>
        {read.line
          ? <>{read.line} <span className="ml-1 inline-block cursor-help whitespace-nowrap border border-rule px-1 text-[10px] uppercase tracking-wide text-muted" title={read.why} data-rule-mark="model">model&apos;s read</span></>
          : <Missing words={NO_READ} why={read.why} />}
      </span>,
    ],
  };
}

const HEAD = ["Date", "Status", "Regulator and docket", "What it would change for a large load"];
function Group({ rows, group, caption }: { rows: RuleRow[]; group: string; caption: string }) {
  const { shown, folded } = foldOf(rows);
  return (
    <div data-rules-group={group} data-rules-count={rows.length}>
      <ToolTable caption={caption} words minWidth={720} head={HEAD} rows={shown.map((r) => rowCells(r, group))} />
      {folded.length ? (
        <details className="border-b border-rule py-1.5" data-rules-fold={group}>
          <summary className="cursor-pointer text-sm text-accent">{folded.length} earlier</summary>
          <div className="pt-2"><ToolTable caption={`${caption}, earlier`} words minWidth={720} head={HEAD} rows={folded.map((r) => rowCells(r, group))} /></div>
        </details>
      ) : null}
    </div>
  );
}

export function RulesInMotion({ x, asked, names }: { x: Inputs; asked: string | undefined; names: Record<string, string> }) {
  const grid = rulesGrid(asked, x.grid), name = names[grid] ?? grid.toUpperCase();
  const { file, error } = rulesFile();
  const b = blockOf(file, grid);
  const built = file?.built_at_utc ? longDay(file.built_at_utc) : null;
  const sources = b.state === "paused" ? [] : sourcesOf(file);
  const left = leftOf(file);
  return (
    <div className="mt-6" id="rules" data-rules="1" data-rules-for={grid} data-rules-state={b.state}>
      <h3 className="mb-2 font-serif text-lg text-accent">Rules in motion, {name}</h3>
      <nav aria-label="Rules in motion, by grid" className="mb-3 flex flex-wrap gap-1 text-xs" data-rules-nav="1">
        {RULE_GRIDS.map((id) => (
          <span key={id} data-rules-choice={id} data-rules-chosen={id === grid ? "1" : "0"}>
            <Link href={hrefOf(x, { grid: id, region: "" })} scroll={false} aria-current={id === grid ? "true" : undefined} style={{ color: id === grid ? "#fff" : "var(--color-ink)" }}
              className={`inline-block border px-2 py-0.5 no-underline ${id === grid ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{names[id] ?? id.toUpperCase()}</Link>
          </span>
        ))}
      </nav>
      {b.state === "paused" ? (
        <p className="text-sm" data-rules-paused="1"><Missing words={b.words ?? ""} why={b.why ?? ""} /></p>
      ) : (
        <>
          {b.state === "shown" ? <Group rows={b.rows} group="grid" caption={`Rules in motion, ${name}`} />
            : <p className="text-sm" data-rules-empty={b.state}>{b.state === "none" ? <Missing words={b.words ?? NONE_WORDS} why={b.why ?? ""} /> : <Missing why={error && error !== "not there" ? `The file of rules in motion could not be read: ${error}.` : b.why ?? ""} />}</p>}
          {file ? (
            <>
              <h4 className="mb-2 mt-5 text-sm font-semibold">Federal, all grids</h4>
              {b.federal.length ? <Group rows={b.federal} group="federal" caption="Rules in motion, federal, all grids" />
                : <p className="text-sm" data-rules-empty="federal"><Missing words={NONE_WORDS} why="No federal action in motion that names no grid operator is held." /></p>}
              <p className="mt-2 text-xs text-muted" data-rules-foot="1">
                {built ? <span className={dotted} title={`The file of rules in motion was built on ${built}.${Number(file.window_months) > 0 ? ` It holds proceedings that are open, and orders and rules dated in the ${Number(file.window_months)} months before it.` : ""}`}>held {built}</span> : null}
                {sources.length ? <>{built ? "; " : ""}regulators&apos; terms: {sources.map((s, i) => (
                  <span key={s.regulator}>{i ? ", " : ""}{s.terms_url
                    ? <a href={s.terms_url} title={termsTip(s) || undefined} className="cursor-help" data-rules-terms={s.regulator}>{s.regulator}</a>
                    : <span className={termsTip(s) ? dotted : ""} title={termsTip(s) || undefined} data-rules-terms={s.regulator}>{s.regulator}</span>}</span>
                ))}</> : null}
                {left ? <>; <span data-rules-left={left.count}><Missing words={`${left.count} held, not shown`} why={left.why} /></span></> : null}
                {b.dropped.length ? <>; <span data-rules-dropped={b.dropped.length}><Missing words={`${b.dropped.length} in the file, not shown`} why={droppedTip(b.dropped)} /></span></> : null}
              </p>
            </>
          ) : null}
        </>
      )}
    </div>
  );
}
