import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import fs from "node:fs";
import path from "node:path";
import type { ReactNode } from "react";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { Sparkline } from "@/components/Sparkline";
import { HeadlineNumber } from "@/components/tool/ToolPage";
import * as BS from "@/lib/batterystack";
import { MARKETS, catalogue, datacenters, daysAgo, deals, latestPrices, newest, series, storageUnits, type CatalogueRow } from "@/lib/data";
import { defaultBill } from "@/lib/bill";
import { inputsKey, inputsOf, stat, type Snapshot } from "@/lib/merchant";
import rules from "@/data/bill_rules.json";
import { count, day, node, price, shown, utc } from "@/lib/format";
import { DOCS, render, topItems, digestTitle } from "@/lib/markdown";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { statusOf } from "@/lib/release";
import markets from "@/data/markets.json";

// the latest-price board refreshes every 15 minutes; the rest of the page reads hourly data
export const revalidate = 900;

function StatusStrip({ cat }: { cat: CatalogueRow[] }) {
  const rows = cat.reduce((a, r) => a + (r.n_rows ?? 0), 0);
  const last = cat.map((r) => r.last_run).filter(Boolean).sort().at(-1) ?? null;
  const pass = cat.filter((r) => r.validator_status === "pass").length;
  const cells = [
    { k: "Public tables", v: <Num check="catalogue|count" raw={cat.length}>{count(cat.length)}</Num> },
    { k: "Rows", v: <Num check="catalogue|sum_n_rows" raw={rows}>{count(rows)}</Num> },
    { k: "Last refresh", v: <Num check="catalogue|max_last_run" raw={last ?? ""}>{utc(last)}</Num> },
    {
      k: "Validator",
      v: (
        <Num check="catalogue|n_pass" raw={pass}>
          {count(pass)} of {count(cat.length)} pass
        </Num>
      ),
    },
  ];
  return (
    <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
      {cells.map((c) => (
        <div key={c.k} className="bg-panel px-3 py-2">
          <div className="text-xs text-muted">{c.k}</div>
          <div className="text-base tabular-nums">{c.v}</div>
        </div>
      ))}
    </div>
  );
}

async function PriceBoard() {
  const latest = await attempt(latestPrices);
  const since = daysAgo(7);
  const cards = await Promise.all(
    MARKETS.map(async (m) => {
      const src = m.rt ?? m.da;
      const spark = await attempt(() => series(src.table, { entity: m.main, variable: src.variable, since }));
      return { m, src, spark };
    }),
  );
  if (!latest.ok) return <NoData what="latest prices" reason={latest.reason} />;
  return (
    <>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-2 lg:grid-cols-3">
        {cards.map(({ m, src, spark }) => {
          const p = latest.data.find((r) => r.entity === m.main);
          const pts = spark.ok ? spark.data.map((r) => ({ ts_utc: r.ts_utc, value: r.value })) : [];
          const spanDays = pts.length > 1 ? (new Date(pts.at(-1)!.ts_utc).getTime() - new Date(pts[0].ts_utc).getTime()) / 86_400_000 : 0;
          return (
            <div key={m.iso} className="bg-panel p-3">
              <div className="flex items-baseline justify-between gap-2">
                <span className="font-serif text-lg">{m.iso}</span>
                <Link href={`/prices/${encodeURIComponent(m.main)}`} className="font-mono text-xs" gate="plain">
                  {node(m.main)}
                </Link>
              </div>
              {p ? (
                <>
                  <div className="mt-1 text-2xl tabular-nums">
                    <Num check={`latest_prices|${p.entity}|${p.variable}`} raw={p.value}>{price(p.value)}</Num>{" "}
                    <span className="text-sm text-muted">{p.unit}</span>
                  </div>
                  <div className="text-xs text-muted">
                    real time, interval starting {utc(p.ts_utc)} <span className="font-mono">({p.variable})</span>
                  </div>
                </>
              ) : (
                <NoData reason={`latest_prices has no row for ${m.main}`} />
              )}
              <div className="mt-2">
                {spark.ok && pts.length > 1 ? (
                  <>
                    <Sparkline points={pts} width={220} height={40} label={`${m.iso} ${node(m.main)} ${src.variable}, last 7 days`} />
                    <div className="text-[11px] text-muted">
                      {m.rt ? "real time" : "day-ahead (no real-time series in the ERW)"}, {src.freq === "PT15M" ? "15-minute" : "hourly"},{" "}
                      {spanDays < 6.5 ? `${spanDays.toFixed(1)} days in the ERW table` : "7 days"} to {utc(pts.at(-1)!.ts_utc)}
                    </div>
                  </>
                ) : (
                  <NoData what="the 7-day sparkline" reason={spark.ok ? `${src.table} has fewer than two rows for ${m.main} since ${since}` : spark.reason} />
                )}
              </div>
            </div>
          );
        })}
      </div>
      <Cite
        tables={["latest_prices", ...cards.map((c) => c.src.table)]}
        note="Latest prices refresh every 15 minutes; sparklines come from the ERW tables, refreshed daily. Prices in USD/MWh as published by each ISO"
      />
    </>
  );
}

async function Fuels() {
  const f = markets.fuels;
  const rows = await Promise.all(f.entities.map(async (e) => ({ e, r: await attempt(() => newest(f.table, e.entity, f.variable)) })));
  return (
    <>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
        {rows.map(({ e, r }) => (
          <div key={e.entity} className="bg-panel p-3">
            <div className="text-sm">{e.label}</div>
            {r.ok && r.data ? (
              <>
                <div className="text-2xl tabular-nums">
                  <Num check={`series|${f.table}|${e.entity}|${f.variable}|newest`} raw={r.data.value}>{price(r.data.value)}</Num>{" "}
                  <span className="text-sm text-muted">{r.data.unit}</span>
                </div>
                <div className="text-xs text-muted">daily spot, {day(r.data.ts_utc)}</div>
              </>
            ) : (
              <NoData reason={r.ok ? `${f.table} has no row for ${e.entity}` : r.reason} />
            )}
          </div>
        ))}
      </div>
      <Cite tables={[f.table]} note="EIA publishes daily spot prices with a lag of several days" />
    </>
  );
}

function Digest() {
  const items = topItems(DOCS.latest, 5);
  if (!items || items.length === 0) return <NoData what="the digest" reason="docs/digest/latest.md has no 'Top of the industry' section" />;
  return (
    <>
      <p className="mb-2 text-sm text-muted">What is happening in energy today, from scored news.</p>
      <ol className="prose-erw list-decimal pl-5">
        {items.map((md, i) => (
          <li key={i} dangerouslySetInnerHTML={{ __html: render(md, "docs/digest/latest.md") }} />
        ))}
      </ol>
      {statusOf("/digest") === "live" ? (
        <p className="text-sm">
          <Link href="/digest">The full digest ({digestTitle(DOCS.latest).replace(/^(?:ERW's )?Energy Digest,\s*/, "")}) and the archive</Link>
        </p>
      ) : null}
    </>
  );
}

// Session 53: the home page v2. Three audiences, each a set of tool cards: the tool's name, the question it answers, one
// live number from the warehouse where natural (each with its check key, as everywhere on the site), and a link.
// docs/tools.md is the inventory the cards follow. Session 19's four entry paths and session 20's Explore grid gave way
// to these; every page is still in the nav.
type Card = { href: string; name: string; question: string; num?: ReactNode; numLabel?: string; table?: string };

const n0 = (v: number) => Math.round(v).toLocaleString("en-US");

function ToolCard({ c }: { c: Card }) {
  return (
    <Link href={c.href} className="flex flex-col bg-panel p-3 no-underline">
      <span className="font-serif text-lg text-ink">{c.name}</span>
      <span className="text-sm text-muted">{c.question}</span>
      {c.num ? <span className="mt-2 text-sm text-ink"><span className="text-base tabular-nums">{c.num}</span> <span className="text-xs text-muted">{c.numLabel}</span></span> : null}
    </Link>
  );
}

/** Session 71: an audience shows only its live tools' cards (lib/release.ts); the tools in review are named once, in
 * the "In review" section near the bottom. An audience with no live tool is not shown. */
function Audience({ title, line, cards }: { title: string; line: string; cards: Card[] }) {
  cards = cards.filter((c) => statusOf(c.href) === "live");
  if (!cards.length) return null;
  return (
    <section className="mb-8" aria-label={title}>
      <h2 className="mb-1 font-serif text-2xl">{title}</h2>
      <p className="mb-2 max-w-3xl text-sm text-muted">{line}</p>
      <div className={`grid gap-px border border-rule bg-rule ${cards.length === 1 ? "max-w-sm" : cards.length === 2 ? "max-w-2xl sm:grid-cols-2" : "sm:grid-cols-2 lg:grid-cols-3"}`}>
        {cards.map((c) => <ToolCard key={c.href + c.name} c={c} />)}
      </div>
    </section>
  );
}

/** The cards' live numbers, each read here and checked by scripts/check-values.mjs under its key. */
async function liveNumbers() {
  const [ercotDemand, wti, fleet, uri, cop, deal, dc, cat] = await Promise.all([
    attempt(() => newest("eia930_all_demand", "eia930:ERCO", "demand_mw")),
    attempt(() => newest("eia_fuel_spot_prices", "eia:wti_cushing", "spot_price")),
    attempt(storageUnits),
    attempt(() => series("event_window_daily", { event: "uri_2021", entity: "ercot:HB_HUBAVG", variable: "rt_max" })),
    attempt(() => series("cost_of_power_monthly", { entity: "ercot:HB_HUBAVG" })),
    attempt(deals),
    attempt(datacenters),
    attempt(catalogue),
  ]);
  const out: Record<string, ReactNode> = {};
  if (ercotDemand.ok && ercotDemand.data) {
    const r = ercotDemand.data;
    out.grid = <Num check={`series|eia930_all_demand|eia930:ERCO|demand_mw|newest`} raw={r.value}>{n0(r.value)}</Num>;
    out.gridLabel = `MW, ERCOT's demand at ${r.ts_utc.slice(11, 16)} UTC on ${r.ts_utc.slice(0, 10)}`;
  }
  if (wti.ok && wti.data) {
    out.wti = <Num check={`series|eia_fuel_spot_prices|eia:wti_cushing|spot_price|newest`} raw={wti.data.value}>{price(wti.data.value)}</Num>;
    out.wtiLabel = `USD/bbl, WTI Cushing on ${wti.data.ts_utc.slice(0, 10)}; the calculator's default oil prices are monthly means of these daily prices`;
  }
  if (fleet.ok) {
    const op = fleet.data.filter((u) => u.iso === "ERCOT" && u.status === "operating");
    const mw = Math.round(op.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
    out.fleet = <Num check="storage|iso_mw|ERCOT|operating" raw={mw}>{shown(mw)}</Num>;
    out.fleetLabel = "MW of batteries operating in ERCOT (EIA-860M), the real fleet the game sets beside its own";
  }
  if (uri.ok) {
    const w = uri.data.filter((r) => r.ts_utc >= "2021-02-07" && r.ts_utc < "2021-02-25");
    if (w.length) {
      const v = Math.max(...w.map((r) => r.value));
      out.uri = <Num check="series_max|event_window_daily|rt_max|2021-02-07T00:00:00Z|2021-02-25T00:00:00Z|ercot:HB_HUBAVG" raw={v}>{price(v)}</Num>;
      out.uriLabel = "USD/MWh, the highest 15-minute real-time price at ERCOT's hub average during Winter Storm Uri";
    }
  }
  if (cop.ok) {
    const by = new Map<string, Record<string, { value: number; ts_utc: string }>>();
    for (const r of cop.data) (by.get(r.ts_utc) ?? by.set(r.ts_utc, {}).get(r.ts_utc)!)[r.variable] = r;
    const full = [...by.entries()].filter(([, m]) => m.rt_load_weighted && m.rt_hours && m.hours_in_month && m.rt_hours.value === m.hours_in_month.value).sort((a, b) => (a[0] < b[0] ? -1 : 1));
    const last = full.at(-1);
    if (last) {
      const r = last[1].rt_load_weighted;
      out.cop = <Num check={`series|cost_of_power_monthly|ercot:HB_HUBAVG|rt_load_weighted|${r.ts_utc}`} raw={r.value}>{price(r.value)}</Num>;
      out.copLabel = `USD/MWh, what ERCOT's load paid at the hub in ${r.ts_utc.slice(0, 7)}, load-weighted`;
    }
  }
  if (deal.ok) {
    const now = new Date().toISOString().slice(0, 7);
    const prev = new Date(Date.UTC(Number(now.slice(0, 4)), Number(now.slice(5, 7)) - 2, 1)).toISOString().slice(0, 7);
    const month = deal.data.some((d) => d.event_date.slice(0, 7) === now) ? now : prev;
    const k = deal.data.filter((d) => d.event_date.slice(0, 7) === month).length;
    out.deals = <Num check={`deals|month_count|${month}`} raw={k}>{n0(k)}</Num>;
    out.dealsLabel = `deals dated ${month}`;
  }
  if (dc.ok) {
    out.dc = <Num check="datacenters|count" raw={dc.data.length}>{n0(dc.data.length)}</Num>;
    out.dcLabel = "datacenter facilities tracked";
  }
  if (cat.ok) {
    out.tables = <Num check="catalogue|count" raw={cat.data.length}>{n0(cat.data.length)}</Num>;
    out.tablesLabel = "public tables, each with its source, license and method";
  }
  // the bill explainer's default PG&E bill, recomputed by check-values from the tariff rates
  const ca = defaultBill(rules, "CA");
  out.bill = <Num check="bill|CA|total" raw={ca.total}>{shown2(ca.total)}</Num>;
  out.billLabel = "USD, a PG&E home's 600 kWh bill, built line by line from the tariff";
  // the seller's tab: the median month of 100 MW of ERCOT solar, from the snapshot the tab reads
  try {
    const snap = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "merchant_snapshot.json"), "utf8")) as Snapshot;
    const x = inputsOf({});
    const v = stat(snap, x, "median");
    if (v !== null) {
      out.seller = <span data-format="usd"><Num check={`mr|${inputsKey(x)}|median`} raw={v}>{v.toLocaleString("en-US")}</Num></span>;
      out.sellerLabel = "USD, the median month of 100 MW of solar selling at ERCOT's hub";
    }
  } catch { /* the snapshot is missing: the card shows no number */ }
  // session 67, the "Open now" strip: the US operating fleet, and the default battery (100 MW, 4 hours, ERCOT, perfect
  // foresight) from battery_stack_monthly, as /cost-of-power/battery computes it. Session 71: the last twelve months per
  // kW, the battery page's own lead, never the average of every year held (57 percent of it is February 2021)
  if (fleet.ok) {
    const op = fleet.data.filter((u) => u.status === "operating");
    const mw = Math.round(op.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
    out.us = <Num check="storage|mw|operating" raw={mw}>{shown(mw)}</Num>;
  }
  const bx = BS.inputsOf({});
  const stack = await attempt(() => rest<BS.Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${BS.TABLE}`, entity: `eq.${BS.gridOf(bx.grid).entity}`,
    variable: `like.${bx.strat}_${bx.dur}h_*`, order: "variable,ts_utc" }, HOURLY));
  if (stack.ok) {
    const v = BS.stat(stack.data, [], bx, "l12_kw:total");
    const l12 = BS.lastTwelve(BS.monthsOf(stack.data, bx.strat, bx.dur));
    if (v !== null && l12) {
      out.battery = <Num check={`bs|${BS.inputsKey(bx)}|l12_kw:total`} raw={v}>{v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Num>;
      out.batteryLabel = `${BS.monthName(l12[0].m)} to ${BS.monthName(l12[11].m)}`;
    }
  }
  return out;
}

/** Session 67: the tools open to every visitor (lib/release.ts), each with one line and one number read from the tables. */
function OpenNow({ L }: { L: Record<string, ReactNode> }) {
  const tools: { href: string; name: string; line: string; num?: ReactNode; pre?: string; unit?: string }[] = [
    { href: "/cost-of-power/battery", name: "What a battery earns", line: `The last twelve months of a 100 MW, 4-hour battery in ERCOT${L.batteryLabel ? ` (${L.batteryLabel})` : ""}, energy and ancillary services together, with perfect foresight.`, num: L.battery, pre: "USD ", unit: "per kW" },
    { href: "/cost-of-power/seller", name: "What a generator earns", line: "The median month of 100 MW of solar selling at ERCOT's hub.", num: L.seller, pre: "USD " },
    { href: "/network", name: "The network", line: `ERCOT's demand in the newest hour held, one of the grids the 3D network draws${L.gridLabel ? ` (${String(L.gridLabel).replace(/^MW, ERCOT's demand /, "")})` : ""}.`, num: L.grid, unit: "MW" },
    { href: "/storage", name: "Storage", line: "Batteries operating in the US, nameplate power, from EIA's monthly generator inventory.", num: L.us, unit: "MW" },
  ];
  return (
    <section className="mb-8 border border-rule bg-white px-4 py-4" aria-label="Open now">
      <h2 className="mb-3 font-serif text-xl text-accent">Open now</h2>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {tools.map((t) => (
          <HeadlineNumber key={t.href} label="" unit={t.unit}
            value={t.num ? <><span className="font-sans text-sm text-muted">{t.pre ?? ""}</span>{t.num}</> : <span className="font-sans text-sm text-muted">not held</span>}
            note={<><Link href={t.href} className="font-serif text-base">{t.name}</Link><span className="mt-0.5 block">{t.line}</span></>} />
        ))}
      </div>
    </section>
  );
}
/** Session 71: the tools in review, named once, greyed and not links (in the internal view they are links). */
function InReview({ tools }: { tools: { href: string; name: string }[] }) {
  if (!tools.length) return null;
  return (
    <section className="mb-8" aria-label="In review" data-home-in-review="1">
      <h2 className="mb-1 font-serif text-lg text-muted">In review</h2>
      <p className="max-w-3xl text-sm leading-relaxed text-muted">
        {tools.map((t, i) => <span key={t.href}>{i ? ", " : ""}<Link href={t.href} gate="quiet">{t.name}</Link></span>)}.
        {" "}They open when they are approved.
      </p>
    </section>
  );
}
const shown2 = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default async function Home() {
  const cat = await attempt(catalogue);
  const L = await liveNumbers();
  const num = (k: string) => ({ num: L[k], numLabel: L[`${k}Label`] as string | undefined });
  const students: Card[] = [
    { href: "/grid/ercot", name: "Your grid", question: "What is each of the seven ISO grids, and what is it doing today?", ...num("grid"), table: "eia930_all_demand" },
    { href: "/network", name: "The network", question: "Which balancing authorities trade power, and how much, hour by hour, in 3D?" },
    { href: "/learn/bill", name: "What is on a bill", question: "What does a home's electricity bill pay for, line by line, at five utilities?", ...num("bill") },
    { href: "/learn/problems", name: "Problem sets", question: "Fifteen questions on grids, prices and storms, answered from the latest data." },
    { href: "/play/battery", name: "Home battery game", question: "Can you run a home battery through a real day of ERCOT prices better than perfect foresight?", ...num("fleet"), table: "storage_capacity" },
    { href: "/events", name: "Events", question: "What did Uri, Elliott, COVID-19 and two heat waves do to the grid, day by day?", ...num("uri"), table: "event_window_daily" },
  ];
  const investors: Card[] = [
    { href: "/board", name: "Price board", question: "What is power selling for at each ISO's main hub right now, and how did it move?" },
    { href: "/cost-of-power", name: "Cost of power: buying", question: "What does a MWh cost to buy at each hub, weighted by when the grid uses it?", ...num("cop"), table: "cost_of_power_monthly" },
    { href: "/cost-of-power/seller", name: "Cost of power: selling", question: "What does a merchant solar, wind, battery or peaker asset earn, and does it cover its debt?", ...num("seller"), table: "merchant_revenue_monthly" },
    { href: "/deals", name: "Deals", question: "Which PPAs, acquisitions and financings happened, with their sources?", ...num("deals"), table: "energy_deals" },
    { href: "/datacenters", name: "Datacenters", question: "Which datacenters are being built, by whom, where and how large?", ...num("dc"), table: "datacenter_facilities" },
    { href: "/severance", name: "Severance tax and the lease tool", question: "What state production tax is due on oil and gas in Texas, Louisiana and New Mexico, well by well?", ...num("wti"), table: "eia_fuel_spot_prices" },
    { href: "/companies", name: "Companies (the Thesis Builder)", question: "Which energy companies has the Thesis Builder mapped, at what stage and with what funding?" },
  ];
  const researchers: Card[] = [
    { href: "/data", name: "Data and downloads", question: "What tables does the ERW hold, and how do I read them in Python or on Redivis?", ...num("tables"), table: "catalogue" },
    { href: "/data/methods/event_study", name: "Event studies and the notebook", question: "How large was each event's effect, with and without the weather, and how do I reproduce it?" },
    { href: "/data/standard", name: "Methods and the data standard", question: "How is every number built, and what shape is every table?" },
    { href: "/ask", name: "Ask the ERW", question: "Ask the warehouse a question; every number in the answer comes from a table it read." },
  ];
  // session 71: every tool in review the home page used to link, named once near the bottom
  const inReview = [
    { href: "/tour", name: "The tour" }, { href: "/board", name: "Price board" }, { href: "/prices", name: "Every hub and zone" },
    ...[...students, ...investors, ...researchers].map((c) => ({ href: c.href, name: c.name })),
    { href: "/digest", name: "Energy Digest archive" }, { href: "/roundup", name: "ERW's Roundup" },
  ].filter((t, i, all) => statusOf(t.href) === "review" && all.findIndex((u) => u.href === t.href) === i);
  return (
    <>
      <h1 className="mb-1 text-3xl">Energy Research Warehouse</h1>
      <p className="mb-2 max-w-3xl text-base">
        The live, citable record of the whole US energy system, from power prices to pipelines, plants, deals and policy, with AI&apos;s demand for power as
        its sharpest lens.
      </p>
      {statusOf("/tour") === "live" ? (
        <p className="mb-5 text-sm"><Link href="/tour" className="border border-accent px-3 py-1 text-accent no-underline">Start the tour</Link> <span className="text-muted">five stops, about three minutes</span></p>
      ) : <div className="mb-5" />}

      <OpenNow L={L} />

      <Section title="Power prices, real time" aside={statusOf("/board") === "live" ? <><Link href="/board">Price board</Link> <span className="text-muted">|</span> <Link href="/prices">Every hub and zone</Link></> : undefined}>
        <PriceBoard />
      </Section>

      <Audience title="Students and teachers" line="How the grid works, what a bill pays for, and what storms and heat waves do, from the data itself." cards={students} />
      <Audience title="Investors and lenders" line="Prices, the cost and the earnings of power, deals, datacenters and the taxes on oil and gas, each number traced to its source." cards={investors} />
      <Audience title="Researchers" line="Every table with its method, license and download, the event studies and their notebook, and a warehouse you can ask." cards={researchers} />
      <div className="mb-8"><Cite tables={["battery_stack_monthly", "merchant_revenue_monthly", "eia930_all_demand", "storage_capacity",
        ...[...students, ...investors, ...researchers].filter((c) => statusOf(c.href) === "live" && c.table).map((c) => c.table!)]}
        note="The numbers of the tools open now, each checked against its table; the full list of tools is docs/tools.md" /></div>

      <Section title="Gas and oil">
        <Fuels />
      </Section>

      <Section
        title="ERW's Energy Digest"
        aside={statusOf("/digest") === "live" ? (
          <>
            <Link href="/digest">Archive</Link> <span className="text-muted">|</span> <Link href="/roundup">ERW&apos;s Roundup</Link>
          </>
        ) : undefined}
      >
        <Digest />
      </Section>

      <InReview tools={inReview} />

      <section className="mb-10" aria-label="Warehouse status">
        {cat.ok ? <StatusStrip cat={cat.data} /> : <NoData what="warehouse status" reason={cat.reason} />}
        {cat.ok ? <Cite tables={["catalogue"]} note="Rebuilt on every daily run; public tables only" /> : null}
      </section>
    </>
  );
}
