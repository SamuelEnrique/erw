// Energy Research Warehouse (ERW) site: how numbers and times are written.
// Values are shown as stored, rounded for display only; the rounding is stated where it matters.

/** "2026-09-26 07:30 UTC" from an ISO timestamp. */
export function utc(ts: string | null | undefined): string {
  if (!ts) return "";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return d.toISOString().slice(0, 16).replace("T", " ") + " UTC";
}

/** "2026-09-26" from an ISO timestamp. */
export function day(ts: string | null | undefined): string {
  if (!ts) return "";
  const d = new Date(ts);
  return Number.isNaN(d.getTime()) ? ts : d.toISOString().slice(0, 10);
}

/** A price with two decimals: "31.19". */
export function price(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "";
  return v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** A count with thousands separators: "3,725,119". */
export function count(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "";
  return Math.round(v).toLocaleString("en-US");
}

/** The node part of an entity: "ercot:HB_HUBAVG" gives "HB_HUBAVG". */
export function node(entity: string): string {
  const i = entity.indexOf(":");
  return i < 0 ? entity : entity.slice(i + 1);
}

/** Units as the ERW writes them, for display. */
export function unit(u: string | null | undefined): string {
  return u ?? "";
}
