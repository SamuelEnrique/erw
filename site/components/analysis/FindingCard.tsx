// Session 170: the finding card, modeled on the peak premium panel of the owner's thesis: a short section title in
// capitals, the insight as an italic subtitle, one interactive chart that compares, two or three callout boxes with a
// before and after number, one paragraph giving the why with the context numbers, and a method footnote as precise as
// his. Every number here is the card's JSON, which the engine computed and a test reproduces from the CSV download.
import { CardChart } from "./CardChart";
import { RoundupButton } from "./RoundupButton";
import type { Card } from "@/lib/findings";

const fmtP = (p: number) => (p < 0.001 ? "< 0.001" : p.toFixed(3));
const fmtN = (v: number, nd = 2) => v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd });

export function FindingCard({ card, render = false, roundup = true }: { card: Card; render?: boolean; roundup?: boolean }) {
  const dl = `/findings/${card.downloads.csv}`;
  return (
    <article className={`finding-card ${render ? "finding-card-render" : ""}`} data-finding={card.id} data-card={card.card_id}>
      <header>
        <div className="finding-title text-xs font-semibold tracking-[0.18em] text-muted" data-finding-title={card.id}>{card.title}</div>
        <p className="finding-subtitle mt-1 text-lg italic" data-finding-subtitle="1">{card.subtitle}</p>
        <p className="text-xs text-muted">{Object.entries(card.inputs_words).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`).join(" | ")}</p>
      </header>
      <CardChart spec={card.chart} label={card.title} height={render ? 420 : 340} />
      {card.placeholders?.length ? (
        <p className="mt-1 text-xs text-muted">
          {card.placeholders.map((p) => (
            <span key={p.grid} className="mr-3 cursor-help italic text-muted" title={p.text} data-placeholder={p.grid}>{p.words}: {p.text}</span>
          ))}
        </p>
      ) : null}
      <div className="finding-callouts mt-3 grid gap-3 sm:grid-cols-3">
        {card.callouts.map((c, i) => (
          <div key={i} className="border border-rule bg-panel p-3" data-callout={i}>
            <div className="text-[11px] uppercase tracking-wide text-muted">{c.label}</div>
            <div className="mt-1 text-sm">
              <span className="text-muted">{c.before.period}: </span><strong className="text-lg" data-callout-before={i}>{c.before.text}</strong>
              <span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span>
            </div>
            <div className="text-sm">
              <span className="text-muted">{c.after.period}: </span><strong className="text-lg" data-callout-after={i}>{c.after.text}</strong>
              <span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span>
            </div>
          </div>
        ))}
      </div>
      <p className="finding-why mt-3 max-w-3xl text-sm" data-finding-why="1">{card.why}</p>
      {card.effect_table ? (
        <div className="mt-3 overflow-x-auto" data-effect-table="1">
          <table className="w-full max-w-3xl text-xs">
            <thead>
              <tr className="border-b border-rule text-left text-muted">
                <th className="py-1 pr-3">Measure (monthly)</th><th className="py-1 pr-3 text-right">Per GW of batteries</th><th className="py-1 pr-3 text-right">SE (HC1)</th>
                <th className="py-1 pr-3 text-right">p</th><th className="py-1 pr-3 text-right">Months</th><th className="py-1 text-right">R2</th>
              </tr>
            </thead>
            <tbody>
              {card.effect_table.rows.map((r) => (
                <tr key={r.measure} className="border-b border-rule">
                  <td className="py-1 pr-3">{r.measure}</td><td className="py-1 pr-3 text-right font-mono">{fmtN(r.coef_per_gw)}</td>
                  <td className="py-1 pr-3 text-right font-mono">{fmtN(r.se)}</td><td className="py-1 pr-3 text-right font-mono">{fmtP(r.p)}</td>
                  <td className="py-1 pr-3 text-right font-mono">{r.n}</td><td className="py-1 text-right font-mono">{fmtN(r.r2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <p className="finding-footnote mt-3 max-w-3xl text-[11px] leading-snug text-muted" data-finding-footnote="1">{card.footnote}</p>
      {!render ? (
        <p className="mt-2 flex flex-wrap items-center gap-3 text-xs">
          <span className="text-muted">Downloads:</span>
          <a href={dl} download data-download="csv">data (CSV)</a>
          <a href={`/findings/${card.downloads.python}`} download data-download="python">Python</a>
          <a href={`/findings/${card.downloads.stata}`} download data-download="stata">Stata do-file</a>
          <span className="text-muted">Renders:</span>
          <a href={`/findings/${card.card_id}_1080x1350.png`} data-download="png-linkedin">1080 x 1350</a>
          <a href={`/findings/${card.card_id}_1600x900.png`} data-download="png-x">1600 x 900</a>
          {roundup ? <RoundupButton cardId={card.card_id} /> : null}
        </p>
      ) : null}
      <p className="mt-1 text-[11px] text-muted">{card.source_line} Computed {card.computed_at.replace("T", " ").replace("Z", " UTC")}.</p>
    </article>
  );
}
