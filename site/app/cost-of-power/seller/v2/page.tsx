import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { HEAT_RATE, VOM, type Snapshot } from "@/lib/merchant";
import { ASSETS, GRIDS, PAUSED, choiceOf, href, monthName, monthsOf, sentence, spans, usd, whole, years, type Span } from "@/lib/seller2";

// Session 107: the seller's tab, version 2, in the battery page's layout and its framing: the last twelve months
// first, the long-run averages beside them and labeled as long-run averages. Solar, wind and the gas peaker, from the
// live tab's own model and snapshot (lib/merchant.ts, data/merchant_snapshot.json): no figure here is computed another
// way. The live seller tab (/cost-of-power/seller) is as it was.

export const metadata: Metadata = { title: "What a generator earns", robots: { index: false, follow: false } };

let SNAP: Snapshot | null = null;
function snapshot(): Snapshot {
  if (!SNAP) SNAP = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "merchant_snapshot.json"), "utf8")) as Snapshot;
  return SNAP;
}

const ACCENT = "var(--color-accent)";

/** Revenue by calendar year as bars; a year short of twelve held months is hatched. Plain SVG, no library. */
function YearBars({ ys, label }: { ys: { y: string; complete: boolean; v: number; months: number }[]; label: string }) {
  const W = 640, H = 220, L = 44, B = 26, T = 14;
  const top = Math.max(...ys.map((y) => y.v), 0), low = Math.min(...ys.map((y) => y.v), 0);
  const span = top - low || 1;
  const yOf = (v: number) => T + ((top - v) * (H - T - B)) / span;
  const bw = (W - L - 8) / ys.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label} className="block w-full max-w-2xl">
      <defs>
        <pattern id="seller2-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="6" height="6" fill="#fff" /><rect width="3" height="6" fill={ACCENT} />
        </pattern>
      </defs>
      <line x1={L} x2={W - 8} y1={yOf(0)} y2={yOf(0)} stroke="var(--color-rule)" />
      {ys.map((y, i) => {
        const x = L + i * bw + bw * 0.15, w = bw * 0.7, y0 = yOf(Math.max(y.v, 0)), h = Math.abs(yOf(y.v) - yOf(0));
        return (
          <g key={y.y}>
            <title>{`${y.y}: USD ${usd(y.v)} per kW${y.complete ? "" : ` (${y.months} months held, not a full year)`}`}</title>
            <rect x={x} y={y0} width={w} height={Math.max(h, 0.5)} fill={y.complete ? ACCENT : "url(#seller2-hatch)"} stroke={ACCENT} strokeWidth={y.complete ? 0 : 1} />
            <text x={x + w / 2} y={y0 - 3} textAnchor="middle" fontSize="10" fill="var(--color-ink)">{whole(y.v)}</text>
            <text x={x + w / 2} y={H - 8} textAnchor="middle" fontSize="10" fill="var(--color-muted)">{y.y}</text>
          </g>
        );
      })}
      <text x={4} y={T + 4} fontSize="10" fill="var(--color-muted)">USD/kW</text>
    </svg>
  );
}

export default async function SellerTwo({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const c = choiceOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])));
  const snap = snapshot();
  const g = GRIDS.find((x) => x.id === c.grid)!, a = ASSETS.find((x) => x.id === c.asset)!;
  const ms = monthsOf(snap, c);
  const held = ms.filter((r) => r.held);
  const s = spans(ms);
  const line = sentence(c, s);
  const ys = years(ms);
  const peaker = c.asset === "peaker";
  const money = peaker ? "Margin over fuel" : "Revenue";
  const cell = (x: Span | null, f: (x: Span) => string, why: string) => (x ? f(x) : <span className="text-muted">{why}</span>);
  const threeWhy = `not held: ${g.name} holds ${s.everyYears.length === 0 ? "no full year" : s.everyYears.length === 1 ? `one full year (${s.everyYears[0]})` : `${s.everyYears.length} full years`}`;
  const everyWhy = "not held: no full year";
  const twelveWhy = "not held: no twelve months in a row";
  const head = [
    "",
    <span key="t">Last twelve months{s.twelve ? <span className="block text-xs font-normal opacity-80">{monthName(s.twelve.from)} to {monthName(s.twelve.to)}</span> : null}</span>,
    <span key="3">Long-run average, a year{s.threeYears ? <span className="block text-xs font-normal opacity-80">{s.threeYears[0]} to {s.threeYears[2]}, the last three full years</span> : <span className="block text-xs font-normal opacity-80">the last three full years</span>}</span>,
    <span key="e">Long-run average, a year{s.everyYears.length ? <span className="block text-xs font-normal opacity-80">every full year held, {s.everyYears[0]} to {s.everyYears.at(-1)}</span> : <span className="block text-xs font-normal opacity-80">every full year held</span>}</span>,
  ];
  const row = (label: string, f: (x: Span) => string, key: string, highlight = false) => ({
    key, highlight, cells: [label, <span key="t" data-seller2={`twelve|${key}`}>{cell(s.twelve, f, twelveWhy)}</span>, <span key="3" data-seller2={`three|${key}`}>{cell(s.three, f, threeWhy)}</span>, <span key="e" data-seller2={`every|${key}`}>{cell(s.every, f, everyWhy)}</span>],
  });

  return (
    <ToolPage>
      <ToolHeader title="What a generator earns" crumb={<>Version 2 of the seller&apos;s tab, in review. The tab as it is: <Link href="/cost-of-power/seller" className="underline">/cost-of-power/seller</Link></>}
        lead={<>What a merchant solar plant, wind plant or gas peaker earned selling at the hub price, per kW of nameplate. The last twelve months come first; the long-run averages are beside them and labeled.</>} />
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>{PAUSED.words}</>}>
            <div className="text-xs uppercase tracking-wide text-muted">Grid</div>
            <ul className="mt-1 space-y-1 text-sm">
              {GRIDS.map((x) => <li key={x.id}>{x.id === c.grid ? <span className="font-semibold" aria-current="true" data-seller2-grid={x.id}>{x.name}</span> : <Link href={href({ ...c, grid: x.id })} className="underline">{x.name}</Link>}</li>)}
            </ul>
            <div className="mt-3 text-xs uppercase tracking-wide text-muted">Asset</div>
            <ul className="mt-1 space-y-1 text-sm">
              {ASSETS.map((x) => <li key={x.id}>{x.id === c.asset ? <span className="font-semibold" aria-current="true" data-seller2-asset={x.id}>{x.name}</span> : <Link href={href({ ...c, asset: x.id })} className="underline">{x.name}</Link>}</li>)}
            </ul>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {held.length === 0 ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-seller2-none="1">
              No month of {a.name.toLowerCase()} is held for {g.name}, so no number is shown{c.asset === "solar" && c.grid === "nyiso" ? ": EIA-930 itemizes no solar generation for New York" : ""}.
            </p>
          ) : (
            <>
              {line
                ? <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-seller2-summary="1">{line}</p>
                : <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">{g.name} holds no twelve months of {a.name.toLowerCase()} in a row, so the last twelve months are not shown.</p>}

              {s.twelve ? (
                <HeadlineRow>
                  <HeadlineNumber label={`${money}, last twelve months`} value={usd(s.twelve.revenue_kw)} unit="USD/kW" note={<>{monthName(s.twelve.from)} to {monthName(s.twelve.to)}</>} />
                  <HeadlineNumber label={peaker ? "Price while running" : "Capture price"} value={s.twelve.capture !== null ? usd(s.twelve.capture) : "not held"} unit={s.twelve.capture !== null ? "USD/MWh" : undefined}
                    note={<>against {usd(s.twelve.flat)} for every hour{s.twelve.rate !== null ? <>: {whole(s.twelve.rate)} percent of it</> : null}</>} />
                  <HeadlineNumber label={s.three ? "Long-run average" : "Long-run average"} value={s.three ? usd(s.three.revenue_kw) : "not held"} unit={s.three ? "USD/kW a year" : undefined}
                    note={s.three ? <>{s.threeYears![0]} to {s.threeYears![2]}, the last three full years</> : <>{threeWhy.replace("not held: ", "")}</>} />
                </HeadlineRow>
              ) : null}

              <ChartFrame title={`${money} by year, USD per kW`} legend={[{ label: "A full year", color: ACCENT }, { label: "Incomplete year", color: ACCENT, hatch: true }]}
                note={<>Per kW of nameplate. A hatched year holds fewer than twelve months and is not a full year&apos;s {peaker ? "margin" : "revenue"}; it is in no long-run average. {g.name} is held from {monthName(held[0].m)}.</>}>
                <YearBars ys={ys.map((y) => ({ y: y.y, complete: y.complete, v: y.revenue / 1000, months: y.months }))} label={`${a.name} in ${g.name}: ${money.toLowerCase()} by year, USD per kW`} />
              </ChartFrame>

              <ToolSection title="The last twelve months beside the long-run averages" id="spans"
                note={<>A long-run average is the sum over its full calendar years divided by their number; a year with a month missing is in none. The last twelve months are the newest twelve held in a row, so they overlap the newest full year where one is held.</>}>
                <ToolTable caption={`${a.name} in ${g.name}, by span`} minWidth={680} head={head}
                  rows={[
                    row(`${money}, USD per kW`, (x) => usd(x.revenue_kw), "revenue", true),
                    row(peaker ? "Energy sold while running, MWh per MW" : "Energy sold, MWh per MW", (x) => whole(x.energy), "energy"),
                    row(peaker ? "Price while running, USD per MWh" : "Capture price, USD per MWh", (x) => (x.capture !== null ? usd(x.capture) : "not held"), "capture"),
                    row("Price of every hour, USD per MWh", (x) => usd(x.flat), "flat"),
                    row(peaker ? "Price while running over every hour's, percent" : "Capture rate, percent", (x) => (x.rate !== null ? whole(x.rate) : "not held"), "rate"),
                  ]} />
              </ToolSection>
            </>
          )}

          <Fold title="How it is measured">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              {peaker
                ? <li><strong>The peaker</strong> runs in each hour the hub price is above its fuel and variable cost: Henry Hub gas at {HEAT_RATE} MMBtu per MWh plus USD {VOM} per MWh (Lazard&apos;s midpoints for a new gas peaker). Its figure here is its margin over that cost, not its sales. No start cost, minimum run, ramp, outage or regional gas price.</li>
                : <li><strong>{a.name}</strong> is the grid&apos;s whole fleet, hour by hour: EIA-930&apos;s {c.asset === "solar" ? "solar" : "wind"} generation over the fleet&apos;s installed nameplate that month (EIA-860M). A fleet average, not a site; curtailed output is not in it.</li>}
              <li><strong>The price</strong> is the real-time price at {g.at} of {g.name}, hour by hour. A plant is paid at its own node, which can differ in either direction.</li>
              <li><strong>A month is held</strong> when at least {Math.round(snap.defaults.near * 100)} percent of its hours are. A year is full when all twelve months are held.</li>
              <li><strong>Per kW of nameplate</strong>, before any cost but the peaker&apos;s fuel: no fixed cost, debt, tax or contract. The live tab has the costs and the debt coverage.</li>
              {c.grid === "caiso" && !peaker ? <li><strong>California.</strong> EIA&apos;s California hours from 1 November 2023 to 2 December 2025 sit one hour late and are read one hour earlier here, as on the live tab; from 16 December 2025 EIA&apos;s generation series for California changed (the page of known data faults has both).</li> : null}
            </ul>
          </Fold>
          <Fold title="What this does not tell you">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li>What a plant with a contract earns: most solar and wind is sold under one, not at the hub.</li>
              <li>What your site earns: this is a fleet&apos;s output at a hub&apos;s price.</li>
              <li>Whether it pays: no cost is taken off but the peaker&apos;s fuel.</li>
              <li>Next year: {s.everyYears.length >= 3 ? "the long-run averages show how far a single year can stand from them" : "with fewer than three full years held, one unusual season moves every figure here"}.</li>
            </ul>
          </Fold>
          <SourceLine tables={["merchant_revenue_monthly"]} note={<>The seller tab&apos;s own model and snapshot, built {snap.built.slice(0, 10)}; Lazard&apos;s Levelized Cost of Energy v18.0 for the peaker&apos;s heat rate and variable cost. This page is in review; the live tab is unchanged.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
