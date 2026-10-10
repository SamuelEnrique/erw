// Session 170: the finding card, modeled on the peak premium panel of the owner's thesis: a short section title in
// capitals, the insight as an italic subtitle, one interactive chart that compares, two or three callout boxes with a
// before and after number, one paragraph giving the why with the context numbers, and a method footnote as precise as
// his. Every number here is the card's JSON, which the engine computed and a test reproduces from the CSV download.
import { CardChart } from "./CardChart";
import { FormChart } from "./FormChart";   // session 182, part 4: the card's chart in a chosen form (the default: as before)
import { RoundupButton } from "./RoundupButton";
import type { Card } from "@/lib/findings";

const fmtP = (p: number) => (p < 0.001 ? "< 0.001" : p.toFixed(3));
const fmtN = (v: number, nd = 2) => v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd });

// Session 182, part 4: `formKey` names where the chosen chart form is kept in the address ("form" on a card's own page;
// by default form.<card id>, so that several cards on one page keep their own). The renderer's frame draws the default.
export function FindingCard({ card, render = false, roundup = true, found, files = true, formKey }: { card: Card; render?: boolean; roundup?: boolean; found?: string; files?: boolean; formKey?: string }) {
  const dl = card.downloads ? `/findings/${card.downloads.csv}` : "";
  return (
    <article className={`finding-card ${render ? "finding-card-render" : ""}`} data-finding={card.id} data-card={card.card_id}>
      <header>
        <div className="finding-title text-xs font-semibold tracking-[0.18em] text-muted" data-finding-title={card.id}>{card.title}</div>
        {found ? <p className="mt-1 text-xs font-semibold text-accent" data-found-by-scanner={card.card_id}>Found by the scanner, {found}</p> : null}
        {card.draft && !found ? <p className="mt-1 text-xs font-semibold text-accent" data-draft-mark={card.card_id}>Draft: raised by the scanner, not reviewed</p> : null}
        <p className="finding-subtitle mt-1 break-words text-lg italic" data-finding-subtitle="1">{card.subtitle}</p>
        <p className="text-xs text-muted">{Object.entries(card.inputs_words).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`).join(" | ")}</p>
      </header>
      {card.refusal ? <p className="mt-3 max-w-3xl border border-rule bg-panel p-3 text-sm" data-refusal="1">{card.refusal}</p> : null}
      {card.chart.kind === "none" ? null : render
        ? <CardChart spec={card.chart} label={card.title} height={420} />   /* the renderer's frame: the card's own drawing, the markup the photographs were taken from */
        : <FormChart spec={card.chart} label={card.title} height={340} addressKey={formKey ?? `form.${card.card_id}`} />}
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
      {card.why ? <p className="finding-why mt-3 max-w-3xl text-sm" data-finding-why="1">{card.why}</p> : null}
      {card.effect_table ? (
        <div className="mt-3 overflow-x-auto" data-effect-table="1">
          <table className="w-full max-w-3xl text-xs">
            <thead>
              <tr className="border-b border-rule text-left text-muted">
                {(card.effect_table.columns?.length === 6 ? card.effect_table.columns : ["Measure (monthly)", "Per GW of batteries", "SE (HC1)", "p", "Months", "R2"]).map((h, i) => (
                  <th key={h} className={i === 0 ? "py-1 pr-3" : i === 5 ? "py-1 text-right" : "py-1 pr-3 text-right"}>{h}</th>
                ))}
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
      {(render ? [] : card.more_charts ?? []).map((m) => (
        <figure key={m.title} className="mt-4" data-more-chart="1">
          <figcaption className="text-xs font-semibold text-muted">{m.title}</figcaption>
          <CardChart spec={m.spec} label={m.title} height={render ? 260 : 240} />
        </figure>
      ))}
      <p className="finding-footnote mt-3 max-w-3xl break-words text-[11px] leading-snug text-muted" data-finding-footnote="1">{card.footnote}</p>
      {!render && card.downloads && files ? (
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
      <p className="mt-1 break-words text-[11px] text-muted">{card.source_line} Computed {card.computed_at.replace("T", " ").replace("Z", " UTC")}.</p>
    </article>
  );
}
