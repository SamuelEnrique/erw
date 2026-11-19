// Session 8602 (chain 504, 19 November 2026): the Grid tool with one of EIA's thirteen regions in view
// (/grid?region=se&view=mix). The same page, the same four tabs and the same Ask panel as for a grid; what each tab
// draws for a region is components/grid/RegionViews.tsx, from the whole country's page files (data/regions/, the data
// machine's). The page for a grid (page.tsx) is not changed by this file: it hands over only when the address names a
// region the index holds.
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { TableLicenses } from "@/components/tool/TableLicenses";
import { ToolPicker, ToolTabs } from "@/components/tool/Choose";
import { AskView } from "@/components/grid/AskView";
import { AskExamples } from "@/components/grid/AskExamples";
import { NetworkView } from "@/components/grid/NetworkView";
import { RegionAuthorities, RegionCleanView, RegionMixView, RegionPicker, RegionTradeView, isNewRegion } from "@/components/grid/RegionViews";
import { GRID_VIEW_TABLES } from "@/lib/gridtables";
import { ALIKE, regionHref, type Alike, type IndexRegion, type RegionIndex } from "@/lib/gridregions";
import { GRID_CHOICES, GRID_VIEWS, gridHref, type GridView } from "@/lib/gridtool";
import { licenseNeededTables } from "@/lib/license";
import { regionAlike, regionMix, regionTrade } from "@/lib/regionsdata";

type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

/** The `alike` object of each region that has one (Texas, New York, New England, the Mid-Atlantic), for the picker's hovers. */
export function alikeOf(index: RegionIndex | null): Record<string, Alike | null> {
  return index ? Object.fromEntries(Object.keys(ALIKE).map((code) => [code, regionAlike(code)])) : {};
}

const LEAD: Record<GridView, (r: IndexRegion) => string> = {
  network: (r) => `The balancing authorities that report to EIA-930 and the power they exchange. ${r.name} is ${r.bas.length} of them.`,
  mix: (r) => `What generates the power in ${r.name}: the latest hour held, the last 35 days hour by hour, the average day of any month, and year after year.`,
  clean: (r) => `How much CO2 the power of ${r.name} carries: what is held for a region, and what is not.`,
  gravity: (r) => `The power ${r.name} takes from and sends to each neighbouring region, by month, as each side reported it.`,
};

/** The choices this page makes for a region, said on the page. */
function RegionDecisions({ region }: { region: IndexRegion }) {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="8602">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (the thirteen regions, session 8602)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm">
        <li>A region is one of the thirteen of EIA&apos;s hourly grid monitor (Form EIA-930), with the balancing authorities EIA places in it. The page draws no region of its own making.</li>
        <li>A region is chosen by its own word in the address (<code className="font-mono">region={region.code.toLowerCase()}</code>), so every address of a grid reads as it did.</li>
        <li>A region has the tool&apos;s four tabs. A part of a tab that the region&apos;s file does not hold is drawn blank with its reason on hover; none is hidden and none is filled.</li>
        <li>A region&apos;s days and local hours are counted in the time zone of most of its demand, as its file says ({region.tz}).</li>
        <li>Demand is the sum of the region&apos;s balancing authorities that file demand, for an hour that every one of them holds; net imports are EIA&apos;s total interchange with its sign turned.</li>
        <li>Trade between two regions is shown from both sides&apos; reports with their gap; neither is adjusted to the other.</li>
        <li>The Ask panel is not changed: it answers from the warehouse&apos;s tables, as for the Lower 48, and does not read a region&apos;s page file.</li>
      </ul>
    </details>
  );
}

export async function RegionTool({ sp, index, region, view, node }: { sp: Query; index: RegionIndex; region: IndexRegion; view: GridView; node: string | null }) {
  const code = region.code, slug = code.toLowerCase();
  const us48 = GRID_CHOICES.find((g) => g.slug === "us48")!;
  const mixFile = view === "mix" ? regionMix(code) : null;
  const trade = view === "gravity" ? regionTrade(code) : null;
  const tabName = GRID_VIEWS.find(([k]) => k === view)![1];
  const tables = view === "mix" ? mixFile?.tables ?? [] : view === "gravity" ? trade?.tables ?? [] : view === "network" ? GRID_VIEW_TABLES.network : [];
  const fresh = isNewRegion(code);
  return (
    <Brand>
      <ToolPage>
        <div data-grid-tool="region" data-grid-region={code} data-grid-tool-view={view}>
          <ToolHeader crumb="The grid" title={`${region.name}: an EIA region`}
            lead={<>{LEAD[view](region)}{fresh ? <> <span title="Until the whole country's files (19 November 2026) the site drew the seven grids and the Lower 48. None of the seven grids is among this region's balancing authorities." className="cursor-help border-b border-dotted border-muted" data-region-new="1">None of the seven grids is among its balancing authorities.</span></> : null}</>}
            under={tables.length ? <TableLicenses tables={tables} /> : undefined} />
          <ToolPicker label="Grid" items={GRID_CHOICES.map((g) => ({ key: g.slug, label: g.label, href: gridHref(g.slug, view), on: false, title: g.name }))} />
          <RegionPicker index={index} on={code} view={view} alike={alikeOf(index)} />
          <ToolTabs label="Views" items={GRID_VIEWS.map(([k, label]) => ({ key: k, label, href: regionHref(code, k), on: k === view }))} />
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="min-w-0">
              {view === "network" ? (
                <div data-region-view="network">
                  <RegionAuthorities region={region} index={index} node={node} />
                  {/* keyed by the authority chosen: the network restores its view from the address once, when it is first drawn, so a new choice from the list above draws it anew with that panel open */}
                  <NetworkView key={node ?? "none"} keep={`?region=${slug}&view=network`} node={node} />
                </div>
              ) : null}
              {view === "mix" ? <RegionMixView region={region} mixFile={mixFile} period={one(sp.period) ?? null} cal={one(sp.cal) ?? null} /> : null}
              {view === "clean" ? <RegionCleanView region={region} /> : null}
              {view === "gravity" ? <RegionTradeView region={region} trade={trade} month={one(sp.month) ?? null} /> : null}
              <RegionDecisions region={region} />
            </div>
            <aside className="min-w-0 lg:border-l lg:border-rule lg:pl-6" aria-label="Ask" data-ask-side="us48" data-ask-tab={view} data-ask-region={code}>
              <h2 className="mb-1 font-serif text-lg text-accent" id="ask">Ask</h2>
              <p className="mb-3 text-xs text-muted" data-ask-on-screen="1">On screen: {region.name}, an EIA region, the {tabName} tab. The answer comes only from the warehouse&apos;s tables, each number with its table; the panel is asked as for the Lower 48 and does not read this region&apos;s page file.</p>
              <p className="mb-3 text-xs leading-relaxed text-muted" data-ask-licenses={licenseNeededTables().length}>
                Tables read, with their licenses: the public tables of the site&apos;s live set, through the panel&apos;s tools; the {licenseNeededTables().length} tables held for a license are refused by name or, for a table held by grid, read without the held grids&apos; rows.
              </p>
              <AskView grid={us48} question={one(sp.q) ?? ""} tab={view} compact />
              <AskExamples grid={us48} />
            </aside>
          </div>
          <Related href="/grid" />
        </div>
      </ToolPage>
    </Brand>
  );
}
