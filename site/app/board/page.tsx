import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { InlineBars, InlineSpark } from "@/components/InlineSpark";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { MARKETS, series, type SeriesRow } from "@/lib/data";
import { day, node, price } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 30 (Part A5): price board v2, one dense screen. Every number is a value of a derived table
// (price_board_latest, price_board_peak_offpeak, price_board_spreads, price_board_carbon; docs/methods/price_board.md)
// or of ercot_peak_premium_annual, read as stored: the page computes nothing. The one assumption, the 7.0 MMBtu/MWh heat
// rate of the spark spread, is labelled where it is used.
export const metadata: Metadata = { title: "Price board" };
export const revalidate = 3600;

type Idx = Map<string, SeriesRow[]>;
const METHOD = "/data/methods/price_board";

function index(rows: SeriesRow[]): Idx {
  const m: Idx = new Map();
  for (const r of rows) {
    const k = `${r.entity}|${r.variable}`;
    const a = m.get(k) ?? [];
    a.push(r);
    m.set(k, a);
  }
  for (const a of m.values()) a.sort((x, y) => x.ts_utc.localeCompare(y.ts_utc));
  return m;
}
const one = (ix: Idx, e: string, v: string) => ix.get(`${e}|${v}`)?.at(-1);
const all = (ix: Idx, e: string, v: string) => ix.get(`${e}|${v}`) ?? [];

function Tier({ tier }: { tier: "derived" | "source" }) {
  return (
    <Link href="/data/standard" title={TIER_TITLE[tier]} className="rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL[tier]}
    </Link>
  );
}

/** A value of a table, with its check key; `signed` writes + or a minus and colors the move by its sign. */
function V({ table, r, signed, unit }: { table: string; r?: SeriesRow; signed?: boolean; unit?: string }) {
  if (!r) return <span className="text-muted">not held</span>;
  // the number inside Num is exactly the stored value as displayed (a minus sign included), for check-values
  const n = <Num check={`series|${table}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{price(r.value)}</Num>;
  if (!signed) return <>{n}{unit ? <span className="text-muted">{unit}</span> : null}</>;
  const cls = r.value > 0 ? "text-up" : r.value < 0 ? "text-down" : "";
  return (
    <span className={cls}>
      {r.value > 0 ? "▲ +" : r.value < 0 ? "▼ " : ""}
      {n}
      {unit ? unit : null}
    </span>
  );
}

function Head({ title, tier, aside }: { title: string; tier: "derived" | "source"; aside?: React.ReactNode }) {
  return (
    <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-0.5">
      <h2 className="text-lg">
        {title} <Tier tier={tier} />
      </h2>
      {aside ? <div className="text-xs text-muted">{aside}</div> : null}
    </div>
  );
}

function MarketRow({ ix, entity, k, iso }: { ix: Idx; entity: string; k: "da" | "rt"; iso: string }) {
  const T = "price_board_latest";
  const latest = one(ix, entity, `${k}_latest_day_mean`);
  const intervals = one(ix, entity, `${k}_intervals_30d`);
  const label = k === "da" ? "Day-ahead" : "Real-time";
  if (!latest) {
    return (
      <tr className="border-b border-rule">
        <td className="py-0.5 pr-2 text-muted">{label}</td>
        <td colSpan={7} className="text-xs text-muted">
          {intervals && intervals.value > 0
            ? "no complete operating day in the last 30 days"
            : `no ${label.toLowerCase()} series in the ERW for ${iso} ${node(entity)}`}
        </td>
      </tr>
    );
  }
  const d30 = one(ix, entity, `${k}_days_30d`);
  const spark = all(ix, entity, `${k}_daily_mean`).map((r) => ({ t: r.ts_utc, v: r.value }));
  return (
    <tr className="border-b border-rule align-middle">
      <td className="py-0.5 pr-2 text-muted">
        {label} <span className="text-[11px]">{day(latest.ts_utc).slice(5)}</span>
      </td>
      <td className="pr-2 text-right font-semibold">
        <V table={T} r={latest} />
      </td>
      <td className="whitespace-nowrap pr-2 text-right text-xs">
        <V table={T} r={one(ix, entity, `${k}_day_change`)} signed />{" "}
        <span className="text-muted">
          (<V table={T} r={one(ix, entity, `${k}_day_change_pct`)} signed unit="%" />)
        </span>
      </td>
      <td className="pr-2 text-right">
        <V table={T} r={one(ix, entity, `${k}_avg_7d`)} />
      </td>
      <td className="pr-2 text-right">
        <V table={T} r={one(ix, entity, `${k}_avg_30d`)} />
        {d30 && d30.value < 30 ? (
          <span className="block text-[10px] text-muted">
            <Num check={`series|${T}|${d30.entity}|${d30.variable}|${d30.ts_utc}`} raw={d30.value}>{d30.value}</Num> days
          </span>
        ) : null}
      </td>
      <td className="whitespace-nowrap pr-2 text-right text-xs">
        <V table={T} r={one(ix, entity, `${k}_min_30d`)} /> to <V table={T} r={one(ix, entity, `${k}_max_30d`)} />
      </td>
      <td className="whitespace-nowrap pr-2 text-right text-xs">
        {k === "da" ? (
          <>
            <V table={T} r={one(ix, entity, "da_minus_rt")} signed />
            {one(ix, entity, "da_minus_rt") ? (
              <span className="block text-[10px] text-muted">{day(one(ix, entity, "da_minus_rt")!.ts_utc).slice(5)}</span>
            ) : null}
          </>
        ) : null}
      </td>
      <td>
        <InlineSpark values={spark} label={`${iso} ${node(entity)} ${label.toLowerCase()} daily mean, last 30 days, USD/MWh`} />
      </td>
    </tr>
  );
}

function Power({ ix }: { ix: Idx }) {
  return (
    <>
      <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-[11px] text-muted">
            <th className="py-0.5 font-normal">Market, latest complete day</th>
            <th className="pr-2 text-right font-normal">Daily mean</th>
            <th className="pr-2 text-right font-normal">Change on the day before</th>
            <th className="pr-2 text-right font-normal">7-day avg</th>
            <th className="pr-2 text-right font-normal">30-day avg</th>
            <th className="pr-2 text-right font-normal">30-day low to high</th>
            <th className="pr-2 text-right font-normal">DA minus RT</th>
            <th className="font-normal">Last 30 days</th>
          </tr>
        </thead>
        {MARKETS.map((m) => (
          <tbody key={m.iso}>
            <tr>
              <td colSpan={8} className="pt-1.5 text-xs">
                <span className="font-serif text-base">{m.iso}</span>{" "}
                <Link href={`/prices/${encodeURIComponent(m.main)}`} className="font-mono text-[11px]">
                  {node(m.main)}
                </Link>
              </td>
            </tr>
            <MarketRow ix={ix} entity={m.main} k="da" iso={m.iso} />
            <MarketRow ix={ix} entity={m.main} k="rt" iso={m.iso} />
          </tbody>
        ))}
      </table>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        USD/MWh. Means of complete local operating days only (a day missing an interval is left out, never filled); the
        day-ahead latest day may be tomorrow, which the ISO has already cleared. Low to high: of the daily means.
      </p>
    </>
  );
}

const PEAK_RULE: Record<string, string> = { CAISO: "HE 7 to 22, Mon to Sat (WECC 6x16)" };

function Peak({ ix }: { ix: Idx }) {
  const T = "price_board_peak_offpeak";
  return (
    <>
      <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-[11px] text-muted">
            <th className="py-0.5 font-normal">ISO, market, latest peak day</th>
            <th className="pr-2 text-right font-normal">Peak</th>
            <th className="pr-2 text-right font-normal">Off-peak</th>
            <th className="pr-2 text-right font-normal">Peak minus off-peak</th>
            <th className="font-normal">Peak minus off-peak, peak days</th>
          </tr>
        </thead>
        <tbody>
          {MARKETS.flatMap((m) =>
            (["da", "rt"] as const).map((k) => {
              const daily = all(ix, m.main, `${k}_peak_minus_offpeak`).filter((r) => r.freq === "P1D");
              const last = daily.at(-1);
              const pk = last ? all(ix, m.main, `${k}_peak_mean`).find((r) => r.ts_utc === last.ts_utc) : undefined;
              const op = last ? all(ix, m.main, `${k}_offpeak_mean`).find((r) => r.ts_utc === last.ts_utc) : undefined;
              return (
                <tr key={m.iso + k} className="border-b border-rule">
                  <td className="py-0.5 pr-2">
                    {m.iso} <span className="text-muted">{k === "da" ? "day-ahead" : "real-time"}</span>{" "}
                    <span className="text-[11px] text-muted">{last ? day(last.ts_utc).slice(5) : ""}</span>
                  </td>
                  {last ? (
                    <>
                      <td className="pr-2 text-right"><V table={T} r={pk} /></td>
                      <td className="pr-2 text-right"><V table={T} r={op} /></td>
                      <td className="pr-2 text-right"><V table={T} r={last} signed /></td>
                      <td>
                        <InlineSpark values={daily.slice(-30).map((r) => ({ t: r.ts_utc, v: r.value }))}
                          label={`${m.iso} ${k === "da" ? "day-ahead" : "real-time"} peak minus off-peak, last 30 peak days`} />
                      </td>
                    </>
                  ) : (
                    <td colSpan={4} className="text-xs text-muted">no complete peak day in the table</td>
                  )}
                </tr>
              );
            }),
          )}
        </tbody>
      </table>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        USD/MWh, main hub. Peak: hours ending 7 to 22 local, Monday to Friday (CAISO: {PEAK_RULE.CAISO}), NERC holidays
        off-peak. ERCOT reaches 90 days through its history; the other ISOs&apos; tables hold about 35.
      </p>
    </>
  );
}

function Spreads({ ix }: { ix: Idx }) {
  const T = "price_board_spreads";
  const hh = all(ix, "eia:henry_hub", "henry_hub");
  const bw = all(ix, "erw:brent_minus_wti", "brent_minus_wti");
  return (
    <>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-2">
        <div className="bg-panel p-2">
          <div className="text-xs text-muted">Henry Hub, USD/MMBtu {hh.at(-1) ? `(${day(hh.at(-1)!.ts_utc)})` : ""}</div>
          <div className="text-xl tabular-nums"><V table={T} r={hh.at(-1)} /></div>
          <InlineSpark values={hh.map((r) => ({ t: r.ts_utc, v: r.value }))} width={220} label="Henry Hub, last 365 days" />
        </div>
        <div className="bg-panel p-2">
          <div className="text-xs text-muted">Brent minus WTI, USD/bbl {bw.at(-1) ? `(${day(bw.at(-1)!.ts_utc)})` : ""}</div>
          <div className="text-xl tabular-nums"><V table={T} r={bw.at(-1)} signed /></div>
          <InlineSpark values={bw.map((r) => ({ t: r.ts_utc, v: r.value }))} width={220} label="Brent minus WTI, last 365 days" />
        </div>
      </div>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm tabular-nums">
          <thead>
            <tr className="border-b border-rule text-left text-[11px] text-muted">
              <th className="py-0.5 font-normal">ISO, operating day</th>
              <th className="pr-2 text-right font-normal">Spark spread, USD/MWh</th>
              <th className="pr-2 text-right font-normal">Implied heat rate, MMBtu/MWh</th>
              <th className="font-normal">Spark spread, the year the table holds</th>
            </tr>
          </thead>
          <tbody>
            {MARKETS.map((m) => {
              const ss = all(ix, m.main, "spark_spread_7");
              const last = ss.at(-1);
              return (
                <tr key={m.iso} className="border-b border-rule">
                  <td className="py-0.5 pr-2">
                    {m.iso} <span className="text-[11px] text-muted">{last ? day(last.ts_utc).slice(5) : ""}</span>
                  </td>
                  <td className="pr-2 text-right"><V table={T} r={last} signed /></td>
                  <td className="pr-2 text-right"><V table={T} r={one(ix, m.main, "implied_heat_rate")} /></td>
                  <td><InlineSpark values={ss.map((r) => ({ t: r.ts_utc, v: r.value }))} width={160} label={`${m.iso} spark spread`} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Spark spread: the main hub&apos;s day-ahead daily mean minus <strong>7.0 MMBtu/MWh (an assumed heat rate, the one
        assumption on this page)</strong> times Henry Hub; implied heat rate: the same mean over Henry Hub, with the gas price
        of the day or the latest trading day up to 4 days before. EIA publishes Henry Hub several days late, so the newest
        days have no spread yet. ERCOT covers the year; the other ISOs about 35 days.
      </p>
    </>
  );
}

function Carbon({ rows }: { rows: SeriesRow[] }) {
  const T = "price_board_carbon";
  if (!rows.length) {
    return (
      <p className="text-sm">
        The ERW holds CARB&apos;s and RGGI&apos;s auction results (<code className="font-mono">price_board_carbon</code>), but
        both publishers&apos; terms are unconfirmed, so they are licensed internal and the public site shows none of their
        prices. The ERW holds no secondary-market carbon prices. <Link href={METHOD}>Method</Link>.
      </p>
    );
  }
  const ix = index(rows);
  const ents = Array.from(new Set(rows.map((r) => r.entity))).sort();
  return (
    <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
      {ents.map((e) => {
        const p = one(ix, e, "latest_price");
        return (
          <div key={e} className="bg-panel p-2">
            <div className="text-xs text-muted">{e.replace(":", ", ").replace(/_/g, " ")}</div>
            <div className="text-xl tabular-nums"><V table={T} r={p} /> <span className="text-xs text-muted">{p?.unit}</span></div>
            <div className="text-[11px] text-muted">
              auction of {p ? day(p.ts_utc) : ""}; change <V table={T} r={one(ix, e, "price_change")} signed />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Ercot({ ix, prem }: { ix: Idx; prem: SeriesRow[] }) {
  const T = "price_board_peak_offpeak";
  const e = "ercot:HB_HUBAVG";
  const annual = all(ix, e, "rt_year_all_mean");
  const premium = prem.filter((r) => r.entity === e && r.variable === "peak_minus_midday_median");
  return (
    <>
      <div className="grid gap-3 lg:grid-cols-2">
        <div>
          <div className="text-xs text-muted">Real-time annual mean, HB_HUBAVG, USD/MWh, since 2015</div>
          <InlineBars values={annual.map((r) => ({ k: r.ts_utc.slice(0, 4), v: r.value }))} label="ERCOT HB_HUBAVG real-time annual mean, USD/MWh" />
        </div>
        <div>
          <div className="text-xs text-muted">Peak premium: median peak minus median midday, HB_HUBAVG real time, USD/MWh</div>
          <InlineBars values={premium.map((r) => ({ k: r.ts_utc.slice(0, 4), v: r.value }))} label="ERCOT peak premium by year, USD/MWh" color="var(--color-ink)" />
        </div>
      </div>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[560px] text-xs tabular-nums">
          <thead>
            <tr className="border-b border-rule text-left text-[11px] text-muted">
              <th className="py-0.5 font-normal">Year</th>
              <th className="pr-2 text-right font-normal">All hours</th>
              <th className="pr-2 text-right font-normal">Peak</th>
              <th className="pr-2 text-right font-normal">Off-peak</th>
              <th className="pr-2 text-right font-normal">Peak minus off-peak</th>
              <th className="pr-2 text-right font-normal">Peak premium (medians)</th>
            </tr>
          </thead>
          <tbody>
            {annual.map((r) => {
              const at = (v: string) => all(ix, e, v).find((x) => x.ts_utc === r.ts_utc);
              const pm = premium.find((x) => x.ts_utc === r.ts_utc);
              const days = at("rt_year_days");
              return (
                <tr key={r.ts_utc} className="border-b border-rule">
                  <td className="py-0.5 pr-2">
                    {r.ts_utc.slice(0, 4)}
                    {days && r === annual.at(-1) && days.value < 365 ? (
                      <span className="text-muted">
                        {" "}to date, <Num check={`series|${T}|${e}|rt_year_days|${days.ts_utc}`} raw={days.value}>{days.value}</Num> days
                      </span>
                    ) : null}
                  </td>
                  <td className="pr-2 text-right"><V table={T} r={r} /></td>
                  <td className="pr-2 text-right"><V table={T} r={at("rt_year_peak_mean")} /></td>
                  <td className="pr-2 text-right"><V table={T} r={at("rt_year_offpeak_mean")} /></td>
                  <td className="pr-2 text-right"><V table={T} r={at("rt_year_peak_minus_offpeak")} signed /></td>
                  <td className="pr-2 text-right">{pm ? <V table="ercot_peak_premium_annual" r={pm} signed /> : <span className="text-muted">not held</span>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Means over complete operating days (Central time), from the ERCOT history since 2015 and the rolling tables.
        The peak premium is the ERW&apos;s median-based measure (
        <Link href="/explorer/ercot-peak-premium">explorer</Link>, <Link href="/data/methods/ercot_peak_premium">method</Link>).
      </p>
    </>
  );
}

function AllHubs({ ix }: { ix: Idx }) {
  const T = "price_board_latest";
  const ents = Array.from(new Set(Array.from(ix.keys()).map((k) => k.split("|")[0]))).sort();
  return (
    <details>
      <summary className="cursor-pointer text-sm">Every hub and zone ({ents.length}), day-ahead and real-time</summary>
      <div className="mt-1 overflow-x-auto">
        <table className="w-full min-w-[560px] text-xs tabular-nums">
          <thead>
            <tr className="border-b border-rule text-left text-[11px] text-muted">
              <th className="py-0.5 font-normal">Hub or zone</th>
              <th className="pr-2 text-right font-normal">Day-ahead</th>
              <th className="pr-2 text-right font-normal">Change</th>
              <th className="pr-2 text-right font-normal">Real-time</th>
              <th className="pr-2 text-right font-normal">Change</th>
              <th className="font-normal">Real-time, 30 days</th>
            </tr>
          </thead>
          <tbody>
            {ents.map((e) => (
              <tr key={e} className="border-b border-rule">
                <td className="py-0.5 pr-2 font-mono">{e}</td>
                <td className="pr-2 text-right"><V table={T} r={one(ix, e, "da_latest_day_mean")} /></td>
                <td className="pr-2 text-right"><V table={T} r={one(ix, e, "da_day_change")} signed /></td>
                <td className="pr-2 text-right"><V table={T} r={one(ix, e, "rt_latest_day_mean")} /></td>
                <td className="pr-2 text-right"><V table={T} r={one(ix, e, "rt_day_change")} signed /></td>
                <td>
                  <InlineSpark values={all(ix, e, "rt_daily_mean").map((r) => ({ t: r.ts_utc, v: r.value }))} width={100} height={20}
                    label={`${e} real-time daily mean, last 30 days`} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

export default async function Board() {
  const [latest, peak, spreads, carbon, prem] = await Promise.all([
    attempt(() => series("price_board_latest", {})),
    attempt(() => series("price_board_peak_offpeak", {})),
    attempt(() => series("price_board_spreads", {})),
    attempt(() => series("price_board_carbon", {})),
    attempt(() => series("ercot_peak_premium_annual", { entity: "ercot:HB_HUBAVG", variable: "peak_minus_midday_median" })),
  ]);
  const lx = latest.ok ? index(latest.data) : null;
  const px = peak.ok ? index(peak.data) : null;
  const sx = spreads.ok ? index(spreads.data) : null;
  return (
    <>
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-3xl">Price board</h1>
        <p className="text-xs text-muted">
          Six ISOs, gas, oil and carbon, from the warehouse&apos;s derived tables, refreshed with the daily run.{" "}
          <Link href={METHOD}>Method</Link>
          {" | "}
          <Link href="/prices">Latest intervals</Link>
        </p>
      </div>

      <section className="mb-5" aria-label="Power">
        <Head title="Power, main hubs" tier="derived" aside={<Link href={METHOD}>how each number is computed</Link>} />
        {lx ? <Power ix={lx} /> : <NoData what="the power board" reason={latest.ok ? "" : latest.reason} />}
        <Cite tables={["price_board_latest"]} note="Derived from iso_dam_hub_prices, iso_rtm_hub_prices, nyiso_dam_zone_prices, nyiso_rtm_zone_prices, isone_dam_zone_prices and isone_rtm_zone_prices_hourly" />
      </section>

      <div className="grid gap-5 xl:grid-cols-2">
        <section className="mb-5 min-w-0" aria-label="Peak and off-peak">
          <Head title="Peak and off-peak" tier="derived" />
          {px ? <Peak ix={px} /> : <NoData what="peak and off-peak" reason={peak.ok ? "" : peak.reason} />}
          <Cite tables={["price_board_peak_offpeak"]} note="Derived from the same price tables and ercot_all_hub_prices_history" />
        </section>
        <section className="mb-5 min-w-0" aria-label="Gas and spreads">
          <Head title="Gas, oil and spark spreads" tier="derived" />
          {sx ? <Spreads ix={sx} /> : <NoData what="the spreads" reason={spreads.ok ? "" : spreads.reason} />}
          <Cite tables={["price_board_spreads"]} note="Derived from the day-ahead price tables, ercot_all_hub_prices_history and eia_fuel_spot_prices" />
        </section>
      </div>

      <section className="mb-5" aria-label="Carbon">
        <Head title="Carbon" tier="derived" />
        {carbon.ok ? <Carbon rows={carbon.data} /> : <NoData what="carbon" reason={carbon.reason} />}
      </section>

      <section className="mb-5" aria-label="ERCOT since 2015">
        <Head title="ERCOT since 2015" tier="derived" aside={<Link href="/explorer/ercot-peak-premium">the peak premium explorer</Link>} />
        {px && prem.ok ? <Ercot ix={px} prem={prem.data} /> : <NoData what="the ERCOT history" reason={!peak.ok ? peak.reason : !prem.ok ? prem.reason : ""} />}
        <Cite tables={["price_board_peak_offpeak", "ercot_peak_premium_annual"]} />
      </section>

      <section className="mb-5" aria-label="Every hub and zone">
        {lx ? <AllHubs ix={lx} /> : null}
      </section>
    </>
  );
}
