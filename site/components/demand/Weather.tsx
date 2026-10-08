import Link from "next/link";
import { ChartFrame, Fold, InputPanel, SourceLine, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/demand_weather.json";
import { FIGURES, ORDER, TABLE, choices, day, figureOf, href, one, reading, signed, split, whole, years, type Figure, type WeatherFile } from "@/lib/demandweather";
import { Hint } from "./Hint";
import { Hover } from "./Hover";

// Session 152: "With the weather taken out", the second view of /demand (lib/demandpage.ts). It holds what the page
// sessions 126 and 129 built at /demand/weather showed (that page file is kept, unrouted, under
// app/_retired/demand-weather): for the seven grids and each year after 2021, the growth of demand against the average
// of 2019 to 2021, the part the year's temperature and dew point explain and the part they do not, each with an
// uncertainty from years the fit had not seen. Every number is a row of eia930_demand_weather
// (warehouse/derived/demand_weather.py), read from the site's own copy (data/demand_weather.json). The chart answers
// the mouse (Hover); no method stands on the face: what explained a chart or a table is a short placeholder's hover,
// and the method is docs/methods/demand_weather.md.

const file = fileJson as unknown as WeatherFile;
/** The years the fit was made on: growth is against their average. */
export const FIT_YEARS = { from: file.train[0], to: file.train[file.train.length - 1] };
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;
const WEATHER = "var(--color-muted)", REST = "var(--color-accent)";

/** For each grid, two bars: the growth the weather explains and the growth it does not, the second with its uncertainty. */
function Explained({ year, fig }: { year: string; fig: (typeof FIGURES)[number] }) {
  const rows = ORDER.map((ba) => ({ ba, name: file.grids[ba].name, g: figureOf(file, ba, year, fig.key) }));
  const W = 760, L = 78, R = 64, top = 26, rh = 50, H = top + rows.length * rh + 8;
  const ends = rows.flatMap((r) => (r.g ? [r.g.weather_pct, r.g.unexplained_pct - (r.g.uncertainty_pct ?? 0), r.g.unexplained_pct + (r.g.uncertainty_pct ?? 0)] : []));
  const low = Math.min(0, ...ends), high = Math.max(0, ...ends) || 1;
  const lo = low - (low < 0 ? 0.09 : 0.01) * (high - low), hi = high + 0.04 * (high - low);   // room for the labels of bars that point left
  const x = (v: number) => L + ((v - lo) / (hi - lo)) * (W - L - R);
  const step = [1, 2, 5, 10, 20].find((s) => (hi - lo) / s <= 9) ?? 20;
  const ticks: number[] = [];
  for (let t = Math.ceil(low / step) * step; t <= hi; t += step) ticks.push(t);
  const bar = (v: number, y: number, fill: string, label: string) => (
    <rect x={Math.min(x(0), x(v))} y={y} width={Math.max(1, Math.abs(x(v) - x(0)))} height={14} fill={fill} data-tip={label} aria-label={label} />
  );
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="explained" aria-label={`${fig.name}, ${year}: growth against the average of ${file.train[0]} to ${file.train[file.train.length - 1]}, the part the weather explains and the part it does not, by grid, percent`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={top - 4} y2={H - 6} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={x(t)} y={14} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{t > 0 ? `+${t}` : t}</text>
        </g>
      ))}
      <text x={W - R + 6} y={14} fontSize="11" fill="var(--color-muted)">percent</text>
      {rows.map((r, i) => {
        const y = top + i * rh + 6;
        if (!r.g) return <g key={r.ba} data-tip={`${r.name}, ${year}: not held`}><rect x={L} y={y} width={W - L - R} height={30} fill="transparent" /><text x={L - 8} y={y + 19} textAnchor="end" fontSize="12" fill="var(--color-ink)">{r.name}</text><text x={x(0) + 6} y={y + 19} fontSize="11" fill="var(--color-muted)">not held</text></g>;
        const g = r.g, u = g.uncertainty_pct;
        const end = (v: number) => (v >= 0 ? { x: x(v) + 5, a: "start" as const } : { x: x(v) - 5, a: "end" as const });
        const e1 = end(g.weather_pct), e2 = end(u === null ? g.unexplained_pct : g.unexplained_pct >= 0 ? g.unexplained_pct + u : g.unexplained_pct - u);
        const rest = `${r.name}, ${year}: ${signed(g.unexplained_pct)} percent the weather does not explain${u === null ? "" : `, give or take ${one(u)}`} (${reading(g)})`;
        return (
          <g key={r.ba} data-grid={r.ba}>
            <text x={L - 8} y={y + 19} textAnchor="end" fontSize="12" fill="var(--color-ink)">{r.name}</text>
            {bar(g.weather_pct, y, WEATHER, `${r.name}, ${year}: the weather explains ${signed(g.weather_pct)} percent of ${signed(g.growth_pct)} percent growth`)}
            <text x={e1.x} y={y + 11} textAnchor={e1.a} fontSize="11" fill="var(--color-ink)">{signed(g.weather_pct)}</text>
            {bar(g.unexplained_pct, y + 16, REST, rest)}
            {u === null ? null : <g stroke="var(--color-ink)" strokeWidth="1.5" data-tip={rest}><line x1={x(g.unexplained_pct - u)} x2={x(g.unexplained_pct + u)} y1={y + 23} y2={y + 23} /><line x1={x(g.unexplained_pct - u)} x2={x(g.unexplained_pct - u)} y1={y + 19} y2={y + 27} /><line x1={x(g.unexplained_pct + u)} x2={x(g.unexplained_pct + u)} y1={y + 19} y2={y + 27} /></g>}
            <text x={e2.x} y={y + 27} textAnchor={e2.a} fontSize="11" fill="var(--color-ink)" fontWeight={g.finding ? 600 : 400}>{signed(g.unexplained_pct)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function WeatherView({ q }: { q: Record<string, string | undefined> }) {
  const { figure, year } = choices(file, q);
  const ys = years(file);
  const t0 = file.train[0], t1 = file.train[file.train.length - 1];
  const { found, not, absent } = split(file, year, figure.key);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const pm = (g: Figure, k: string) => (g.uncertainty_pct === null ? NOT : <N k={k}>{one(g.uncertainty_pct)}</N>);
  const lower = figure.name.charAt(0).toLowerCase() + figure.name.slice(1);
  const partial = (ba: string, y: string) => Number(y) === file.grids[ba].newest && file.grids[ba].through < "12-31";
  const stations = file.weather ? Object.entries(file.weather.stations) : [];
  const best = file.california.windows.map((x) => Math.min(...["-1", "0", "1"].map((k) => x.shifts[k].mape_pct ?? Infinity)));
  const asRead = file.california.windows.filter((x, i) => x.shifts["0"].mape_pct === best[i]).length;
  const closest = Math.max(...file.california.windows.map((x, i) => (x.shifts["0"].mape_pct ?? 0) - best[i]));
  const w = file.weather;
  const through = day(`${file.through}T00:00:00Z`);
  const dew = file.dew?.adopted ? " and dew point" : "";

  return (
    <div data-view-body="weather">
      <p className="mb-4 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
        In {year}, against the average of {t0} to {t1}, {lower} grew by more than the temperature explains in <N k="sum|found">{String(found.length)}</N> of the {ORDER.length - absent.length} grids that hold the figure
        {found.length ? <>: {found.map((x, i) => <span key={x.ba}>{i ? (i === found.length - 1 ? " and " : ", ") : ""}{x.name} (<N k={`sum|${x.ba}|u`}>{signed(x.g!.unexplained_pct)}</N> percent, give or take <N k={`sum|${x.ba}|pm`}>{one(x.g!.uncertainty_pct!)}</N>)</span>)}</> : null}
        {not.length ? <>; in {found.length ? "the other " : ""}<N k="sum|not">{String(not.length)}</N> the part the temperature does not explain is smaller than the fit&apos;s own error</> : null}.
      </p>
      <p className="mb-8 text-sm" data-remainder="1">
        <Hint words="What the remainder is not." why="It is growth the temperature does not explain. More people, electric heating and vehicles, new industry and datacenters are all in it together, and so are things that lower metered demand: rooftop solar, efficiency, a recession. The warehouse cannot split them, and this page does not say which it is." />
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>The newest year stops on {through}. <Hint words="How it is compared" why={`Its energy and its overnight minimum are compared with the same days of ${t0} to ${t1}.`} /></>}>
            <nav aria-label="Figure" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Figure</div>
              {FIGURES.map((f) => <div key={f.slug}><Link href={href(f.slug, year)} aria-current={f.slug === figure.slug ? "true" : undefined} className={item(f.slug === figure.slug)} title={f.what}>{f.name}</Link></div>)}
            </nav>
            <nav aria-label="Year" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Year in the chart</div>
              {ys.map((y) => <div key={y}><Link href={href(figure.slug, y)} aria-current={y === year ? "true" : undefined} className={item(y === year)}>{y}</Link></div>)}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          <ToolSection title={`${figure.name}, ${year}`}
            note={<Hint words="How to read the bars" why={`${figure.name}: ${figure.what}. Growth is against the mean of ${t0} to ${t1}. The grey bar is what the year's temperature${dew} explain; the red bar is the rest, and the black line across it is its uncertainty: the largest miss the method made on a year it had not seen. A red bar shorter than half its black line is not a finding.`} />}>
            <ChartFrame title={`${figure.name}, ${year}: growth against the average of ${t0} to ${t1}, percent`} legend={[{ label: "Explained by the temperature", color: WEATHER }, { label: "Not explained, with its uncertainty", color: REST }]}>
              <Hover><Explained year={year} fig={figure} /></Hover>
            </ChartFrame>
          </ToolSection>

          <ToolSection title="By grid and year" id="table"
            note={<Hint words="What the columns mean" why={`Percent of the mean of ${t0} to ${t1}. Growth is the sum of the two columns after it. Temperature: the growth the year's temperature${dew} explain. A remainder is called a finding only when it is larger than its give or take; "beyond" when the peak hour was hotter (summer) or colder (winter) than any hour of ${t0} to ${t1}, so the fit is reaching past what it was made on and the figure is not called a finding. A peak is one hour, so its uncertainty is never less than the fit's error on a single hour. "${ys[ys.length - 1]}, part" is 1 January to ${through}, against the same days of ${t0} to ${t1}.`} />}>
            <ToolTable minWidth={640} caption={`${figure.name}: growth, the part the temperature explains and the part it does not, by grid and year`}
              head={["Grid", "Year", "Metered, MW", "Growth", "Temperature", "Not explained", "Give or take", "Finding"]}
              rows={ORDER.flatMap((ba) => ys.map((y) => {
                const g = figureOf(file, ba, y, figure.key), k = `t|${ba}|${y}`;
                return { key: k, highlight: y === year, muted: !g, cells: g
                  ? [file.grids[ba].name, partial(ba, y) && g.window !== "the season" ? `${y}, part` : y, <N key="a" k={`${k}|mw`}>{whole(g.actual)}</N>, <N key="g" k={`${k}|g`}>{signed(g.growth_pct)}</N>, <N key="w" k={`${k}|w`}>{signed(g.weather_pct)}</N>,
                    <N key="u" k={`${k}|u`}>{signed(g.unexplained_pct)}</N>, pm(g, `${k}|pm`), <span key="r" data-reading={g.finding ? "finding" : "no"} title={reading(g)}>{g.finding ? "yes" : g.outside ? "beyond" : "no"}</span>]
                  : [file.grids[ba].name, y, NOT, NOT, NOT, NOT, NOT, ""] };
              }))} />
          </ToolSection>

          <Fold title="The check: years the fit had not seen">
            <p className="mb-3"><Hint words="What this check is" why={`Each of ${t0}, ${file.train[1]} and ${t1} is left out in turn; the fit is made on the other two and the left-out year is read against them. A grid whose customers did not change should come back near zero. What comes back is the method's miss plus whatever really changed that year, and ${file.train[1]} holds the lockdowns. The largest of the three, in absolute value, is the uncertainty in the table above.`} /></p>
            <ToolTable minWidth={640} caption={`${figure.name}: growth the temperature does not explain in a year left out of the fit, percent`}
              head={["Grid", ...file.train.map((y) => `${y} left out`), "Error on an hour left out, percent", "On a day left out"]}
              rows={ORDER.map((ba) => ({ key: ba, cells: [file.grids[ba].name, ...file.train.map((y) => { const h = file.grids[ba].holdout[String(y)]?.[figure.key]; return h ? <N key={y} k={`h|${ba}|${y}`}>{signed(h.unexplained_pct)}</N> : NOT; }),
                <N key="e" k={`h|${ba}|hour`}>{one(file.grids[ba].fit.oos_mape_pct)}</N>, <N key="d" k={`h|${ba}|day`}>{one(file.grids[ba].fit.oos_daily_mape_pct)}</N>] }))} />
          </Fold>
          <Fold title="The stations and their weights">
            {w ? <>
              <p className="mb-3 max-w-3xl">
                <Hint words="How the stations were chosen and weighted" why={`Five airports a grid: the principal airport of each of the five most populous metropolitan areas whose principal city the grid operator serves. The weight is the area's population over the sum of the grid's five, by the Census Bureau's count for 1 April 2020 (its population estimates, vintage 2025); New York's area is counted by its part in New York State.${w.rule_check?.length ? ` By those counts the five held are the rule's five in every grid but one: ${w.rule_check.map((x) => x.replace(/^[A-Z-]+: /, "")).join("; ")}.` : ""} A missing hour is counted and never interpolated across more than three hours; a grid's hour is used only when all five stations hold it. NOAA's hourly database ends on 27 August 2025, so the hours from August 2025 come from its Local Climatological Data, checked hour by hour against the first over eight weeks.`} />
                {file.equal_weights?.moved ? <> Weights: the Census Bureau&apos;s counts. With five equal weights in their place, the year&apos;s energy not explained moves by at most <N k="eq|energy">{one(file.equal_weights.moved.largest_energy)}</N> points in any grid and year.</> : <> Weights: the Census Bureau&apos;s counts.</>}
              </p>
              <ToolTable minWidth={900} caption="The 35 stations: weight, and hours measured, interpolated and missing"
                head={["Grid", "Airport", "NOAA's name for the station", "Stands for", "People, 2020", "Weight", "Hours measured", "Interpolated", "Missing", "Longest gap, hours"]}
                rows={stations.map(([code, s]) => ({ key: code, cells: [file.grids[s.ba.toUpperCase()].name, code, <span key="n" className="block text-left">{s.name}</span>, <span key="m" className="block text-left">{s.cbsa_name ?? s.metro}</span>, s.population ? <N key="p" k={`s|${code}|p`}>{whole(s.population)}</N> : NOT, <N key="w" k={`s|${code}|w`}>{s.weight.toFixed(3)}</N>,
                  <N key="h" k={`s|${code}|h`}>{whole(s.measured)}</N>, <N key="i" k={`s|${code}|i`}>{whole(s.interpolated)}</N>, <N key="x" k={`s|${code}|x`}>{whole(s.missing)}</N>, <N key="l" k={`s|${code}|l`}>{whole(s.longest_gap)}</N>] }))} />
              <p className="mt-2 max-w-3xl text-xs text-muted">Of {whole(stations[0]?.[1].hours ?? 0)} hours from 1 January {t0} to {day(w.through)}. {whole(w.rows_read)} rows were read from NOAA, of a ceiling of {whole(w.ceiling)}.</p>
            </> : <p><Hint words="not held in this copy" why="The list of stations is written when the table is built on the machine that holds NOAA's files; this copy was built without it. It is in the table noaa_grid_weather_stations." /></p>}
          </Fold>
          {file.isne_four_of_five ? (
            <Fold title="New England under two rules">
              <p className="mb-3 max-w-3xl">
                <Hint words="What the two rules are" why={`A grid's hour is used only when all five of its stations hold it. Bridgeport's station lacks hours in 2025 and 2026, and under that rule some of New England's figures fall just short of the 95 percent of hours a figure needs. The second column of each pair is the same figure with an hour used when at least ${file.isne_four_of_five.least} of the five stations hold it, the weights restated over those that do. The table above uses the first rule. Which rule stands is a ruling still to be made.`} />
                {" "}With four of five: {whole(file.isne_four_of_five.hours_held)} of {whole(file.isne_four_of_five.hours)} hours held, {whole(file.isne_four_of_five.hours_on_four)} of them on four stations.
              </p>
              <ToolTable minWidth={720} caption={`${figure.name}, ISO-NE: the part the temperature does not explain under the rule of five stations and with four of five`}
                head={["Year", "All five: not explained", "Give or take", "Four of five: not explained", "Give or take"]}
                rows={ys.map((y) => { const a = figureOf(file, "ISNE", y, figure.key), b = file.isne_four_of_five!.years[y]?.[figure.key] ?? null;
                  return { key: y, cells: [y, a ? <N key="a" k={`ne|${y}|five`}>{signed(a.unexplained_pct)}</N> : NOT, a && a.uncertainty_pct !== null ? one(a.uncertainty_pct) : NOT,
                    b ? <N key="b" k={`ne|${y}|four`}>{signed(b.unexplained_pct)}</N> : NOT, b && b.uncertainty_pct !== null ? one(b.uncertainty_pct) : NOT] }; })} />
            </Fold>
          ) : null}
          <Fold title="California across December 2025">
            <p className="mb-3 max-w-3xl">
              <Hint words="What this check is" why={`EIA dated California's hours one hour late until ${day(file.california.late_to)}, and changed its generation series on ${day(file.california.join)}. Demand is a different series from generation, and the late hours are set back before anything is computed. The check here is the weather's: if demand sat on the wrong hour, the fit would match it clearly better moved by an hour. The last column is how far metered demand stood above the fit: it rises from autumn to winter in both years, with or without the change. Comparable across the change: the year's energy, the peaks and the overnight minimum, which rest on demand and on hours dated right. Not comparable, and not used here: California's generation by source in EIA's series either side of ${day(file.california.join)}.`} />
              {" "}{asRead === file.california.windows.length
                ? <>In each of the {asRead} windows the error is smallest with demand as it is read.</>
                : <>In {asRead} of the {file.california.windows.length} windows the error is smallest with demand as it is read; in the others the smallest is within {one(closest)} points of it.</>}
            </p>
            <ToolTable minWidth={720} caption="California: the fit's error with demand an hour early, as read, and an hour late"
              head={["Window", "From", "Error an hour early, percent", "As read", "An hour late", "Metered against the fit, percent"]}
              rows={file.california.windows.map((x, i) => ({ key: String(i), cells: [<span key="l" className="block text-left">{x.label}{x.a_year_earlier ? ", a year earlier" : ""}</span>, day(x.start),
                ...["-1", "0", "1"].map((s) => (x.shifts[s].mape_pct === null ? NOT : <N key={s} k={`ca|${i}|${s}`}>{one(x.shifts[s].mape_pct!)}</N>)), x.shifts["0"].bias_pct === null ? NOT : <N key="b" k={`ca|${i}|b`}>{signed(x.shifts["0"].bias_pct!)}</N>] }))} />
          </Fold>
          <SourceLine tables={[TABLE, "noaa_grid_weather_hourly", "noaa_grid_weather_stations"]} note={<>Derived from EIA Form EIA-930 hourly demand and NOAA NCEI station observations (ISD-Lite; Local Climatological Data, version 2); built {file.built_at.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the table.</>} />
        </div>
      </div>
    </div>
  );
}
