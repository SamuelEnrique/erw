// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part D): the project map's line layers. Each is one
// file of the data machine's (warehouse/connectors/hifld_lines.py, site/data/map_layers/<file>.json; method
// docs/methods/map_layers.md), served by app/map/lines/[name]/route.ts and read by the map only when its switch is
// turned on. The files are in columns (fields, rows, names, paths): this module turns a row back into its figures.

export type LineFile = { built: string; tables: string[]; method: string; license: string; source: string; source_url: string; retrieved_at: string;
  simplify_tolerance_deg: number; unit: string; lines: number; km: number; fields: string[]; text_fields: string[]; names: string[];
  rows: (string | number | null)[][]; paths: number[][][] };

export type LineLayer = { key: string; label: string; color: string; width: number; table: string;
  hover: (get: (k: string) => string | number | null) => { name: string; operator: string; size: string } };

/** Session 9601 (chain 620, the browser read of 20 November 2026): HIFLD writes "UNKNOWN201257" where it does not name
 *  a line's end (a third of the lines of 230 kV and above have one, 881 have two). The hover printed the mark as a
 *  place ("UNKNOWN201257 to UNKNOWN203126"). An end so marked is said to be unnamed, with HIFLD's mark kept beside it. */
const HIFLD_UNNAMED = /^UNKNOWN\d+$/;
export const lineEnd = (v: string | number | null): string => {
  const s = v === null ? "" : String(v);
  return HIFLD_UNNAMED.test(s) ? `an end HIFLD does not name (its mark ${s})` : s;
};

/** The two line layers, in the order of their switches. Each is off when the page opens. */
export const LINE_LAYERS: LineLayer[] = [
  { key: "transmission", label: "Transmission lines, 230 kV and above", color: "--color-ink", width: 0.8, table: "hifld_transmission_lines",
    hover: (g) => ({
      name: g("from") && g("to") ? `${lineEnd(g("from"))} to ${lineEnd(g("to"))}` : "No end named in the source",
      operator: (g("owner") as string | null) ?? "Owner not stated",
      size: `${g("kv") === null ? "Voltage not stated" : `${g("kv")} kV`}, ${g("km") === null ? "" : `${g("km")} km as drawn by HIFLD`}`,
    }) },
  { key: "hgl", label: "HGL pipelines (EIA)", color: "--color-fuel-gas", width: 1.2, table: "eia_hgl_pipelines",
    hover: (g) => ({
      name: (g("name") as string | null) ?? "No name in the source",
      operator: (g("operator") as string | null) ?? "Operator not stated",
      size: `${g("km") === null ? "Length not stated" : `${g("km")} km`} (EIA gives no capacity)`,
    }) },
];

/** A row's value by field name, a text field read through the file's names. */
export function getter(f: LineFile, i: number): (k: string) => string | number | null {
  return (k: string) => {
    const j = f.fields.indexOf(k);
    if (j < 0) return null;
    const v = f.rows[i]?.[j] ?? null;
    return f.text_fields.includes(k) && typeof v === "number" ? f.names[v] ?? null : v;
  };
}

/** A line's parts as lists of [longitude, latitude]. */
export function partsOf(f: LineFile, i: number): [number, number][][] {
  return (f.paths[i] ?? []).map((flat) => {
    const out: [number, number][] = [];
    for (let k = 0; k + 1 < flat.length; k += 2) out.push([flat[k], flat[k + 1]]);
    return out;
  });
}

/** The layer's words of source, for the hover and the key. */
export const sourceLine = (f: LineFile, l: LineLayer) =>
  `${f.source}, as the ERW's table ${l.table} holds it (retrieved ${f.retrieved_at.slice(0, 10)}); simplified for the web at ${f.simplify_tolerance_deg} degrees.`;
