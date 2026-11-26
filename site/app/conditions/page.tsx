import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { pfKey } from "@/lib/pagefile";
import { LineChart, type Line } from "@/components/LineChart";
import { TimeChart, type TimeSeries } from "@/components/TimeChart";
import { ChartFrame, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { FILES, INDEX, OP_IDS, col, toMs, windowOf, type OperatorFile, type Strip } from "@/lib/conditions";
import { ConditionsDecisions } from "./Decisions";

// Session 9000 (chain 601, part G): "Grid conditions", a new page. For a chosen operator, now and through its history:
// demand against the day-ahead forecast, megawatts out of service, the constraints binding, the scarcity adder, the
// alerts in force, each a strip on one time axis, so that a tight day reads at a glance. Any day in history, or one of
// the nine events of /events; two operators side by side. A strip an operator's terms hold, or that no open source
// publishes, is drawn blank with its reason on hover. Reads data/conditions/*.json (warehouse/derived/conditions_page.py,
// contract docs/state/page_files_conditions.md, method docs/methods/grid_conditions.md). In review, in no menu.
export const metadata: Metadata = { title: "Grid conditions", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const NONE = "none";
const TABLES = ["eia930_ba_demand_hourly", "generation_outages_hourly", "constraints_binding_hourly", "ercot_rtm_price_adders", "grid_all_alerts"];
const STRIP_NAMES: Record<string, string> = { demand: "Demand and forecast", out: "Out of service", constraints: "Constraints binding", scarcity: "Scarcity adder", alerts: "Alerts", reserves: "Reserves against the requirement" };

function Blank({ s, name, k }: { s: Strip; name: string; k: string }) {
  return (
    <div className="my-2 flex h-16 cursor-help items-center justify-center border border-dashed border-rule bg-panel text-sm text-muted" title={`${s.status}: ${s.why ?? ""}`} data-blank-strip={k}>
      {name}: {s.status}
    </div>
  );
}

// Session 9001, row H3: a strip whose window holds no figure (ERCOT's adder ends on 2025-12-04; SPP's outages begin in
// 2016) says so in words, with the last day the file holds, instead of drawing an empty chart with a broken axis.
function lastHeld(f: OperatorFile, c: string): string | null {
  const i = col(f.daily_columns, c);
  for (let j = f.daily.length - 1; j >= 0; j--) if (f.daily[j][i] !== null) return f.daily[j][0] as string;
  return null;
}

function NoneHeld({ title, f, c, w, k }: { title: string; f: OperatorFile; c: string; w: { start: string; end: string }; k: string }) {
  const last = lastHeld(f, c);
  return (
    <div className="my-2 border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" data-none-held={k}>
      {title}: no figure held from {w.start} to {w.end}. {last ? `The file's last figure is of ${last}.` : "The file holds none."}
    </div>
  );
}

// Session 9001 (part H): the window at a glance, the day of each strip's highest figure, each figure a pf| key into the
// operator's page file (lib/pagefile.ts) so scripts/check-values.mjs reads it again from the file on its own.
const GLANCE: { c: string; words: string; unit: string }[] = [
  { c: "demand_peak", words: "Highest peak demand", unit: "MW" },
  { c: "out_max", words: "Most megawatts out of service in an hour", unit: "MW" },
  { c: "cons_hours", words: "Most constraint-hours in a day", unit: "" },
  { c: "adder_hours", words: "Most hours with the adder above zero in a day", unit: "" },
];

function Glance({ f, w, k }: { f: OperatorFile; w: { start: string; end: string }; k: string }) {
  const items = GLANCE.map((g) => {
    const j = col(f.daily_columns, g.c);
    let best = -1;
    f.daily.forEach((r, i) => {
      if (r[0] < w.start || r[0] > w.end || r[j] === null) return;
      if (best < 0 || (r[j] as number) > (f.daily[best][j] as number)) best = i;
    });
    return best < 0 ? null : { ...g, i: best, j, v: f.daily[best][j] as number, day: f.daily[best][0] as string };
  }).filter((x): x is NonNullable<typeof x> => x !== null && (x.c !== "adder_hours" || x.v > 0));
  if (!items.length) return null;
  return (
    <ul className="mb-3 list-none p-0 text-sm" data-glance={k}>
      {items.map((x) => (
        <li key={x.c}>
          {x.words}: <Num check={pfKey(`conditions/${f.op}.json`, ["daily", x.i, x.j])} raw={x.v} source={`${f.strips[x.c.startsWith("demand") ? "demand" : x.c.startsWith("out") ? "out" : x.c.startsWith("cons") ? "constraints" : "scarcity"]?.source ?? ""}. The day's figure in the page file, ${x.day}.`}>{Math.round(x.v).toLocaleString("en-US")}</Num>{x.unit ? ` ${x.unit}` : ""}, on {x.day}
        </li>
      ))}
    </ul>
  );
}

function hourlyLines(f: OperatorFile, rows: (string | number | null)[][], names: { c: string; label: string; color: string }[]): Line[] {
  return names.map((n) => {
    const i = col(f.hourly_columns, n.c);
    return { label: n.label, color: n.color, gap: 3600, points: rows.filter((r) => r[i] !== null).map((r) => ({ t: Date.parse(r[0] as string) / 1000, v: r[i] as number })) };
  }).filter((l) => l.points.length);
}

function dailySeries(f: OperatorFile, rows: (string | number | null)[][], names: { c: string; label: string; color: string }[]): TimeSeries[] {
  return names.map((n) => {
    const i = col(f.daily_columns, n.c);
    return { name: n.label, color: n.color, points: rows.map((r): [number, number | null] => [toMs(r[0] as string), r[i] as number | null]) };
  }).filter((s) => s.points.some((p) => p[1] !== null));
}

// Session 10219 (the conditions audit, finding 11): the operator line said "days and hours in <zone> clock time for days
// and hours" (the file's own time line), where every hourly chart labels UTC instants (components/TimeChart.tsx); and the
// newest window, counted from the build's UTC day, ends on a day that holds EIA's forecast but no demand yet. The line
// now names the clock of each and, when the window's last days carry the forecast only, the last day of demand.
function demandEnds(f: OperatorFile, daily: OperatorFile["daily"], end: string): string {
  const i = col(f.daily_columns, "demand_peak");
  let last: string | null = null;
  for (const r of daily) if (r[i] !== null) last = r[0] as string;
  return last && last < end ? ` EIA's demand is held to ${last}; the days after it carry the forecast only.` : "";
}

function Operator({ f, event, day, tag }: { f: OperatorFile; event?: string; day?: string; tag: string }) {
  const w = windowOf(f, event, day);
  const daily = f.daily.filter((r) => r[0] >= w.start && r[0] <= w.end);
  let hourly = w.hourly ? f.hourly[w.hourly] : [];
  if (w.hourly && day && !event) {
    const a = toMs(day) - 86_400_000;
    const b = toMs(day) + 2 * 86_400_000;
    hourly = hourly.filter((r) => { const t = Date.parse(r[0]); return t >= a && t < b; });
  }
  const st = f.strips;
  const alerts = f.alerts.filter((a) => a[0] >= w.start && a[0] <= w.end);
  const src = (k: string) => st[k]?.source ?? "";
  const hDemand = hourlyLines(f, hourly, [{ c: "demand", label: "Demand", color: "accent" }, { c: "forecast", label: "Day-ahead forecast", color: "series-3" }]);
  const hOut = hourlyLines(f, hourly, [{ c: "out_total", label: "Total", color: "accent" }, { c: "out_planned", label: "Planned", color: "series-3" }, { c: "out_forced", label: "Forced", color: "series-5" }]);
  const hCons = [...hourlyLines(f, hourly, [{ c: "cons_n", label: "Constraints binding", color: "accent" }]), ...hourlyLines(f, hourly, [{ c: "cons_max", label: "Largest shadow price", color: "series-3" }]).map((l) => ({ ...l, y2: true }))];
  const hAdder = hourlyLines(f, hourly, [{ c: "adder", label: "Adder", color: "accent" }]);
  const dDemand = dailySeries(f, daily, [{ c: "demand_peak", label: "Peak demand", color: "accent" }, { c: "forecast_peak", label: "Forecast peak", color: "series-3" }]);
  const dOut = dailySeries(f, daily, [{ c: "out_mean", label: "Mean", color: "accent" }, { c: "out_max", label: "Highest hour", color: "series-3" }]);
  const dCons = dailySeries(f, daily, [{ c: "cons_hours", label: "Constraint-hours", color: "accent" }]);
  const dAdder = dailySeries(f, daily, [{ c: "adder_hours", label: "Hours", color: "accent" }]);
  return (
    // Session 9001, row H4: min-w-0, so a wide table (the 47 notices of a heat wave) scrolls inside its own frame and
    // the column, a grid item beside a second operator, never widens the page past a phone's screen
    <div className="min-w-0" data-operator={f.op} data-tag={tag}>
      <h3 className="mb-1 font-serif text-xl text-accent">{f.name}</h3>
      <p className="mb-2 text-xs text-muted">{w.title}, {w.start} to {w.end}; days in {f.time.split(" ")[0]} clock time, the hourly charts in UTC.{demandEnds(f, daily, w.end)} {hourly.length ? `Hour by hour (${hourly.length} hours), then day by day.` : "Day by day (no hourly figures are kept for this window: they are kept for the newest days and the nine events)."}</p>
      <Glance f={f} w={w} k={tag} />
      {hourly.length ? (
        <>
          {hDemand.length ? (
            <ChartFrame title="Demand and the day-ahead forecast, MW" tip={<Hint words=" (source)" why={src("demand")} />}>
              <LineChart lines={hDemand} unit="MW" ariaLabel={`${f.name} demand and forecast by hour`} />
            </ChartFrame>
          ) : <NoneHeld title="Demand and the day-ahead forecast" f={f} c="forecast_peak" w={w} k={`${tag}-demand`} />}
          {st.out.status === "shown" ? (hOut.length ? (
            <ChartFrame title="Out of service, MW" tip={<Hint words=" (source)" why={src("out")} />}>
              <LineChart lines={hOut} unit="MW" ariaLabel={`${f.name} megawatts out of service by hour`} />
            </ChartFrame>
          ) : <NoneHeld title="Out of service" f={f} c="out_mean" w={w} k={`${tag}-out`} />) : <Blank s={st.out} name={STRIP_NAMES.out} k={`${tag}-out`} />}
          {st.constraints.status === "shown" ? (hCons.length ? (
            <ChartFrame title="Constraints binding (count) and the largest shadow price (USD/MWh)" tip={<Hint words=" (source)" why={`${src("constraints")}. The largest shadow price is by size: SPP prints them negative.`} />}>
              <LineChart lines={hCons} unit="count" unit2="USD/MWh" ariaLabel={`${f.name} constraints binding by hour`} />
            </ChartFrame>
          ) : <NoneHeld title="Constraints binding" f={f} c="cons_hours" w={w} k={`${tag}-cons`} />) : <Blank s={st.constraints} name={STRIP_NAMES.constraints} k={`${tag}-cons`} />}
          {st.scarcity.status === "shown" ? (hAdder.length ? (
            <ChartFrame title="Online reserve price adder, USD/MWh (hourly mean)" tip={<Hint words=" (source)" why={`${src("scarcity")}. ${st.scarcity.note ?? ""}`} />}>
              <LineChart lines={hAdder} unit="USD/MWh" ariaLabel={`${f.name} reserve price adder by hour`} />
            </ChartFrame>
          ) : <NoneHeld title="Online reserve price adder" f={f} c="adder_hours" w={w} k={`${tag}-scar`} />) : <Blank s={st.scarcity} name={STRIP_NAMES.scarcity} k={`${tag}-scar`} />}
        </>
      ) : null}
      {dDemand.length ? (
        <ChartFrame title="Peak demand and the forecast's peak, MW a day" tip={<Hint words=" (source)" why={src("demand")} />}>
          <TimeChart series={dDemand} unit="MW" x="day" ariaLabel={`${f.name} peak demand by day`} />
        </ChartFrame>
      ) : <NoneHeld title="Peak demand and the forecast's peak" f={f} c="forecast_peak" w={w} k={`${tag}-demand-d`} />}
      {st.out.status === "shown" ? (dOut.length ? (
        <ChartFrame title="Out of service: the day's mean and highest hour, MW" tip={<Hint words=" (source)" why={src("out")} />}>
          <TimeChart series={dOut} unit="MW" x="day" ariaLabel={`${f.name} out of service by day`} />
        </ChartFrame>
      ) : hourly.length ? null : <NoneHeld title="Out of service" f={f} c="out_mean" w={w} k={`${tag}-out-d`} />) : hourly.length ? null : <Blank s={st.out} name={STRIP_NAMES.out} k={`${tag}-out-d`} />}
      {st.constraints.status === "shown" ? (dCons.length ? (
        <ChartFrame title="Constraint-hours a day" tip={<Hint words=" (source)" why={`${src("constraints")}. The number of (constraint, hour) pairs that bound in the day-ahead market.`} />}>
          <TimeChart series={dCons} unit="count" x="day" ariaLabel={`${f.name} constraint-hours by day`} />
        </ChartFrame>
      ) : hourly.length ? null : <NoneHeld title="Constraints binding" f={f} c="cons_hours" w={w} k={`${tag}-cons-d`} />) : hourly.length ? null : <Blank s={st.constraints} name={STRIP_NAMES.constraints} k={`${tag}-cons-d`} />}
      {st.scarcity.status === "shown" ? (dAdder.length ? (
        <ChartFrame title="Hours the adder was above zero, a day" tip={<Hint words=" (source)" why={`${src("scarcity")}. ${st.scarcity.note ?? ""}`} />}>
          <TimeChart series={dAdder} unit="hours" x="day" ariaLabel={`${f.name} scarcity hours by day`} />
        </ChartFrame>
      ) : hourly.length ? null : <NoneHeld title="Hours the adder was above zero" f={f} c="adder_hours" w={w} k={`${tag}-scar-d`} />) : hourly.length ? null : <Blank s={st.scarcity} name={STRIP_NAMES.scarcity} k={`${tag}-scar-d`} />}
      {st.alerts.status === "shown" ? (
        <>
          <h4 className="mb-1 mt-4 font-serif text-base text-accent" data-alerts-heading={tag}>Alerts and notices in force, {w.start} to {w.end} ({alerts.length})</h4>
          {alerts.length ? (
            <ToolTable minWidth={360} caption={`Alerts and notices, ${w.start} to ${w.end} (${alerts.length})`} head={["Date", "Kind, as the operator words it", "Start", "End"]}
              rows={alerts.slice(0, 40).map((a, i) => ({ key: `${a[0]}-${i}`, cells: [<a key="d" className="underline" href={a[4]} title={src("alerts")}>{a[0]}</a>, a[1], a[2] ?? "", a[3] ?? ""] }))} />
          ) : (
            <p className="text-sm text-muted" data-none-held={`${tag}-alerts`}>None held in this window. {f.alerts.length ? `The last the file holds is of ${f.alerts.reduce((m, a) => (a[0] > m ? a[0] : m), f.alerts[0][0])}.` : "The file holds none."}</p>
          )}
        </>
      ) : <Blank s={st.alerts} name={STRIP_NAMES.alerts} k={`${tag}-alerts`} />}
      <Blank s={st.reserves} name={STRIP_NAMES.reserves} k={`${tag}-reserves`} />
    </div>
  );
}

export default async function ConditionsPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const a = OP_IDS.includes(one(q, "a") ?? "") ? (one(q, "a") as string) : "ercot";
  const bRaw = one(q, "b");
  const b = bRaw && bRaw !== NONE && OP_IDS.includes(bRaw) && bRaw !== a ? bRaw : NONE;
  const event = INDEX.events.some((e) => e.id === one(q, "event")) ? (one(q, "event") as string) : undefined;
  const dayRaw = one(q, "day");
  const day = !event && dayRaw && /^\d{4}-\d{2}-\d{2}$/.test(dayRaw) ? dayRaw : undefined;
  const ops = [FILES[a], ...(b !== NONE ? [FILES[b]] : [])];
  const opOptions = INDEX.operators.map((o) => ({ value: o.op, label: o.name }));
  const statusRows = INDEX.operators.map((o) => ({ key: o.op, highlight: o.op === a || o.op === b, cells: [o.name, ...Object.keys(STRIP_NAMES).map((k) => {
    const s = FILES[o.op].strips[k];
    return <span key={k} className={s.status === "shown" ? "" : "cursor-help text-muted"} title={s.status === "shown" ? s.source : s.why} data-status={`${o.op}-${k}`}>{s.status}</span>;
  })] }));

  return (
    <Brand>
    <ToolPage>
      <div data-conditions="1">
      <ToolHeader
        title="Grid conditions"
        lead={<>Is the grid tight, and is it congested: demand against the day-ahead forecast, the megawatts out of service, the constraints binding, the scarcity adder and the alerts in force, each a strip on one time axis. Any day in history, or one of the nine events; two operators side by side. {" "}
          <Hint words="What it does not say" why="The page shows what the operators and EIA published. It makes no estimate of its own and gives no advice. A strip an operator's terms hold, or that no open source publishes, is drawn blank with the reason on hover." /></>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public. Files built {INDEX.built.slice(0, 10)}.</p>}
      />

      <form method="get" action="/conditions#strips" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-conditions-form="1">
        <AutoSubmitSelect name="a" value={a} options={opOptions} label="Operator" />
        <AutoSubmitSelect name="b" value={b} options={[{ value: NONE, label: "No second operator" }, ...opOptions.filter((o) => o.value !== a)]} label="Side by side with" />
        <AutoSubmitSelect name="event" value={event ?? NONE} options={[{ value: NONE, label: "No event" }, ...INDEX.events.map((e) => ({ value: e.id, label: `${e.title} (${e.start})` }))]} label="Event" />
        <label className="flex flex-col text-sm">Day<input type="date" name="day" defaultValue={day ?? ""} min="2018-07-01" className="border border-rule bg-white px-2 py-1" /></label>
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
      </form>

      <ToolSection title="The strips" id="strips">
        <div className={ops.length > 1 ? "grid gap-6 lg:grid-cols-2" : ""}>
          {ops.map((f, i) => <Operator key={f.op} f={f} event={event} day={day} tag={i ? "b" : "a"} />)}
        </div>
      </ToolSection>

      <ToolSection title="What is held for each grid" id="held">
        <ToolTable minWidth={720} caption="Each strip's state for each grid: shown, or the reason it is blank (on hover)" head={["Grid", ...Object.values(STRIP_NAMES)]} rows={statusRows} />
      </ToolSection>

      <ConditionsDecisions />
      <TableDownloads tables={TABLES} />
      <SourceLine tables={TABLES} note={<>Method: <a href="/data/methods/grid_conditions">the page&apos;s method note</a>. EIA&apos;s demand and forecast, the operators&apos; outages, constraints, adders and notices as published; the page takes the day&apos;s peak, mean, highest and count, and nothing else.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
