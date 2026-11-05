// Energy Research Warehouse (ERW) site, session 1009 (chain 070): the download's filters, as the packages send them
// (docs/methods/packages.md, fetch: entity, variable, a UTC window). No import, so a test can run it with Node and set
// its query beside the Python package's (erw.live.series_filters), filter for filter.
//
//   entity     entities as the table writes them (ercot:HB_NORTH), or nodes as the grid operator writes them (HB_NORTH);
//              an entities table's ids; an events table's sources. Several, comma separated
//   variable   variables, entity types or event types, comma separated
//   start, end a window of interval starts, [start, end), in UTC: YYYY-MM-DD or YYYY-MM-DDThh:mm:ssZ

export type Shape = "series" | "entities" | "events";
export type Filter = { query: string; words: string[] } | { error: string };

const VALUE = /^[A-Za-z0-9_.:\- ]{1,80}$/;
const TIME = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z)?$/;

/** A value as a PostgREST list item: in double quotes, encoded as the Python package encodes it (%22). */
const item = (v: string) => `%22${encodeURIComponent(v).replace(/%3A/gi, ":").replace(/%20/g, "+")}%22`;
const list = (vs: string[]) => `in.(${vs.map(item).join(",")})`;
const utc = (t: string) => (t.length === 10 ? `${t}T00:00:00Z` : t);

/** The query a download adds to its pages' reads, and the words its header says, or the error to answer with. */
export function downloadFilter(shape: Shape, p: { entity?: string | null; variable?: string | null; start?: string | null; end?: string | null }): Filter {
  const cols = shape === "series" ? ["entity", "variable", "ts_utc"] : shape === "entities" ? ["entity_id", "entity_type", "status_date"] : ["source", "event_type", "event_date"];
  const split = (s: string | null | undefined) => (s ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  const ents = split(p.entity), vars = split(p.variable);
  for (const v of [...ents, ...vars]) if (!VALUE.test(v)) return { error: `${v.slice(0, 40)}: a value is letters, digits and _ . : - or a space` };
  for (const t of [p.start, p.end]) if (t && !TIME.test(t)) return { error: `${t.slice(0, 40)}: a time is YYYY-MM-DD or YYYY-MM-DDThh:mm:ssZ, in UTC` };
  let query = "";
  const words: string[] = [];
  if (ents.length) {
    let col = cols[0];
    if (shape === "series") {
      const colon = ents.filter((e) => e.includes(":")).length;
      if (colon && colon < ents.length) return { error: "entity: name entities (ercot:HB_NORTH) or nodes (HB_NORTH), not both" };
      col = colon ? "entity" : "node";
    }
    query += `&${col}=${list(ents)}`;
    words.push(`${col} ${ents.join(", ")}`);
  }
  if (vars.length) {
    query += `&${cols[1]}=${list(vars)}`;
    words.push(`${cols[1]} ${vars.join(", ")}`);
  }
  if (p.start) {
    query += `&${cols[2]}=gte.${utc(p.start)}`;
    words.push(`from ${utc(p.start)}`);
  }
  if (p.end) {
    query += `&${cols[2]}=lt.${utc(p.end)}`;
    words.push(`before ${utc(p.end)}`);
  }
  return { query, words };
}
