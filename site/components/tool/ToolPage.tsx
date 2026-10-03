// Session 67: the shared pieces of a tool page, for /cost-of-power/battery, /storage and the home page's "Open now"
// strip, so later pages can adopt them: the page frame and header, a section heading, a headline number, a chart
// frame, an input panel, a table with a cardinal header row, a folded section and the grey source line. Plain:
// Georgia in cardinal for the title and headings, Stanford black for text, fog beige for the input panel and
// highlighted rows, thin grey rules. Colors and typefaces come from app/tokens.css.
import type { ReactNode } from "react";

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
/** A chart with its title, its legend and one line under it. The chart itself is the child. */
export function ChartFrame({ title, legend, note, children }: { title: string; legend?: LegendItem[]; note?: ReactNode; children: ReactNode }) {
  return (
    <figure className="mb-10">
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-xl text-accent">{title}</span>
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
export function InputPanel({ title, children, note }: { title: string; children: ReactNode; note?: ReactNode }) {
  return (
    <section className="mb-4 bg-paper px-4 py-4" aria-label={title}>
      <h2 className="mb-3 font-serif text-lg text-accent">{title}</h2>
      {children}
      {note ? <p className="mt-3 text-xs leading-snug text-muted">{note}</p> : null}
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
