import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { caisoJoinDay } from "@/lib/caisoJoin";
import { GRIDS, TABLE, at, defaultYear, fuelRows, get, href, isGrid, one, pct, span, when, whole, wholeYear, yearsOf, type GridFile } from "@/lib/stress";
import { FILES } from "./data";

// Session 123: "How hard the system works", in review (lib/release.ts), in the battery page's layout. For each of the
// seven grids and each year since 2019: the evening ramp of net load, the lowest net load and when, what each fuel gave
// in the 100 tightest hours as a share of its installed capacity, and the longest dark, calm stretch with what it
// would take the grid's batteries to cover it. Every number is a row of grid_stress_yearly (warehouse/derived/
// mix_stress.py; docs/methods/grid_stress.md), read from the site's own copy (app/mix/stress/data.ts); the page does no
// arithmetic. Each definition is stated on the page as it is computed. The panel's links are plain next/link.
export const metadata: Metadata = { title: "How hard the system works", robots: { index: false, follow: false } };

const METHOD = "/data/methods/grid_stress";
const notHeld = <span className="text-muted">not held</span>;
const show = (v: string) => (v === "not held" ? notHeld : v);

/** The largest evening ramp of each year as a share of that year's peak demand: one-hour and three-hour, a pair of bars a year. */
function RampBars({ f, years, chosen }: { f: GridFile; years: string[]; chosen: string }) {
  const W = 760, H = 270, L = 44, R = 10, top = 22, bot = 40;
  const v1 = years.map((y) => get(f, y, "evening_ramp_max_share_of_peak_pct")), v3 = years.map((y) => get(f, y, "evening_ramp_3h_max_share_of_peak_pct"));
  const hi = Math.max(10, ...[...v1, ...v3].filter((x): x is number => x !== null)) * 1.15;
  const step = hi > 40 ? 10 : 5;
  const ticks: number[] = [];
  for (let t = 0; t <= hi; t += step) ticks.push(t);
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  const bw = (W - L - R) / years.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-ramp-bars={f.grid} aria-label={`${f.name}: the largest evening ramp of net load each year, as a share of the year's peak demand`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      <text x={L - 38} y={12} fontSize="11" fill="var(--color-muted)">percent of the year&apos;s peak demand</text>
      {years.map((yr, i) => {
        const x0 = L + i * bw + bw * 0.14, w = bw * 0.34, a = v1[i], b = v3[i];
        return (
          <g key={yr} data-ramp-year={yr} opacity={yr === chosen ? 1 : 0.7}>
            {a === null ? null : <><rect x={x0} width={w} y={y(a)} height={Math.max(0.5, y(0) - y(a))} fill="var(--color-accent)" /><text x={x0 + w / 2} y={y(a) - 5} textAnchor="middle" fontSize="10" fill="var(--color-ink)">{a.toFixed(1)}</text></>}
            {b === null ? null : <><rect x={x0 + w + 2} width={w} y={y(b)} height={Math.max(0.5, y(0) - y(b))} fill="var(--color-ink)" /><text x={x0 + w * 1.5 + 2} y={y(b) - 5} textAnchor="middle" fontSize="10" fill="var(--color-ink)">{b.toFixed(1)}</text></>}
            <text x={x0 + w + 1} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)" fontWeight={yr === chosen ? 700 : 400}>{yr}</text>
            {wholeYear(f, yr) ? null : <text x={x0 + w + 1} y={H - bot + 30} textAnchor="middle" fontSize="10" fill="var(--color-muted)">to date</text>}
            <title>{`${yr}: the largest one-hour evening rise of net load was ${a === null ? "not held" : `${a.toFixed(1)} percent`} of the year's peak demand; the largest three-hour rise ${b === null ? "not held" : `${b.toFixed(1)} percent`}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

export default async function Stress({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const grid = isGrid(sp.grid) ? sp.grid : "ercot";
  const f = FILES[grid];
  const years = yearsOf(f);
  const year = typeof sp.year === "string" && years.includes(sp.year) ? sp.year : defaultYear(f);
  const g = (k: string) => (year ? get(f, year, k) : null);
  const t = (k: string) => (year ? when(at(f, year, k), f.tz) : "not held");
  const fuels = year ? fuelRows(f, year) : [];
  const solarOff = year ? get(f, year, "solar_reported") === 0 : false;
  const windOff = year ? get(f, year, "wind_reported") === 0 : false;
  const [w0, w1] = f.window;

  return (
    <ToolPage>
      <ToolHeader
        title="How hard the system works"
        lead={<span data-stress-what="1">Four measures of strain on a grid, by year, each defined on this page as it is computed: how fast demand net of wind and solar rises in the evening, how low it falls,
          what each kind of plant gives in the hours that are tightest, and how long wind and solar can stay near nothing. From the hourly figures each grid reports; a year is left out where too many of its hours are
          missing or faulty, and nothing is filled. <SiteLink href={METHOD}>Method</SiteLink>.</span>}
      />
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Grid">
            <ul className="space-y-1 text-sm">
              {GRIDS.map((x) => <li key={x}>{x === grid ? <strong data-stress-grid={x}>{FILES[x].name}</strong> : <Link href={href(x, year && FILES[x].years[year] ? year : null)} className="underline">{FILES[x].name}</Link>}</li>)}
            </ul>
          </InputPanel>
          <InputPanel title="Year" note={<>A year is written when it holds at least nine tenths of its hours. The newest year runs to the last hour held and is not a whole year: its records can still be beaten.</>}>
            <ul className="flex flex-wrap gap-x-3 gap-y-1 text-sm">
              {years.map((y) => <li key={y}>{y === year ? <strong data-stress-year={y}>{y}</strong> : <Link href={href(grid, y)} className="underline">{y}</Link>}{wholeYear(f, y) ? "" : "*"}</li>)}
            </ul>
            <p className="mt-2 text-xs text-muted">* to date</p>
          </InputPanel>
          <InputPanel title="The definitions">
            <ul className="list-disc space-y-1.5 pl-4 text-sm">
              <li><strong>Net load.</strong> Demand less wind less solar, hour by hour.</li>
              <li><strong>The evening ramp.</strong> The largest rise of net load from one hour to the next between {w0}:00 and {w1}:00 local time, each day; and the largest rise over three hours in the same window.</li>
              <li><strong>The tightest hours.</strong> The {f.tight} hours of the year with the highest net load.</li>
              <li><strong>Dark and calm.</strong> An hour in which wind and solar together put out less than {f.calm_pct} percent of their installed capacity. A stretch is a run of such hours with no gap.</li>
              <li><strong>Hours not used.</strong> An hour the source&apos;s own balance does not close for, an hour that repeats the one before to the MW, and a one-hour rise the next hour takes back: they are in the file and would be records.</li>
            </ul>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!year || g("peak_demand_mw") === null ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-stress-state="none">No year of {f.name} is held, so no number is shown.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-stress-summary="1">
                In {year}{wholeYear(f, year) ? "" : " to date"}, {f.name}&apos;s net load rose by as much as {whole(g("evening_ramp_max_mw_per_h"))} MW in one evening hour, {pct(g("evening_ramp_max_share_of_peak_pct"))} of the
                year&apos;s peak demand, and fell as low as {whole(g("net_load_min_mw"))} MW.
              </p>
              {grid === "caiso" ? (
                <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-stress-join="1">
                  <strong>California is two series, not one.</strong> Until {caisoJoinDay()} its wind and solar are the federal energy agency&apos;s (EIA); from that day they are the California grid operator&apos;s own, which
                  run higher, while demand stays EIA&apos;s throughout. A step between the last year on one and the first on the other is partly the change of source. <SiteLink href="/data/methods/eia930_caiso_break">The note on the break</SiteLink>.
                </p>
              ) : null}
              {solarOff || windOff ? (
                <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-stress-unreported="1">
                  <strong>{f.name}&apos;s {solarOff && windOff ? "wind and solar are" : solarOff ? "solar is" : "wind is"} not in the source file for {year}.</strong> Net load here is demand less {solarOff && windOff ? "nothing" : solarOff ? "wind only" : "solar only"},
                  and the installed capacity in the dark, calm measure is {solarOff && windOff ? "none" : solarOff ? "wind's only" : "solar's only"}. The figures understate how far net load falls at midday.
                </p>
              ) : null}

              <HeadlineRow>
                <HeadlineNumber label={`Largest evening ramp, ${year}`} value={<span data-stress-ramp={year} data-stress-raw={g("evening_ramp_max_mw_per_h") ?? ""}>{show(whole(g("evening_ramp_max_mw_per_h")))}</span>} unit="MW in one hour"
                  note={<>Starting {t("evening_ramp_max_mw_per_h")}. The median day&apos;s largest evening rise: {whole(g("evening_ramp_median_mw_per_h"))} MW in an hour.</>} />
                <HeadlineNumber label="Lowest net load" value={<span data-stress-min={year}>{show(whole(g("net_load_min_mw")))}</span>} unit="MW"
                  note={<>{t("net_load_min_mw")}: {pct(g("net_load_min_share_of_peak_pct"))} of the year&apos;s peak demand. Wind and solar were {pct(g("net_load_min_wind_solar_share_pct"))} of demand in that hour.</>} />
                <HeadlineNumber label="Longest dark, calm stretch" value={<span data-stress-calm={year}>{show(span(g("calm_longest_hours")))}</span>}
                  note={<>From {t("calm_longest_hours")}. In the year, {whole(g("calm_hours"))} hours were below the line.</>} />
              </HeadlineRow>

              <ChartFrame title={`${f.name}: the largest evening ramp of each year`}
                legend={[{ label: "Largest rise in one hour", color: "var(--color-accent)" }, { label: "Largest rise over three hours", color: "var(--color-ink)" }]}
                note={<>As a share of the same year&apos;s peak demand, so that a grid that grew is compared with itself. Net load is demand less wind and solar: as solar grows, the evening rise is the sun going down on top of the evening&apos;s own demand.</>}>
                <RampBars f={f} years={years} chosen={year} />
              </ChartFrame>

              <ToolSection title="The evening ramp and the lowest net load, by year" note={<>Local time ({f.tz.replace("_", " ")}). The ramp is between hours that are both used and next to each other; a rise the next hour takes back by more than half is a spike in the data and is not counted.</>}>
                <ToolTable caption="The evening ramp and the lowest net load by year" minWidth={900}
                  head={["Year", "Peak demand, MW", <>Largest ramp<span className="mt-0.5 block text-xs opacity-80">MW in one hour</span></>, "Share of peak", "When it started",
                    <>Largest ramp over three hours<span className="mt-0.5 block text-xs opacity-80">MW</span></>, "Lowest net load, MW", "Share of peak", "When"]}
                  rows={[...years].reverse().map((y) => ({
                    key: y, highlight: y === year, muted: !wholeYear(f, y),
                    cells: [<span key="y" data-stress-row={y}>{y}{wholeYear(f, y) ? null : <span className="block text-xs">to date</span>}</span>, show(whole(get(f, y, "peak_demand_mw"))),
                      show(whole(get(f, y, "evening_ramp_max_mw_per_h"))), show(pct(get(f, y, "evening_ramp_max_share_of_peak_pct"))), when(at(f, y, "evening_ramp_max_mw_per_h"), f.tz),
                      show(whole(get(f, y, "evening_ramp_3h_max_mw"))), show(whole(get(f, y, "net_load_min_mw"))), show(pct(get(f, y, "net_load_min_share_of_peak_pct"))), when(at(f, y, "net_load_min_mw"), f.tz)],
                  }))} />
              </ToolSection>

              <ToolSection title={`What each fuel gave in the ${f.tight} tightest hours, ${year}`} note={<>The {f.tight} hours of {year} with the highest net load: mean net load {whole(g("tight_net_load_mw"))} MW. A fuel&apos;s share is its mean output in those hours over its installed
                capacity (nameplate, from the federal generator inventory, month by month). The inventory read lists units operating now and those retired since January {f.from_year}, so for natural gas, coal, nuclear, and hydro and storage, the share
                is given from {f.from_year} only: before that, plants since retired are missing and the share would be overstated. Hydro and storage are set against capacity together: the inventory counts pumped storage
                with storage, and the grids do not all report it that way.</>}>
                <ToolTable caption={`Each fuel in the ${f.tight} tightest hours of ${year}`} minWidth={640}
                  head={["Fuel", <>Mean output in those hours<span className="mt-0.5 block text-xs opacity-80">MW</span></>, <>Installed capacity<span className="mt-0.5 block text-xs opacity-80">MW</span></>, "Output as a share of installed capacity"]}
                  rows={fuels.map((r) => ({
                    key: r.fuel,
                    ...(r.mw === null ? { cells: [r.name], wide: `Not held: ${r.why}.` } : {
                      cells: [<span key="f" data-stress-fuel={r.fuel}>{r.name}</span>, whole(r.mw), r.capacity === null ? notHeld : whole(r.capacity),
                        r.share === null ? <span key="s" className="text-muted">not held: {r.why}</span> : <span key="s" data-stress-share={r.fuel} data-stress-raw={r.share}>{pct(r.share)}</span>],
                    }),
                  }))} />
                <p className="mt-3 max-w-3xl text-sm">This is what the fleet did, not what it could do: a plant below its capacity in a tight hour may have been held in reserve, on outage, out of fuel or simply not needed. Wind and solar in these hours
                  are what the weather gave. Where the tightest hours are after dark, solar&apos;s share is near nothing whatever is installed.</p>
              </ToolSection>

              <ToolSection title="Dark, calm stretches, by year" note={<>An hour is dark and calm when wind and solar together put out less than {f.calm_pct} percent of their installed capacity of that month. The energy missing is, over the stretch, the
                year&apos;s average output of wind and solar less what they put out. The batteries are the grid&apos;s operating fleet in the stretch&apos;s first month: the energy over the fleet&apos;s power is the hours it would have to
                discharge at full power; over the fleet&apos;s energy, how many times it would have to be emptied. No fleet can do either: a battery holds a few hours.</>}>
                <ToolTable caption="Dark, calm stretches by year" minWidth={900}
                  head={["Year", "Hours below the line", "Stretches of a day or more", "The longest", "It began", <>Energy missing<span className="mt-0.5 block text-xs opacity-80">MWh</span></>,
                    <>The battery fleet<span className="mt-0.5 block text-xs opacity-80">MW; MWh</span></>, "Hours at full power to cover it", "Times the fleet's energy"]}
                  rows={[...years].reverse().map((y) => ({
                    key: y, highlight: y === year, muted: !wholeYear(f, y),
                    cells: [<span key="y" data-stress-calm-row={y}>{y}{wholeYear(f, y) ? null : <span className="block text-xs">to date</span>}</span>, show(whole(get(f, y, "calm_hours"))), show(whole(get(f, y, "calm_stretches_ge24h"))),
                      show(span(get(f, y, "calm_longest_hours"))), when(at(f, y, "calm_longest_hours"), f.tz), show(whole(get(f, y, "calm_longest_missing_mwh"))),
                      get(f, y, "calm_longest_fleet_mw") === null ? notHeld : `${whole(get(f, y, "calm_longest_fleet_mw"))}; ${whole(get(f, y, "calm_longest_fleet_mwh"))}`,
                      show(one(get(f, y, "calm_longest_fleet_full_power_hours"))), show(one(get(f, y, "calm_longest_fleet_energy_multiples")))],
                  }))} />
                <p className="mt-3 max-w-3xl text-sm">The early years&apos; figures in the last two columns are large because the fleets were small, not because the stretches were long. Read them as the size of the gap that something other
                  than today&apos;s batteries filled: gas, coal, nuclear, hydro and imports.</p>
              </ToolSection>

              <ToolSection title={`The seven grids, ${year}`} note={<>The same measures for each grid, for the year chosen where the grid holds it.</>}>
                <ToolTable caption={`The seven grids in ${year}`} minWidth={860}
                  head={["Grid", "Largest evening ramp, share of peak", "Largest over three hours, share of peak", "Lowest net load, share of peak", "Wind in the tightest hours, share of capacity",
                    "Solar in the tightest hours, share of capacity", "Longest dark, calm stretch"]}
                  rows={GRIDS.map((x) => {
                    const o = FILES[x];
                    return { key: x, highlight: x === grid,
                      ...(o.years[year] ? { cells: [<Link key="g" href={href(x, year)} className="underline" data-stress-across={x}>{o.name}</Link>, show(pct(get(o, year, "evening_ramp_max_share_of_peak_pct"))),
                        show(pct(get(o, year, "evening_ramp_3h_max_share_of_peak_pct"))), show(pct(get(o, year, "net_load_min_share_of_peak_pct"))), show(pct(get(o, year, "tight_wind_share_of_capacity_pct"))),
                        get(o, year, "solar_reported") === 0 ? <span key="s" className="text-muted">not in the source file</span> : show(pct(get(o, year, "tight_solar_share_of_capacity_pct"))), show(span(get(o, year, "calm_longest_hours")))] }
                        : { cells: [o.name], wide: `${year} is not written for ${o.name}: too many of its hours are missing or faulty.` }) };
                  })} />
              </ToolSection>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[TABLE]}
        note={<>Derived by the ERW from the hourly demand and generation by energy source each grid reports to the US Energy Information Administration (Form EIA-930), from January 2019; California&apos;s wind and solar from {caisoJoinDay()}
          from the California ISO&apos;s own supply by fuel; installed capacity and the battery fleet from EIA&apos;s monthly generator inventory (EIA-860M). Built {f.built.slice(0, 10)}. <SiteLink href={METHOD}>Method</SiteLink>.</>} />
    </ToolPage>
  );
}
