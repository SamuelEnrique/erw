import type { Metadata } from "next";
import { SiteLink } from "@/components/SiteLink";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Legend } from "@/components/StackedArea";
import { HOURLY_FUELS, Hourly, LATEST, MONTHLY, Missing, Monthly, Today } from "@/components/mix/Now";
import { Chips, CleanView, DayView, DuckView, ForecastView, HistoryView, RecordsView, StressView, SupplyView } from "@/components/mix/views";
import { daysAgo, series } from "@/lib/data";
import { GRIDS, calName, periodOf } from "@/lib/mix2";
import { CLEAN, HISTORY, MIX, PLUS, STRESS } from "@/lib/mixdata";
import { FACTORS, MAX_GRIDS, SEASON_NAMES, VIEWS, choiceOf, hrefOf, toggled, type Choice } from "@/lib/mixpage";
import { BAS, STATES } from "@/lib/regions";
import { attempt } from "@/lib/supabase";

// Session 133: the energy mix, one page at one address. It holds what /mix (session 18), /mix/v2 (94), /mix/clean (122)
// and /mix/stress (123) showed, as views of this page (those addresses redirect here: next.config.ts; their pages are
// kept, unrouted, under app/_retired), and the views the session added. The original page is the first view, with its
// filters and hover as they were. The whole state is in the address. No method stands on the page face: it is in
// docs/methods/generation_mix_hourly.md.
export const revalidate = 3600;
export const metadata: Metadata = { title: "Energy mix", robots: { index: false, follow: false } };

const METHOD = "/data/methods/generation_mix_hourly";

function Controls({ c }: { c: Choice }) {
  const perGrid = !["now", "forecast", "history"].includes(c.view);
  const first = c.grids[0];
  const years = (() => {
    if (c.view === "clean") return Object.keys(CLEAN[first].years).sort();
    if (c.view === "stress") return Object.keys(STRESS[first].years).sort();
    if (c.view === "supply") return Object.keys(PLUS[first].availability).sort();
    if (c.view === "records") return Object.keys(PLUS[first].records).filter((y) => y !== "all").sort();
    return Object.keys(MIX[first].years).sort();
  })();
  const period = c.period ?? MIX[first].upto;
  const py = period.slice(0, 4);
  const allYears = Array.from({ length: Number(MIX[first].upto.slice(0, 4)) - 2018 }, (_, i) => String(2019 + i));
  return (
    <div className="mb-5 grid gap-1.5 border-y border-rule py-2" data-controls="1">
      {perGrid ? (
        <Chips label="Select grids" items={GRIDS.map((g) => { const on = c.grids.includes(g.slug); const full = !on && c.grids.length >= MAX_GRIDS;
          return { key: g.slug, label: g.name, on, off: full, title: full ? `Up to ${MAX_GRIDS} grids at once: take one off first.` : on && c.grids.length === 1 ? "The last grid stays." : undefined, href: hrefOf(c, { grids: toggled(c.grids, g.slug) }) }; })} />
      ) : null}
      {c.view === "day" ? (
        <>
          <Chips label="Year" items={allYears.map((y) => ({ key: y, label: y, on: py === y, href: hrefOf(c, { period: period.length === 7 && periodOf(MIX[first], `${y}-${period.slice(5)}`) ? `${y}-${period.slice(5)}` : y }) }))} />
          <Chips label="Month" items={[{ key: "year", label: "Whole year", on: period.length === 4, off: !MIX[first].years[py], title: MIX[first].years[py] ? undefined : `${py} is not written for ${GRIDS.find((g) => g.slug === first)!.name}: more than one of its months is missing.`, href: hrefOf(c, { period: py }) },
            ...Array.from({ length: 12 }, (_, i) => { const m = `${py}-${String(i + 1).padStart(2, "0")}`; const held = c.grids.some((g) => MIX[g].months[m]);
              return { key: m, label: calName(m.slice(5)).slice(0, 3), on: period === m, off: !held, title: held ? calName(m.slice(5)) : `${calName(m.slice(5))} ${py} is not held for the grids chosen.`, href: hrefOf(c, { period: m }) }; })]} />
        </>
      ) : null}
      {c.view === "duck" ? <Chips label="Month" items={Array.from({ length: 12 }, (_, i) => { const m = String(i + 1).padStart(2, "0"); return { key: m, label: calName(m).slice(0, 3), title: calName(m), on: (c.cal ?? "04") === m, href: hrefOf(c, { cal: m }) }; })} /> : null}
      {["records", "clean", "stress", "supply"].includes(c.view) || (c.view === "duck" && c.grids.length > 1)
        ? <Chips label="Year" items={years.map((y) => ({ key: y, label: y, on: c.year === y, href: hrefOf(c, { year: y }) }))} /> : null}
      {c.view === "supply" ? <Chips label="Season" items={SEASON_NAMES.map(([k, label]) => ({ key: k, label, on: c.season === k, href: hrefOf(c, { season: k }) }))} /> : null}
      {c.view === "day" || c.view === "duck" ? (
        <>
          <Chips label="Scale" items={[{ key: "mw", label: "MW", on: c.norm === "mw", href: hrefOf(c, { norm: "mw" }) }, { key: "peak", label: "Share of peak", on: c.norm === "peak", title: "Each grid's MW as a percent of the highest hour of its average-day demand in the period, so small grids compare with large ones.", href: hrefOf(c, { norm: "peak" }) }]} />
          <Chips label="Add factors" items={FACTORS.map(([k, label]) => ({ key: k, label, on: c.factor === k, href: hrefOf(c, { factor: k }) }))} />
        </>
      ) : null}
      {c.view === "forecast" ? <Chips label="Source" items={(["wind", "solar"] as const).map((s) => ({ key: s, label: s === "wind" ? "Wind" : "Solar", on: c.src === s, href: hrefOf(c, { src: s }) }))} /> : null}
      {c.view === "history" ? (
        <>
          <Chips label="Select states" items={Object.keys(STATES).filter((s) => HISTORY.states[s]).map((s) => { const on = c.states.includes(s); const full = !on && c.states.length >= MAX_GRIDS;
            return { key: s, label: s, on, off: full, title: full ? `${STATES[s]}. Up to ${MAX_GRIDS} at once: take one off first.` : STATES[s], href: hrefOf(c, { states: toggled(c.states, s) }) }; })} />
          <Chips label="Scale" items={[{ key: "mw", label: "Million MWh", on: c.norm === "mw", href: hrefOf(c, { norm: "mw" }) }, { key: "peak", label: "Share of generation", on: c.norm === "peak", href: hrefOf(c, { norm: "peak" }) }]} />
        </>
      ) : null}
    </div>
  );
}

async function NowView({ c }: { c: Choice }) {
  const ba = BAS.find((b) => b.code === c.ba) ?? BAS[0];
  const st = c.state && c.state in STATES ? c.state : "US";
  const table = "eia930_all_generation";
  const [latest, hourly, monthly] = await Promise.all([
    attempt(() => series(LATEST, { entity: ba.entity })),
    attempt(() => series(table, { entity: ba.entity, since: daysAgo(9) })),
    attempt(() => series(MONTHLY, { entity: `eia:${st}` })),
  ]);
  // session 118: EIA-930's generation for California is the series the faults register calls changed; it is not drawn
  const withheld = ba.code === "ciso";
  const caiso = "EIA's hourly generation series for California changed on 16 December 2025 and is not drawn. California's mix from CAISO's own data is in the views beside this one.";
  const failed = (reason: string) => <Missing why={`The table could not be read just now: ${reason}`} words="working on it" />;
  const h2 = "mb-2 border-b border-accent pb-0.5 font-serif text-lg text-accent";
  return (
    <>
      <form method="get" className="mb-6 flex flex-wrap items-end gap-4" data-now-form="1">
        <AutoSubmitSelect name="ba" label="Grid operator (hourly)" value={ba.code} options={BAS.map((b) => ({ value: b.code, label: b.label }))} />
        <AutoSubmitSelect name="state" label="State (monthly)" value={st} options={Object.entries(STATES).map(([k, v]) => ({ value: k, label: v }))} />
        <button type="submit" className="border border-rule bg-panel px-3 py-1 text-sm">Show</button>
      </form>
      <section id="today" className="mb-8">
        <h2 className={h2}>{ba.label}: today so far</h2>
        {withheld ? <Missing why={caiso} /> : latest.ok ? <Today rows={latest.data} label={ba.label} /> : failed(latest.reason)}
      </section>
      <section id="hourly" className="mb-8">
        <h2 className={h2}>{ba.label}: hourly mix, last 7 days</h2>
        <Legend items={HOURLY_FUELS.map((f) => ({ key: f.key, label: f.label, color: `var(--color-fuel-${f.key})` }))} />
        {withheld ? <Missing why={caiso} /> : hourly.ok ? <Hourly rows={hourly.data} table={table} label={ba.label} /> : failed(hourly.reason)}
      </section>
      <section id="monthly" className="mb-8">
        <h2 className={h2}>{STATES[st]}: monthly mix since 2001</h2>
        {monthly.ok ? <Monthly rows={monthly.data} st={st} /> : failed(monthly.reason)}
      </section>
    </>
  );
}

export default async function MixPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const c = choiceOf(await searchParams);
  return (
    <div className="border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-mix={c.view}>
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h1 className="font-serif text-3xl text-accent">Energy mix</h1>
        <p className="text-xs text-muted"><SiteLink href={METHOD}>Method, sources and gaps</SiteLink></p>
      </header>
      <nav aria-label="Views" className="mb-3 flex flex-wrap gap-1 text-xs" data-views="1">
        {VIEWS.map(([k, label]) => (
          <a key={k} href={hrefOf(c, { view: k })} aria-current={c.view === k ? "page" : undefined} data-view={k}
            className={`border px-2 py-1 no-underline ${c.view === k ? "border-accent bg-accent text-white" : "border-rule bg-white text-ink hover:border-accent"}`}>{label}</a>
        ))}
      </nav>
      {c.view === "now" ? null : <Controls c={c} />}
      {c.view === "now" ? <NowView c={c} /> : null}
      {c.view === "day" ? <DayView c={c} /> : null}
      {c.view === "duck" ? <DuckView c={c} /> : null}
      {c.view === "records" ? <RecordsView c={c} /> : null}
      {c.view === "clean" ? <CleanView c={c} /> : null}
      {c.view === "stress" ? <StressView c={c} /> : null}
      {c.view === "supply" ? <SupplyView c={c} /> : null}
      {c.view === "forecast" ? <ForecastView c={c} /> : null}
      {c.view === "history" ? <HistoryView c={c} /> : null}
    </div>
  );
}
