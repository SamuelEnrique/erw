// Session 40: the severance tax calculator's arithmetic, on the rules of data/severance_rules.json (each rule cites the
// page that states it; docs/methods/severance.md). Shared by /severance (server defaults, the reader's inputs in the
// browser) and site/scripts/test-severance.mjs. No imports: Node runs this file as it is. An estimate for education and
// planning, not tax advice.

export type Base = {
  id: string; name: string; basis: "pct_value" | "per_unit"; rate: number | "variant" | "choice" | "input";
  choices?: { label: string; rate: number }[]; input?: { label: string; default: number };
  effective: string | null; cite: string; quote: string; cite2?: string; quote2?: string;
};
export type Option = {
  id: string; group: "rate" | "credit"; name: string;
  kind: "rate" | "rate_param" | "per_unit" | "exempt_pct" | "credit_tier";
  rate?: number | null; pct?: number; exempt_below_price?: number;
  param?: { label: string; min: number; max: number; default: number };
  tiers?: { label: string; pct: number }[];
  who: string; what: string; how_long: string | null; cite: string; quote: string; cite2?: string; quote2?: string;
};
export type Product = {
  unit: string; base: Base[]; fees: { id: string; name: string; per_unit: number; effective: string | null; cite: string; quote: string }[];
  options: Option[]; variants?: { id: string; label: string; rate: number }[];
};
export type State = {
  name: string; basis_note: string; rates_as_of?: string;
  value_deduction?: { products: string[]; royalty?: boolean; label: string; cite: string; quote: string };
  products: Record<string, Product>;
};
export type Rules = { version: string; sources: Record<string, { publisher: string; title: string; url: string }>; states: Record<string, State> };

export type Input = {
  state: string; product: string; volume: number; price: number;
  variant?: string;                         // Louisiana oil: the well's completion date
  choice?: number;                          // New Mexico oil: the conservation rate chosen
  adval?: number;                           // New Mexico: the unit's ad valorem production rate, percent
  royaltyPct?: number; trucking?: number;   // New Mexico: royalties (percent of value) and trucking (USD per unit)
  transport?: number;                       // Louisiana oil and condensate: trucking, barging and pipeline, USD per bbl
  option?: { id: string; param?: number; tierPct?: number };  // one rate-group option
  credit?: { id: string; tierPct: number };                   // one credit-group option (Texas oil)
};
export type Line = { id: string; name: string; rate: number; basis: string; tax: number; cite: string };
export type Result = {
  gross: number; taxable: number; perUnitValue: number;
  base: Line[]; baseTotal: number; withTotal: number; savings: number;
  applied: { id: string; name: string; effect: string; cite: string }[];
  fees: { id: string; name: string; amount: number; cite: string }[];
};

function baseRate(b: Base, p: Product, x: Input): number {
  if (typeof b.rate === "number") return b.rate;
  if (b.rate === "variant") {
    const v = p.variants?.find((w) => w.id === x.variant) ?? p.variants?.[0];
    if (!v) throw new Error(`${b.id}: no variant`);
    return v.rate;
  }
  if (b.rate === "choice") return x.choice ?? b.choices![0].rate;
  return (x.adval ?? b.input?.default ?? 0) / 100;
}

export function compute(rules: Rules, x: Input): Result {
  const st = rules.states[x.state];
  const p = st?.products[x.product];
  if (!p) throw new Error(`no rules for ${x.state} ${x.product}`);
  const gross = x.volume * x.price;
  // the deductions each state's rule states: Louisiana's transport on oil and condensate, New Mexico's royalties and trucking
  let taxable = gross;
  const vd = st.value_deduction;
  if (vd && vd.products.includes(x.product)) {
    if (vd.royalty) taxable = gross - gross * ((x.royaltyPct ?? 0) / 100) - x.volume * (x.trucking ?? 0);
    else taxable = gross - x.volume * (x.transport ?? 0);
  }
  taxable = Math.max(0, taxable);
  const perUnitValue = x.volume > 0 ? taxable / x.volume : 0;
  const base: Line[] = p.base.map((b) => {
    const rate = baseRate(b, p, x);
    return { id: b.id, name: b.name, rate, basis: b.basis, tax: b.basis === "per_unit" ? x.volume * rate : taxable * rate, cite: b.cite };
  });
  const baseTotal = base.reduce((a, l) => a + l.tax, 0);
  let withTotal = baseTotal;
  const applied: Result["applied"] = [];
  const opt = x.option ? p.options.find((o) => o.id === x.option!.id && o.group === "rate") : undefined;
  if (x.option && !opt) throw new Error(`${x.option.id}: not a rate option of ${x.state} ${x.product}`);
  if (opt) {
    const first = base[0];
    const rest = baseTotal - first.tax;
    let tax = first.tax, effect = "";
    if (opt.kind === "rate") {
      tax = taxable * (opt.rate as number);
      effect = `${((opt.rate as number) * 100).toFixed(3).replace(/\.?0+$/, "")} percent of value`;
      if (opt.exempt_below_price !== undefined && perUnitValue < opt.exempt_below_price) {
        tax = 0;
        effect += `; exempt, the value is below $${opt.exempt_below_price} per ${p.unit}`;
      }
    } else if (opt.kind === "per_unit") {
      tax = x.volume * (opt.rate as number);
      effect = `${((opt.rate as number) * 100).toFixed(4).replace(/\.?0+$/, "")} cents per ${p.unit}`;
    } else if (opt.kind === "rate_param") {
      const v = x.option!.param ?? opt.param!.default;
      const r = opt.rate == null ? v / 100 : (opt.rate as number) * (1 - v / 100);
      tax = taxable * r;
      effect = `${(r * 100).toFixed(4).replace(/\.?0+$/, "")} percent of value`;
    } else if (opt.kind === "exempt_pct") {
      tax = first.tax * (1 - (opt.pct as number) / 100);
      effect = `${opt.pct} percent of the tax exempt`;
    } else if (opt.kind === "credit_tier") {
      const pct = x.option!.tierPct ?? 0;
      tax = first.tax * (1 - pct / 100);
      effect = `a ${pct} percent credit`;
    }
    withTotal = rest + tax;
    applied.push({ id: opt.id, name: opt.name, effect, cite: opt.cite });
  }
  const cr = x.credit ? p.options.find((o) => o.id === x.credit!.id && o.group === "credit") : undefined;
  if (x.credit && !cr) throw new Error(`${x.credit.id}: not a credit of ${x.state} ${x.product}`);
  if (cr) {
    withTotal = withTotal * (1 - x.credit!.tierPct / 100);
    applied.push({ id: cr.id, name: cr.name, effect: `a ${x.credit!.tierPct} percent credit`, cite: cr.cite });
  }
  const fees = p.fees.map((f) => ({ id: f.id, name: f.name, amount: x.volume * f.per_unit, cite: f.cite }));
  return { gross, taxable, perUnitValue, base, baseTotal, withTotal, savings: baseTotal - withTotal, applied, fees };
}
