// Energy Research Warehouse (ERW) site, session 69: the storage build-out page's own pieces (/storage/buildout).
//
// Session 72 (session 69's finish): the frame, panel, headline numbers, chart frames, sections, folds and source line
// are now session 67's shared pieces; what stays here is what only this page draws: the panel's choices, the two
// server-drawn charts and the two tables. Charts are server-drawn SVG: no script runs in the browser; each mark carries
// its value as a hover title, and a folded table gives every number. Their colors are tokens (app/tokens.css).
// The panel's and the table's links point at this same page (another grid or measure): plain next/link, not the gated
// link, because the page is itself in review and a gated link to it would render greyed in the server's HTML.
import Link from "next/link";
import { Num } from "@/components/Num";
import { BUCKETS, checkKey, GRIDS, MEASURES, NOT_REPORTED, shown, whole, written, type Grid, type Measure, type Row, type View, type YearPoint } from "@/lib/buildout";

// Duration is one hue, cardinal, light to dark: longer duration reads darker. Not reported is a neutral grey. The
// values are in app/tokens.css (session 72); the page holds no color of its own.
export const RAMP = ["var(--color-duration-1)", "var(--color-duration-2)", "var(--color-duration-3)", "var(--color-duration-4)"];
export const GREY = "var(--color-not-reported)";
export const SURFACE = "var(--color-surface)"; // the white sheet of the tool page, between stacked segments

/** A value of the table with its check key (components/Num.tsx), or "not held" where the table has no such row.
 * Session 90: MW and MWh are written without decimals (lib/buildout.ts written); hours keep two. */
export function V({ row, className }: { row: Row | undefined; className?: string }) {
  if (!row) return <span className="text-muted">not held</span>;
  return <Num check={checkKey(row)} raw={row.value} className={className}>{written(row.variable, row.value)}</Num>;
}

/** The left panel: the grid and the measure, each choice a link, so it works without a script. */
export function Panel({ grid, measure }: { grid: Grid; measure: Measure }) {
  const href = (g: string, m: string) => `/storage/buildout?grid=${g}&measure=${m}`;
  const item = (on: boolean) => `block border-l-2 px-2 py-1 no-underline ${on ? "border-accent font-semibold text-accent" : "border-transparent text-ink hover:text-accent"}`;
  return (
    <div aria-label="Choices">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-1">
        <nav aria-label="Grid">
          <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
          <ul className="text-sm">
            {GRIDS.map((g) => (
              <li key={g.slug}>
                <Link href={href(g.slug, measure)} aria-current={g.slug === grid.slug ? "true" : undefined} className={item(g.slug === grid.slug)}>{g.label}</Link>
              </li>
            ))}
          </ul>
        </nav>
        <nav aria-label="Measure">
          <div className="mb-1 text-xs uppercase tracking-wide text-muted">Measure</div>
          <ul className="text-sm">
            {(Object.keys(MEASURES) as Measure[]).map((m) => (
              <li key={m}>
                <Link href={href(grid.slug, m)} aria-current={m === measure ? "true" : undefined} className={item(m === measure)}>{MEASURES[m].label}</Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </div>
  );
}

/** A round axis top at or above v, and its ticks. */
function axis(v: number): number[] {
  if (v <= 0) return [0, 1];
  const p = 10 ** Math.floor(Math.log10(v));
  const step = [0.2, 0.5, 1, 2, 5, 10].map((k) => k * p).find((s) => v / s <= 5)!;
  const n = Math.ceil(v / step - 1e-9);
  return Array.from({ length: n + 1 }, (_, i) => Math.round(i * step * 1e6) / 1e6);
}
const tick = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });

/** Chart 1: operating storage by year, one bar per year, stacked by duration bucket, shortest at the bottom. */
export function DurationBars({ v }: { v: View }) {
  const unit = MEASURES[v.measure].unit;
  const W = 760, H = 300, L = 62, R = 10, top = 18, bot = 30;
  const stacks = v.years.map((y) => {
    const parts = y.buckets.map((b, i) => ({ label: b.label, color: RAMP[i], value: b.row?.value ?? 0 }));
    if (v.measure === "mw" && (y.notReported?.value ?? 0) > 0) parts.push({ label: NOT_REPORTED.label, color: GREY, value: y.notReported!.value });
    return { y, parts, sum: parts.reduce((a, p) => a + p.value, 0) };
  });
  const ticks = axis(Math.max(...stacks.map((s) => s.sum), 0));
  const hi = ticks.at(-1)!;
  const py = (val: number) => top + (1 - val / hi) * (H - top - bot);
  const slot = (W - L - R) / stacks.length;
  const bw = Math.min(44, slot * 0.7);
  return (
    <div>
      <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img"
        aria-label={`${v.grid.name}: operating battery storage at each year's end, ${unit}, stacked by duration bucket`}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={L} x2={W - R} y1={py(t)} y2={py(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 1} />
            <text x={L - 6} y={py(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{tick(t)}</text>
          </g>
        ))}
        <text x={L} y={11} fontSize="11" fill="var(--color-muted)">{unit}</text>
        {stacks.map((s, i) => {
          const x = L + i * slot + (slot - bw) / 2;
          let acc = 0;
          return (
            <g key={s.y.month}>
              {s.parts.map((p) => {
                const y0 = py(acc), y1 = py(acc + p.value);
                acc += p.value;
                if (p.value <= 0) return null;
                return (
                  <rect key={p.label} x={x} width={bw} y={y1} height={Math.max(0.5, y0 - y1)} fill={p.color} stroke={SURFACE} strokeWidth={y0 - y1 > 4 ? 1 : 0}>
                    <title>{`${s.y.label}, ${p.label}: ${whole(p.value)} ${unit}`}</title>
                  </rect>
                );
              })}
              {i === stacks.length - 1 && s.y.total ? (
                <text x={x + bw / 2} y={py(s.sum) - 5} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{tick(Math.round(s.y.total.value))}</text>
              ) : null}
              <text x={x + bw / 2} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{s.y.month.endsWith("-12") ? s.y.month.slice(0, 4) : `${s.y.month.slice(0, 4)}*`}</text>
            </g>
          );
        })}
      </svg>
      </div>
    </div>
  );
}

/** Chart 2: battery MWh per MW of operating solar, by year. One line. */
export function SolarLine({ v }: { v: View }) {
  const pts = v.years.filter((y) => y.perSolar).map((y) => ({ y, value: y.perSolar!.value }));
  if (pts.length < 2) return <p className="text-sm text-muted">not held: fewer than two years have both batteries and solar here.</p>;
  const W = 760, H = 240, L = 62, R = 46, top = 18, bot = 30;
  const ticks = axis(Math.max(...pts.map((p) => p.value)));
  const hi = ticks.at(-1)!;
  const py = (val: number) => top + (1 - val / hi) * (H - top - bot);
  const px = (i: number) => L + ((i + 0.5) / pts.length) * (W - L - R);
  const last = pts.at(-1)!;
  return (
    <div className="overflow-x-auto">
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img"
      aria-label={`${v.grid.name}: battery energy in MWh per MW of operating solar, at each year's end`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={py(t)} y2={py(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 1} />
          <text x={L - 6} y={py(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{tick(t)}</text>
        </g>
      ))}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MWh of batteries per MW of solar (hours)</text>
      <path d={pts.map((p, i) => `${i ? "L" : "M"}${px(i).toFixed(1)},${py(p.value).toFixed(1)}`).join(" ")} fill="none" stroke="var(--color-accent)" strokeWidth="2" />
      {pts.map((p, i) => (
        <g key={p.y.month}>
          <circle cx={px(i)} cy={py(p.value)} r="4" fill="var(--color-accent)" stroke={SURFACE} strokeWidth="2">
            <title>{`${p.y.label}: ${shown(p.value)} MWh of batteries per MW of solar`}</title>
          </circle>
          <text x={px(i)} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{p.y.month.endsWith("-12") ? p.y.month.slice(0, 4) : `${p.y.month.slice(0, 4)}*`}</text>
        </g>
      ))}
      <text x={px(pts.length - 1) + 8} y={py(last.value) + 4} fontSize="11" fill="var(--color-ink)">{shown(last.value)}</text>
    </svg>
    </div>
  );
}

const th = "px-1 py-1 text-right align-bottom font-normal";
const td = "whitespace-nowrap px-1 py-1 text-right";
const HEAD = "bg-accent text-left text-xs text-white";

/** Every number of the two charts, folded: the charts' table view. */
export function YearTable({ v }: { v: View }) {
  const unit = MEASURES[v.measure].unit;
  return (
    <details className="mt-1 text-sm">
      <summary className="cursor-pointer text-muted">The numbers behind both charts, year by year</summary>
      <div className="overflow-x-auto">
        <table className="mt-1 w-full min-w-[760px] tabular-nums">
          <thead>
            <tr className={HEAD}>
              <th className="px-2 py-1 font-normal">Year end</th>
              {BUCKETS.map((b) => <th key={b.key} className={th}>{b.label}, {unit}</th>)}
              <th className={th}>Energy not reported, MW</th>
              <th className={th}>Total, {unit}</th>
              <th className={th}>Average hours</th>
              <th className={th}>Solar, MW</th>
              <th className={th}>MWh per MW of solar</th>
            </tr>
          </thead>
          <tbody>
            {v.years.map((y: YearPoint) => (
              <tr key={y.month} className="border-b border-rule">
                <td className="px-2 py-1">{y.label}</td>
                {y.buckets.map((b) => <td key={b.key} className={td}><V row={b.row} /></td>)}
                <td className={td}><V row={y.notReported} /></td>
                <td className={td}><V row={y.total} /></td>
                <td className={td}><V row={y.hours} /></td>
                <td className={td}><V row={y.solar} /></td>
                <td className={td}><V row={y.perSolar} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

/** The one table by grid: the seven ISOs, the units outside them, and the United States. */
export function GridTable({ v }: { v: View }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] text-xs tabular-nums">
        <thead>
          <tr className={HEAD}>
            <th rowSpan={2} className="px-1.5 py-1 align-bottom font-normal">Grid</th>
            <th colSpan={4} className="border-b border-white/40 px-1.5 py-1 text-center font-normal">Operating</th>
            <th colSpan={1 + v.plannedYears.length} className="border-b border-l border-white/40 px-1.5 py-1 text-center font-normal">Planned, MW, by the year expected online</th>
          </tr>
          <tr className={HEAD}>
            <th className={th}>MW</th>
            <th className={th}>MWh</th>
            <th className={th}>Average hours</th>
            <th className={th}>Added in 12 months, MW</th>
            <th className={`${th} border-l border-white/40`}>All years</th>
            {v.plannedYears.map((y) => <th key={y} className={th}>{y}</th>)}
          </tr>
        </thead>
        <tbody>
          {v.table.map((g) => {
            const on = g.entity === v.grid.entity;
            return (
              <tr key={g.slug} className={`border-b border-rule ${on ? "bg-paper" : ""} ${g.slug === "us" ? "font-semibold" : ""}`}>
                <td className="whitespace-nowrap px-1.5 py-1">
                  {GRIDS.some((x) => x.slug === g.slug) ? <Link href={`/storage/buildout?grid=${g.slug}&measure=${v.measure}`} className="no-underline">{g.label}</Link> : g.label}
                </td>
                <td className={td}><V row={g.mw} /></td>
                <td className={td}><V row={g.mwh} /></td>
                <td className={td}><V row={g.hours} /></td>
                <td className={td}><V row={g.addedMw} /></td>
                <td className={td}><V row={g.planned} /></td>
                {g.plannedByYear.map((p) => <td key={p.year} className={td}><V row={p.row} /></td>)}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
