import { SiteLink as Link } from "@/components/SiteLink";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { ChartFrame, SourceLine, ToolHeader } from "@/components/tool/ToolPage";
import { HeldRows } from "@/components/tool/HeldRows";
import { BarsHover } from "@/components/tool/BarsHover";   // session 1853 (deals faults row 8): the brand's hover card on the two charts by quarter
import duplicates from "@/data/deal_duplicates.json";
import { deals } from "@/lib/data";
import { fold, toDeal, whole, type DealRow, type Pair } from "@/lib/deals2";
import { GROUPS, aiShare, mwByQuarter, pricePoints, topParties } from "@/lib/dealsai";
import { isLicenseReason } from "@/lib/license";
import { attempt } from "@/lib/supabase";
import { DealsHeld } from "../Held";

// Session 2241 (chain 156): the deals' four charts (/deals?view=charts, in review, under the tracker's tab). The colors
// are the brand's five series in order (docs/brand.md, "Chart series"); fills that touch are parted by a 1 px white
// line and each series is named in the legend; every mark's hover gives its values (an SVG title); every figure's key
// is on its mark (data-check) and in the table under each chart, and scripts/check_deals.py recomputes it.

const PAIRS = (duplicates as unknown as { pairs: Pair[] }).pairs;
const W = 760;
const T = "var(--color-ink)", M = "var(--color-muted)";

function Legend({ items }: { items: [string, string][] }) {
  return (
    <ul className="mb-2 flex flex-wrap gap-x-4 gap-y-1 text-xs" aria-label="Legend">
      {items.map(([label, color]) => (
        <li key={label} className="flex items-center gap-1"><span aria-hidden="true" className="inline-block h-3 w-3" style={{ background: color }} />{label}</li>
      ))}
    </ul>
  );
}

function Axis({ x0, x1, y, ticks }: { x0: number; x1: number; y: (v: number) => number; ticks: number[] }) {
  return (
    <g aria-hidden="true">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x0} x2={x1} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth="1" />
          <text x={x0 - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill={M}>{whole(t)}</text>
        </g>
      ))}
    </g>
  );
}

const nice = (hi: number) => {
  if (hi <= 0) return [0];
  const step = 10 ** Math.floor(Math.log10(hi / 4));
  const s = [1, 2, 5, 10].map((m) => m * step).find((x) => hi / x <= 5) ?? step * 10;
  return Array.from({ length: Math.floor(hi / s) + 1 }, (_, i) => i * s);
};

function MwChart({ stacks }: { stacks: ReturnType<typeof mwByQuarter> }) {
  const L = 56, R = 12, top = 10, H = 260, B = 24;
  const ticks = nice(Math.max(1, ...stacks.map((s) => s.total)));
  const hi = Math.max(ticks[ticks.length - 1], 1);
  const y = (v: number) => top + (1 - v / hi) * (H - top - B);
  const bw = (W - L - R) / Math.max(1, stacks.length);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="MW stated by quarter, stacked by kind of supply" data-chart="mw">
      <Axis x0={L} x1={W - R} y={y} ticks={ticks} />
      {stacks.map((s, i) => {
        let base = 0;
        const x = L + i * bw + bw * 0.15, w = bw * 0.7;
        return (
          <g key={s.quarter} data-chart-quarter={s.quarter}>
            {s.parts.filter((p) => p.mw > 0).map((p) => {
              const g = GROUPS.find(([id]) => id === p.group)!;
              const y0 = y(base), y1 = y(base + p.mw);
              base += p.mw;
              return (
                <rect key={p.group} x={x} y={y1} width={w} height={Math.max(0.5, y0 - y1)} fill={g[2]} stroke="#FFFFFF" strokeWidth="1"
                  data-check={`deals|chart_mw|${s.quarter}|${p.group}`} data-value={p.mw}>
                  <title>{`${s.quarter}, ${g[1]}: ${whole(p.mw)} MW from ${p.deals} deals that state MW`}</title>
                </rect>
              );
            })}
            <rect x={L + i * bw} y={top} width={bw} height={H - top - B} fill="transparent">
              <title>{`${s.quarter}: ${whole(s.total)} MW stated; ${s.without} deals of the quarter state no MW`}</title>
            </rect>
            <text x={x + w / 2} y={H - 8} textAnchor="middle" fontSize="11" fill={M}>{s.quarter}</text>
          </g>
        );
      })}
    </svg>
  );
}

function PriceChart({ pts }: { pts: ReturnType<typeof pricePoints> }) {
  const techs = [...new Set(pts.map((p) => p.tech))];
  const colors = ["var(--chart-ink)", "var(--color-accent)", "var(--chart-blue)", "var(--chart-grey)", "var(--chart-light)"];
  const L = 56, R = 12, top = 10, H = 240, B = 24;
  const ticks = nice(Math.max(1, ...pts.map((p) => p.price)));
  const hi = ticks[ticks.length - 1] || 1;
  const t0 = Date.parse(pts[0].date), t1 = Math.max(Date.parse(pts[pts.length - 1].date), t0 + 86400000);
  const x = (d: string) => L + ((Date.parse(d) - t0) / (t1 - t0)) * (W - L - R);
  const y = (v: number) => top + (1 - v / hi) * (H - top - B);
  return (
    <>
      <Legend items={techs.map((t, i) => [t, colors[i % colors.length]])} />
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Prices stated per MWh over time, by technology" data-chart="price">
        <Axis x0={L} x1={W - R} y={y} ticks={ticks} />
        {pts.map((p) => (
          <circle key={p.id} cx={x(p.date)} cy={y(p.price)} r="5" fill={colors[techs.indexOf(p.tech) % colors.length]} stroke="#FFFFFF" strokeWidth="2"
            data-check={`deals|chart_price|${p.id}|price`} data-value={p.price}>
            <title>{`${p.date}, ${p.tech}: USD ${whole(p.price)} per MWh (${p.label})`}</title>
          </circle>
        ))}
        <text x={L} y={H - 6} fontSize="11" fill={M}>{pts[0].date}</text>
        <text x={W - R} y={H - 6} textAnchor="end" fontSize="11" fill={M}>{pts[pts.length - 1].date}</text>
      </svg>
    </>
  );
}

function ShareChart({ shares }: { shares: ReturnType<typeof aiShare> }) {
  const L = 56, R = 12, top = 10, H = 220, B = 24;
  const y = (v: number) => top + (1 - v / 100) * (H - top - B);
  const bw = (W - L - R) / Math.max(1, shares.length);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="The AI-power deals' share of the MW stated, by quarter" data-chart="ai">
      <Axis x0={L} x1={W - R} y={y} ticks={[0, 25, 50, 75, 100]} />
      {shares.map((s, i) => {
        const x = L + i * bw + bw * 0.2, w = bw * 0.6;
        return (
          <g key={s.quarter}>
            {s.share !== null ? (
              <rect x={x} y={y(s.share)} width={w} height={Math.max(0.5, y(0) - y(s.share))} fill="var(--color-accent)"
                data-check={`deals|chart_ai|${s.quarter}|share`} data-value={s.share}>
                <title>{`${s.quarter}: ${s.share}% of the ${whole(s.allMw)} MW stated is of AI-power deals (${whole(s.aiMw)} MW); ${s.aiDeals} of ${s.deals} deals tagged AI`}</title>
              </rect>
            ) : (
              <text x={x + w / 2} y={y(0) - 4} textAnchor="middle" fontSize="10" fill={M}>
                no MW<title>{`${s.quarter}: no deal of the quarter states MW; ${s.aiDeals} of ${s.deals} deals tagged AI`}</title>
              </text>
            )}
            <text x={x + w / 2} y={H - 8} textAnchor="middle" fontSize="11" fill={M}>{s.quarter}</text>
          </g>
        );
      })}
    </svg>
  );
}

function PartyChart({ parties }: { parties: ReturnType<typeof topParties> }) {
  const L = 230, R = 70, rowH = 24, top = 4, H = top + parties.length * rowH + 4;
  const hi = Math.max(1, ...parties.map((p) => p.mw));
  const x = (v: number) => L + (v / hi) * (W - L - R);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="The counterparties with the most MW stated" data-chart="party">
      {parties.map((p, i) => {
        const yy = top + i * rowH;
        return (
          <g key={p.name}>
            <text x={L - 8} y={yy + rowH / 2 + 4} textAnchor="end" fontSize="12" fill={T}>{p.name.length > 32 ? `${p.name.slice(0, 31)}.` : p.name}</text>
            <rect x={L} y={yy + 4} width={Math.max(0.5, x(p.mw) - L)} height={rowH - 8} fill="var(--chart-ink)"
              data-check={`deals|chart_party|${p.name}|mw`} data-value={p.mw}>
              <title>{`${p.name}: ${whole(p.mw)} MW stated by ${p.withMw} of its ${p.deals} deals`}</title>
            </rect>
            <text x={x(p.mw) + 6} y={yy + rowH / 2 + 4} fontSize="12" fill={T}>{whole(p.mw)} MW</text>
          </g>
        );
      })}
    </svg>
  );
}

function Table({ head, rows, caption }: { head: string[]; rows: (string | React.ReactNode)[][]; caption: string }) {
  return (
    <details className="mt-2 text-sm">
      <summary className="cursor-pointer text-xs text-muted">The figures as a table</summary>
      <div className="overflow-x-auto">
        <table className="mt-1 w-full border-collapse text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          <thead><tr className="border-b border-rule text-xs text-muted">{head.map((h) => <th key={h} scope="col" className="py-1 pr-3 font-normal">{h}</th>)}</tr></thead>
          <tbody>{rows.map((r, i) => <tr key={i} className="border-b border-rule/60">{r.map((c, j) => <td key={j} className="py-1 pr-3 tabular-nums">{c}</td>)}</tr>)}</tbody>
        </table>
      </div>
    </details>
  );
}

export async function ChartsView() {
  const read = await attempt(deals);
  const all = read.ok ? fold((read.data as unknown as DealRow[]).map(toDeal), PAIRS) : [];
  const stacks = mwByQuarter(all), pts = pricePoints(all), shares = aiShare(all), parties = topParties(all);
  return (
    <>
      <ToolHeader title="Deals in charts"
        crumb={<>Every deal: <Link href="/deals?tab=tracker" className="underline">Tracker</Link>. For AI power: <Link href="/deals?view=ai" className="underline">AI power</Link></>}
        lead={<>The deals the news reported, in four charts. Each sum is of the figures the stories state; hover a mark for its values, and open a chart&apos;s table for every figure.</>} />
      {!read.ok && isLicenseReason(read.reason) ? (
        <>
          <p className="mb-3 text-sm"><NoData what="deals" reason={read.reason} /></p>
          <DealsHeld />
        </>
      ) : !read.ok ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
      ) : !all.length ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No deal is held in the live set.</p>
      ) : (
        <>
          <HeldRows shape="events" table="energy_deals" shown={all.length} method="/data/methods/energy_deals" />
          <ChartFrame title="MW stated, by quarter and kind of supply"
            note={<>The quarter of each deal&apos;s date; the deals that state no MW are counted in the hover and the table, not drawn. The kind of supply is read from the deal&apos;s kind and its stated technology.</>}>
            <Legend items={GROUPS.map(([, label, color]) => [label, color])} />
            {/* session 1853 (deals faults row 8): the fog card a quarter, each kind of supply in its own color, the total and the count that state no MW */}
            <BarsHover id="deals-mw-quarter" left={56} right={12} width={W}
              cards={stacks.map((s) => ({ label: s.quarter, sub: `${whole(s.without)} deals of the quarter state no MW`,
                lines: [...s.parts.filter((p) => p.mw > 0).map((p) => { const g = GROUPS.find(([id]) => id === p.group)!; return { name: `${g[1]} (${p.deals})`, color: g[2], text: `${whole(p.mw)} MW` }; }),
                  { name: "MW stated", color: T, text: `${whole(s.total)} MW` }] }))}>
              <MwChart stacks={stacks} />
            </BarsHover>
            <Table caption="MW stated by quarter and kind of supply" head={["Quarter", ...GROUPS.map(([, l]) => l), "Deals stating no MW"]}
              rows={stacks.map((s) => [s.quarter, ...s.parts.map((p) => <Num key={p.group} check={`deals|chart_mw|${s.quarter}|${p.group}`} raw={p.mw}>{whole(p.mw)}</Num>),
                <Num key="w" check={`deals|chart_mw|${s.quarter}|without`} raw={s.without}>{whole(s.without)}</Num>])} />
          </ChartFrame>
          <ChartFrame title="Prices stated per MWh, over time" note={<>The PPAs and offtakes whose stories state a price in US dollars per MWh, each a point; the four most common technologies, the rest as other.</>}>
            {pts.length ? (
              <>
                <PriceChart pts={pts} />
                <Table caption="The prices stated" head={["Date", "Technology", "Parties", "USD per MWh"]}
                  rows={pts.map((p) => [p.date, p.tech, p.label, <Num key="p" check={`deals|chart_price|${p.id}|price`} raw={p.price}>{whole(p.price)}</Num>])} />
              </>
            ) : (
              <p className="text-sm text-muted" role="status" data-chart-empty="price">No PPA or offtake held states a price in US dollars per MWh, so there is no point to draw.</p>
            )}
          </ChartFrame>
          <ChartFrame title="The AI-power deals' share of the MW stated, by quarter" note={<>Of the MW the quarter&apos;s deals state, the part stated by the deals the AI-power rule tags; a quarter whose deals state no MW has no share.</>}>
            <BarsHover id="deals-ai-share" left={56} right={12} width={W}
              cards={shares.map((s) => ({ label: s.quarter, sub: `${whole(s.aiDeals)} of ${whole(s.deals)} deals tagged AI`,
                lines: s.share === null ? [{ name: "MW stated", color: T, text: "none" }] : [
                  { name: "AI-power share", color: "var(--color-accent)", text: `${s.share}%` },
                  { name: "AI-power MW", color: "var(--color-accent)", text: `${whole(s.aiMw)} MW` },
                  { name: "MW stated", color: T, text: `${whole(s.allMw)} MW` }] }))}>
              <ShareChart shares={shares} />
            </BarsHover>
            <Table caption="The AI-power share by quarter" head={["Quarter", "Share, %", "AI MW", "All MW stated", "AI deals", "Deals"]}
              rows={shares.map((s) => [s.quarter, s.share === null ? "no MW stated" : <Num key="s" check={`deals|chart_ai|${s.quarter}|share`} raw={s.share}>{String(s.share)}</Num>,
                <Num key="a" check={`deals|chart_ai|${s.quarter}|ai_mw`} raw={s.aiMw}>{whole(s.aiMw)}</Num>, <Num key="b" check={`deals|chart_ai|${s.quarter}|all_mw`} raw={s.allMw}>{whole(s.allMw)}</Num>,
                whole(s.aiDeals), whole(s.deals)])} />
          </ChartFrame>
          <ChartFrame title="The counterparties with the most MW stated" note={<>A deal counts for each of its two parties, as one name a company; the MW of the deals that state it.</>}>
            {parties.length ? (
              <>
                <PartyChart parties={parties} />
                <Table caption="The counterparties with the most MW" head={["Counterparty", "MW stated", "Deals stating MW", "Deals"]}
                  rows={parties.map((p) => [p.name, <Num key="m" check={`deals|chart_party|${p.name}|mw`} raw={p.mw}>{whole(p.mw)}</Num>, whole(p.withMw), whole(p.deals)])} />
              </>
            ) : <p className="text-sm text-muted" role="status">No deal held states MW.</p>}
          </ChartFrame>
        </>
      )}
      <SourceLine tables={["energy_deals"]} note={<>The deals as <code className="font-mono">warehouse/deals/extract.py</code> extracted them, with <code className="font-mono">warehouse/deals/duplicates.csv</code>&apos;s pairs shown once; every figure traced by <code className="font-mono">scripts/check_deals.py</code>. <Link href="/data/methods/energy_deals">Method</Link>. This view is in review.</>} />
    </>
  );
}
