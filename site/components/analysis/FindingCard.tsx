// Session 170: the finding card, modeled on the peak premium panel of the owner's thesis: a short section title in
// capitals, the insight as an italic subtitle, one interactive chart that compares, two or three callout boxes with a
// before and after number, one paragraph giving the why with the context numbers, and a method footnote as precise as
// his. Every number here is the card's JSON, which the engine computed and a test reproduces from the CSV download.
import { CardChart } from "./CardChart";
import { FormChart } from "./FormChart";   // session 182, part 4: the card's chart in a chosen form (the default: as before)
import { RoundupButton } from "./RoundupButton";
import type { Card, Callout } from "@/lib/findings";
import { Num } from "@/components/Num";
import type { ReactNode } from "react";

// Session 315 (the owner's ruling of 13 October 2026: every card is a Num with its table): each callout figure and each
// cell of the table of estimates is a Num whose check key names the card and the figure's place in the card's own JSON
// (finding|<card>|callout|<i>|before or after|<grid>, finding|<card>|effect|<row>|<column>|<grid>); the value checker
// (scripts/check-values.mjs) reads the same file. The grid is the one the figure's own words name (its label, its
// period, its row), or "-": a grid held under its publisher's terms from 21 October 2026 (lib/license.ts) reads
// "license needed" in the figure's place, the card staying (ruling 6a of the Research pack).
const GRID_WORD: [RegExp, string][] = [[/\bERCOT\b/i, "ercot"], [/\bCAISO\b/i, "caiso"], [/\bPJM\b/i, "pjm"], [/\bMISO\b/i, "miso"], [/\bSPP\b/i, "spp"], [/\bNYISO\b/i, "nyiso"], [/\bISO-NE\b/i, "isone"]];
export const gridOfWords = (s: string): string => GRID_WORD.find(([re]) => re.test(s))?.[1] ?? "-";
const calloutKey = (card: Card, i: number, side: "before" | "after", c: Callout) => `finding|${card.card_id}|callout|${i}|${side}|${gridOfWords(`${c[side].period} ${c.label}`)}`;

// Session 238 (/research, one card a screen): with `fold` the card's method footnote, its table of estimates and its
// further charts stand under one fold, closed until it is opened, so that the claim, the chart, the numbers, the why,
// the files and the source fill about one window. Nothing is dropped: the fold holds the same markup. Without `fold`
// (a card's own page, the review list, the renderer's frame) the card is as it was.
function Unfolded({ children }: { children: ReactNode }) { return <>{children}</>; }
function Folded({ children, title }: { children: ReactNode; title?: string }) {
  return <details className="fold-more" data-finding-more="1"><summary>{title}</summary>{children}</details>;
}

const fmtP = (p: number) => (p < 0.001 ? "< 0.001" : p.toFixed(3));

/** Session 355: the statistics session 361 added to a card (lib/findings.ts, CardStatistics), under its table of
 * estimates: the Newey-West errors beside HC1, the round's multiple-comparisons line with the card's own q-values, and a
 * hunt draft's step-versus-trend flag. A caveat beside the card, never a figure or a verdict of it. */
function Statistics({ st }: { st: NonNullable<Card["statistics"]> }) {
  const nw = st.newey_west?.rows ?? [], rd = st.round, sh = st.shape;
  const q = rd?.q_bh;
  const qs = q === null || q === undefined ? [] : typeof q === "number" ? [["this claim", q] as [string, number]] : Object.entries(q);
  const label = (k: string) => nw.find((r) => `${r.numbers_key}_p` === k)?.label ?? k.replace(/_p$/, "").replace(/_/g, " ");
  return (
    <div className="mt-3 max-w-3xl text-xs" data-card-statistics={st.session ?? 1}>
      {sh && sh.step_better ? <p className="mb-2 font-semibold" data-step-flag={String(sh.break_year)}>A step, not a trend: {sh.words.replace(/^a step, not a trend: /, "")}.</p> : null}
      {nw.length ? (
        <div className="overflow-x-auto" data-newey-west={nw.length}>
          <table className="w-full text-xs">
            <thead><tr className="border-b border-rule text-left text-muted">
              <th className="py-1 pr-3">Measure</th><th className="py-1 pr-3 text-right">SE (HC1)</th><th className="py-1 pr-3 text-right">p (HC1)</th><th className="py-1 pr-3 text-right">SE (Newey-West)</th><th className="py-1 pr-3 text-right">p (Newey-West)</th><th className="py-1 text-right">Lags</th>
            </tr></thead>
            <tbody>
              {nw.map((r) => (
                <tr key={r.spec} className="border-b border-rule" data-nw-row={r.numbers_key}>
                  <td className="py-1 pr-3">{r.label}</td><td className="py-1 pr-3 text-right font-mono">{fmtN(r.se_hc1, 3)}</td><td className="py-1 pr-3 text-right font-mono">{fmtP(r.p_hc1)}</td>
                  <td className="py-1 pr-3 text-right font-mono">{fmtN(r.se_nw, 3)}</td><td className="py-1 pr-3 text-right font-mono">{fmtP(r.p_nw)}</td><td className="py-1 text-right font-mono">{r.nw_lag}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {st.newey_west?.words ? <p className="mt-1 text-muted">{st.newey_west.words} Lags: {st.newey_west.rule}.</p> : null}
        </div>
      ) : null}
      {rd ? (
        <p className="mt-2 text-muted" data-multiple-comparisons={rd.claims_tested}>
          {rd.name ? `In ${rd.name}, ` : "In this round, "}{rd.claims_tested} claims were tested and {rd.claims_passing} passed{rd.alpha ? ` at ${Math.round(rd.alpha * 100)} percent` : ""}.
          {qs.length ? <> The q-value{qs.length > 1 ? "s" : ""} over the round: {qs.map(([k, v], i) => <span key={k}>{i ? "; " : ""}{label(k)} {fmtP(v)}</span>)}.</> : null}
          {rd.caveat ? <> {rd.caveat}</> : null}
        </p>
      ) : null}
    </div>
  );
}
const fmtN = (v: number, nd = 2) => v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd });

// Session 182, part 4: `formKey` names where the chosen chart form is kept in the address ("form" on a card's own page;
// by default form.<card id>, so that several cards on one page keep their own). The renderer's frame draws the default.
// Session 238 (/research, the findings library): `held` says which of the card's three files the site holds
// (lib/research.ts, filesHeld). A file that is not held is named "not held" and is never a link; without `held` the
// row is as it was.
export function FindingCard({ card, render = false, roundup = true, found, files = true, formKey, held, fold = false }: { card: Card; render?: boolean; roundup?: boolean; found?: string; files?: boolean; formKey?: string; held?: { csv: boolean; python: boolean; stata: boolean }; fold?: boolean }) {
  const More = fold && !render ? Folded : Unfolded;
  const moreTitle = `Method${card.effect_table ? ", the table of estimates" : ""}${card.more_charts?.length ? ", a further chart" : ""}`;
  const dl = card.downloads ? `/findings/${card.downloads.csv}` : "";
  return (
    <article className={`finding-card ${render ? "finding-card-render" : ""}`} data-finding={card.id} data-card={card.card_id}>
      <header>
        <div className="finding-title text-xs font-semibold tracking-[0.18em] text-muted" data-finding-title={card.id}>{card.title}</div>
        {found ? <p className="mt-1 text-xs font-semibold text-accent" data-found-by-scanner={card.card_id}>Found by the scanner, {found}</p> : null}
        {card.draft && !found ? <p className="mt-1 text-xs font-semibold text-accent" data-draft-mark={card.card_id}>{card.hunt ? "Draft: raised by the weekly hunt, not reviewed" : "Draft: raised by the scanner, not reviewed"}</p> : null}
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
              <span className="text-muted">{c.before.period}: </span><Num check={calloutKey(card, i, "before", c)} raw={c.before.text}><strong className="text-lg" data-callout-before={i}>{c.before.text}</strong></Num>
              <span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span>
            </div>
            <div className="text-sm">
              <span className="text-muted">{c.after.period}: </span><Num check={calloutKey(card, i, "after", c)} raw={c.after.text}><strong className="text-lg" data-callout-after={i}>{c.after.text}</strong></Num>
              <span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span>
            </div>
          </div>
        ))}
      </div>
      {card.why ? <p className="finding-why mt-3 max-w-3xl text-sm" data-finding-why="1">{card.why}</p> : null}
      <More title={moreTitle}>
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
              {card.effect_table.rows.map((r, ri) => {
                const g = gridOfWords(r.measure);
                const cell = (col: "coef_per_gw" | "se" | "p" | "n" | "r2", text: string) => <Num check={`finding|${card.card_id}|effect|${ri}|${col}|${g}`} raw={r[col]}>{text}</Num>;
                return (
                <tr key={r.measure} className="border-b border-rule">
                  <td className="py-1 pr-3">{r.measure}</td><td className="py-1 pr-3 text-right font-mono">{cell("coef_per_gw", fmtN(r.coef_per_gw))}</td>
                  <td className="py-1 pr-3 text-right font-mono">{cell("se", fmtN(r.se))}</td><td className="py-1 pr-3 text-right font-mono">{cell("p", fmtP(r.p))}</td>
                  <td className="py-1 pr-3 text-right font-mono">{cell("n", String(r.n))}</td><td className="py-1 text-right font-mono">{cell("r2", fmtN(r.r2))}</td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
      {/* session 355: the card's statistics (session 361), beside its figures */}
      {!render && card.statistics ? <Statistics st={card.statistics} /> : null}
      {(render ? [] : card.more_charts ?? []).map((m) => (
        <figure key={m.title} className="mt-4" data-more-chart="1">
          <figcaption className="text-xs font-semibold text-muted">{m.title}</figcaption>
          <CardChart spec={m.spec} label={m.title} height={render ? 260 : 240} />
        </figure>
      ))}
      <p className="finding-footnote mt-3 max-w-3xl break-words text-[11px] leading-snug text-muted" data-finding-footnote="1">{card.footnote}</p>
      </More>
      {!render && card.downloads && files ? (
        <p className="mt-2 flex flex-wrap items-center gap-3 text-xs">
          <span className="text-muted">Downloads:</span>
          {held && !held.csv ? <span className="text-muted" data-not-held="csv">data (CSV): not held</span> : <a href={dl} download data-download="csv">data (CSV)</a>}
          {held && !held.python ? <span className="text-muted" data-not-held="python">Python: not held</span> : <a href={`/findings/${card.downloads.python}`} download data-download="python">Python</a>}
          {held && !held.stata ? <span className="text-muted" data-not-held="stata">Stata do-file: not held</span> : <a href={`/findings/${card.downloads.stata}`} download data-download="stata">Stata do-file</a>}
          <span className="text-muted">Renders:</span>
          <a href={`/findings/${card.card_id}_1080x1350.png`} data-download="png-linkedin">1080 x 1350</a>
          <a href={`/findings/${card.card_id}_1600x900.png`} data-download="png-x">1600 x 900</a>
          {roundup ? <RoundupButton cardId={card.card_id} /> : null}
        </p>
      ) : null}
      {!render && held && !card.downloads && files ? <p className="mt-2 text-xs text-muted" data-not-held="all">Downloads: data (CSV), Python and Stata do-file: not held.</p> : null}
      <p className="mt-1 break-words text-[11px] text-muted">{card.source_line} Computed {card.computed_at.replace("T", " ").replace("Z", " UTC")}.</p>
    </article>
  );
}
