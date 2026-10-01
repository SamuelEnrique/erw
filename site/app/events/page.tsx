import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";

// Session 36B: the Historical Event Analyzer's index (session 36C: two events; session 39: five, each a card with its
// dates, its grids and one headline number read from event_window_daily, docs/methods/events.md).
export const metadata: Metadata = { title: "Events" };
export const revalidate = 3600;

const T = "event_window_daily";

type Card = {
  href: string; title: string; dates: string; grids: string; event: string;
  entity: string; variable: string; how: "max" | "min"; within: [string, string]; unit: string; lead: string;
};

const EVENTS: Card[] = [
  { href: "/events/uri-2021", title: "Winter Storm Uri: ERCOT, February 2021", dates: "2021-02-07 to 2021-02-24", grids: "ERCOT", event: "uri_2021",
    entity: "ercot:HB_HUBAVG", variable: "rt_max", how: "max", within: ["2021-02-07", "2021-02-24"], unit: "USD/MWh", lead: "Highest 15-minute real-time price" },
  { href: "/events/covid-2020", title: "COVID-19: demand in the seven ISO grids, spring 2020", dates: "2020-03-01 to 2020-05-31", grids: "CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP and the lower 48", event: "covid_2020",
    entity: "eia930:US48", variable: "demand_pct_vs_baseline_week", how: "min", within: ["2020-03-01", "2020-05-31"], unit: "% against the same weeks of 2019", lead: "Lower 48, deepest weekly drop" },
  { href: "/events/caiso-heat-2020", title: "The August 2020 heat wave: CAISO", dates: "2020-08-10 to 2020-08-24", grids: "CAISO", event: "caiso_heat_2020",
    entity: "eia930:CISO", variable: "demand_max_pct_vs_baseline", how: "max", within: ["2020-08-10", "2020-08-24"], unit: "% above the baseline", lead: "Peak hour, highest against the baseline" },
  // session 58
  { href: "/events/caiso-heat-2022", title: "The September 2022 heat wave: CAISO", dates: "2022-08-31 to 2022-09-09", grids: "CAISO", event: "caiso_heat_2022",
    entity: "eia930:CISO", variable: "demand_max_mw", how: "max", within: ["2022-08-31", "2022-09-09"], unit: "MW", lead: "CAISO's highest hour of demand served" },
  { href: "/events/elliott-2022", title: "Winter Storm Elliott: six grids, December 2022", dates: "2022-12-19 to 2022-12-29", grids: "PJM, MISO, SPP, NYISO, ISO-NE and ERCOT", event: "elliott_2022",
    entity: "eia930:PJM", variable: "demand_max_mw", how: "max", within: ["2022-12-19", "2022-12-29"], unit: "MW", lead: "PJM's highest hour of demand served" },
  { href: "/events/ercot-heat-2023", title: "The summer 2023 heat: ERCOT", dates: "2023-08-01 to 2023-09-10", grids: "ERCOT", event: "ercot_heat_2023",
    entity: "ercot:HB_HUBAVG", variable: "rt_max", how: "max", within: ["2023-08-01", "2023-09-10"], unit: "USD/MWh", lead: "Highest 15-minute real-time price" },
];

async function headline(c: Card): Promise<SeriesRow | undefined> {
  const rows = await series(T, { event: c.event, entity: c.entity, variable: c.variable });
  const xs = rows.filter((r) => r.ts_utc.slice(0, 10) >= c.within[0] && r.ts_utc.slice(0, 10) <= c.within[1]);
  if (!xs.length) return undefined;
  return xs.reduce((a, b) => (c.how === "max" ? (b.value > a.value ? b : a) : b.value < a.value ? b : a));
}

export default async function Events() {
  const heads = await Promise.all(EVENTS.map((c) => attempt(() => headline(c))));
  return (
    <>
      <h1 className="mb-1 text-3xl">Events</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        What happened to a grid during a major event, day by day, set against the same days of earlier years. Every figure is read from the
        warehouse&apos;s table event_window_daily. <Link href="/data/methods/events">Method</Link>.
      </p>
      <Section title="Events in the warehouse">
        <div className="grid gap-4 md:grid-cols-2">
          {EVENTS.map((c, i) => {
            const h = heads[i];
            const r = h.ok ? h.data : undefined;
            return (
              <div key={c.href} className="border border-rule bg-panel p-3">
                <Link href={c.href} className="text-lg">{c.title}</Link>
                <div className="text-xs text-muted">{c.dates}. {c.grids}.</div>
                <p className="mt-2 text-sm">
                  {c.lead}:{" "}
                  {r ? (
                    <><strong><Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}|${c.event}`} raw={r.value}>{shown(r.value)}</Num></strong> {c.unit}, {r.ts_utc.slice(0, 10)}</>
                  ) : <span className="text-muted">not held</span>}
                </p>
              </div>
            );
          })}
        </div>
        <Cite tables={[T]} />
      </Section>
    </>
  );
}
