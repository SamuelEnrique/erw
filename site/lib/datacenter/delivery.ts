// Session 236 (the owner's chain prompt of 12 October 2026): Texas's delivery charges on "What a datacenter pays"
// (/cost-of-power) as one row a component, each in USD per MWh for a flat load, and their total; the tariff's own lines
// (the schedule names, the rates as filed) are in the page's download, tables.csv. Pure arithmetic, no React, no
// import: Node runs this file as it is (scripts/check-values.mjs recomputes every figure here from the site's own file,
// data/datacenter/texas_delivery.json). Until this session the page drew each tariff line in a cell and stated one
// figure per MWh, the transmission cost recovery factor alone, for the two utilities that bill it per kW:
// (rate x 12,000) / 8,760. That figure is `perMwh` of the same line here, to the bit. The method is
// docs/methods/datacenter_pays_algorithm.md, section 4.18.

/** A tariff line as data/datacenter/texas_delivery.json holds it (the fields the arithmetic reads). */
export type Charge = { utility: string; kind?: string; charge: string; value: number; unit: string; applies?: string };
/** How a line is billed, read from the unit the tariff prints. */
export type Basis = "four_peak_demand" | "billing_demand" | "customer_month" | "energy";
export const KINDS = ["transmission", "distribution", "other"] as const;
export type Kind = (typeof KINDS)[number];
export const KIND_LABELS: Record<Kind, string> = { transmission: "Transmission", distribution: "Distribution", other: "Other riders" };
/** The hours of the year a flat load's energy is counted over (the page's figure since session 138). */
export const YEAR_HOURS = 8760;

/** The basis a unit names: "per kWh" is energy; a unit naming the four coincident peaks is the load's demand in them;
 * any other "kW" or "kVA" is its billing demand; "per Retail Customer", "per Meter" and "per ESI ID" are an account a
 * month. A unit that names none of these is not converted (null). */
export function basisOf(unit: string): Basis | null {
  const u = unit.toLowerCase().replace(/\s+/g, "");
  if (u.includes("kwh")) return "energy";
  if (u.includes("4cp")) return "four_peak_demand";
  if (u.includes("kw") || u.includes("kva")) return "billing_demand";
  if (u.includes("customer") || u.includes("meter") || u.includes("esiid")) return "customer_month";
  return null;
}
/** Whether a line applies only to some loads by the tariff's own words (a municipal fee or credit, a charge of one
 * former service area): it stands in the download and is not added. */
export const conditional = (r: Charge) => (r.applies ?? "").trim().toLowerCase().startsWith("conditional");
export const kindOf = (r: Charge): Kind => (r.kind === "distribution" ? "distribution" : r.kind === "other" ? "other" : "transmission");

/** One line in USD per MWh for a flat load of `mw` megawatts: its demand in the four peak intervals and its billing
 * demand are its size (a kVA is counted as a kW, a power factor of 1), every hour of 8,760 is run, and it is one
 * account with one meter.
 *   a rate per kW a month:      (rate x 12,000) / 8,760        (12 months, 1,000 kW a MW, over the MWh a MW uses in a year)
 *   a rate per kWh:             rate x 1,000
 *   a rate per account a month: (rate x 12) / (mw x 8,760)
 * Null when the unit names no basis. */
export function perMwh(r: Charge, mw: number): number | null {
  const b = basisOf(r.unit);
  if (b === null) return null;
  if (b === "energy") return r.value * 1000;
  if (b === "customer_month") return mw > 0 ? (r.value * 12) / (mw * YEAR_HOURS) : null;
  return (r.value * 12000) / YEAR_HOURS;
}

export type Component = { kind: Kind; label: string; perMwh: number; lines: number; conditional: number; unread: number };
export type UtilityDelivery = { utility: string; components: Component[]; total: number; lines: number; conditional: number; unread: number };
/** One utility's charges by component: the sum of its lines that apply to every such load, in USD per MWh, the count of
 * lines added, of lines left out as conditional and of lines whose unit names no basis; and the total of the three. */
export function deliveryOf(rows: Charge[], utility: string, mw: number): UtilityDelivery {
  const mine = rows.filter((r) => r.utility === utility);
  const components = KINDS.map((kind) => {
    const c: Component = { kind, label: KIND_LABELS[kind], perMwh: 0, lines: 0, conditional: 0, unread: 0 };
    for (const r of mine) {
      if (kindOf(r) !== kind) continue;
      if (conditional(r)) { c.conditional++; continue; }
      const v = perMwh(r, mw);
      if (v === null) { c.unread++; continue; }
      c.perMwh += v; c.lines++;
    }
    return c;
  });
  const sum = (f: (c: Component) => number) => components.reduce((a, c) => a + f(c), 0);
  return { utility, components, total: sum((c) => c.perMwh), lines: sum((c) => c.lines), conditional: sum((c) => c.conditional), unread: sum((c) => c.unread) };
}
/** The utilities of a file, in its order. */
export const utilitiesOf = (rows: Charge[]): string[] => [...new Set(rows.map((r) => r.utility))];
/** A utility's name as a check key writes it: lower case, a run of other characters one underscore. */
export const slugOf = (utility: string) => utility.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");

/** One figure by its name, for the check key dcd|<mw>|<utility's slug>:<kind or total>: the page writes it, and
 * scripts/check-values.mjs recomputes it from the file. Rounded to the cent, as the page states it. */
export function deliveryStat(rows: Charge[], mw: number, stat: string): number | undefined {
  const [slug, what] = stat.split(":");
  const utility = utilitiesOf(rows).find((u) => slugOf(u) === slug);
  if (!utility) return undefined;
  const d = deliveryOf(rows, utility, mw);
  const v = what === "total" ? d.total : d.components.find((c) => c.kind === what)?.perMwh;
  return v === undefined ? undefined : Math.round(v * 100) / 100;
}
