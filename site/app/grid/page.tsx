import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { ToolPicker, ToolTabs } from "@/components/tool/Choose";
import { AskView } from "@/components/grid/AskView";
import { MixTable } from "@/components/grid/Conditions";
import { EmissionsParts } from "@/components/grid/Emissions";
import { ExchangeView } from "@/components/grid/ExchangeView";
import { MixClean, MixView } from "@/components/grid/MixView";
import { NetworkView } from "@/components/grid/NetworkView";
import { NowView } from "@/components/grid/NowView";
import { GridCleanParts, GridMixParts } from "@/components/grid/YourGrid";
import { gridOf, load } from "@/lib/grid";
import { GRID_CHOICES, GRID_VIEWS, gridHref, gridPick } from "@/lib/gridtool";
import { choiceOf } from "@/lib/mixpage";

// Session 237 (the owner's task of 12 October 2026; the roadmap's item 2): the Grid tool. One page, one address. A
// picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP and the Lower 48) and the views of the grid chosen. The
// grid and the view are in the address (lib/gridtool.ts: /grid?grid=ercot&view=mix), so any view can be shared.
// What stood at this address until then, "Grid conditions" (sessions 15 to 118), is drawn by the Now blocks (the grid's
// block) and the Mix view (the table of every region): components/grid/Conditions.tsx. The pages that redirect here
// (next.config.ts) are drawn whole by the views: /network by Network, /mix and /mix/stress by Mix, /emissions and
// /mix/clean by Clean, the seven /grid/<iso> by Mix, Clean and the Ask panel. runs/session237/inventory.md, copied into
// the session's report, lists every block of every one of them and where it is now.
// Every grid's four numbers come from the public EIA-930 tables; a block that reads a grid operator's own table keeps
// the gate it had (lib/license.ts through lib/supabase.ts and components/Num.tsx).
// Session 299 (the owner's merge of 18 October 2026, and the Grid pack's rulings): four tabs across the top, Network,
// Mix, Clean and Gravity; the grid picker once, above them; Ask as a panel on the right of every tab, reading the grid
// and the tab on screen and answering from the warehouse through the existing /api/ask routes. The Now view's blocks
// (the latest hour: demand, the exchange, carbon, the mix in that hour) open the Mix tab; the Exchange view's blocks sit
// under the gravity shape; an old address (view=now, view=exchange, view=ask) opens the tab that holds its blocks
// (lib/gridtool.ts, OLD_VIEWS). The page opens on the Lower 48 (ruling 4b); the gravity shape's pull is a square-root
// scale (2c), EIA-930 is its one source with CAISO's break named (1a), and the 63 other balancing authorities stay out
// (6a); the exchange hour's age is said twice, against the snapshot's refresh (checkable, in the data line) and against
// the clock when the page was drawn (3c). No block changed its markup inside the wrapper; no number moved.
export const revalidate = 3600;

type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

export async function generateMetadata({ searchParams }: { searchParams: Promise<Query> }): Promise<Metadata> {
  const p = gridPick(await searchParams);
  return { title: `The grid: ${p.grid.label}, ${GRID_VIEWS.find(([k]) => k === p.view)![1]}` };
}

const LEAD: Record<string, string> = {
  network: "The balancing authorities that report to EIA-930 and the power they exchange, with this grid in view.",
  mix: "What the grid is doing in the latest hours held, and what generates the power: now, the average day of any month, year after year, and how hard the system works.",
  clean: "How much CO2 the power carries, now and since 2018, and how clean each hour is.",
  gravity: "The seven grids around the Lower 48, each sized by its generation and pulled by its imports; and the power this grid sends to and takes from its neighbours.",
};

/** Session 299: the rulings this page carries, said on the page (the chain prompt of 19 October 2026 asks for a decisions block). */
function Decisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="299">
      <summary className="cursor-pointer text-accent">Decisions on this page (the owner&apos;s rulings of 18 October 2026, session 299)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm">
        <li>One page, four tabs (Network, Mix, Clean, Gravity), the grid picked once above them, and Ask as a panel beside every tab. The Now view&apos;s blocks open the Mix tab; the Exchange view&apos;s sit under the gravity shape; every older address still resolves to the tab that holds its blocks.</li>
        <li>The page opens on the Lower 48, then the reader picks a grid (ruling 4b; ERCOT until then).</li>
        <li>The gravity shape keeps EIA-930&apos;s net generation as its one source for every grid, and says that CAISO&apos;s reads smaller and more pulled in since December 2025 (1a); its pull is a square-root scale, full at 25 percent of generation (2c); the 63 other balancing authorities are not drawn (6a).</li>
        <li>How old &quot;now&quot; is, said twice: the hour&apos;s age against the snapshot&apos;s hourly refresh, which the value checker can recompute, in the data line; and against the clock when this page was drawn, beside it (3c).</li>
        <li>Nothing a block showed moved: every number carried over keeps its markup inside the wrapper and its check key; ERCOT at full depth, the other grids where their tables are public, &quot;license needed&quot; where they are not.</li>
      </ul>
    </details>
  );
}

export default async function GridTool({ searchParams }: { searchParams: Promise<Query> }) {
  const sp = await searchParams;
  const p = gridPick(sp);
  const { grid, view } = p;
  const cfg = grid.slug === "us48" ? null : gridOf(grid.slug);
  // the grid's own reads (lib/grid.ts), for the tabs that draw its page's blocks
  const data = cfg && (view === "mix" || view === "clean") ? await load(cfg) : null;
  // the mix page's own choice, read from the same address: its view is written under "mix", its grids open on the grid in view
  const mixQuery: Query = { ...sp, view: view === "clean" ? "clean" : one(sp.mix), grid: undefined };
  if (grid.slug === "us48") { if (!one(sp.ba)) mixQuery.ba = "us48"; } else if (!one(sp.grids)) mixQuery.grids = grid.slug;
  const mix = { ...choiceOf(mixQuery), base: { href: gridHref(grid.slug, view === "clean" ? "clean" : "mix"), viewKey: view === "clean" ? null : "mix", grid: grid.slug } };
  // the page's own words the network component keeps in the address; on the Gravity tab the shape word is the component's own
  const keep = view === "gravity" ? `?grid=${grid.slug}&view=gravity` : gridHref(grid.slug, "network").slice("/grid".length);
  const tabName = GRID_VIEWS.find(([k]) => k === view)![1];
  return (
    <Brand>
      <ToolPage>
        <div data-grid-tool={grid.slug} data-grid-tool-view={view} data-grid-ask={p.ask ? "open" : "panel"}>
          <ToolHeader crumb="The grid" title={grid.slug === "us48" ? "The Lower 48 states" : `${grid.label}: ${grid.name}`} lead={LEAD[view]} />
          <ToolPicker label="Grid" items={GRID_CHOICES.map((g) => ({ key: g.slug, label: g.label, href: gridHref(g.slug, view), on: g.slug === grid.slug, title: g.name }))} />
          <ToolTabs label="Views" items={GRID_VIEWS.map(([k, label]) => ({ key: k, label, href: gridHref(grid.slug, k), on: k === view }))} />
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="min-w-0">
              {view === "network" ? <NetworkView keep={keep} node={p.node} /> : null}
              {view === "mix" ? (
                <div data-grid-view="mix">
                  {/* session 299: the Now view's blocks, the grid's latest hour, open the tab */}
                  <div data-grid-now="1"><NowView grid={grid} cfg={cfg} data={data} /></div>
                  {grid.slug === "us48" && mix.view !== "now" && mix.view !== "history" ? <p className="mb-3 max-w-3xl text-sm text-muted">This view is by grid, and the Lower 48 is not one of its grids: it opens on ERCOT. Choose grids below, or a grid above.</p> : null}
                  <MixView c={mix} />
                  {cfg && data ? <div className="mt-10"><GridMixParts g={cfg} d={data} /></div> : null}
                  <div className="mt-10"><MixTable /></div>
                </div>
              ) : null}
              {view === "clean" ? (
                <div data-grid-view="clean">
                  {cfg && data ? <GridCleanParts g={cfg} d={data} /> : null}
                  <EmissionsParts focus={`eia930:${grid.ba}`} />
                  <div className="mt-10"><MixClean c={mix} /></div>
                </div>
              ) : null}
              {view === "gravity" ? (
                <div data-grid-view="gravity">
                  {/* session 299: the network component in its gravity shape (the address carries shape=gravity), the Exchange view's blocks under it */}
                  <NetworkView keep={keep} node={p.node} shape="gravity" />
                  <div className="mt-10"><ExchangeView grid={grid} /></div>
                </div>
              ) : null}
              <Decisions />
            </div>
            {/* session 299: Ask as a panel beside every tab: it names the grid and the tab on screen, and answers through the existing routes */}
            <aside className="min-w-0 lg:border-l lg:border-rule lg:pl-6" aria-label="Ask" data-ask-side={grid.slug} data-ask-tab={view}>
              <h2 className="mb-1 font-serif text-lg text-accent" id="ask">Ask</h2>
              <p className="mb-3 text-xs text-muted" data-ask-on-screen="1">On screen: {grid.slug === "us48" ? "the Lower 48" : grid.label}, the {tabName} tab. The answer comes only from the warehouse&apos;s tables, each number with its table.</p>
              <AskView grid={grid} question={one(sp.q) ?? ""} tab={view} compact />
            </aside>
          </div>
          <Related href="/grid" />
        </div>
      </ToolPage>
    </Brand>
  );
}
