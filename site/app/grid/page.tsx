import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { ToolPicker, ToolTabs } from "@/components/tool/Choose";
import { AskBox, AskView } from "@/components/grid/AskView";
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
// picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP and the Lower 48) and six views of the grid chosen:
// Now, Network, Mix, Clean, Exchange and Ask. The grid and the view are in the address (lib/gridtool.ts:
// /grid?grid=ercot&view=mix), so any view can be shared.
// What stood at this address until now, "Grid conditions" (sessions 15 to 118), is drawn by the Now view (the grid's
// block) and the Mix view (the table of every region): components/grid/Conditions.tsx. The pages that redirect here
// (next.config.ts) are drawn whole by the views: /network by Network, /mix and /mix/stress by Mix, /emissions and
// /mix/clean by Clean, the seven /grid/<iso> by Now, Mix, Clean and Ask. runs/session237/inventory.md, copied into the
// session's report, lists every block of every one of them and where it is now.
// Every grid's four numbers come from the public EIA-930 tables; a block that reads a grid operator's own table keeps
// the gate it had (lib/license.ts through lib/supabase.ts and components/Num.tsx).
export const revalidate = 3600;

type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

export async function generateMetadata({ searchParams }: { searchParams: Promise<Query> }): Promise<Metadata> {
  const p = gridPick(await searchParams);
  return { title: `The grid: ${p.grid.label}, ${GRID_VIEWS.find(([k]) => k === p.view)![1]}` };
}

const LEAD: Record<string, string> = {
  now: "What the grid is doing in the latest hours held: demand, the mix, the exchange with its neighbours and carbon.",
  network: "The balancing authorities that report to EIA-930 and the power they exchange, with this grid in view.",
  mix: "What generates the power: now, the average day of any month, year after year, and how hard the system works.",
  clean: "How much CO2 the power carries, now and since 2018, and how clean each hour is.",
  exchange: "The power this grid sends to and takes from its neighbours: the latest hour, the week and twelve months.",
  ask: "A question about this grid, answered from the warehouse's tables.",
};

export default async function GridTool({ searchParams }: { searchParams: Promise<Query> }) {
  const sp = await searchParams;
  const p = gridPick(sp);
  const { grid, view } = p;
  const cfg = grid.slug === "us48" ? null : gridOf(grid.slug);
  // the grid's own reads (lib/grid.ts), for the views that draw its page's blocks
  const data = cfg && (view === "now" || view === "mix" || view === "clean") ? await load(cfg) : null;
  // the mix page's own choice, read from the same address: its view is written under "mix", its grids open on the grid in view
  const mixQuery: Query = { ...sp, view: view === "clean" ? "clean" : one(sp.mix), grid: undefined };
  if (grid.slug === "us48") { if (!one(sp.ba)) mixQuery.ba = "us48"; } else if (!one(sp.grids)) mixQuery.grids = grid.slug;
  const mix = { ...choiceOf(mixQuery), base: { href: gridHref(grid.slug, view === "clean" ? "clean" : "mix"), viewKey: view === "clean" ? null : "mix", grid: grid.slug } };
  const keep = gridHref(grid.slug, "network").slice("/grid".length);
  return (
    <Brand>
      <ToolPage>
        <div data-grid-tool={grid.slug} data-grid-tool-view={view}>
          <ToolHeader crumb="The grid" title={grid.slug === "us48" ? "The Lower 48 states" : `${grid.label}: ${grid.name}`} lead={LEAD[view]} />
          <ToolPicker label="Grid" items={GRID_CHOICES.map((g) => ({ key: g.slug, label: g.label, href: gridHref(g.slug, view), on: g.slug === grid.slug, title: g.name }))} />
          <ToolTabs label="Views" items={GRID_VIEWS.map(([k, label]) => ({ key: k, label, href: gridHref(grid.slug, k), on: k === view }))} />
          {view === "now" ? <NowView grid={grid} cfg={cfg} data={data} /> : null}
          {view === "network" ? <NetworkView keep={keep} node={p.node} /> : null}
          {view === "mix" ? (
            <div data-grid-view="mix">
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
          {view === "exchange" ? <ExchangeView grid={grid} /> : null}
          {view === "ask" ? <AskView grid={grid} question={one(sp.q) ?? ""} /> : <AskBox grid={grid} />}
          <Related href="/grid" />
        </div>
      </ToolPage>
    </Brand>
  );
}
