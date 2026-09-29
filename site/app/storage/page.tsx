import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { InlineBars, InlineSpark } from "@/components/InlineSpark";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, series, storageUnits, type SeriesRow, type StorageUnit } from "@/lib/data";
import { count, day, shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 31 (Part B3): battery storage. The fleet from storage_capacity (EIA-860M battery units, derived), the daily
// cycle from storage_daily_cycle (derived), and the hourly charge and discharge from eia930_all_storage (EIA-930,
// source). Sums of storage_capacity's rows are the only arithmetic on the page, each checked by check-values.mjs.
// Session 34: CAISO reports no battery series to EIA-930; its row of the daily cycle and its line in the charts come from
// CAISO's own data (caiso_battery_storage, Today's Outlook), labeled as CAISO's with their own tier chip and citation.
export const metadata: Metadata = { title: "Storage" };
export const revalidate = 3600;

const METHOD = "/data/methods/storage";
const BAS = [
  { code: "us48", entity: "eia930:US48", label: "US Lower 48", tz: "Eastern", color: "ink" },
  { code: "erco", entity: "eia930:ERCO", label: "ERCOT", tz: "Central", color: "accent" },
  { code: "isne", entity: "eia930:ISNE", label: "ISO-NE", tz: "Eastern", color: "var(--color-fuel-gas)" },
  { code: "miso", entity: "eia930:MISO", label: "MISO", tz: "EST", color: "var(--color-fuel-hydro)" },
  { code: "swpp", entity: "eia930:SWPP", label: "SPP", tz: "Central", color: "var(--color-fuel-coal)" },
];
// session 34: CAISO's own data, not EIA-930's
const CAISO = { code: "ciso", entity: "caiso:ISO", label: "CAISO", tz: "Pacific", color: "var(--color-fuel-solar)" };
const ISOS = ["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"];
const BUILD = ["under_construction", "planned"];

function Tier({ tier }: { tier: "derived" | "source" }) {
  return (
    <Link href="/data/standard" title={TIER_TITLE[tier]} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL[tier]}
    </Link>
  );
}

const mw = (units: StorageUnit[]) => units.reduce((a, u) => a + (u.capacity_mw ?? 0), 0);
const mwText = shown; // the checker writes a whole number without decimals, else 2

/** A sum of storage_capacity MW, with the check key check-values.mjs recomputes. */
function MW({ units, check }: { units: StorageUnit[]; check: string }) {
  const v = Math.round(mw(units) * 10) / 10;
  return <Num check={`storage|${check}`} raw={v}>{mwText(v)}</Num>;
}

const hasMwh = (u: StorageUnit) => u.mwh !== null && u.mwh !== "";

/** Session 34: a sum of storage_capacity's energy capacity (MWh), where EIA gives it, with its check key. */
function MWh({ units, check }: { units: StorageUnit[]; check: string }) {
  const v = Math.round(units.filter(hasMwh).reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;
  return <Num check={`storage|${check}`} raw={v}>{mwText(v)}</Num>;
}

function Fleet({ units }: { units: StorageUnit[] }) {
  const by = (s: string) => units.filter((u) => u.status === s);
  const cells = [
    ["Operating", "operating"],
    ["Under construction", "under_construction"],
    ["Planned", "planned"],
    ["Retired", "retired"],
  ];
  return (
    <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
      {cells.map(([label, s]) => (
        <div key={s} className="bg-panel p-3">
          <div className="text-xs text-muted">{label}</div>
          <div className="text-2xl tabular-nums">
            <MW units={by(s)} check={`mw|${s}`} /> <span className="text-sm text-muted">MW</span>
          </div>
          <div className="text-xs text-muted">
            <Num check={`storage|n|${s}`} raw={by(s).length}>{count(by(s).length)}</Num> units
          </div>
          <div className="mt-1 text-xs text-muted tabular-nums">
            {by(s).some(hasMwh) ? (
              <>
                <span className="text-ink"><MWh units={by(s)} check={`mwh|${s}`} /></span> MWh (
                <Num check={`storage|n_mwh|${s}`} raw={by(s).filter(hasMwh).length}>{count(by(s).filter(hasMwh).length)}</Num> units)
              </>
            ) : (
              <>MWh: EIA-860M gives none</>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function ByIso({ units }: { units: StorageUnit[] }) {
  const rows = [...ISOS.map((i) => ({ label: i, key: i, u: units.filter((x) => x.iso === i) })),
    { label: "Outside the seven ISOs", key: "none", u: units.filter((x) => !x.iso) }];
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[460px] text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-[11px] text-muted">
            <th className="py-0.5 font-normal">ISO (the unit&apos;s balancing authority)</th>
            <th className="pr-2 text-right font-normal">Operating MW</th>
            <th className="pr-2 text-right font-normal">Under construction MW</th>
            <th className="pr-2 text-right font-normal">Planned MW</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className="border-b border-rule">
              <td className="py-0.5 pr-2">{r.label}</td>
              {["operating", "under_construction", "planned"].map((s) => (
                <td key={s} className="pr-2 text-right">
                  <MW units={r.u.filter((x) => x.status === s)} check={`iso_mw|${r.key}|${s}`} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ByState({ units }: { units: StorageUnit[] }) {
  const states = Array.from(new Set(units.map((u) => u.state ?? "").filter(Boolean)));
  const op = (s: string) => mw(units.filter((u) => u.state === s && u.status === "operating"));
  const top = states.sort((a, b) => op(b) - op(a) || a.localeCompare(b)).slice(0, 15);
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[420px] text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-[11px] text-muted">
            <th className="py-0.5 font-normal">State (the 15 with the most operating MW)</th>
            <th className="pr-2 text-right font-normal">Operating MW</th>
            <th className="pr-2 text-right font-normal">Under construction and planned MW</th>
          </tr>
        </thead>
        <tbody>
          {top.map((s) => (
            <tr key={s} className="border-b border-rule">
              <td className="py-0.5 pr-2">{s}</td>
              <td className="pr-2 text-right"><MW units={units.filter((u) => u.state === s && u.status === "operating")} check={`state_mw|${s}|operating`} /></td>
              <td className="pr-2 text-right"><MW units={units.filter((u) => u.state === s && BUILD.includes(u.status ?? ""))} check={`state_mw|${s}|build`} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ByYear({ units }: { units: StorageUnit[] }) {
  const future = units.filter((u) => BUILD.includes(u.status ?? "") && u.planned_year);
  const years = Array.from(new Set(future.map((u) => u.planned_year!))).sort();
  return (
    <>
      <div className="max-w-md">
        <InlineBars values={years.map((y) => ({ k: y, v: mw(future.filter((u) => u.planned_year === y)) }))}
          label="Planned battery additions by planned year, MW (under construction and planned)" height={80} />
      </div>
      <div className="mt-1 flex flex-wrap gap-x-4 text-sm tabular-nums">
        {years.map((y) => (
          <span key={y}>
            {y}: <MW units={future.filter((u) => u.planned_year === y)} check={`year_mw|${y}`} /> MW
          </span>
        ))}
      </div>
    </>
  );
}

/** The tag beside CAISO's rows and line: its data is CAISO's own, not EIA-930's. */
function CaisoTag() {
  return (
    <span className="ml-1 whitespace-nowrap text-[11px] text-muted">
      CAISO&apos;s data<Tier tier="derived" />
    </span>
  );
}

/** Hourly means of CAISO's 5-minute Total batteries (MW), by UTC hour, for the charts. */
function caisoHourly(rows: SeriesRow[]) {
  const by = new Map<number, { s: number; n: number }>();
  for (const r of rows) {
    const h = Math.floor(new Date(r.ts_utc).getTime() / 3_600_000) * 3_600;
    const a = by.get(h) ?? { s: 0, n: 0 };
    a.s += r.value;
    a.n += 1;
    by.set(h, a);
  }
  return Array.from(by.entries()).filter(([, a]) => a.n === 12).sort((a, b) => a[0] - b[0]).map(([t, a]) => ({ t, v: a.s / a.n }));
}

function Cycle({ rows }: { rows: SeriesRow[] }) {
  const T = "storage_daily_cycle";
  const get = (e: string, v: string) => rows.filter((r) => r.entity === e && r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const N = (r?: SeriesRow, whole = false) =>
    r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{whole ? String(r.value) : shown(r.value)}</Num> : <span className="text-muted">none</span>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-[11px] text-muted">
            <th className="py-0.5 font-normal">Balancing authority, latest complete local day</th>
            <th className="pr-2 text-right font-normal">Discharged MWh</th>
            <th className="pr-2 text-right font-normal">Charged MWh</th>
            <th className="pr-2 text-right font-normal">Out over in</th>
            <th className="pr-2 text-right font-normal">Peak discharge hour</th>
            <th className="pr-2 text-right font-normal">Peak charge hour</th>
            <th className="font-normal">Discharged, last 30 days</th>
          </tr>
        </thead>
        <tbody>
          {[...BAS, CAISO].map((b) => {
            const dis = get(b.entity, "mwh_discharged");
            const last = dis.at(-1);
            const at = (v: string) => (last ? get(b.entity, v).find((r) => r.ts_utc === last.ts_utc) : undefined);
            return (
              <tr key={b.code} className="border-b border-rule">
                <td className="py-0.5 pr-2">
                  {b.label}{b.code === "ciso" ? <CaisoTag /> : null} <span className="text-[11px] text-muted">{last ? day(last.ts_utc) : ""} ({b.tz})</span>
                </td>
                <td className="pr-2 text-right">{N(last)}</td>
                <td className="pr-2 text-right">{N(at("mwh_charged"))}</td>
                <td className="pr-2 text-right">{N(at("round_trip_ratio"))}</td>
                <td className="pr-2 text-right">{N(at("peak_discharge_hour"), true)}{at("peak_discharge_hour") ? ":00" : ""}</td>
                <td className="pr-2 text-right">{N(at("peak_charge_hour"), true)}{at("peak_charge_hour") ? ":00" : ""}</td>
                <td>
                  <InlineSpark values={dis.slice(-30).map((r) => ({ t: r.ts_utc, v: r.value }))} label={`${b.label} battery MWh discharged per day, last 30 days`} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="mt-1 text-[11px] text-muted">
        From EIA-930&apos;s hourly battery net generation (positive discharging, negative charging), complete local days only;
        CAISO&apos;s row from CAISO&apos;s own 5-minute Total batteries, averaged to hours, complete Pacific days.
        Out over in is the day&apos;s energy discharged over energy charged as reported, not a measured efficiency: charge
        carried across midnight moves it. Hours are local, the hour&apos;s start.
      </p>
    </div>
  );
}

/** The CAISO line's own tier chip and citation: CAISO's data, not EIA-930's. */
function CaisoCite() {
  return (
    <>
      <p className="mt-2 text-xs text-muted">
        The CAISO line is CAISO&apos;s own data<Tier tier="source" />, not EIA-930&apos;s: Today&apos;s Outlook &quot;Total batteries&quot;
        (hybrid plants&apos; batteries included), 5-minute values averaged to UTC hours.
      </p>
      <Cite tables={["caiso_battery_storage"]} note="California ISO, Today's Outlook, storage history files" />
    </>
  );
}

export default async function Storage() {
  const since30 = daysAgo(31);
  const [units, cycle, hourly, caiso] = await Promise.all([
    attempt(storageUnits),
    attempt(() => series("storage_daily_cycle", { since: daysAgo(45) })),
    attempt(() => series("eia930_all_storage", { variable: "net_generation_battery_mw", since: since30 })),
    attempt(() => series("caiso_battery_storage", { variable: "batteries_mw", since: since30 })),
  ]);
  const caisoPoints = caiso.ok ? caisoHourly(caiso.data) : [];
  const lines = (from: number): Line[] =>
    hourly.ok
      ? [
          ...BAS.filter((b) => b.code !== "us48").map((b) => ({
            label: b.label,
            color: b.color,
            points: hourly.data.filter((r) => r.entity === b.entity && new Date(r.ts_utc).getTime() >= from)
              .map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })),
          })),
          ...(caisoPoints.length
            ? [{ label: "CAISO (CAISO's data)", color: CAISO.color, points: caisoPoints.filter((p) => p.t * 1000 >= from && p.t * 1000 <= newest) }]
            : []),
        ]
      : [];
  const newest = hourly.ok && hourly.data.length ? Math.max(...hourly.data.map((r) => new Date(r.ts_utc).getTime())) : 0;
  const us48 = hourly.ok ? hourly.data.filter((r) => r.entity === "eia930:US48") : [];
  return (
    <>
      <h1 className="mb-1 text-3xl">Battery storage</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        The US battery fleet from EIA&apos;s monthly generator inventory, and how the batteries charge and discharge each
        hour from EIA-930. <Link href={METHOD}>Method</Link>.
      </p>

      <Section title="The fleet" aside={<>EIA-860M<Tier tier="derived" /></>}>
        {units.ok ? <Fleet units={units.data} /> : <NoData what="the fleet" reason={units.reason} />}
        <Cite tables={["storage_capacity"]} note="Nameplate MW of every battery unit (prime mover BA) in EIA-860M, by EIA's status, and its Nameplate Energy Capacity (MWh) where EIA gives it: for operating and retired units, not for planned ones (EIA's Planned sheet has no such column). MWh is never estimated from MW" />
      </Section>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="mb-8 min-w-0" aria-label="By ISO">
          <h2 className="mb-2 border-b border-rule pb-1 text-xl">By ISO<Tier tier="derived" /></h2>
          {units.ok ? <ByIso units={units.data} /> : <NoData what="the fleet by ISO" reason={units.reason} />}
          <Cite tables={["storage_capacity"]} note="The ISO is the unit's balancing authority when it is one of the seven" />
        </section>
        <section className="mb-8 min-w-0" aria-label="By state">
          <h2 className="mb-2 border-b border-rule pb-1 text-xl">By state<Tier tier="derived" /></h2>
          {units.ok ? <ByState units={units.data} /> : <NoData what="the fleet by state" reason={units.reason} />}
          <Cite tables={["storage_capacity"]} />
        </section>
      </div>

      <Section title="Planned additions by year" aside={<Tier tier="derived" />}>
        {units.ok ? <ByYear units={units.data} /> : <NoData what="planned additions" reason={units.reason} />}
        <Cite tables={["storage_capacity"]} note="Units under construction or planned, by the year of EIA's planned operation date" />
      </Section>

      <Section title="The daily cycle" aside={<Tier tier="derived" />}>
        {cycle.ok && cycle.data.length ? <Cycle rows={cycle.data} /> : <NoData what="the daily cycle" reason={cycle.ok ? "storage_daily_cycle returned no rows" : cycle.reason} />}
        <Cite tables={["storage_daily_cycle"]} note="Derived from eia930_all_storage; CAISO's row from caiso_battery_storage, CAISO's own data, because CAISO reports no battery series in EIA-930. NYISO and PJM report none in either" />
      </Section>

      <Section title="Hour by hour, the last 30 days" aside={<Tier tier="source" />}>
        {hourly.ok && newest ? (
          <>
            <LineChart lines={lines(newest - 30 * 86_400_000)} unit="MW" height={240} ariaLabel="Battery net generation by ISO, hourly, last 30 days" />
            <LineChart lines={[{ label: "US Lower 48", color: "ink", points: us48.map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })) }]}
              unit="MW" height={180} ariaLabel="US Lower 48 battery net generation, hourly, last 30 days" />
          </>
        ) : (
          <NoData what="the hourly series" reason={hourly.ok ? "eia930_all_storage returned no rows in the last 30 days" : hourly.reason} />
        )}
        <Cite tables={["eia930_all_storage"]} note="EIA-930 net generation of battery storage, MW: above zero discharging, below zero charging. UTC hours" />
        <CaisoCite />
      </Section>

      <Section title="The last 24 hours" aside={<Tier tier="source" />}>
        {hourly.ok && newest ? (
          <LineChart lines={lines(newest - 23 * 3_600_000)} unit="MW" height={220} ariaLabel="Battery net generation by ISO, the last 24 hours EIA has published" />
        ) : (
          <NoData what="the last 24 hours" reason={hourly.ok ? "no rows" : hourly.reason} />
        )}
        <Cite tables={["eia930_all_storage"]} note={newest ? `The 24 hours to ${new Date(newest).toISOString().slice(0, 16).replace("T", " ")} UTC, the newest EIA has published for every hour of its day` : undefined} />
        <CaisoCite />
      </Section>
    </>
  );
}
