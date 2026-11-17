// Energy Research Warehouse (ERW) site, session 7709: ruling alternative 3 of /explore/demand-growth (branch
// wip/alt-demand-growth-3; not a default on main). A site's own MW, typed in the address (?site=), as a share of each
// grid's growth since the base year: the whole year's average demand at its last whole year less the base year's
// (lib/explore/demandgrowth.ts siteShare). A plain GET form: nothing is sent but the address. No figure that stands moves.
import { Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { BASE, GRIDS, entityOf, siteShare, type Row } from "@/lib/explore/demandgrowth";

const whole = (x: number) => Math.round(x).toLocaleString("en-US");
const two = (x: number) => x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function SiteShareSection({ rows, grid, win, mw, typed }: { rows: Row[]; grid: string; win: string; mw: number | null; typed: string | undefined }) {
  return (
    <ToolSection title="A site's MW against the growth"
      note={<>The share of each grid&apos;s growth since {BASE} a site of the size typed would take.<Tip id="demand-growth-site" label="how the share is read"><span data-site-tip="1">The site&apos;s MW over the
        grid&apos;s growth in MW: the whole year&apos;s average demand at its last whole year less {BASE}&apos;s, two rows of the table. A grid whose demand fell has no growth to take a share of. A site&apos;s MW is set
        beside average demand, not peak: a site that runs every hour at its size adds about that much to the average. Default on the site: no input. Source: EIA Form EIA-930 (eia930_demand_growth).</span></Tip></>}>
      <form method="get" action="/explore/demand-growth" className="mb-3 flex flex-wrap items-end gap-2 text-sm" data-site-form="1">
        <input type="hidden" name="grid" value={grid} /><input type="hidden" name="window" value={win} />
        <label className="block"><span className="font-semibold">A site&apos;s size</span> <span className="text-xs text-muted">MW</span>
          <input type="text" inputMode="decimal" name="site" defaultValue={typed ?? ""} className="mt-1 block w-32 border border-rule bg-white px-2 py-1" data-site-input="1" /></label>
        <button type="submit" className="border border-rule bg-white px-3 py-1">Show</button>
      </form>
      {mw === null ? <p className="text-sm" role="status" data-site="none">{typed ? `"${typed}" is not a size this page can use (more than 0, up to 100,000 MW).` : "Type a site's size in MW to see its share of each grid's growth."}</p> : (
        <ToolTable caption={`A ${whole(mw)} MW site as a share of each grid's growth since ${BASE}`} minWidth={520}
          head={["Grid", `${BASE}, MW`, "Last whole year, MW", "Growth, MW", `A ${whole(mw)} MW site, percent of it`]}
          rows={GRIDS.map((g) => {
            const s = siteShare(rows, entityOf(g.ba), mw);
            return { key: g.slug, highlight: g.slug === grid, cells: s === null ? [g.name, "not held", "not held", "not held", ""] : [
              g.name, whole(s.base), `${whole(s.latest)} (${s.year})`, `${s.growthMw > 0 ? "+" : ""}${whole(s.growthMw)}`,
              s.sharePct === null ? <span key="n" className="text-muted" data-site-share={g.slug}>demand fell: no share</span> : <span key="p" data-site-share={g.slug}>{two(s.sharePct)}</span>] };
          })} />
      )}
    </ToolSection>
  );
}
