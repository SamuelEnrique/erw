import type { Metadata } from "next";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { DOCS, render } from "@/lib/markdown";
import { filesOf, pyramidsOf, toggleGroups, KX, MIN_CELL_PX, QUEUE_GRIDS, type Layer } from "@/lib/resources";
import { readManifest } from "@/lib/resourcesdata";
import { ResourceMap } from "./ResourceMap";

// Session 146: "Where the resources are" (/resources, in review), under Projects. The project map shows what is built;
// this page shows the natural resource itself: one map, a toggle a resource layer, each at the finest grain its source
// and the screen allow, a legend in the source's own unit, and a hover that gives the value under the pointer with the
// layer's vintage. The layers are files the data side writes and lists in data/resources/manifest.json
// (warehouse/connectors/resource_layers.py); the page has one renderer a kind of layer and reads the rest from that
// list, so a layer that arrives later needs no code. What is built or planned is laid over it from tables the site
// already holds. The face is the title, one sentence, the toggles, the map and the legends: everything of method is in
// the Method note at the foot, closed until it is opened. No hub or zone is drawn: no operator's boundary is held.
// Session 159: hydropower is held (Oak Ridge National Laboratory's two assessments, in the form published); the gross
// capacity factor is a greyed toggle whose hover says why it is not fetched; the Method note states the queue grid by
// grid: each grid that is not shown reads its operator's own words, which are written once, in lib/resources.ts.

export const metadata: Metadata = { title: "Where the resources are", robots: { index: false, follow: false } };

const day = (s: string | undefined) => (s ? s.slice(0, 10) : "not stated");

function LayerNote({ l }: { l: Layer }) {
  const cells = (l.levels ?? []).map((v) => v.cell_deg).sort((a, b) => b - a);
  const parts = l.kind === "grid" ? pyramidsOf(l).slice(1) : [];
  const quotes = [...new Set([l.terms_quote, ...(Array.isArray(l.terms_quotes) ? l.terms_quotes : []), l.terms_notice, l.terms_in_file].filter((q): q is string => typeof q === "string" && q.trim().length > 0))];
  const credit = [l.credit, l.acknowledgment].filter((c): c is string => typeof c === "string" && c.trim().length > 0);
  const columns = l.columns_meaning && typeof l.columns_meaning === "object" ? Object.entries(l.columns_meaning) : [];
  return (
    <section className="mb-5" data-method-layer={l.id}>
      <h3 className="mb-1 font-serif text-base text-accent">{l.title}</h3>
      <dl className="grid max-w-3xl grid-cols-[6.5rem_minmax(0,1fr)] gap-x-3 gap-y-1 sm:grid-cols-[9rem_minmax(0,1fr)] [&>dd]:break-words">
        <dt className="text-muted">What it is</dt>
        <dd>{[l.value_label, l.source_title].filter(Boolean).join(". From: ") || "not stated"}{l.unit ? `, in ${l.unit}` : ""}{l.extent ? `; ${l.extent}` : ""}.{l.source_url ? <> <a href={l.source_url} rel="noreferrer">Source</a>.</> : null}</dd>
        <dt className="text-muted">Publisher</dt><dd>{l.publisher ?? "not stated"}</dd>
        <dt className="text-muted">Vintage</dt><dd>{l.vintage ?? "not stated"}; retrieved {day(l.retrieved_at_utc)}.</dd>
        {l.source_resolution ? <><dt className="text-muted">The source&apos;s grain</dt><dd>{l.source_resolution}</dd></> : null}
        {l.reduction ? <><dt className="text-muted">How it was reduced</dt><dd>{l.reduction}</dd></> : null}
        {cells.length ? <><dt className="text-muted">Drawn as</dt><dd>cells of {cells.join(", ")} degrees, the finer ones as the map is zoomed in.{parts.length ? ` In files of their own, read when the map shows them: ${parts.map((x) => `${x.extent} (cells of ${x.levels.map((v) => v.cell_deg).sort((a, b) => b - a).join(", ")} degrees)`).join("; ")}.` : ""}</dd></> : null}
        {l.kind === "points" ? <><dt className="text-muted">Drawn as</dt><dd>one mark a row of the source, at the source&apos;s own coordinates{typeof l.point_spacing_km === "number" ? `; a square of ${l.point_spacing_km} km, the source's own spacing` : ""}.</dd></> : null}
        {columns.length ? <><dt className="text-muted">On hover</dt><dd>{columns.map(([k, v]) => `${k}: ${v}`).join("; ")}.</dd></> : null}
        {l.classes?.length ? <><dt className="text-muted">Classes</dt><dd>{l.classes.map((c) => `${c.value}: ${c.label}`).join("; ")}</dd></> : null}
        <dt className="text-muted">Terms</dt>
        <dd>{quotes.length ? quotes.map((q, i) => <span key={i}>{i ? " " : ""}<q>{q}</q></span>) : "not quoted in the list of layers"}{l.terms_url ? <> (<a href={l.terms_url} rel="noreferrer">the publisher&apos;s terms</a>)</> : null}</dd>
        {credit.length ? <><dt className="text-muted">Credit</dt><dd>{credit.join("; ")}</dd></> : null}
        {l.notes_for_method ? <><dt className="text-muted">What it is not</dt><dd>{l.notes_for_method}</dd></> : null}
      </dl>
    </section>
  );
}

export default function Resources() {
  const { manifest, reason } = readManifest();
  const groups = toggleGroups(manifest);
  // what the map needs of each layer; the words of method stay on the server, in the note below
  const layers: Layer[] = manifest.layers.map((l) => ({
    id: l.id, group: l.group, title: l.title, kind: l.kind, unit: l.unit, publisher: l.publisher, vintage: l.vintage, extent: l.extent,
    levels: l.levels, file: l.kind === "grid" ? undefined : filesOf(l)[0], legend: l.legend, classes: l.classes,
    other_extents: l.other_extents?.map((x) => ({ extent: x.extent, levels: x.levels, legend: x.legend, grid: x.grid })), point_spacing_km: l.point_spacing_km,
    hover_fields: Array.isArray(l.hover_fields) ? l.hover_fields.filter((f) => Array.isArray(f) && typeof f[0] === "string" && typeof f[1] === "string") : undefined,
  }));
  const doc = DOCS.methods?.resources;
  const missing = groups.flatMap((g) => g.items.flatMap((it) => (it.held ? [] : [{ group: g.label, label: it.label, reason: it.reason }])));
  return (
    <ToolPage>
      <ToolHeader title="Where the resources are"
        lead={<>The project map shows what is built; this shows the natural resource itself: switch a layer on and point at the map for the value there.</>} />
      <ResourceMap layers={layers} groups={groups} manifestReason={reason} />

      <details className="mt-8 border-y border-rule py-2" data-method-note="1">
        <summary className="cursor-pointer font-serif text-lg text-accent">Method note</summary>
        <div className="pb-3 pt-3 text-sm leading-relaxed">
          <h3 className="mb-1 font-serif text-base text-accent">How the map is drawn</h3>
          <ul className="mb-5 max-w-3xl list-disc space-y-1 pl-5">
            <li>Longitude and latitude are drawn straight, with longitude squeezed by the cosine of 37.5 degrees north ({KX.toFixed(4)}), so that a cell of a grid is a rectangle on the screen. Shapes far from that latitude, Alaska above all, look wider than on a globe; no value depends on it.</li>
            <li>A grid layer is a pyramid of levels, each a regular grid of cells in degrees. The level drawn is the finest whose cells are at least {MIN_CELL_PX} of a screen pixel wide at the current zoom; a finer level is asked for only when the zoom calls for it. Cells are drawn as stored, with no smoothing between them and nothing filled in: a cell the source leaves empty stays empty.</li>
            <li>The value on hover is the stored value of the cell under the pointer in the level being drawn, in the source&apos;s own unit, so the same place can read slightly differently at two zooms: a coarser cell is the mean of the source&apos;s cells inside it. The legend&apos;s range is the one the list of layers gives for the layer.</li>
            <li>A resource layer is the publisher&apos;s estimate of a resource over an area. It is not a siting study, and it says nothing of land use, access to transmission, permits or cost.</li>
            <li>No price hub or zone is drawn: no operator&apos;s published boundary or coordinates are held, and none is invented.</li>
            <li>The address holds what is switched on, the zoom and the centre, so a view can be shared. Every file is read from this site; the page asks nothing of any other.</li>
            <li>While the map is being moved, a layer of many shapes or points is shown as a still picture of itself, and a map with very many marks on it at once (every layer and every overlay, or the operating plants at the widest view) is shown as the picture last drawn in full, moved and scaled with the view over the bare states. When the map comes to rest everything is drawn again as it is. No value is read from a picture: the hover is read from the files, at rest.</li>
          </ul>

          {manifest.layers.map((l) => <LayerNote key={l.id} l={l} />)}

          {missing.length ? (
            <section className="mb-5" data-method-missing="1">
              <h3 className="mb-1 font-serif text-base text-accent">Layers not held</h3>
              <ul className="max-w-3xl list-disc space-y-1 pl-5">{missing.map((m) => <li key={`${m.group}:${m.label}`}>{m.group}, {m.label}: {m.reason}</li>)}</ul>
            </section>
          ) : null}

          <section className="mb-5" data-method-overlays="1">
            <h3 className="mb-1 font-serif text-base text-accent">What is built or planned</h3>
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li><strong>Plants.</strong> Every operating and planned generating unit of the U.S. Energy Information Administration&apos;s monthly inventory, Form EIA-860M (public domain), at the coordinates EIA gives for its plant, from the tables <code className="font-mono text-xs">eia860m_operating_generators</code> and <code className="font-mono text-xs">eia860m_planned_generators</code> as the project map&apos;s own copy holds them. A mark is a unit, not a plant; its color is its fuel, as on the project map, and its size grows with its nameplate MW. The form covers plants of 1 MW and more.</li>
              <li><strong>The interconnection queue.</strong> The queue rows of the table <code className="font-mono text-xs">energy_projects</code> in the live set, which holds requests that are not withdrawn, from the queue reports of the grids whose operators allow it: {QUEUE_GRIDS.filter((g) => g.shown).map((g) => g.label).join(", ")}. The count of rows drawn and not drawn, in all and for each grid, is the live set&apos;s own each time the overlay is read. {QUEUE_GRIDS.filter((g) => !g.shown).map((g) => <span key={g.id} data-method-queue-grid={g.id}>{g.label}: {g.words}. {g.why} Any row of {g.label}&apos;s that the table holds is counted and left out of the map. </span>)}The reports give a county, not a site. A row is counted in the county whose published outline (the Census Bureau&apos;s cartographic boundary files, as the us-atlas package carries them) holds the point the table gives for that county, or, where the outline leaves that point at sea, in the one county of that name in that state; the county is shaded, darker with more MW asked for, and nothing is drawn at a site. A row that names neither a county the Census Bureau&apos;s county list holds nor coordinates is not drawn and is counted. A request is not a plant: most are withdrawn before they are built.</li>
              <li><strong>Datacenters.</strong> The facilities of the table <code className="font-mono text-xs">datacenter_facilities</code> that the table places: at the operator&apos;s own coordinates, or at the point of the county or city a source names, which is not the site. It is not a census of every facility, and MW is shown only where a source states it.</li>
            </ul>
          </section>

          {doc ? (
            <section data-method-doc="1">
              <h3 className="mb-1 font-serif text-base text-accent">The method document</h3>
              <p className="mb-2 text-xs text-muted"><code className="font-mono">docs/methods/resources.md</code>, as committed.</p>
              <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(doc, "docs/methods/resources.md") }} />
            </section>
          ) : (
            <p className="text-xs text-muted" data-method-doc="0">The method document <code className="font-mono">docs/methods/resources.md</code> was not in the repository when this page was built.</p>
          )}
          <p className="mt-4 text-xs text-muted">List of layers built {day(manifest.built_at_utc)}.</p>
        </div>
      </details>
    </ToolPage>
  );
}
