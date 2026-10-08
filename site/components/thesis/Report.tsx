// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the report of one run, drawn in tabs.
//
// The report is written on the server and only drawn here: nothing on this page says how it was made (that is the
// Method note's, one link). What the page adds is form:
//   sources      every fact, row and cell carries the ids of its sources; each is a small raised link that opens the
//                source and shows its title on hover (an ERW table has no address: its title on hover only)
//   missing      a value that is not held is a short placeholder whose hover carries the reason the report gives
//   PitchBook    a cell the PitchBook stage will fill reads "PitchBook pending" until the answer is submitted; after
//                that every PitchBook figure stands with a visible "PitchBook" tag, never merged into a cell without it
//   confidence   the number, and the one line that explains it, beside it
// Any part may be absent or empty: a tab with nothing in it says so. A server component: only the charts and the
// forms run in the browser.
//
// Session 150: a run may also hold an answer of Harmonic or of Crunchbase (lib/thesis/providers.ts). A run that holds
// PitchBook's answer alone, or none, is drawn exactly as before. Once another provider's answer is held, the PitchBook
// column becomes the providers' column (components/thesis/ProviderBlock.tsx): every figure with the label of the
// provider that supplied it, the terms line on the label's hover, and a short mark where two providers give the same
// fact differently. A figure with no provider keeps the label it had.
import Link from "next/link";
import type { ReactNode } from "react";
import { ProviderBlock, ProviderCell, ProviderFound } from "@/components/thesis/ProviderBlock";
import { FunnelChart, TrendChart } from "@/components/thesis/ThesisCharts";
import { heldOf, hoverOf, type FactId, type Held } from "@/lib/thesis/providers";
import type { Cell, PitchbookPayload, Report, Run, Source, Text } from "@/lib/thesis/types";
import { EMPTY_TAB, PB_PENDING, PB_PENDING_WHY, PLACEHOLDER, TABS, arr, chartOf, hrefOf, isMissing, nameKey, num, pbFigureFor, pbFigures, pitchbookFor, safeUrl, str, whenWords, type Choice, type TabId } from "@/lib/thesis/view";

type Ctx = {
  choice: Choice; sources: Map<string, Source>; pb: PitchbookPayload | null; asked: Set<string>; pbColumn: boolean; notes: Map<string, string>;
  /** Session 150: every provider's answer the run holds, PitchBook's first; `others` when one of them is not PitchBook's. */
  held: Held[]; others: boolean;
};
/** The fact of the providers that answers a cell of the report: the same four cells PitchBook has answered since session 135. */
const CELL_FACT: Record<string, FactId> = { founders: "founders", raised: "total_raised", location: "hq", stage: "last_round" };

const MISSING = "cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted";
const TH = "py-1 pr-3 text-left align-bottom font-normal";
const TD = "py-1.5 pr-3 align-top";
const HEAD = "border-b border-rule text-[10px] uppercase tracking-wide text-muted";

function Gap({ words, why, kind }: { words: string; why: string; kind: string }) {
  return <span className={MISSING} title={why} data-missing={kind}>{words}</span>;
}
/** The visible tag every PitchBook figure carries; its hover says where the figure came from. */
function PbTag({ ctx }: { ctx: Ctx }) {
  // the hover keeps the note it has carried since session 135 and adds the terms line and the answer's stamp
  const stamp = ctx.held.find((h) => h.provider === "pitchbook");
  return <>{" "}<span className="whitespace-nowrap rounded-sm border border-accent px-1 align-baseline text-[10px] font-semibold not-italic text-accent" title={stamp ? hoverOf(stamp) : str(ctx.pb?.received_note) || "PitchBook"} data-pb-tag="1">PitchBook</span></>;
}

/** The sources of a fact, a row or a cell: small raised ids, each opening its source. */
function Src({ ids, ctx }: { ids: string[] | null | undefined; ctx: Ctx }) {
  const list = arr(ids).map(str).filter(Boolean);
  if (!list.length) return null;
  return (
    <sup className="ml-0.5 whitespace-nowrap text-[10px] font-normal not-italic" data-sources={list.join(",")}>
      {list.map((id, i) => {
        const s = ctx.sources.get(id);
        const url = s && s.kind !== "erw" ? safeUrl(s.url) : null;
        const title = s ? `${str(s.title) || id}${s.retrieved ? ` (read ${whenWords(str(s.retrieved))})` : ""}` : `${id}: this run does not list this source`;
        return (
          <span key={`${id}|${i}`}>
            {i ? ", " : ""}
            {url
              ? <a href={url} target="_blank" rel="noopener noreferrer" title={title} className="text-accent underline decoration-rule underline-offset-2" data-source={id}>{id}</a>
              : <span title={title} className="cursor-help text-muted" data-source={id}>{id}</span>}
          </span>
        );
      })}
    </sup>
  );
}

const asText = (t: Text | string | null | undefined): Text => (typeof t === "string" ? { text: t, sources: [] } : { text: str(t?.text), sources: arr(t?.sources) });
function Fact({ t, ctx, className = "mb-3 max-w-4xl text-sm" }: { t: Text | string | null | undefined; ctx: Ctx; className?: string }) {
  const x = asText(t);
  if (!x.text) return null;
  return <p className={className}>{x.text}<Src ids={x.sources} ctx={ctx} /></p>;
}

/** One cell: its text as it is, or its placeholder. `company` and `field` name the PitchBook figure that answers a
 * cell the PitchBook stage fills. */
function CellView({ cell, ctx, company, field }: { cell: Cell | null | undefined; ctx: Ctx; company?: string; field?: string }) {
  if (isMissing(cell)) {
    if (cell.missing !== "pitchbook_pending") return <Gap words={PLACEHOLDER[cell.missing] ?? "not held"} why={str(cell.note) || "The report gives no reason."} kind={cell.missing} />;
    if (ctx.others && company && field && CELL_FACT[field]) {
      // every provider that holds this figure, each with its label; with none, the cell reads as it did
      const figures = ProviderCell({ held: ctx.held, company, fact: CELL_FACT[field] });
      if (figures) return figures;
    }
    if (!ctx.pb) return <Gap words={PB_PENDING} why={PB_PENDING_WHY} kind="pitchbook_pending" />;
    const fig = company && field ? pbFigureFor(pitchbookFor(ctx.pb, company), field) : null;
    if (!fig) return <Gap words="not in PitchBook's answer" why="PitchBook's answer holds no figure for this cell." kind="pitchbook_absent" />;
    return <span data-pb-figure={field}>{fig.label}: {fig.value}<PbTag ctx={ctx} /></span>;
  }
  const s = str(cell);
  return s ? <>{s}</> : <Gap words="not held" why="This run holds no value here." kind="not_held" />;
}

/** The PitchBook block of one company: pending until the answer is submitted, then every figure with its tag. */
function PbBlock({ name, ctx }: { name: string; ctx: Ctx }) {
  if (ctx.others) return <ProviderBlock name={name} held={ctx.held} asked={ctx.asked.has(nameKey(name))} />;
  if (!ctx.pb) {
    return ctx.asked.has(nameKey(name))
      ? <Gap words={PB_PENDING} why={PB_PENDING_WHY} kind="pitchbook_pending" />
      : <Gap words="not asked" why="This company is not among those asked of PitchBook." kind="pitchbook_not_asked" />;
  }
  const c = pitchbookFor(ctx.pb, name);
  if (!c) return <Gap words="not in PitchBook's answer" why="PitchBook's answer does not name this company." kind="pitchbook_absent" />;
  const figs = pbFigures(c);
  if (!c.found) return <Gap words="not found in PitchBook" why="PitchBook returned no company under this name." kind="pitchbook_not_found" />;
  if (!figs.length) return <Gap words="no PitchBook figure" why="PitchBook returned this company with no figure." kind="pitchbook_absent" />;
  return (
    <ul className="min-w-[14rem] space-y-0.5 text-xs" data-pb-block={name}>
      {figs.map((f) => <li key={f.id} data-pb-figure={f.id}><span className="text-muted">{f.label}:</span> {f.value}<PbTag ctx={ctx} /></li>)}
    </ul>
  );
}

function TrendChips({ ns, ctx }: { ns: number[] | null | undefined; ctx: Ctx }) {
  const list = arr(ns).filter((n) => typeof n === "number" && Number.isFinite(n));
  if (!list.length) return null;
  return (
    <span className="inline-flex flex-wrap gap-1 align-baseline" data-trend-chips="1">
      {list.map((n) => (
        <Link key={n} href={hrefOf(ctx.choice, { tab: "trends" }, `trend-${n}`)} className="border border-rule bg-white px-1 text-[10px] text-ink no-underline hover:border-accent" title={`Trend ${n}: open it in the Trends tab`}>Trend {n}</Link>
      ))}
    </span>
  );
}
function Chips({ words }: { words: string[] | null | undefined }) {
  const list = arr(words).map(str).filter(Boolean);
  if (!list.length) return null;
  return <span className="inline-flex flex-wrap gap-1">{list.map((w, i) => <span key={`${w}|${i}`} className="border border-rule bg-panel px-1 text-[10px] text-muted">{w}</span>)}</span>;
}
/** The confidence score: the number, and the one line that explains it, beside it. */
function Confidence({ n, note }: { n: number | null | undefined; note: string }) {
  if (typeof n !== "number" || !Number.isFinite(n)) return <Gap words="not scored" why={note || "This run holds no score here."} kind="not_held" />;
  return <span data-confidence="1"><span className="font-semibold tabular-nums">{num(n)}</span>{note ? <span className="ml-1.5 text-xs text-muted">{note}</span> : null}</span>;
}
function Nothing() {
  return <p className="text-sm text-muted" data-thesis-empty="1">{EMPTY_TAB}</p>;
}
function Table({ min, caption, head, children }: { min: number; caption?: string; head: ReactNode; children: ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm" style={{ minWidth: min }}>
        {caption ? <caption className="mb-1 caption-top text-left text-xs text-muted">{caption}</caption> : null}
        <thead><tr className={HEAD}>{head}</tr></thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}
const H2 = ({ children }: { children: ReactNode }) => <h3 className="mb-1 mt-5 border-b border-rule pb-0.5 font-serif text-base text-accent first:mt-0">{children}</h3>;
function Site({ url }: { url: unknown }) {
  const u = safeUrl(url);
  if (!u) return null;
  return <a href={u} target="_blank" rel="noopener noreferrer" className="ml-1.5 text-[11px] font-normal text-accent underline decoration-rule underline-offset-2">{new URL(u).hostname.replace(/^www\./, "")}</a>;
}

function Scope({ r, ctx }: { r: Report; ctx: Ctx }) {
  const s = r.scope;
  const chain = arr(s?.value_chain), excluded = arr(s?.excluded), defs = arr(s?.definitions);
  if (!asText(s?.definition).text && !chain.length && !excluded.length && !defs.length) return <Nothing />;
  return (
    <>
      <Fact t={s?.definition} ctx={ctx} className="mb-4 max-w-4xl text-base" />
      {chain.length ? <><H2>Value chain</H2>
        <Table min={520} head={<><th className={`${TH} pl-1`}>Stage</th><th className={TH}>What it is</th></>}>
          {chain.map((c, i) => { const t = asText(c?.what); return <tr key={i} className="border-b border-rule/70"><th scope="row" className={`${TD} whitespace-nowrap pl-1 text-left font-semibold`}>{str(c?.stage)}</th><td className={TD}>{t.text}<Src ids={t.sources} ctx={ctx} /></td></tr>; })}
        </Table></> : null}
      {defs.length ? <><H2>Definitions</H2>
        <dl className="max-w-4xl text-sm">
          {defs.map((d, i) => { const t = asText(d?.meaning); return <div key={i} className="border-b border-rule/70 py-1.5 sm:grid sm:grid-cols-[14rem_minmax(0,1fr)] sm:gap-3"><dt className="font-semibold">{str(d?.term)}</dt><dd>{t.text}<Src ids={t.sources} ctx={ctx} /></dd></div>; })}
        </dl></> : null}
      {excluded.length ? <><H2>Excluded</H2>
        <Table min={520} head={<><th className={`${TH} pl-1`}>Niche</th><th className={TH}>Why</th></>}>
          {excluded.map((e, i) => <tr key={i} className="border-b border-rule/70"><th scope="row" className={`${TD} pl-1 text-left font-semibold`}>{str(e?.niche)}</th><td className={TD}>{str(e?.why)}</td></tr>)}
        </Table></> : null}
    </>
  );
}

function Trends({ r, ctx }: { r: Report; ctx: Ctx }) {
  const trends = arr(r.trends);
  if (!trends.length) return <Nothing />;
  return (
    <>
      {trends.map((t, k) => {
        const chart = chartOf(t);
        const kind = t?.chart?.kind;
        const columns = arr(t?.table?.columns), rows = arr(t?.table?.rows).filter(Array.isArray);
        const n = typeof t?.n === "number" ? t.n : k + 1;
        return (
          <section key={k} id={`trend-${n}`} className="mb-8 scroll-mt-4" data-trend={n}>
            <h3 className="mb-1 border-b border-accent pb-0.5 font-serif text-lg text-accent">{n}. {str(t?.title)}<Src ids={t?.sources} ctx={ctx} /></h3>
            <Fact t={t?.fact} ctx={ctx} />
            {chart ? (
              <figure className="mb-3">
                <figcaption className="mb-1 text-xs text-muted">{chart.title}{chart.unit ? `, ${chart.unit}` : ""}</figcaption>
                <TrendChart data={chart} />
              </figure>
            ) : kind === "bar" || kind === "line" ? <p className="mb-3"><Gap words="no chart" why="No row of this trend's table holds a number to draw." kind="not_held" /></p> : null}
            {columns.length || rows.length ? (
              <Table min={Math.min(900, 160 * Math.max(columns.length, 2))} head={columns.map((c, i) => <th key={i} className={`${TH} ${i ? "" : "pl-1"}`}>{str(c)}</th>)}>
                {rows.map((row, i) => (
                  <tr key={i} className="border-b border-rule/70">
                    {row.map((c, j) => <td key={j} className={`${TD} tabular-nums ${j ? "" : "pl-1"}`}><CellView cell={c} ctx={ctx} /></td>)}
                  </tr>
                ))}
              </Table>
            ) : null}
          </section>
        );
      })}
    </>
  );
}

function Landscape({ r, ctx }: { r: Report; ctx: Ctx }) {
  const l = r.landscape;
  const cs = arr(l?.companies);
  if (!cs.length && !asText(l?.fact).text) return <Nothing />;
  return (
    <>
      <Fact t={l?.fact} ctx={ctx} />
      {cs.length ? (
        <Table min={ctx.pbColumn ? 1320 : 1080} caption={str(l?.rule)} head={<>
          <th className={`${TH} pl-1`}>Company</th><th className={TH}>Founders</th><th className={TH}>Stage</th><th className={TH}>Raised</th><th className={TH}>Location</th>
          <th className={TH}>Signal</th><th className={TH}>Why it is here</th><th className={TH}>Confidence</th>{ctx.pbColumn ? <th className={TH}>{ctx.others ? "Data providers" : "PitchBook"}</th> : null}
        </>}>
          {cs.map((c, i) => { const name = str(c?.name);
            return (
              <tr key={`${name}|${i}`} className="border-b border-rule/70" data-company={name}>
                <th scope="row" className={`${TD} max-w-[18rem] pl-1 text-left font-normal`}>
                  <span className="font-semibold">{name}</span><Src ids={c?.sources} ctx={ctx} /><Site url={c?.website} />
                  {str(c?.description) ? <span className="mt-0.5 block text-xs text-muted">{str(c?.description)}</span> : null}
                  {arr(c?.sourcing).length ? <span className="mt-1 block"><Chips words={c?.sourcing} /></span> : null}
                </th>
                <td className={TD}><CellView cell={c?.founders} ctx={ctx} company={name} field="founders" /></td>
                <td className={TD}><CellView cell={c?.stage} ctx={ctx} company={name} field="stage" /></td>
                <td className={`${TD} tabular-nums`}><CellView cell={c?.raised} ctx={ctx} company={name} field="raised" /></td>
                <td className={TD}><CellView cell={c?.location} ctx={ctx} company={name} field="location" /></td>
                <td className={`${TD} max-w-[14rem] text-xs`}>{str(c?.signal)}</td>
                <td className={`${TD} max-w-[16rem] text-xs`} data-reason="1">{str(c?.reason)}{arr(c?.trends).length ? <span className="mt-1 block"><TrendChips ns={c?.trends} ctx={ctx} /></span> : null}</td>
                <td className={`${TD} max-w-[14rem]`}><Confidence n={c?.confidence} note={str(c?.confidence_note)} /></td>
                {ctx.pbColumn ? <td className={TD}><PbBlock name={name} ctx={ctx} /></td> : null}
              </tr>
            ); })}
        </Table>
      ) : null}
    </>
  );
}

function Funnel({ r, ctx }: { r: Report; ctx: Ctx }) {
  const stages = arr(r.funnel?.stages).filter((s) => s && typeof s.n === "number" && Number.isFinite(s.n)).map((s) => ({ id: str(s.id), label: str(s.label) || str(s.id), n: s.n }));
  const cs = arr(r.funnel?.companies);
  const more = arr(ctx.pb?.additional_companies).filter((c) => c?.found);
  const found = ctx.held.filter((h) => h.provider !== "pitchbook");
  if (!stages.length && !cs.length && !more.length && !found.length) return <Nothing />;
  const label = (id: string) => stages.find((s) => s.id === id)?.label ?? id;
  return (
    <>
      {stages.length ? <figure className="mb-5 max-w-3xl"><figcaption className="mb-1 text-xs text-muted">Companies at each stage of the funnel</figcaption><FunnelChart stages={stages} /></figure> : null}
      {cs.length ? (
        <Table min={ctx.pbColumn ? 1080 : 820} head={<>
          <th className={`${TH} pl-1`}>Company</th><th className={TH}>Reached</th><th className={TH}>Stopped</th><th className={TH}>Score</th><th className={TH}>Sourcing</th>{ctx.pbColumn ? <th className={TH}>{ctx.others ? "Data providers" : "PitchBook"}</th> : null}
        </>}>
          {cs.map((c, i) => { const name = str(c?.name);
            return (
              <tr key={`${name}|${i}`} className="border-b border-rule/70" data-company={name}>
                <th scope="row" className={`${TD} pl-1 text-left font-semibold`}>{name}<Src ids={c?.sources} ctx={ctx} /></th>
                <td className={`${TD} whitespace-nowrap`}>{label(str(c?.reached))}</td>
                <td className={`${TD} max-w-[22rem] text-xs`}>{str(c?.stopped)}</td>
                <td className={`${TD} tabular-nums`}>{typeof c?.score === "number" && Number.isFinite(c.score) ? <span className="font-semibold" data-score="1">{num(c.score)}</span> : <Gap words="not scored" why="This run holds no score for this company." kind="not_held" />}</td>
                <td className={TD}><Chips words={c?.sourcing} /></td>
                {ctx.pbColumn ? <td className={TD}><PbBlock name={name} ctx={ctx} /></td> : null}
              </tr>
            ); })}
        </Table>
      ) : null}
      {more.length ? (
        <section className="mt-6" data-pb-additional="1">
          <H2>Found by PitchBook<PbTag ctx={ctx} /></H2>
          <ul className="grid gap-3 text-sm lg:grid-cols-2">
            {more.map((c, i) => (
              <li key={`${str(c?.name)}|${i}`} className="border border-rule bg-panel px-2 py-1.5" data-company={str(c?.name)}>
                <span className="font-semibold">{str(c?.name)}</span><PbTag ctx={ctx} />
                {str(c?.why) ? <span className="mt-0.5 block text-xs">{str(c?.why)}<PbTag ctx={ctx} /></span> : null}
                <ul className="mt-1 space-y-0.5 text-xs">
                  {pbFigures(c).map((f) => <li key={f.id} data-pb-figure={f.id}><span className="text-muted">{f.label}:</span> {f.value}<PbTag ctx={ctx} /></li>)}
                </ul>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {found.map((h) => <ProviderFound key={h.provider} h={h} heading={(children) => <H2>{children}</H2>} />)}
    </>
  );
}

function Pipeline({ r, ctx }: { r: Report; ctx: Ctx }) {
  const cs = arr(r.pipeline?.companies);
  if (!cs.length) return <Nothing />;
  return (
    <Table min={ctx.pbColumn ? 1240 : 980} head={<>
      <th className={`${TH} pl-1`}>Company</th><th className={TH}>Founders</th><th className={TH}>Signal</th><th className={TH}>Access</th><th className={TH} title="Total addressable market">Market size (TAM)</th>
      <th className={TH}>Trends</th><th className={TH}>Confidence</th>{ctx.pbColumn ? <th className={TH}>{ctx.others ? "Data providers" : "PitchBook"}</th> : null}
    </>}>
      {cs.map((c, i) => { const name = str(c?.name);
        return (
          <tr key={`${name}|${i}`} className="border-b border-rule/70" data-company={name}>
            <th scope="row" className={`${TD} pl-1 text-left font-semibold`}>{name}<Src ids={c?.sources} ctx={ctx} /></th>
            <td className={TD}><CellView cell={c?.founders} ctx={ctx} company={name} field="founders" /></td>
            <td className={`${TD} max-w-[16rem] text-xs`}>{str(c?.signal)}</td>
            <td className={`${TD} max-w-[14rem] text-xs`}><CellView cell={c?.access} ctx={ctx} company={name} field="access" /></td>
            <td className={`${TD} max-w-[14rem] text-xs tabular-nums`}><CellView cell={c?.tam} ctx={ctx} company={name} field="tam" /></td>
            <td className={TD}><TrendChips ns={c?.trends} ctx={ctx} /></td>
            <td className={`${TD} max-w-[14rem]`}><Confidence n={c?.confidence} note={ctx.notes.get(nameKey(name)) ?? ""} /></td>
            {ctx.pbColumn ? <td className={TD}><PbBlock name={name} ctx={ctx} /></td> : null}
          </tr>
        ); })}
    </Table>
  );
}

function Capital({ r, ctx }: { r: Report; ctx: Ctx }) {
  const rounds = arr(r.capital?.rounds);
  if (!rounds.length && !asText(r.capital?.fact).text) return <Nothing />;
  return (
    <>
      <Fact t={r.capital?.fact} ctx={ctx} />
      {rounds.length ? (
        <Table min={860} head={<><th className={`${TH} pl-1`}>Date</th><th className={TH}>Company</th><th className={TH}>Round</th><th className={TH}>Amount</th><th className={TH}>Investors</th></>}>
          {rounds.map((x, i) => (
            <tr key={i} className="border-b border-rule/70">
              <td className={`${TD} whitespace-nowrap pl-1 tabular-nums`}><CellView cell={x?.date} ctx={ctx} /></td>
              <th scope="row" className={`${TD} text-left font-semibold`}>{str(x?.company)}<Src ids={x?.sources} ctx={ctx} /></th>
              <td className={TD}>{str(x?.kind)}</td>
              <td className={`${TD} tabular-nums`}><CellView cell={x?.amount} ctx={ctx} /></td>
              <td className={`${TD} max-w-[26rem] text-xs`}><CellView cell={x?.investors} ctx={ctx} /></td>
            </tr>
          ))}
        </Table>
      ) : null}
    </>
  );
}

function Incumbents({ r, ctx }: { r: Report; ctx: Ctx }) {
  const ps = arr(r.incumbents?.players);
  if (!ps.length && !asText(r.incumbents?.fact).text) return <Nothing />;
  return (
    <>
      <Fact t={r.incumbents?.fact} ctx={ctx} />
      {ps.length ? (
        <Table min={820} head={<><th className={`${TH} pl-1`}>Company</th><th className={TH}>Kind</th><th className={TH}>Measure</th><th className={TH}>Value</th><th className={TH}>As of</th></>}>
          {ps.map((p, i) => (
            <tr key={i} className="border-b border-rule/70">
              <th scope="row" className={`${TD} pl-1 text-left font-semibold`}>{str(p?.name)}{str(p?.ticker) ? <span className="ml-1.5 font-mono text-[11px] font-normal text-muted">{str(p?.ticker)}</span> : null}<Src ids={p?.sources} ctx={ctx} /></th>
              <td className={TD}>{str(p?.kind)}</td>
              <td className={TD}>{str(p?.metric)}</td>
              <td className={`${TD} tabular-nums`}><CellView cell={p?.value} ctx={ctx} /></td>
              <td className={`${TD} whitespace-nowrap text-xs text-muted`}>{whenWords(str(p?.as_of))}</td>
            </tr>
          ))}
        </Table>
      ) : null}
    </>
  );
}

function Risks({ r, ctx }: { r: Report; ctx: Ctx }) {
  const rs = arr(r.risks);
  if (!rs.length) return <Nothing />;
  return (
    <Table min={820} head={<><th className={`${TH} pl-1`}>Risk</th><th className={TH}>How</th><th className={TH}>Not known</th></>}>
      {rs.map((x, i) => (
        <tr key={i} className="border-b border-rule/70">
          <th scope="row" className={`${TD} max-w-[18rem] pl-1 text-left font-semibold`}>{str(x?.risk)}<Src ids={x?.sources} ctx={ctx} /></th>
          <td className={`${TD} max-w-[26rem]`}>{str(x?.how)}</td>
          <td className={`${TD} max-w-[22rem] text-muted`}>{str(x?.not_known)}</td>
        </tr>
      ))}
    </Table>
  );
}

function Policy({ r }: { r: Report }) {
  const actions = arr(r.policy?.actions);
  const fact = str(r.policy?.fact);
  if (!actions.length && !fact) return <Nothing />;
  return (
    <>
      {fact ? <p className="mb-3 max-w-4xl text-sm">{fact}</p> : null}
      {actions.length ? (
        <Table min={900} head={<><th className={`${TH} pl-1`}>Date</th><th className={TH}>Agency</th><th className={TH}>Action</th><th className={TH}>Why</th><th className={TH}>Read</th></>}>
          {actions.map((a, i) => { const url = safeUrl(a?.url);
            return (
              <tr key={i} className="border-b border-rule/70">
                <td className={`${TD} whitespace-nowrap pl-1 tabular-nums`}>{whenWords(str(a?.date))}</td>
                <td className={TD}>{str(a?.agency)}</td>
                <th scope="row" className={`${TD} max-w-[22rem] text-left font-normal`}>{url ? <a href={url} target="_blank" rel="noopener noreferrer" className="text-accent underline decoration-rule underline-offset-2" title="Open the action at its publisher">{str(a?.title)}</a> : str(a?.title)}</th>
                <td className={`${TD} max-w-[20rem] text-xs`}>{str(a?.why)}</td>
                <td className={`${TD} max-w-[20rem] text-xs`}>{str(a?.read)}</td>
              </tr>
            ); })}
        </Table>
      ) : null}
    </>
  );
}

export function ReportTabs({ run, choice }: { run: Run; choice: Choice }) {
  const r = run.report as Report;
  const pb = run.pitchbook && typeof run.pitchbook === "object" ? run.pitchbook : null;
  const held = heldOf(run);
  const others = held.some((h) => h.provider !== "pitchbook");
  const ctx: Ctx = {
    choice, pb, held, others,
    sources: new Map(arr(r.sources).filter((s) => s && typeof s.id === "string").map((s) => [s.id, s])),
    asked: new Set(arr(run.pitchbook_request?.companies).map((c) => nameKey(c?.name)).filter(Boolean)),
    pbColumn: !!pb || !!run.pitchbook_request || others,
    notes: new Map(arr(r.landscape?.companies).filter((c) => c && str(c.confidence_note)).map((c) => [nameKey(c.name), str(c.confidence_note)])),
  };
  const body: Record<TabId, ReactNode> = {
    scope: <Scope r={r} ctx={ctx} />, trends: <Trends r={r} ctx={ctx} />, landscape: <Landscape r={r} ctx={ctx} />, funnel: <Funnel r={r} ctx={ctx} />,
    pipeline: <Pipeline r={r} ctx={ctx} />, capital: <Capital r={r} ctx={ctx} />, incumbents: <Incumbents r={r} ctx={ctx} />, risks: <Risks r={r} ctx={ctx} />, policy: <Policy r={r} />,
  };
  return (
    <section aria-label="Report" data-thesis-report={run.run_id}>
      <nav className="mb-4 flex flex-wrap gap-1 border-b border-accent text-xs" aria-label="The parts of the report" data-thesis-tabs="1">
        {TABS.map((t) => { const on = t.id === choice.tab;
          return <Link key={t.id} href={hrefOf(choice, { tab: t.id })} scroll={false} aria-current={on ? "page" : undefined} data-tab={t.id} style={{ color: on ? "#fff" : "var(--color-ink)" }} className={`-mb-px border px-2 py-1 no-underline ${on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{t.label}</Link>; })}
      </nav>
      <div data-thesis-tab={choice.tab}>
        <h2 className="mb-3 font-serif text-xl text-accent">{TABS.find((t) => t.id === choice.tab)?.label}</h2>
        {body[choice.tab]}
      </div>
    </section>
  );
}
