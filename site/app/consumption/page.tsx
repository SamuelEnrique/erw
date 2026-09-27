import type { Metadata } from "next";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { count, price } from "@/lib/format";
import { STATES } from "@/lib/regions";
import { attempt } from "@/lib/supabase";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Consumption by sector" };

const SALES = "eia_retail_sales_monthly";
const MER = "eia_sector_energy_consumption_monthly";
const SECTORS = [
  { id: "RES", label: "Residential" },
  { id: "COM", label: "Commercial" },
  { id: "IND", label: "Industrial" },
  { id: "TRA", label: "Transportation" },
];
const exact = (v: number) => (Number.isInteger(v) ? count(v) : price(v));
// one decimal; a value that rounds to zero is written 0.0, never -0.0
const one = (v: number) => (Math.abs(v) < 0.05 ? "0.0" : v.toFixed(1));
const pct = (v: number | null) => (v === null ? "" : `${v >= 0.05 ? "+" : ""}${one(v)}%`);
const MER_ROWS = [
  { msn: "TEICBUS", label: "Industrial: total energy consumed" },
  { msn: "ESICBUS", label: "Industrial: electricity bought (retail sales)" },
  { msn: "NNICBUS", label: "Industrial: natural gas" },
  { msn: "TECCBUS", label: "Commercial: total energy consumed" },
  { msn: "ESCCBUS", label: "Commercial: electricity bought (retail sales)" },
];

/** The first day of the month `k` months before `ts` (an ISO month start). */
function monthsBack(ts: string, k: number): string {
  const d = new Date(ts);
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - k, 1)).toISOString().replace(/\.\d{3}Z$/, "Z");
}

type Window = { from: string; to: string }; // [from, to) as ISO month starts

function total(rows: SeriesRow[], entity: string, w: Window, n: number) {
  // compare parsed times: Supabase writes "+00:00" where the window bounds write "Z"
  const f = Date.parse(w.from), t = Date.parse(w.to);
  const r = rows.filter((x) => x.entity === entity && Date.parse(x.ts_utc) >= f && Date.parse(x.ts_utc) < t);
  return r.length === n ? r.reduce((a, x) => a + x.value, 0) : null; // every month present, or no total
}

export default async function ConsumptionPage() {
  const [sales, mer] = await Promise.all([attempt(() => series(SALES, { variable: "retail_sales" })), attempt(() => series(MER, {}))]);
  if (!sales.ok) return <NoData what={SALES} reason={sales.reason} />;
  const rows = sales.data;
  const latest = rows.reduce((a, r) => (r.ts_utc > a ? r.ts_utc : a), "");  // one format within a table
  if (!latest) return <NoData what={SALES} reason="the table returned no rows" />;
  const cur: Window = { from: monthsBack(latest, 11), to: monthsBack(latest, -1) };
  const prev: Window = { from: monthsBack(latest, 23), to: cur.from };
  const label = `${cur.from.slice(0, 7)} to ${latest.slice(0, 7)}`;
  const prevLabel = `${prev.from.slice(0, 7)} to ${monthsBack(latest, 12).slice(0, 7)}`;
  const ent = (st: string, sec: string) => `eia:retail_sales:${st}:${sec}`;
  const states = Object.keys(STATES).filter((s) => s !== "US" && rows.some((r) => r.entity === ent(s, "ALL")));
  const stat = (st: string, sec: string) => {
    const a = total(rows, ent(st, sec), cur, 12);
    const b = total(rows, ent(st, sec), prev, 12);
    return { a, b, growth: a !== null && b !== null && b > 0 ? (100 * (a - b)) / b : null, change: a !== null && b !== null ? a - b : null };
  };
  const table = states.map((st) => ({ st, all: stat(st, "ALL"), by: Object.fromEntries(SECTORS.map((s) => [s.id, stat(st, s.id)])) }));
  const fastest = (sec: string) =>
    table
      .filter((t) => t.by[sec].growth !== null && (t.by[sec].b ?? 0) >= 1_000_000) // at least 1 TWh a year before, so a small base does not lead
      .sort((x, y) => y.by[sec].growth! - x.by[sec].growth!)
      .slice(0, 10);
  const us = { all: stat("US", "ALL"), by: Object.fromEntries(SECTORS.map((s) => [s.id, stat("US", s.id)])) };
  const esum = (st: string, sec: string, w: Window) => `series_esum|${SALES}|${ent(st, sec)}|retail_sales|${w.from}|${w.to}`;

  return (
    <>
      <h1 className="mb-1 text-3xl">Consumption by sector</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Electricity sold to end users by state and sector, from EIA&apos;s monthly survey of utilities and retail sellers (Form EIA-861M): the
        sector shares, the change over the latest 12 months against the 12 before, and where industrial and commercial load is growing fastest.
        Sums of 12 months, so seasons cancel out. The latest month EIA has published is {latest.slice(0, 7)}.
      </p>

      <Section title="United States" id="us">
        {us.all.a === null ? (
          <NoData what="US retail sales" reason={`${SALES} lacks a month of ${label} for eia:retail_sales:US:ALL`} />
        ) : (
          <p className="text-sm">
            Retail sales, {label}:{" "}
            <Num check={esum("US", "ALL", cur)} raw={us.all.a}>
              {exact(us.all.a)}
            </Num>{" "}
            MWh, {pct(us.all.growth)} on {prevLabel}.{" "}
            {SECTORS.map((s) => `${s.label} ${us.by[s.id].a !== null ? `${one((100 * us.by[s.id].a!) / us.all.a!)}%` : "no data"} (${pct(us.by[s.id].growth)})`).join("; ")}.
          </p>
        )}
        <Cite tables={[SALES]} note="Share of all-sector sales, and in brackets the change on the 12 months before" />
      </Section>

      <Section title="Where industrial and commercial load is growing fastest" id="fastest">
        <div className="grid gap-8 lg:grid-cols-2">
          {["IND", "COM"].map((sec) => (
            <div key={sec}>
              <h3 className="mb-2 text-base">{sec === "IND" ? "Industrial" : "Commercial"}</h3>
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b border-rule text-left text-xs text-muted">
                    <th className="py-1 pr-3 font-normal">State</th>
                    <th className="py-1 pr-3 text-right font-normal">MWh, {label}</th>
                    <th className="py-1 pr-3 text-right font-normal">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {fastest(sec).map((t) => (
                    <tr key={t.st} className="border-b border-rule/60">
                      <td className="py-1 pr-3">{STATES[t.st]}</td>
                      <td className="py-1 pr-3 text-right tabular-nums">
                        <Num check={esum(t.st, sec, cur)} raw={t.by[sec].a!}>
                          {exact(t.by[sec].a!)}
                        </Num>
                      </td>
                      <td className="py-1 pr-3 text-right tabular-nums">
                        {pct(t.by[sec].growth)} ({t.by[sec].change! >= 0 ? "+" : ""}
                        {count(t.by[sec].change!)} MWh)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
        <Cite tables={[SALES]} note={`Change: ${label} against ${prevLabel}. States that sold at least 1,000,000 MWh (1 TWh) to the sector in the earlier 12 months, so a small base does not lead`} />
      </Section>

      <Section title="Sector shares and growth, by state" id="states">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">State</th>
                <th className="py-1 pr-3 text-right font-normal">All sectors, MWh</th>
                <th className="py-1 pr-3 text-right font-normal">Change</th>
                {SECTORS.map((s) => (
                  <th key={s.id} className="py-1 pr-3 text-right font-normal">
                    {s.label}: share (change)
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.map((t) => (
                <tr key={t.st} className="border-b border-rule/60">
                  <td className="py-1 pr-3">{STATES[t.st]}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">{t.all.a !== null ? exact(t.all.a) : "no data"}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">{pct(t.all.growth)}</td>
                  {SECTORS.map((s) => {
                    const x = t.by[s.id];
                    return (
                      <td key={s.id} className="py-1 pr-3 text-right tabular-nums">
                        {!rows.some((r) => r.entity === ent(t.st, s.id))
                          ? ""
                          : x.a === null || !t.all.a
                            ? "no data"
                            : `${one((100 * x.a) / t.all.a)}%${x.growth !== null ? ` (${pct(x.growth)})` : ""}`}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-1 text-xs text-muted">
          Share of the state&apos;s all-sector retail sales over {label}; in brackets, the change on {prevLabel} (none where the earlier total
          is zero). &quot;No data&quot;: EIA published no value for a month of the window, so no 12-month total is given. Blank: EIA reports no
          such sector for the state. Transportation is electric rail and transit; EIA counts it only in some
          states.
        </p>
        <Cite tables={[SALES]} />
      </Section>

      <Section title="Industrial and commercial energy, all fuels (US)" id="mer">
        {!mer.ok ? (
          <NoData what={MER} reason={mer.reason} />
        ) : (
          (() => {
            const ml = mer.data.reduce((a, r) => (r.ts_utc > a ? r.ts_utc : a), "");
            const mc: Window = { from: monthsBack(ml, 11), to: monthsBack(ml, -1) };
            const mp: Window = { from: monthsBack(ml, 23), to: mc.from };
            return (
              <>
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-rule text-left text-xs text-muted">
                      <th className="py-1 pr-3 font-normal">Series (Monthly Energy Review)</th>
                      <th className="py-1 pr-3 text-right font-normal">TBtu, {mc.from.slice(0, 7)} to {ml.slice(0, 7)}</th>
                      <th className="py-1 pr-3 text-right font-normal">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {MER_ROWS.map((x) => {
                      const e = `eia:${x.msn}`;
                      const a = total(mer.data, e, mc, 12), b = total(mer.data, e, mp, 12);
                      return (
                        <tr key={x.msn} className="border-b border-rule/60">
                          <td className="py-1 pr-3">
                            {x.label} <span className="font-mono text-xs text-muted">{x.msn}</span>
                          </td>
                          <td className="py-1 pr-3 text-right tabular-nums">
                            {a !== null ? (
                              <Num check={`series_esum|${MER}|${e}|energy_consumption|${mc.from}|${mc.to}`} raw={a}>
                                {exact(a)}
                              </Num>
                            ) : (
                              "no data"
                            )}
                          </td>
                          <td className="py-1 pr-3 text-right tabular-nums">{a !== null && b ? pct((100 * (a - b)) / b) : ""}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <Cite tables={[MER]} note="Trillion British thermal units, as EIA publishes them; the latest 12 months against the 12 before. The MER lags the retail sales by a few months" />
              </>
            );
          })()
        )}
      </Section>
    </>
  );
}
