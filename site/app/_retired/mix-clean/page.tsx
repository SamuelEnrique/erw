import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { caisoJoinDay } from "@/lib/caisoJoin";
import {
  GRIDS, HOURLY, SHAPE_NAME, SUMMARY, cleanestOf, dayOf, defaultYear, get, hoursName, href, isGrid, monthName, monthsOf, one, pct, sideOf, signedPct, two, wholeYear,
  yearView, yearsOf, type GridFile, type YearView,
} from "@/lib/clean";
import { FILES } from "./data";

// Session 122: "How clean, and when", in review (lib/release.ts), in the battery page's layout: a panel of choices on the
// left, a sentence, the headline numbers, then the tables. For each of the seven grids and each year since 2019: the
// carbon-free share of generation; what an annual clean purchase covers hour by hour; the cleanest hours of the
// average day, month by month; and what moving 10 and 20 percent of a flat load's daily energy into those hours changes
// in carbon and in cost. Every number is a row of clean_energy_summary (warehouse/derived/mix_clean.py;
// docs/methods/clean_energy.md), read from the site's own copy (app/mix/clean/data.ts); the page does no arithmetic.
// It says first what the figures are: generation inside the grid, not imports; the average of the hour, not the
// marginal plant. The panel's links are plain next/link: they point at this same page.
export const metadata: Metadata = { title: "How clean, and when", robots: { index: false, follow: false } };

const METHOD = "/data/methods/clean_energy";
const notHeld = <span className="text-muted">not held</span>;
const show = (v: string) => (v === "not held" ? notHeld : v);

/** The carbon-free share by year: a bar a year, the chosen one in the accent. A year that is not whole is hatched. */
function YearBars({ f, views, chosen }: { f: GridFile; views: YearView[]; chosen: string }) {
  const W = 760, H = 260, L = 44, R = 10, top = 22, bot = 40;
  const bw = (W - L - R) / views.length;
  const y = (v: number) => top + ((100 - v) / 100) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-year-bars={f.grid} aria-label={`${f.name}: the carbon-free share of generation by year, percent`}>
      <defs><pattern id="cl-hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill="var(--color-accent)" /></pattern></defs>
      {[0, 25, 50, 75, 100].map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      <text x={L - 38} y={12} fontSize="11" fill="var(--color-muted)">percent of generation</text>
      {views.map((v, i) => {
        const x0 = L + i * bw + bw * 0.18, w = bw * 0.64, whole = wholeYear(f, v.y);
        return v.share === null ? null : (
          <g key={v.y} data-year-bar={v.y}>
            <rect x={x0} width={w} y={y(v.share)} height={Math.max(0.5, y(0) - y(v.share))} fill={whole ? (v.y === chosen ? "var(--color-accent)" : "var(--color-ink)") : "url(#cl-hatch)"}
              stroke={whole ? "none" : "var(--color-accent)"} strokeWidth={whole ? 0 : 0.75} opacity={v.y === chosen || !whole ? 1 : 0.55} />
            <text x={x0 + w / 2} y={y(v.share) - 6} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{v.share.toFixed(1)}</text>
            <text x={x0 + w / 2} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{v.y}</text>
            {!whole ? <text x={x0 + w / 2} y={H - bot + 30} textAnchor="middle" fontSize="10" fill="var(--color-muted)">{v.months} of {v.due} months</text> : null}
            {sideOf(v) !== "eia930" ? <text x={x0 + w / 2} y={H - bot + (whole ? 30 : 40)} textAnchor="middle" fontSize="10" fill="var(--color-muted)">CAISO&apos;s own data</text> : null}
            <title>{`${v.y}: ${v.share.toFixed(1)} percent of ${f.name}'s generation was carbon-free${whole ? "" : ` (${v.months} of ${v.due} months held)`}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

/** The average day of each month of a year: a row a month, a cell an hour, shaded by the carbon-free share; the four cleanest hours outlined. */
function DayGrid({ f, year }: { f: GridFile; year: string }) {
  const months = monthsOf(f, year);
  const W = 760, L = 78, R = 8, top = 22, rowH = 20;
  const H = top + months.length * rowH + 8;
  const cw = (W - L - R) / 24;
  const all = months.flatMap((m) => dayOf(f, m).filter((v): v is number => v !== null));
  const lo = Math.min(...all), hi = Math.max(...all);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-day-grid={`${f.grid}-${year}`} aria-label={`${f.name}, ${year}: the carbon-free share of generation by local hour, the average day of each month`}>
      {[0, 3, 6, 9, 12, 15, 18, 21].map((h) => <text key={h} x={L + (h + 0.5) * cw} y={14} textAnchor="middle" fontSize="10" fill="var(--color-muted)">{String(h).padStart(2, "0")}</text>)}
      {months.map((m, r) => {
        const day = dayOf(f, m), top4 = new Set(cleanestOf(f, m));
        return (
          <g key={m} data-day-row={m}>
            <text x={L - 6} y={top + r * rowH + 14} textAnchor="end" fontSize="11" fill="var(--color-ink)">{monthName(m)}</text>
            {day.map((v, h) => (v === null ? null : (
              <rect key={h} x={L + h * cw} y={top + r * rowH} width={cw - 1} height={rowH - 1} fill="var(--color-accent)" fillOpacity={0.08 + 0.87 * ((v - lo) / (hi - lo || 1))}
                stroke={top4.has(h) ? "var(--color-ink)" : "none"} strokeWidth={top4.has(h) ? 1.5 : 0}>
                <title>{`${monthName(m)} ${year}, ${String(h).padStart(2, "0")}:00 local: ${v.toFixed(1)} percent carbon-free${top4.has(h) ? " (one of the month's four cleanest hours)" : ""}`}</title>
              </rect>
            )))}
          </g>
        );
      })}
    </svg>
  );
}

export default async function Clean({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const grid = isGrid(sp.grid) ? sp.grid : "ercot";
  const f = FILES[grid];
  const years = yearsOf(f);
  const year = typeof sp.year === "string" && years.includes(sp.year) ? sp.year : defaultYear(f);
  const views = years.map((y) => yearView(f, y));
  const v = year ? yearView(f, year) : null;
  const months = year ? monthsOf(f, year) : [];
  const whole = year ? wholeYear(f, year) : false;
  const m100 = v?.match.mix?.[100];
  const across = GRIDS.map((g) => ({ g, file: FILES[g], v: year && FILES[g].years[year] ? yearView(FILES[g], year) : null }));

  return (
    <ToolPage>
      <ToolHeader
        title="How clean, and when"
        lead={<span data-clean-what="1"><strong>What this is.</strong> The generation inside each grid, hour by hour: what its own plants put out. It is not what the grid&apos;s customers used:
          imported power is not in it, and exported power is. And every carbon figure is the average of the hour&apos;s generation, not the marginal plant&apos;s: it does not say what one
          more MWh of load would have emitted. <SiteLink href={METHOD}>Method</SiteLink>.</span>}
      />
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Grid">
            <ul className="space-y-1 text-sm">
              {GRIDS.map((g) => <li key={g}>{g === grid ? <strong data-clean-grid={g}>{FILES[g].name}</strong> : <Link href={href(g, year && FILES[g].years[year] ? year : null)} className="underline">{FILES[g].name}</Link>}</li>)}
            </ul>
          </InputPanel>
          <InputPanel title="Year" note={<>A year is written when at most one of its months is missing. A month is written when at least nine tenths of its days hold every hour; nothing is filled.</>}>
            <ul className="flex flex-wrap gap-x-3 gap-y-1 text-sm">
              {years.map((y) => <li key={y}>{y === year ? <strong data-clean-year={y}>{y}</strong> : <Link href={href(grid, y)} className="underline">{y}</Link>}{wholeYear(f, y) ? "" : "*"}</li>)}
            </ul>
            <p className="mt-2 text-xs text-muted">* not all twelve months held</p>
          </InputPanel>
          <InputPanel title="What is counted">
            <ul className="list-disc space-y-1.5 pl-4 text-sm">
              <li><strong>Carbon-free.</strong> Nuclear, wind, solar and hydro.</li>
              <li><strong>Generation.</strong> Those, and natural gas, coal and &quot;other&quot; (oil, geothermal, biomass and what the source does not name). &quot;Other&quot; is counted as not carbon-free, so a grid with geothermal is shown a little dirtier than it is.</li>
              <li><strong>Storage.</strong> Not a source: what a battery puts out was generated before, and is counted there.</li>
              <li><strong>Hours not used.</strong> An hour whose sources do not add up to its total, whose total is impossible, or in which a main source is missing from the file. California&apos;s months without hydro in the source (October 2019 to August 2020) are in no figure.</li>
            </ul>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!v || !year || v.share === null ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-clean-state="none">No year of {f.name} is held, so no number is shown.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-clean-summary="1">
                In {year}{whole ? "" : ` (${v.months} of ${v.due} months held)`}, {pct(v.share)} of {f.name}&apos;s generation was carbon-free.
                {m100 && m100.energy !== null ? <> A load that draws the same power every hour and buys clean energy equal to all of its yearly use, delivered as the grid&apos;s own carbon-free plants
                  ran, is covered in the hour it uses power for {pct(m100.energy)} of its energy.</> : null}
              </p>
              {sideOf(v) !== "eia930" || (grid === "caiso") ? (
                <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-clean-join="1">
                  <strong>California is two series, not one.</strong> Until {caisoJoinDay()} its hours are the federal energy agency&apos;s (EIA); from that day they are the California grid operator&apos;s own.
                  The two do not agree on the same months (EIA&apos;s California gas output was well above the operator&apos;s own), so the step between the last year on one and the first on the other
                  is partly the change of source, not a change in the grid. The month of the change is not written. <SiteLink href="/data/methods/eia930_caiso_break">The note on the break</SiteLink>.
                </p>
              ) : null}
              {grid === "nyiso" ? (
                <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-clean-nuclear="1">
                  <strong>New York has hours that are not used.</strong> In stretches from 2021 on, the source file has New York&apos;s nuclear output at zero and its &quot;other&quot; higher by about
                  as much: the nuclear plants are in the file under another name. Their carbon-free share cannot be told, so those hours are left out, and a month or a year that loses too many of them is not written.
                </p>
              ) : null}

              <HeadlineRow>
                <HeadlineNumber label={`Carbon-free share of generation, ${year}`} value={<span data-clean-share={year} data-clean-raw={v.share}>{one(v.share)}</span>} unit="percent"
                  note={<>Carbon-free MWh over all MWh generated. The mean of the hours&apos; shares, which is what a load that never varies meets, is {pct(v.flat)}.</>} />
                <HeadlineNumber label="Hours at least half carbon-free" value={<span data-clean-ge50={year}>{show(one(v.ge[50] ?? null))}</span>} unit="percent of hours"
                  note={<>At least three quarters: {pct(v.ge[75] ?? null)}. At least nine tenths: {pct(v.ge[90] ?? null)}.</>} />
                <HeadlineNumber label="A 100 percent annual purchase, hour by hour" value={<span data-clean-match={year}>{show(one(m100?.energy ?? null))}</span>} unit="percent of energy"
                  note={<>The load&apos;s energy met in the hour it is used. Hours met in full: {pct(m100?.hours ?? null)}.</>} />
              </HeadlineRow>

              <ChartFrame title={`${f.name}: carbon-free share of generation by year`}
                legend={[{ label: `${year}`, color: "var(--color-accent)" }, { label: "Other whole years", color: "var(--color-ink)" }, { label: "Not all twelve months", color: "var(--color-accent)", hatch: true }]}
                note={<>Generation inside {f.name}, not imports. A hatched year does not hold all twelve months and is the held months&apos; figure: it is not a whole year&apos;s, and the months it lacks are not filled.</>}>
                <YearBars f={f} views={views} chosen={year} />
              </ChartFrame>

              <ToolSection title="Annual against hourly matching" note={<>A load of the same power in every hour buys clean energy equal to a share of its yearly use. &quot;Annual matching&quot; counts the year&apos;s MWh and stops there.
                Here the purchase is delivered in the shape of the grid&apos;s own plants, hour by hour, and what arrives in an hour beyond what the load uses in that hour is not counted. {year}{whole ? "" : `, ${v.months} of ${v.due} months`}.</>}>
                <ToolTable caption="What an annual clean purchase covers hour by hour" minWidth={760}
                  head={["Purchase, as a share of the year's use", ...f.shapes.flatMap((s) => [
                    <span key={`${s}e`}>Delivered as {SHAPE_NAME[s] ?? s}<span className="mt-0.5 block text-xs opacity-80">energy met in its own hour</span></span>,
                    <span key={`${s}h`}>the same<span className="mt-0.5 block text-xs opacity-80">hours met in full</span></span>])]}
                  rows={f.purchases.map((p) => ({
                    key: String(p), highlight: p === 100,
                    cells: [`${p} percent`, ...f.shapes.flatMap((s) => {
                      const x = v.match[s]?.[p];
                      return [<span key={`${s}e`} data-clean-match-cell={`${s}-${p}`}>{show(pct(x?.energy ?? null))}</span>, show(pct(x?.hours ?? null))];
                    })],
                  }))} />
                <p className="mt-3 max-w-3xl text-sm">A purchase of the whole year&apos;s use never covers every hour: plants make more than the load needs in some hours and less in others. The gap between the row of 100 percent
                  and 100 is the part of the load that an annual claim calls clean and that was served, in its own hour, by something else. A shape with nights (solar) leaves the most uncovered whatever is bought.</p>
              </ToolSection>

              <ToolSection title={`The cleanest hours of the average day, ${year}`} note={<>Each row is a month&apos;s average day, each cell a local hour ({f.tz.replace("_", " ")}), darker where a larger share of the hour&apos;s generation was carbon-free.
                The four cleanest hours of each month are outlined. Shaded from the lowest to the highest share of the year, so the shading compares hours within this grid and year only.</>}>
                {months.length ? <DayGrid f={f} year={year} /> : <p className="border border-rule bg-paper px-3 py-2 text-sm">No month of {year} is held.</p>}
                <div className="mt-4">
                  <ToolTable caption="The cleanest hours of the average day by month" minWidth={620}
                    head={["Month", "The four cleanest hours", "Share in the cleanest hour", "Share in the dirtiest hour", "The month's share"]}
                    rows={months.map((m) => {
                      const day = dayOf(f, m).filter((x): x is number => x !== null);
                      return { key: m, cells: [<span key="m" data-clean-month={m}>{monthName(m)}</span>, hoursName(cleanestOf(f, m)), day.length ? pct(Math.max(...day)) : notHeld, day.length ? pct(Math.min(...day)) : notHeld,
                        show(pct(get(f.months[m], "carbon_free_share_pct")))] };
                    })} />
                </div>
              </ToolSection>

              <ToolSection title="Moving load into the cleanest hours" note={<>A flat load of 1 MW. Each day, 10 or 20 percent of the day&apos;s energy is taken evenly from every hour and put into that month&apos;s four cleanest hours;
                the day&apos;s energy is unchanged. The hours are those of the month&apos;s own average day, known only afterwards: this is what a load that knew the month&apos;s pattern could do, not a forecast.
                Carbon is the hour&apos;s average, kg of CO2 per MWh generated in the grid. Cost is at the grid&apos;s day-ahead hub price. A day counts only when every one of its hours has the figure.</>}>
                <ToolTable caption="A flat load, and the same with part of each day's energy moved into the cleanest hours" minWidth={880}
                  head={["Year", <>Flat load<span className="mt-0.5 block text-xs opacity-80">kg CO2 per MWh</span></>, "10 percent moved: carbon", "20 percent moved: carbon", "Days",
                    <>Flat load<span className="mt-0.5 block text-xs opacity-80">USD per MWh, day-ahead hub</span></>, "10 percent moved: cost", "20 percent moved: cost", "Days priced"]}
                  rows={[...views].reverse().map((r) => ({
                    key: r.y, highlight: r.y === year, muted: !wholeYear(f, r.y),
                    cells: [<span key="y" data-clean-shift-year={r.y}>{r.y}{wholeYear(f, r.y) ? null : <span className="block text-xs">{r.months} of {r.due} months</span>}</span>,
                      show(one(r.carbon.flat)), <span key="c10" data-clean-shift={`${r.y}-10`} data-clean-raw={r.carbon.change[10] ?? ""}>{show(signedPct(r.carbon.change[10] ?? null))}</span>, show(signedPct(r.carbon.change[20] ?? null)),
                      r.carbon.days === null ? notHeld : r.carbon.days.toLocaleString("en-US"),
                      r.cost.flat === null ? notHeld : two(r.cost.flat), show(signedPct(r.cost.change[10] ?? null)), show(signedPct(r.cost.change[20] ?? null)),
                      r.cost.days === null ? notHeld : r.cost.days.toLocaleString("en-US")],
                  }))} />
                {f.no_price ? <p className="mt-3 max-w-3xl text-sm" data-clean-no-price={grid}>No cost is shown for {f.name}: {f.no_price}.</p>
                  : <p className="mt-3 max-w-3xl text-sm">The cost figures rest on the days priced, which for most grids begin in September 2024: a year with few days priced is those days only, not the year.</p>}
                <p className="mt-2 max-w-3xl text-sm">The carbon moves little because it is an average: in most hours most of the grid&apos;s plants are the same ones. What one more MWh of load emits in an hour is the marginal plant&apos;s,
                  which this page does not hold, and it can differ from the average in either direction.</p>
              </ToolSection>

              <ToolSection title={`The seven grids, ${year}`} note={<>The same figures for each grid, for the year chosen where the grid holds it. Each grid is its own generation; none is adjusted for what it imports.</>}>
                <ToolTable caption={`The seven grids in ${year}`} minWidth={820}
                  head={["Grid", "Months held", "Carbon-free share", "Hours at least half carbon-free", "100 percent purchase: energy met in its hour", "20 percent moved: carbon", "20 percent moved: cost"]}
                  rows={across.map(({ g, file, v: r }) => ({
                    key: g, highlight: g === grid,
                    ...(r === null ? { cells: [file.name], wide: `${year} is not written for ${file.name}: too many of its months are missing.` } : {
                      cells: [<Link key="g" href={href(g, year)} className="underline" data-clean-across={g}>{file.name}</Link>, `${r.months} of ${r.due}`, show(pct(r.share)), show(pct(r.ge[50] ?? null)),
                        show(pct(r.match.mix?.[100]?.energy ?? null)), show(signedPct(r.carbon.change[20] ?? null)), r.cost.change[20] == null ? <span className="text-muted">no price</span> : signedPct(r.cost.change[20])],
                    }),
                  }))} />
              </ToolSection>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[SUMMARY, HOURLY]}
        note={<>Derived by the ERW from the hourly generation by energy source that each grid reports to the US Energy Information Administration (Form EIA-930), from January 2019; California from {caisoJoinDay()} from
          the California ISO&apos;s own supply by fuel. Carbon from the ERW&apos;s hourly carbon intensity of generation. Built {f.built.slice(0, 10)}. <SiteLink href={METHOD}>Method</SiteLink>.</>} />
    </ToolPage>
  );
}
