import type { Metadata } from "next";
import type { ReactNode } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import duplicates from "@/data/deal_duplicates.json";
import { deals } from "@/lib/data";
import {
  GRIDS, GROUPS, NOT_STATED, TYPE_LABEL, counts, fold, hrefOf, inputsOf, monthWords, months, parties, select, selectionWords, summary, technologies, toDeal, usd, whole,
  type Deal, type DealRow, type Inputs, type Pair,
} from "@/lib/deals2";
import { attempt } from "@/lib/supabase";

// Session 113: the deals tracker, version 2, in the battery page's layout: the choices in a fog beige panel on the
// left, the answer on the right. It reads the deals already extracted (energy_deals, warehouse/deals/extract.py) and
// nothing else: no model is called and no figure is computed beyond counts and sums of what the stories state. A figure
// a story does not give is "not stated", never an estimate. Rows the register warehouse/deals/duplicates.csv names as
// one deal are shown once (data/deal_duplicates.json). The choices live in the address and the form is a plain GET
// form, so the page works without JavaScript. The older tracker (/deals) is as it was.
export const metadata: Metadata = { title: "The deals tracker", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const PAIRS = (duplicates as unknown as { pairs: Pair[] }).pairs;
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const none = <span className="text-muted">{NOT_STATED}</span>;
const shortMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });

/** Deals by month: one bar a month from the first deal held to the last, the count written above it. */
function MonthBars({ ms }: { ms: { month: string; n: number }[] }) {
  const W = 760, H = 260, L = 40, R = 10, top = 22, bot = 40;
  const hi = Math.max(1, ...ms.map((m) => m.n));
  const step = [1, 2, 5, 10, 20, 25, 50, 100, 200].find((s) => hi / s <= 5) ?? 500;
  const max = Math.ceil(hi / step) * step;
  const y = (v: number) => top + ((max - v) / max) * (H - top - bot);
  const bw = (W - L - R) / ms.length;
  const ticks: number[] = [];
  for (let t = 0; t <= max; t += step) ticks.push(t);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Deals by month, the number of deals dated in each month">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "#2E2D29" : "#D9D2C3"} strokeWidth={t === 0 ? 1 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="#6B665E">{t}</text>
        </g>
      ))}
      {ms.map((m, i) => {
        const x0 = L + i * bw + bw * 0.15, w = bw * 0.7;
        return (
          <g key={m.month} data-deals-month={m.month} data-deals-n={m.n}>
            {m.n ? <rect x={x0} width={w} y={y(m.n)} height={Math.max(0.5, y(0) - y(m.n))} fill="#8C1515" /> : null}
            <text x={x0 + w / 2} y={y(m.n) - 5} textAnchor="middle" fontSize="10" fill={m.n ? "#2E2D29" : "#6B665E"}>{m.n}</text>
            {m.month.endsWith("-01") || i === 0 || i % 3 === 0 ? <text x={x0 + w / 2} y={H - bot + 15} textAnchor="middle" fontSize="10" fill="#2E2D29">{shortMonth(m.month)}</text> : null}
            <title>{`${monthWords(m.month)}: ${m.n} ${m.n === 1 ? "deal" : "deals"}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

function Parties({ d }: { d: Deal }) {
  const lines: [string, string][] = [];
  if (d.buyer) lines.push(["Buyer", d.buyer]);
  if (d.seller) lines.push(["Seller", d.seller]);
  if (d.others.length) lines.push([d.buyer || d.seller ? "Also" : "Parties", d.others.join(", ")]);
  if (!lines.length) return none;
  return <>{lines.map(([k, v]) => <div key={k}><span className="text-xs text-muted">{k}</span> {v}</div>)}</>;
}

function Price({ d }: { d: Deal }) {
  if (d.price !== null) return <>{whole(d.price)} USD/MWh</>;
  if (d.priceOther) return <>{whole(d.priceOther.value)} {d.priceOther.unit}<div className="text-xs text-muted">as extracted; not a price per MWh</div></>;
  return none;
}

function Sources({ d }: { d: Deal }) {
  return (
    <>
      {d.links.map((u, i) => (
        <span key={u}>{i ? ", " : ""}<a href={u} rel="noopener noreferrer" target="_blank" className="underline">{i === 0 ? d.source || "story" : `story ${i + 1}`}</a></span>
      ))}
      {d.folded.length ? <div className="text-xs text-muted">{d.folded.length + 1} rows of the table, one deal</div> : null}
    </>
  );
}

function Choices({ x, all }: { x: Inputs; all: Deal[] }) {
  const c = counts(all);
  const years = [...new Set(all.map((d) => d.year))].sort().reverse();
  const views: { id: Inputs["view"]; label: string }[] = [{ id: "", label: "All deals" }, { id: "storage", label: "Storage only" }, { id: "ai", label: "AI power" }];
  const n = (f: (d: Deal) => boolean) => all.filter(f).length;
  return (
    <form method="get" action="/deals/v2" className="space-y-4 text-sm">
      <div>
        <div className="mb-1 font-semibold" id="view-label">One click</div>
        <div className="grid grid-cols-3 border border-accent" role="group" aria-labelledby="view-label">
          {views.map((v, i) => (
            <Link key={v.id || "all"} href={hrefOf(x, { view: v.id })} scroll={false} aria-current={x.view === v.id ? "true" : undefined} data-view={v.id || "all"}
              style={x.view === v.id ? { color: "#fff" } : undefined}
              className={`px-1 py-1.5 text-center no-underline ${i ? "border-l border-accent" : ""} ${x.view === v.id ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
              {v.label}
            </Link>
          ))}
        </div>
        <input type="hidden" name="view" value={x.view} />
      </div>
      <label className="block"><span className="mb-1 block font-semibold">Deal type</span>
        <select name="type" defaultValue={x.type} className={field}>
          <option value="">All types ({whole(c.deals)})</option>
          {GROUPS.map((g) => <option key={g.id} value={g.id}>{g.label} ({whole(c.byGroup[g.id])})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Technology, as the story states it</span>
        <select name="tech" defaultValue={x.tech} className={field}>
          <option value="">All</option>
          {technologies(all).map((t) => <option key={t.value} value={t.value}>{t.value} ({whole(t.n)})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Grid, by the state the story names</span>
        <select name="grid" defaultValue={x.grid} className={field}>
          <option value="">All</option>
          {GRIDS.map((g) => <option key={g} value={g}>{g} ({whole(n((d) => d.grid === g))})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Counterparty</span>
        <input name="party" type="text" defaultValue={x.party} list="deal-parties" maxLength={80} placeholder="a name, or part of one" className={field} />
        <datalist id="deal-parties">{parties(all).map((p) => <option key={p.name} value={p.name}>{`${p.n} deals`}</option>)}</datalist>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Year</span>
        <select name="year" defaultValue={x.year} className={field}>
          <option value="">All</option>
          {years.map((y) => <option key={y} value={y}>{y} ({whole(n((d) => d.year === y))})</option>)}
        </select>
      </label>
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
        <Link href="/deals/v2" scroll={false} className="text-xs">Show every deal</Link>
      </div>
    </form>
  );
}

export default async function DealsTwo({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const read = await attempt(deals);
  const rows = read.ok ? (read.data as unknown as DealRow[]) : [];
  const all = fold(rows.map(toDeal), PAIRS);
  const x = inputsOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])), all);
  const shown = select(all, x);
  const c = counts(shown), ca = counts(all);
  const words = selectionWords(x);
  const folded = PAIRS.filter((p) => p.ruling === "fold" && all.some((d) => d.folded.includes(p.duplicate)));
  const doubtful = PAIRS.filter((p) => p.ruling === "doubtful");
  const otherTypes = Object.entries(all.filter((d) => d.group === "other").reduce<Record<string, number>>((a, d) => { a[d.type] = (a[d.type] ?? 0) + 1; return a; }, {})).sort((a, b) => b[1] - a[1]);
  const withState = all.filter((d) => d.state).length, withGrid = all.filter((d) => d.grid).length;
  const cell = "px-3 py-1.5 align-top";

  return (
    <ToolPage>
      <ToolHeader title="The deals tracker" crumb={<>Version 2, in review. The tracker as it was: <Link href="/deals" className="underline">/deals</Link></>}
        lead={<>Power purchases, offtakes, financings and acquisitions in energy, as the news reported them: who, what technology, how large and at what price, where a story says so, each with a link to the story. <strong>These are deals reported in the news the ERW reads, not a complete record of the market.</strong></>} />
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Your selection" note={<>The counts in brackets are of every deal held. Grid is the grid operator that serves most of the state a story names; {whole(withState)} of the {whole(ca.deals)} deals name a US state, and {whole(withGrid)} of those states have one grid.</>}>
            <Choices key={hrefOf(x)} x={x} all={all} />
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!read.ok ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
          ) : !all.length ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No deal is held in the live set.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-deals-summary="1">{summary(all, shown, x)}</p>

              <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-deals-stated="1">
                <strong>Most stories give no size and no price.</strong> Of the <span data-deals-all="count">{whole(ca.deals)}</span> deals held,{" "}
                <span data-deals-all="with_mw">{whole(ca.withMw)}</span> state a size in MW and <span data-deals-all="with_price">{whole(ca.withPrice)}</span> state a price in US dollars per MWh
                {ca.withOtherPrice ? <> (<span data-deals-all="with_other_price">{whole(ca.withOtherPrice)}</span> more {ca.withOtherPrice === 1 ? "carries a figure" : "carry figures"} in another unit, shown as extracted)</> : null};{" "}
                <span data-deals-all="with_dollars">{whole(ca.withDollars)}</span> state a value in US dollars. Where a story does not give a figure the table says &quot;{NOT_STATED}&quot;. Nothing is estimated.
              </p>

              <HeadlineRow>
                <HeadlineNumber label={words ? "Deals in this selection" : "Deals held"} value={<span data-deals="count">{whole(c.deals)}</span>}
                  note={words ? <>of {whole(ca.deals)} held: {words}</> : <>{monthWords(all[all.length - 1].month)} to {monthWords(all[0].month)}</>} />
                <HeadlineNumber label="Disclosed megawatts" value={c.withMw ? <span data-deals="mw">{whole(c.mw)}</span> : <span className="text-muted" data-deals="mw">{NOT_STATED}</span>} unit={c.withMw ? "MW" : undefined}
                  note={<>the sum over the <span data-deals="with_mw">{whole(c.withMw)}</span> {c.withMw === 1 ? "deal that states" : "deals that state"} a size; the other {whole(c.deals - c.withMw)} are not counted as zero, they are not known</>} />
                <HeadlineNumber label="State a price" value={<span data-deals="with_price">{whole(c.withPrice)}</span>} unit={`of ${whole(c.deals)}`}
                  note={<>in US dollars per MWh. <span data-deals="with_dollars">{whole(c.withDollars)}</span> state a value in US dollars{c.withDollars ? <>, USD {usd(c.dollars)} in all</> : null}.</>} />
              </HeadlineRow>

              <ChartFrame title="Deals by month"
                note={<>{words ? <>This selection ({words}). </> : null}By the deal&apos;s date: the announced date where a story states it, else the day the first story was published (UTC). A month with 0 has no deal dated in it. Deals are extracted only from stories the ERW has scored: the stories of June to September 2025 are held but not scored, so those months are empty for that reason, not because nothing was reported. The ERW has scored the news daily since 23 September 2026; earlier months come from older stories scored afterwards and are thinner.</>}>
                <MonthBars ms={months(all, shown)} />
              </ChartFrame>

              <ToolSection title={words ? `The ${whole(c.deals)} deals in this selection` : `Every deal held (${whole(c.deals)})`} id="deals"
                note={<>Newest first. A deal reported by several stories is one row, with every story linked; the first link is the outlet named in the table. Many links open through Google News, which is where the ERW found the story.</>}>
                {shown.length ? (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 860 }}>
                      <caption className="sr-only">Deals in this selection</caption>
                      <thead>
                        <tr className="bg-accent text-white">
                          {["Date", "Deal", "Parties", "Technology", "Size", "Price", "Value, USD", "Source"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {shown.map((d) => (
                          <tr key={d.id} className="border-b border-rule" data-deal={d.id}>
                            <th scope="row" className={`${cell} whitespace-nowrap font-normal tabular-nums`}>{d.date}</th>
                            <td className={cell}>
                              {TYPE_LABEL[d.type] ?? (d.type || NOT_STATED)}
                              {d.asset ? <div className="text-xs text-muted">{d.asset}</div> : null}
                              {d.status || d.ai ? <div className="text-xs text-muted">{[d.status, d.ai ? "AI power" : ""].filter(Boolean).join("; ")}</div> : null}
                            </td>
                            <td className={cell}><Parties d={d} /></td>
                            <td className={cell}>{d.technology || none}{d.state ? <div className="text-xs text-muted">{d.state}{d.grid ? `, ${d.grid}` : ""}</div> : null}</td>
                            <td className={`${cell} whitespace-nowrap tabular-nums`} data-deal-mw={d.mw ?? ""}>{d.mw !== null ? <>{whole(d.mw)} MW{d.mwh !== null ? <div className="text-xs text-muted">{whole(d.mwh)} MWh</div> : null}</> : d.mwh !== null ? <>{whole(d.mwh)} MWh</> : none}</td>
                            <td className={cell}><Price d={d} /></td>
                            <td className={`${cell} whitespace-nowrap tabular-nums`}>{d.dollars !== null ? usd(d.dollars) : none}</td>
                            <td className={cell}><Sources d={d} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">
                    No deal held matches this selection.{x.type === "tolling" ? " The extraction has no tolling type, and no deal held names a tolling agreement, so this choice is empty until one is extracted." : ""} <Link href="/deals/v2" className="underline">Show every deal</Link>.
                  </p>
                )}
              </ToolSection>

              <div className="mb-8 border-t border-rule">
                <Fold title="How a deal gets here">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>From the news the ERW reads.</strong> A model reads the title and summary of each scored story about a transaction and extracts the deal: its type, parties, asset, technology, place, size, value, price and term. A deal no story in the ERW&apos;s feeds reported is not here, and a figure a story left out of its title and summary is not here either.</li>
                    <li><strong>Every number was checked against the text.</strong> A number is kept only if the words it was read from are in the story and parse to the same value; otherwise it is left empty, which this page shows as &quot;{NOT_STATED}&quot;. A state, a country and a status are kept only when the story states them.</li>
                    <li><strong>Deal types.</strong> The extraction sorts deals into fourteen types. This page keeps four of them by name (power purchase, offtake, project finance, acquisition) and gathers the rest under Other: {otherTypes.map(([t, k], i) => <span key={t}>{i ? ", " : ""}{(TYPE_LABEL[t] ?? t).toLowerCase()} {whole(k)}</span>)}. <strong>Tolling is not one of the fourteen,</strong> and no deal held names a tolling agreement, so that choice is empty.</li>
                    <li><strong>Storage only</strong> shows the deals whose technology names a battery or storage, or whose asset names a battery, energy storage or a BESS. It is a match on words: a battery plant or a battery-swap network for vehicles matches too, and the table shows what each is.</li>
                    <li><strong>AI power</strong> shows the deals the model tagged as power or infrastructure for AI or datacenters.</li>
                    <li><strong>Grid</strong> is read from the state, for the states one grid operator mostly serves (Texas is counted as ERCOT, though parts of it are in SPP and MISO). A state split between grids or outside all seven is not assigned. The table holds no point of delivery.</li>
                  </ul>
                </Fold>
                <Fold title={`Rows that were one deal (${folded.length} folded, ${doubtful.length} doubtful)`}>
                  <p className="mb-2 max-w-3xl">The extraction is asked to recognise a deal it has already extracted, and some slip through. The table <code className="font-mono">energy_deals</code> holds {whole(rows.length)} rows; the pairs below were found to be one deal each and are shown once here, with the story links of both rows, so this page counts {whole(ca.deals)} deals. The table itself is as the extraction left it.</p>
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5" data-deals-folded={folded.length}>
                    {folded.map((p) => <li key={p.duplicate}><strong>Shown once.</strong> {p.reason}</li>)}
                    {doubtful.map((p) => <li key={p.duplicate}><strong>Doubtful, shown as two.</strong> {p.reason}</li>)}
                  </ul>
                </Fold>
                <Fold title="What this does not tell you">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>How many deals were struck.</strong> This is what a set of news feeds reported and a model extracted. Most contracts are never announced, and the months before the ERW began scoring the news daily are thin.</li>
                    <li><strong>What power sells for.</strong> No deal held states a price per MWh. Contract prices as sellers file them with FERC are on <Link href="/contracts" className="underline">the power contracts page</Link>.</li>
                    <li><strong>A market total.</strong> The megawatts are the sum over the few deals that state a size, of every type together: a purchase of output, a sale of a portfolio and an equipment order are different things, and the table shows which is which.</li>
                    <li><strong>Whether a deal closed.</strong> The status is the one the story states (announced, signed, closed, rumored, cancelled), on the day of the story.</li>
                  </ul>
                </Fold>
              </div>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={["energy_deals"]} note={<>Extracted by <code className="font-mono">warehouse/deals/extract.py</code> from the stories of <code className="font-mono">news_stories</code>; the sentence each deal was read from is outlet text and stays in the internal table. Duplicates: <code className="font-mono">warehouse/deals/duplicates.csv</code>. This page is in review.</>} />
    </ToolPage>
  );
}
