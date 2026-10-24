import { SiteLink } from "@/components/SiteLink";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Legend } from "@/components/StackedArea";
import { HOURLY_FUELS, Hourly, LATEST, MONTHLY, Missing, Monthly, Today } from "@/components/mix/Now";
import { Chips, CleanView, DayView, DuckView, ForecastView, HistoryView, RecordsView, StressView, SupplyView } from "@/components/mix/views";
import { caisoJoinDay } from "@/lib/caisoJoin";
import { daysAgo, renderTime, series, type SeriesRow } from "@/lib/data";
import { GRIDS, calName, periodOf } from "@/lib/mix2";
import { CLEAN, HISTORY, MIX, PLUS, STRESS } from "@/lib/mixdata";
import { ALL_GRIDS, FACTORS, MAX_GRIDS, NO_GRID_CHOICE, SEASON_NAMES, VIEWS, filtered, gridUse, hrefOf, toggled, type Choice } from "@/lib/mixpage";
import { gridHref } from "@/lib/gridtool";
import { BAS, STATES } from "@/lib/regions";
import { attempt, HOURLY, rest } from "@/lib/supabase";
import { HourlyFigures, MONTH_VARIABLES, MonthlyFigures } from "@/components/grid/MixFigures";
import { DEMAND, PROFILE, mixHourly } from "@/lib/mixHourly";
import { EMERGENCIES, gridNotices } from "@/lib/reliability";
import { ercotNotices } from "@/lib/gridErcotNotices";
import { CAISO_HOLDS, generationSince, wholeRead } from "@/lib/gridReads";

// Session 133: the energy mix, one page at one address. It holds what /mix (session 18), /mix/v2 (94), /mix/clean (122)
// and /mix/stress (123) showed, as views of this page (those addresses redirect here: next.config.ts; their pages are
// kept, unrouted, under app/_retired), and the views the session added. The original page is the first view, with its
// filters and hover as they were. The whole state is in the address. No method stands on the page face: it is in
// docs/methods/generation_mix_hourly.md.
// Session 168: "Select grids" stands on every view (lib/mixpage.ts gridUse). The seven views that had it compare the
// grids chosen as before; "Now and by state" and "Wind and solar forecasts" open with every grid, as they did, and draw
// only the grids chosen once some are; "Since 2001" is by state, so its control is greyed and its hover says why.
// Session 237: this file was app/mix/page.tsx. /mix redirects to the Mix view of the Grid tool (/grid, next.config.ts),
// which draws this page whole (MixView): its nine views, its controls and its numbers as they were, at addresses
// under the tool's own (lib/mixpage.ts base). "How clean, and when" is the tool's Clean view (MixClean).

const METHOD = "/data/methods/generation_mix_hourly";

function Controls({ c }: { c: Choice }) {
  const use = gridUse(c.view);
  const every = c.shown.length === ALL_GRIDS.length;
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
      {use === "compare" ? (
        <Chips label="Select grids" items={GRIDS.map((g) => { const on = c.grids.includes(g.slug); const full = !on && c.grids.length >= MAX_GRIDS;
          return { key: g.slug, label: g.name, on, off: full, title: full ? `Up to ${MAX_GRIDS} grids at once: take one off first.` : on && c.grids.length === 1 ? "The last grid stays." : undefined, href: hrefOf(c, { grids: toggled(c.grids, g.slug) }) }; })} />
      ) : use === "filter" ? (
        <Chips label="Select grids" items={GRIDS.map((g) => { const on = c.shown.includes(g.slug);
          return { key: g.slug, label: g.name, on, title: every ? `Show ${g.name} alone.` : on && c.shown.length === 1 ? "Show every grid again." : undefined, href: hrefOf(c, { shown: filtered(c.shown, g.slug) }) }; })} />
      ) : (
        <Chips label="Select grids" items={GRIDS.map((g) => ({ key: g.slug, label: g.name, on: false, off: true, title: NO_GRID_CHOICE, href: "" }))} />
      )}
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

/** Session 168: the EIA-930 balancing authority of each grid of "Select grids" (lib/regions.ts BAS). */
const GRID_BA: Record<string, string> = { ercot: "erco", caiso: "ciso", pjm: "pjm", miso: "miso", spp: "swpp", nyiso: "nyis", isone: "isne" };
/** Session 1152: the grid of each operator of the list (the Grid tool's slug), for the energy mix panel's name. */
const BA_GRID: Record<string, string> = { ...Object.fromEntries(Object.entries(GRID_BA).map(([g, b]) => [b, g])), us48: "us48" };

/** Session 1152: the energy mix panel's two views, as chips; the choice is in the address (mixp=month). */
function PanelToggle({ c, month }: { c: Choice; month: boolean }) {
  return (
    <div className="mb-2" data-mix-panel-toggle={month ? "month" : "hour"}>
      <Chips label="View" items={[
        { key: "hour", label: "Hourly, last 7 days", on: !month, href: `${hrefOf({ ...c, mixp: undefined })}#hourly`, title: "EIA-930's hourly generation by fuel (eia930_all_generation)" },
        { key: "month", label: "By month", on: month, href: `${hrefOf({ ...c, mixp: "month" })}#hourly`, title: "The grid's monthly mix (generation_mix_hourly_profile)" },
      ]} />
    </div>
  );
}

async function NowView({ c }: { c: Choice }) {
  // session 168: with every grid on (as the view opens) the operator list chooses the one drawn, as before; once grids
  // are chosen above, each of them is drawn, in the list's order, and the list gives way to the choice
  const chosen = c.shown.length < ALL_GRIDS.length ? BAS.filter((b) => c.shown.some((g) => GRID_BA[g] === b.code)) : null;
  const bas = chosen ?? [BAS.find((b) => b.code === c.ba) ?? BAS[0]];
  const ba = bas[0];
  const st = c.state && c.state in STATES ? c.state : "US";
  const table = "eia930_all_generation";
  // session 1152: the energy mix panel's view (hourly, the default, or by month) and its own read: the demand of the
  // same days (the peak hour), or the grid's months of generation_mix_hourly_profile (none for the Lower 48)
  const month = c.mixp === "month";
  const extra = (b: (typeof BAS)[number]) => {
    const g = BA_GRID[b.code];
    if (month) return g && g !== "us48" ? attempt(() => rest<SeriesRow>("series", { select: "entity,variable,ts_utc,value,unit", table_name: `eq.${PROFILE}`, entity: `eq.iso:${g}`,
      variable: `in.(${MONTH_VARIABLES.join(",")})`, ts_utc: `gte.${daysAgo(800).slice(0, 7)}-01T00:00:00Z`, order: "entity,variable,ts_utc" }, HOURLY)) : Promise.resolve(null);
    return b.code === "ciso" ? Promise.resolve(null) : attempt(() => series(DEMAND, { entity: b.entity, variable: "demand_mw", since: daysAgo(9) }));
  };
  // session 1155: CAISO's notices, for the alert days of its monthly view (the same read as the Reliability section)
  // session 1174: ERCOT's notices, for the call days of its monthly view (the same read as its state line)
  const [reads, monthly, extras, notices, ercotN] = await Promise.all([
    // session 1179: the 9 days out of the render's read of the grid's generation when the page shares one (lib/gridReads.ts)
    Promise.all(bas.map((b) => Promise.all([attempt(() => series(LATEST, { entity: b.entity })), attempt(() => generationSince(b.entity, daysAgo(9)))]))),
    attempt(() => series(MONTHLY, { entity: `eia:${st}` })),
    Promise.all(bas.map(extra)),
    // session 1181: the whole table answering no row is a failed read (lib/gridReads.ts wholeRead), never "no month marked"
    wholeRead(EMERGENCIES, CAISO_HOLDS, month && bas.some((b) => b.code === "ciso") ? attempt(() => gridNotices()) : Promise.resolve(null)),
    month && bas.some((b) => b.code === "erco") ? attempt(() => ercotNotices()) : Promise.resolve(null),
  ]);
  const now = renderTime();
  // session 118: EIA-930's generation for California is the series the faults register calls changed; it is not drawn
  const caiso = `EIA's hourly generation series for California changed on ${caisoJoinDay()} and is not drawn. California's mix from CAISO's own data is in the views beside this one.`;
  const failed = (reason: string) => <Missing why={`The table could not be read just now: ${reason}`} words="working on it" />;
  const h2 = "mb-2 border-b border-accent pb-0.5 font-serif text-lg text-accent";
  return (
    <>
      <form method="get" className="mb-6 flex flex-wrap items-end gap-4" data-now-form="1">
        {c.base ? <><input type="hidden" name="view" value="mix" />{chosen ? <input type="hidden" name="grid" value={c.base.grid} /> : null}</> : null}
        {month ? <input type="hidden" name="mixp" value="month" /> : null}
        {chosen ? (
          <>
            <input type="hidden" name="grids" value={c.shown.join(",")} />
            <span className="flex flex-col text-xs text-muted" data-now-grids={c.shown.join(",")}>Grid operator (hourly)
              <span className="mt-1 cursor-help border border-rule/60 px-2 py-1 text-sm" title="The grids chosen above are drawn; choose every grid again to use this list.">{chosen.map((b) => b.label).join(", ")}</span></span>
          </>
        ) : <AutoSubmitSelect name="ba" label="Grid operator (hourly)" value={ba.code} options={BAS.map((b) => ({ value: b.code, label: b.label }))} />}
        <AutoSubmitSelect name="state" label="State (monthly)" value={st} options={Object.entries(STATES).map(([k, v]) => ({ value: k, label: v }))} />
        <button type="submit" className="border border-rule bg-panel px-3 py-1 text-sm">Show</button>
      </form>
      {bas.map((b, i) => {
        const [latest, hourly] = reads[i];
        const withheld = b.code === "ciso";
        const more = extras[i];
        const grid = BA_GRID[b.code] ?? b.code;
        const figures = !month && !withheld && hourly.ok ? mixHourly(hourly.data, more && more.ok ? more.data : [], HOURLY_FUELS) : null;
        return (
          <div key={b.code} data-now-ba={b.code}>
            <section id={i ? `today-${b.code}` : "today"} className="mb-8">
              <h2 className={h2}>{b.label}: today so far</h2>
              {withheld ? <Missing why={caiso} /> : latest.ok ? <Today rows={latest.data} label={b.label} /> : failed(latest.reason)}
            </section>
            <section id={i ? `hourly-${b.code}` : "hourly"} className="mb-8">
              <h2 className={h2}>{month ? `${b.label}: monthly mix, by grid` : <>{b.label}: hourly mix, last 7 days</>}</h2>
              {/* session 1152: the energy mix panel, its figures keyed (lib/mixHourly.ts), its two views in the address */}
              <div data-grid-panel={`grid_mix_${grid}`}>
                <PanelToggle c={c} month={month} />
                {month ? (
                  grid === "us48" ? <Missing why="generation_mix_hourly_profile is built for the seven ISO grids, not for the Lower 48: its monthly mix by state is below." words="not built for the Lower 48" />
                    : more && more.ok ? <MonthlyFigures rows={more.data} label={b.label} caiso={withheld} notices={withheld ? notices : undefined} ercot={b.code === "erco" ? ercotN : undefined} /> : failed(more && !more.ok ? more.reason : "no read")
                ) : figures ? <HourlyFigures m={figures} label={b.label} now={now} demandFailed={more && !more.ok ? more.reason : undefined} />
                  // session 1181: the grid's generation could not be read: the panel says so in its own place, and draws no figure
                  : !month && !withheld && !hourly.ok ? <p className="mb-2 text-sm" data-mix-unread="1">The hourly mix: {failed(hourly.reason)}</p> : null}
                {!month && withheld ? <p className="mb-2 text-xs text-muted">California&apos;s monthly mix, from CAISO&apos;s own data since January 2026, is under &quot;By month&quot;.</p> : null}
              </div>
              {month ? null : (
                <>
                  <Legend items={HOURLY_FUELS.map((f) => ({ key: f.key, label: f.label, color: `var(--color-fuel-${f.key})` }))} />
                  {withheld ? <Missing why={caiso} /> : hourly.ok ? <Hourly rows={hourly.data} table={table} label={b.label} share through={figures?.newest.t}
                    marks={figures?.peak ? [{ t: figures.peak.t, name: `Peak demand, ${new Date(figures.peak.t).toISOString().slice(11, 16)} UTC` }] : undefined} /> : failed(hourly.reason)}
                </>
              )}
            </section>
          </div>
        );
      })}
      <section id="monthly" className="mb-8">
        <h2 className={h2}>{STATES[st]}: monthly mix since 2001</h2>
        {monthly.ok ? <Monthly rows={monthly.data} st={st} /> : failed(monthly.reason)}
      </section>
    </>
  );
}

/** Session 237: the energy mix page, whole, as the Mix view of the Grid tool. */
export function MixView({ c }: { c: Choice }) {
  return (
    <div className="border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-mix={c.view}>
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h2 className="font-serif text-3xl text-accent">Energy mix</h2>
        <p className="text-xs text-muted"><SiteLink href={METHOD}>Method, sources and gaps</SiteLink></p>
      </header>
      <nav aria-label="Views of the mix" className="mb-3 flex flex-wrap gap-1 text-xs" data-views="1">
        {VIEWS.map(([k, label]) => (
          <a key={k} href={k === "clean" && c.base ? gridHref(c.base.grid, "clean") : hrefOf(c, { view: k })} aria-current={c.view === k ? "page" : undefined} data-view={k} style={{ color: c.view === k ? "var(--color-surface)" : "var(--color-ink)" }}
            className={`border px-2 py-1 no-underline ${c.view === k ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{label}</a>
        ))}
      </nav>
      <Controls c={c} />
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

/** Session 237: "How clean, and when" (the mix page's view, /mix/clean until session 133), as the Clean view draws it. */
export function MixClean({ c }: { c: Choice }) {
  return (
    <div className="border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-mix="clean">
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h2 className="font-serif text-3xl text-accent">How clean, and when</h2>
        <p className="text-xs text-muted"><SiteLink href={METHOD}>Method, sources and gaps</SiteLink></p>
      </header>
      <Controls c={c} />
      <CleanView c={c} />
    </div>
  );
}
