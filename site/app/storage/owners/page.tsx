import type { Metadata } from "next";
import { AskErcotLink } from "@/components/AskErcotLink";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import data from "@/data/storage_owners.json";
import { GRIDS, SHOWN, TABLE, choices, monthName, rowKey, shown, view, type OwnerRow, type Snapshot } from "@/lib/storageowners";

// Session 87: "Who owns the batteries". Operating and planned battery storage by the company that reports each plant
// to EIA, by grid: MW, MWh, average duration, and the largest. Every number is a row of storage_owners_monthly
// (warehouse/derived/storage_owners.py; EIA-860M, derived), read from the committed snapshot data/storage_owners.json:
// the table is held out of the live set while the live site is frozen for its reviewer, so nothing here is read from
// Supabase. lib/storageowners.ts picks and sorts the values; the page does no arithmetic. Laid out as the battery page
// is (components/tool/ToolPage.tsx). In review (lib/release.ts). The panel's links point at this same page: plain
// next/link, as on the build-out page.
export const metadata: Metadata = { title: "Who owns the batteries", robots: { index: false, follow: false } };

const METHOD = "/data/methods/storage_owners";
const BAR = "var(--color-accent)";

/** A value with the row it is: the table's key in a data attribute and the hover title. */
function V({ entity, grid, metric, month, value, digits = 0 }: { entity: string; grid: string; metric: string; month: string; value: number | undefined; digits?: number }) {
  if (value === undefined) return <span className="text-muted">not held</span>;
  const key = rowKey(entity, grid, metric, month);
  return <span data-row={key} title={key}>{shown(value, digits)}</span>;
}

/** The largest owners by operating MW, as horizontal bars. Server-drawn: no script runs in the browser. */
function Bars({ rows }: { rows: OwnerRow[] }) {
  const top = rows.slice(0, 15);
  const W = 760, rowH = 22, L = 250, R = 70, H = top.length * rowH + 8;
  const max = Math.max(...top.map((r) => r.operating_mw ?? 0), 1);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="The largest owners of operating battery storage, MW">
      {top.map((r, i) => {
        const w = ((r.operating_mw ?? 0) / max) * (W - L - R);
        return (
          <g key={r.entity}>
            <text x={L - 8} y={i * rowH + 15} textAnchor="end" fontSize="11" fill="#2E2D29">{r.name.length > 38 ? `${r.name.slice(0, 37)}...` : r.name}</text>
            <rect x={L} y={i * rowH + 4} width={Math.max(1, w)} height={rowH - 8} fill={BAR} />
            <text x={L + w + 6} y={i * rowH + 15} fontSize="11" fill="#2E2D29">{shown(r.operating_mw)}</text>
            <title>{`${r.name}: ${shown(r.operating_mw, 1)} MW operating`}</title>
          </g>
        );
      })}
    </svg>
  );
}

export default async function Owners({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const { grid } = choices(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])));
  const snap = data as unknown as Snapshot;
  const v = view(snap, grid);
  const g = v.grid;
  const m = v.month;
  const item = (on: boolean) => `block border-l-2 px-2 py-1 no-underline ${on ? "border-accent font-semibold text-accent" : "border-transparent text-ink hover:text-accent"}`;
  const first = v.operating[0];
  return (
    <ToolPage>
      <ToolHeader title="Who owns the batteries"
        lead={<>Operating and planned battery storage by the company that reports each plant, on each US grid, from the monthly generator inventory of the US Energy
          Information Administration. How much has been built is on <SiteLink href="/storage/buildout">Storage build-out</SiteLink>; what a battery earns is
          on <SiteLink href="/cost-of-power/battery">What a battery earns</SiteLink>. <SiteLink href={METHOD}>Method</SiteLink>.</>} />
      {grid.slug === "ercot" ? <AskErcotLink context={{ view: "/storage/owners", title: "Who owns the batteries", settings: { grid: "ERCOT" } }} /> : null}
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={`EIA's inventory of ${monthName(m)}. An owner here is the company that reports the plant to EIA, often a project company; parents are not named.`}>
            <nav aria-label="Grid">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              <ul className="text-sm">
                {GRIDS.map((x) => (
                  <li key={x.slug}><Link href={`/storage/owners?grid=${x.slug}`} aria-current={x.slug === grid.slug ? "true" : undefined} className={item(x.slug === grid.slug)}>{x.label}</Link></li>
                ))}
              </ul>
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!g || !first ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">
              <span className="font-semibold">no data</span>: {grid.name} has no operating battery storage in EIA&apos;s inventory of {monthName(m)}.
            </p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                {grid.name} has <V entity={g.entity} grid={grid.slug} metric="operating_mw" month={m} value={g.operating_mw} /> MW of operating batteries,
                reported by <V entity={g.entity} grid={grid.slug} metric="owners_operating" month={m} value={g.owners_operating} /> companies. The largest, {first.name},
                has <V entity={first.entity} grid={grid.slug} metric="operating_mw" month={m} value={first.operating_mw} /> MW; the ten largest
                hold <V entity={g.entity} grid={grid.slug} metric="top10_share_pct" month={m} value={g.top10_share_pct} digits={1} /> percent.
              </p>

              <HeadlineRow>
                <HeadlineNumber label="Operating" value={<><V entity={g.entity} grid={grid.slug} metric="operating_mw" month={m} value={g.operating_mw} /><span className="ml-1 font-sans text-sm text-muted">MW</span></>}
                  note={<><V entity={g.entity} grid={grid.slug} metric="operating_mwh" month={m} value={g.operating_mwh} /> MWh, an average
                    of <V entity={g.entity} grid={grid.slug} metric="operating_hours" month={m} value={g.operating_hours} digits={1} /> hours,
                    in <V entity={g.entity} grid={grid.slug} metric="operating_units" month={m} value={g.operating_units} /> units.</>} />
                <HeadlineNumber label="Held by the five largest" value={<><V entity={g.entity} grid={grid.slug} metric="top5_share_pct" month={m} value={g.top5_share_pct} digits={1} /><span className="ml-1 font-sans text-sm text-muted">percent</span></>}
                  note={<>Of operating MW. The ten largest: <V entity={g.entity} grid={grid.slug} metric="top10_share_pct" month={m} value={g.top10_share_pct} digits={1} /> percent,
                    among <V entity={g.entity} grid={grid.slug} metric="owners_operating" month={m} value={g.owners_operating} /> companies.</>} />
                <HeadlineNumber label="Planned" value={<><V entity={g.entity} grid={grid.slug} metric="planned_mw" month={m} value={g.planned_mw} /><span className="ml-1 font-sans text-sm text-muted">MW</span></>}
                  note={<><V entity={g.entity} grid={grid.slug} metric="planned_units" month={m} value={g.planned_units} /> units
                    of <V entity={g.entity} grid={grid.slug} metric="owners_planned" month={m} value={g.owners_planned} /> companies. EIA&apos;s planned inventory gives no MWh.</>} />
              </HeadlineRow>

              <ChartFrame title="The largest owners, operating MW" note={<>The fifteen largest of {grid.name.replace(/^The /, "the ")} by nameplate MW, as EIA names the reporting company. Two project companies of one developer are two bars.</>}>
                <Bars rows={v.operating} />
              </ChartFrame>

              <ToolSection title="Operating: the largest owners" note={v.operating.length > SHOWN ? `The ${SHOWN} largest of ${shown(g.owners_operating)} companies, by operating MW.` : "Every company with an operating battery, by operating MW."}>
                <ToolTable caption="Operating battery storage by owner" minWidth={700}
                  head={["", "Company, as EIA names it", "MW", "MWh", "Hours", "Units", "Share, percent", "Planned MW"]}
                  rows={v.operating.slice(0, SHOWN).map((r) => ({
                    key: r.entity,
                    cells: [
                      <V key="k" entity={r.entity} grid={grid.slug} metric="operating_rank" month={m} value={r.operating_rank} />,
                      <span key="n" className="block text-left">{r.name}</span>,
                      <V key="a" entity={r.entity} grid={grid.slug} metric="operating_mw" month={m} value={r.operating_mw} digits={1} />,
                      <V key="b" entity={r.entity} grid={grid.slug} metric="operating_mwh" month={m} value={r.operating_mwh} digits={1} />,
                      <V key="c" entity={r.entity} grid={grid.slug} metric="operating_hours" month={m} value={r.operating_hours} digits={1} />,
                      <V key="d" entity={r.entity} grid={grid.slug} metric="operating_units" month={m} value={r.operating_units} />,
                      <V key="e" entity={r.entity} grid={grid.slug} metric="operating_share_pct" month={m} value={r.operating_share_pct} digits={1} />,
                      r.planned_mw === undefined ? <span key="f" className="text-muted">none</span> : <V key="f" entity={r.entity} grid={grid.slug} metric="planned_mw" month={m} value={r.planned_mw} digits={1} />,
                    ],
                  }))} />
              </ToolSection>

              <ToolSection title="Planned: the largest owners" note={v.planned.length > SHOWN ? `The ${SHOWN} largest of ${shown(g.owners_planned)} companies, by planned MW.` : "Every company with a planned battery, by planned MW."}>
                {v.planned.length ? (
                  <ToolTable caption="Planned battery storage by owner" minWidth={560}
                    head={["Company, as EIA names it", "Planned MW", "Planned units", "Operating MW today"]}
                    rows={v.planned.slice(0, SHOWN).map((r) => ({
                      key: r.entity,
                      cells: [
                        <span key="n" className="block text-left">{r.name}</span>,
                        <V key="a" entity={r.entity} grid={grid.slug} metric="planned_mw" month={m} value={r.planned_mw} digits={1} />,
                        <V key="b" entity={r.entity} grid={grid.slug} metric="planned_units" month={m} value={r.planned_units} />,
                        r.operating_mw === undefined ? <span key="c" className="text-muted">none</span> : <V key="c" entity={r.entity} grid={grid.slug} metric="operating_mw" month={m} value={r.operating_mw} digits={1} />,
                      ],
                    }))} />
                ) : <p className="text-sm text-muted">No planned battery storage in {grid.name.replace(/^The /, "the ")} in EIA&apos;s inventory of {monthName(m)}.</p>}
              </ToolSection>
            </>
          )}

          <div className="mb-8 border-t border-rule">
            <Fold title="What an owner is here">
              <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                <li><strong>The reporting company.</strong> EIA&apos;s monthly inventory names one company for each plant: the one that reports it, its owner or its operator. Very often it is a project company formed for that plant.</li>
                <li><strong>No parents.</strong> The inventory does not say who owns the project company, and nothing here merges names. A developer with ten project companies appears as ten owners, so the shares of the largest are a floor on how concentrated ownership is.</li>
                <li><strong>No shares.</strong> Who owns what fraction of a plant is in EIA&apos;s annual survey, not the monthly one. A plant counts whole for the company that reports it.</li>
              </ul>
            </Fold>
            <Fold title="What is counted">
              <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                <li><strong>A battery</strong> is a generator whose prime mover is EIA&apos;s &quot;Batteries&quot;, in plants of 1 MW and above. Pumped hydro is not counted; nor is storage behind a customer&apos;s meter.</li>
                <li><strong>MW</strong> is nameplate power. <strong>MWh</strong> is EIA&apos;s nameplate energy capacity. <strong>Hours</strong> is MWh over MW for the units that report energy.</li>
                <li><strong>The grid</strong> is the balancing authority EIA records for the unit, where that is one of the seven grids; every other unit is outside the seven. The United States is every unit.</li>
                <li><strong>Planned</strong> is EIA&apos;s planned inventory, from projects with approvals pending to units under construction. It gives no MWh, so none is shown.</li>
                <li><strong>Rank and share</strong> are by operating MW within the grid chosen. Companies of equal MW are ordered by name.</li>
              </ul>
            </Fold>
          </div>
        </div>
      </div>
      <SourceLine tables={[TABLE]}
        note={<>Derived by the ERW from EIA-860M, the Monthly Electric Generator Inventory, of {monthName(m)} (public domain). Hover a number for the row it is. Read from the page&apos;s
          own copy of the table, built {snap.built.slice(0, 4)}-{snap.built.slice(4, 6)}-{snap.built.slice(6, 8)}.</>} />
    </ToolPage>
  );
}
