// Session 67: the shared pieces of a tool page, for /cost-of-power/battery, /storage and the home page's "Open now"
// strip, so later pages can adopt them: the page frame and header, a section heading, a headline number, a chart
// frame, an input panel, a table with a cardinal header row, a folded section and the grey source line. Plain:
// Georgia in cardinal for the title and headings, Stanford black for text, fog beige for the input panel and
// highlighted rows, thin grey rules. Colors and typefaces come from app/tokens.css.
import type { ReactNode } from "react";

// ---- Session 296 (the owner's rulings of 15 October 2026): two pieces for every tool page.

/** A section of a settings box that opens and closes (a plain details element, so it works without script): its title
 *  stays, and while it is closed one line says what it holds ("Financing: 20% debt at 8%, 12% hurdle, no contract").
 *  The line is hidden while the section is open (app/tokens.css, "settings fold"). `open` is the state it starts in. */
export function SettingsFold({ id, title, summary, open, children }: { id: string; title: string; summary: ReactNode; open?: boolean; children: ReactNode }) {
  return (
    <details className="border-t border-rule" data-settings-fold={id} open={open}>
      <summary className="cursor-pointer py-2">
        <span className="font-semibold text-sm">{title}</span>
        <span className="mt-0.5 block text-xs leading-snug text-muted" data-fold-summary={id}>{summary}</span>
      </summary>
      <div className="pb-3">{children}</div>
    </details>
  );
}

/** A hover tip: a small mark after a label that shows its words when pointed at, tapped or focused (CSS alone:
 *  app/tokens.css, "tip"), with the words in `title` as well. The words are the note the page used to print in grey
 *  under the thing (item 9 of the rulings: every grey note becomes a hover tip). `label` says what the tip is about
 *  for a screen reader. */
export function Tip({ label, children, id }: { label: string; children: ReactNode; id: string }) {
  return (
    <span className="tip relative inline-block align-baseline" data-tip={id}>
      <button type="button" className="ml-1 inline-flex h-4 w-4 items-center justify-center border border-muted text-[10px] leading-none text-muted" aria-label={`About ${label}`} aria-describedby={`tip-${id}`}>i</button>
      <span role="tooltip" id={`tip-${id}`} className="absolute left-0 top-5 z-10 hidden w-72 max-w-[80vw] border border-rule bg-paper px-2 py-1.5 text-left text-xs font-normal leading-snug text-ink">{children}</span>
    </span>
  );
}

/** The page's frame: a white sheet on the site's beige, so the beige input panel and highlighted rows read as such. */
export function ToolPage({ children }: { children: ReactNode }) {
  return <div className="border border-rule bg-white px-4 py-6 text-ink sm:px-8 sm:py-8">{children}</div>;
}

export function ToolHeader({ title, lead, crumb }: { title: string; lead?: ReactNode; crumb?: ReactNode }) {
  return (
    <header className="mb-8 border-b border-rule pb-5">
      {crumb ? <div className="mb-2 text-xs text-muted">{crumb}</div> : null}
      <h1 className="font-serif text-3xl text-accent sm:text-4xl">{title}</h1>
      {lead ? <p className="mt-3 max-w-3xl text-base leading-relaxed">{lead}</p> : null}
    </header>
  );
}

export function ToolSection({ title, children, id, note }: { title: string; children: ReactNode; id?: string; note?: ReactNode }) {
  return (
    <section id={id} className="mb-10">
      <h2 className="mb-3 border-b border-rule pb-1 font-serif text-xl text-accent">{title}</h2>
      {children}
      {note ? <p className="mt-2 max-w-3xl text-xs text-muted">{note}</p> : null}
    </section>
  );
}

/** One headline number: a label above, the number large, one line of what it is below. */
export function HeadlineNumber({ label, value, unit, note }: { label: string; value: ReactNode; unit?: string; note?: ReactNode }) {
  return (
    <div className="border-t-2 border-accent pt-2">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 font-serif text-3xl tabular-nums text-ink">{value}{unit ? <span className="ml-1 font-sans text-sm text-muted">{unit}</span> : null}</div>
      {note ? <div className="mt-1 text-xs leading-snug text-muted">{note}</div> : null}
    </div>
  );
}
export function HeadlineRow({ children }: { children: ReactNode }) {
  return <div className="mb-10 grid gap-6 sm:grid-cols-3">{children}</div>;
}

export type LegendItem = { label: string; color: string; hatch?: boolean };
/** A chart with its title, its legend and one line under it. The chart itself is the child. Session 298: `tip`, a
 *  hover tip beside the title (the battery page's manner, session 296), for a note that explains rather than links. */
export function ChartFrame({ title, legend, note, tip, children }: { title: string; legend?: LegendItem[]; note?: ReactNode; tip?: ReactNode; children: ReactNode }) {
  return (
    <figure className="mb-10">
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-xl text-accent">{title}{tip}</span>
        {legend ? (
          <span className="flex flex-wrap gap-x-4 text-xs text-ink">
            {legend.map((l) => (
              <span key={l.label} className="inline-flex items-center gap-1.5">
                <span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={l.hatch ? { background: `repeating-linear-gradient(45deg, ${l.color} 0 2px, #fff 2px 4px)`, border: `1px solid ${l.color}` } : { background: l.color }} />
                {l.label}
              </span>
            ))}
          </span>
        ) : null}
      </figcaption>
      {children}
      {note ? <p className="mt-2 max-w-3xl text-xs text-muted">{note}</p> : null}
    </figure>
  );
}

/** The input panel: fog beige, a serif heading, its fields stacked. */
/** Session 281: `reset`, for a panel whose choices live in the address: the page's plain address, and the defaults it
 *  opens on in words. A plain link, so it works without script. */
export function InputPanel({ title, children, note, reset }: { title: string; children: ReactNode; note?: ReactNode; reset?: { href: string; defaults: string } }) {
  return (
    <section className="mb-4 bg-paper px-4 py-4" aria-label={title}>
      <h2 className="mb-3 font-serif text-lg text-accent">{title}</h2>
      {children}
      {note ? <p className="mt-3 text-xs leading-snug text-muted">{note}</p> : null}
      {reset ? <p className="mt-2 text-xs leading-snug" data-reset="1"><a href={reset.href}>Reset to the defaults</a><span className="text-muted">: {reset.defaults}</span></p> : null}
    </section>
  );
}

/** A table with a cardinal header row and thin grey rules. `highlight` rows are fog beige. */
export function ToolTable({ head, rows, minWidth = 520, caption, words }: {
  head: ReactNode[]; rows: { key: string; cells: ReactNode[]; highlight?: boolean; muted?: boolean; wide?: ReactNode }[]; minWidth?: number; caption?: string;
  /** a table of words, not numbers: every column reads from the left. A row's `wide` is one cell of words across the columns after the first. */
  words?: boolean;
}) {
  const side = words ? "text-left" : "text-right";
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth }}>
        {caption ? <caption className="sr-only">{caption}</caption> : null}
        <thead>
          <tr className="bg-accent text-white">
            {head.map((h, i) => <th key={i} scope="col" className={`px-3 py-1.5 font-normal ${i ? side : ""}`}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className={`border-b border-rule ${r.highlight ? "bg-paper font-semibold" : ""} ${r.muted ? "text-muted" : ""}`}>
              {r.wide !== undefined
                ? <><th scope="row" className="px-3 py-1.5 font-normal">{r.cells[0]}</th><td colSpan={head.length - 1} className="px-3 py-1.5 text-left text-muted">{r.wide}</td></>
                : r.cells.map((c, i) => (i === 0 ? <th key={i} scope="row" className="px-3 py-1.5 font-normal">{c}</th> : <td key={i} className={`px-3 py-1.5 ${side}`}>{c}</td>))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** A folded section, closed by default. */
export function Fold({ title, children }: { title: string; children: ReactNode }) {
  return (
    <details className="border-b border-rule py-2">
      <summary className="cursor-pointer font-serif text-lg text-accent">{title}</summary>
      <div className="pb-3 pt-3 text-sm">{children}</div>
    </details>
  );
}

/** The grey source line: every table the page reads, by name, and one note. */
export function SourceLine({ tables, note }: { tables: string[]; note?: ReactNode }) {
  return (
    <p className="mt-8 border-t border-rule pt-3 text-xs leading-relaxed text-muted">
      Source: ERW tables {tables.map((t, i) => <span key={t}>{i ? ", " : ""}<code className="font-mono">{t}</code></span>)}.{note ? <> {note}</> : null}
    </p>
  );
}

// ---- Session 240: the pieces of a top block and of a list that folds, for any page (first used by /board and /datacenters).

export type TileMove = { label: string; dir: number; text: ReactNode; title?: string };
/** One number of a top block: what it is, the number with its unit, its time, its moves (each signed, with an arrow and
 *  the up or down color of the tokens; the sign is written, so color is never the only cue) and a small trend.
 *  `blank` takes the number's place when it is not shown (paused, licensed, not held). `onOpen` makes the label a button. */
export function NumberTile({ id, label, sub, value, unit, time, moves, trend, blank, onOpen, openTitle }: {
  id?: string; label: string; sub?: string; value?: ReactNode; unit?: string; time?: ReactNode; moves?: TileMove[]; trend?: ReactNode; blank?: ReactNode;
  onOpen?: () => void; openTitle?: string;
}) {
  const name = <>{label}{sub ? <span className="block text-muted">{sub}</span> : null}</>;
  return (
    <div className="min-w-0 border-t border-rule pt-3" data-number-tile={id ?? "1"}>
      {onOpen
        ? <button type="button" onClick={onOpen} title={openTitle} className="block w-full text-left text-xs">{name}</button>
        : <div className="text-xs">{name}</div>}
      {blank !== undefined ? <div className="mt-1 text-sm italic text-muted">{blank}</div> : (
        <>
          <div className="mt-1 whitespace-nowrap font-serif text-3xl tabular-nums text-ink">{value}{unit ? <span className="ml-1 font-sans text-xs text-muted">{unit}</span> : null}</div>
          {time ? <div className="text-xs text-muted">{time}</div> : null}
          {moves?.length ? (
            <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-2 text-xs">
              {moves.map((m) => (
                <div key={m.label} className="contents">
                  <dt className="text-muted">{m.label}</dt>
                  <dd className={`whitespace-nowrap font-mono tabular-nums ${m.dir > 0 ? "text-up" : m.dir < 0 ? "text-down" : "text-muted"}`} title={m.title}>
                    {m.dir > 0 ? <span aria-hidden="true">▲ </span> : m.dir < 0 ? <span aria-hidden="true">▼ </span> : null}{m.text}
                  </dd>
                </div>
              ))}
            </dl>
          ) : null}
          {trend ? <div className="mt-2">{trend}</div> : null}
        </>
      )}
    </div>
  );
}
/** The tiles of a top block: two across on a phone, six on a wide screen. */
export function NumberTileGrid({ children, label }: { children: ReactNode; label?: string }) {
  return <div className="mb-10 grid grid-cols-2 gap-x-6 gap-y-6 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6" role="group" aria-label={label}>{children}</div>;
}

/** A group of a long page that opens and closes: its title and one line about it (a count, a sum, its first number)
 *  stay in view when it is closed. `open` with `onToggle` lets the page hold the state; without them it starts closed. */
export function GroupFold({ title, meta, open, onToggle, children }: { title: ReactNode; meta?: ReactNode; open?: boolean; onToggle?: (open: boolean) => void; children: ReactNode }) {
  return (
    <details className="border-t border-rule" data-group-fold="1" open={open} onToggle={onToggle ? (e) => onToggle((e.currentTarget as HTMLDetailsElement).open) : undefined}>
      <summary className="flex cursor-pointer flex-wrap items-baseline gap-x-4 gap-y-1 py-3">
        <h2 className="font-serif text-lg text-accent">{title}</h2>
        {meta ? <span className="text-xs text-muted">{meta}</span> : null}
      </summary>
      <div className="pb-8">{children}</div>
    </details>
  );
}

/** A group of rows inside one table that opens and closes, so every group shares the table's columns: a head row (the
 *  group's name and one line about it) and the rows in their own tbody, hidden when the group is closed. */
export function FoldRows({ id, cols, title, meta, open, onToggle, children }: { id: string; cols: number; title: ReactNode; meta?: ReactNode; open: boolean; onToggle: () => void; children: ReactNode }) {
  return (
    <>
      <tbody data-fold-head={id}>
        <tr className="border-b border-rule bg-paper">
          <th colSpan={cols} scope="rowgroup" className="px-2 py-2 text-left font-normal">
            <button type="button" aria-expanded={open} onClick={onToggle} className="flex w-full flex-wrap items-baseline gap-x-4 gap-y-1 text-left">
              <span aria-hidden="true" className="font-mono text-xs text-muted">{open ? "−" : "+"}</span>
              <span className="font-semibold">{title}</span>
              {meta ? <span className="text-xs text-muted">{meta}</span> : null}
            </button>
          </th>
        </tr>
      </tbody>
      <tbody hidden={!open} data-fold-rows={id}>{children}</tbody>
    </>
  );
}
