"use client";
// Session 40: the severance tax calculator. The rules (data/severance_rules.json) each cite the page that states them;
// the arithmetic is lib/severance.ts. An estimate for education and planning, not tax advice.
import { useMemo, useState } from "react";
import { compute, type Input, type Rules } from "@/lib/severance";

const usd = (v: number) => `$${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pct = (r: number) => `${(r * 100).toLocaleString("en-US", { maximumFractionDigits: 4 })}%`;
const field = "w-full border border-rule bg-panel px-2 py-1 text-sm";

export function Calculator({ rules, prices }: { rules: Rules; prices: { oil: number | null; gas: number | null; label: { oil: string; gas: string } } }) {
  const [state, setState] = useState("TX");
  const products = Object.keys(rules.states[state].products);
  const [product, setProduct] = useState("oil");
  const prod = rules.states[state].products[product] ?? rules.states[state].products[products[0]];
  const kind = product === "gas" ? "gas" : "oil";
  const [volume, setVolume] = useState(1000);
  const [price, setPrice] = useState<number | "">(prices.oil ?? "");
  const [variant, setVariant] = useState("la_oil_pre2025");
  const [choice, setChoice] = useState(0.0024);
  const [adval, setAdval] = useState(0);
  const [royaltyPct, setRoyaltyPct] = useState(0);
  const [trucking, setTrucking] = useState(0);
  const [transport, setTransport] = useState(0);
  const [option, setOption] = useState<string>("");
  const [param, setParam] = useState<Record<string, number>>({});
  const [tier, setTier] = useState<Record<string, number>>({});
  const [credit, setCredit] = useState<string>("");

  const pick = (s: string, p: string) => {
    const ps = Object.keys(rules.states[s].products);
    const np = ps.includes(p) ? p : ps[0];
    setState(s); setProduct(np); setOption(""); setCredit("");
    setPrice((np === "gas" ? prices.gas : prices.oil) ?? "");
  };
  const x: Input = {
    state, product, volume, price: typeof price === "number" ? price : 0, variant, choice, adval, royaltyPct, trucking, transport,
    option: option ? { id: option, param: param[option], tierPct: tier[option] } : undefined,
    credit: credit ? { id: credit, tierPct: tier[credit] ?? 0 } : undefined,
  };
  const r = useMemo(() => {
    try { return compute(rules, x); } catch { return null; }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(x)]);
  const src = (id: string) => rules.sources[id];
  const Cite = ({ id }: { id: string }) => <a href={src(id)?.url} className="text-xs">{src(id)?.publisher === "Louisiana State Legislature" ? "La. R.S. 47:633" : src(id)?.title}</a>;
  const rateOpts = prod.options.filter((o) => o.group === "rate");
  const credits = prod.options.filter((o) => o.group === "credit");
  const st = rules.states[state];
  const nm = state === "NM", la = state === "LA";

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <div className="space-y-3 text-sm">
        <div className="grid grid-cols-2 gap-3">
          <label className="flex flex-col">State
            <select value={state} onChange={(e) => pick(e.target.value, product)} className={field}>
              {Object.entries(rules.states).map(([k, s]) => <option key={k} value={k}>{s.name}</option>)}
            </select>
          </label>
          <label className="flex flex-col">Product
            <select value={product} onChange={(e) => pick(state, e.target.value)} className={field}>
              {Object.keys(st.products).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </label>
          <label className="flex flex-col">Monthly volume, {prod.unit}
            <input type="number" min={0} value={volume} onChange={(e) => setVolume(Math.max(0, Number(e.target.value)))} className={field} />
          </label>
          <label className="flex flex-col">Price, USD per {prod.unit}
            <input type="number" min={0} step="0.01" value={price} onChange={(e) => setPrice(e.target.value === "" ? "" : Number(e.target.value))} className={field} />
          </label>
        </div>
        <p className="text-xs text-muted">Default price (an assumption, edit it): {kind === "gas" ? prices.label.gas : prices.label.oil}. A hub price is not the value at the well, which is what the states tax.</p>
        {la && product === "oil" ? (
          <label className="flex flex-col">Well completion
            <select value={variant} onChange={(e) => setVariant(e.target.value)} className={field}>
              {prod.variants?.map((v) => <option key={v.id} value={v.id}>{v.label} ({pct(v.rate)})</option>)}
            </select>
          </label>
        ) : null}
        {la && st.value_deduction?.products.includes(product) ? (
          <label className="flex flex-col">{st.value_deduction.label}
            <input type="number" min={0} step="0.01" value={transport} onChange={(e) => setTransport(Math.max(0, Number(e.target.value)))} className={field} />
          </label>
        ) : null}
        {nm ? (
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col">Royalties to the US, NM or a tribe, % of value
              <input type="number" min={0} max={100} step="0.1" value={royaltyPct} onChange={(e) => setRoyaltyPct(Math.min(100, Math.max(0, Number(e.target.value))))} className={field} />
            </label>
            <label className="flex flex-col">Trucking, USD per {prod.unit}
              <input type="number" min={0} step="0.01" value={trucking} onChange={(e) => setTrucking(Math.max(0, Number(e.target.value)))} className={field} />
            </label>
            {product === "oil" ? (
              <label className="flex flex-col">Conservation tax rate
                <select value={choice} onChange={(e) => setChoice(Number(e.target.value))} className={field}>
                  {prod.base.find((b) => b.rate === "choice")?.choices?.map((c) => <option key={c.rate} value={c.rate}>{c.label}</option>)}
                </select>
              </label>
            ) : null}
            <label className="flex flex-col">Ad valorem production rate, % (your unit&apos;s)
              <input type="number" min={0} step="0.0001" value={adval} onChange={(e) => setAdval(Math.max(0, Number(e.target.value)))} className={field} />
            </label>
          </div>
        ) : null}
        <fieldset className="border border-rule p-2">
          <legend className="px-1 text-xs text-muted">Reduced rate or exemption (one per well and month)</legend>
          <label className="block"><input type="radio" name="opt" checked={option === ""} onChange={() => setOption("")} /> None: the base rate</label>
          {rateOpts.length === 0 ? <p className="text-xs text-muted">None listed for {st.name} {product} on the pages read (see the method).</p> : null}
          {rateOpts.map((o) => (
            <div key={o.id} className="mt-1">
              <label className="block"><input type="radio" name="opt" checked={option === o.id} onChange={() => setOption(o.id)} /> {o.name}</label>
              {option === o.id && o.kind === "rate_param" ? (
                <label className="ml-5 flex flex-col text-xs">{o.param!.label}
                  <input type="number" min={o.param!.min} max={o.param!.max} step="0.1" value={param[o.id] ?? o.param!.default} onChange={(e) => setParam({ ...param, [o.id]: Math.min(o.param!.max, Math.max(o.param!.min, Number(e.target.value))) })} className={field} />
                </label>
              ) : null}
              {option === o.id && o.kind === "credit_tier" ? (
                <select value={tier[o.id] ?? 0} onChange={(e) => setTier({ ...tier, [o.id]: Number(e.target.value) })} className={field + " ml-5 text-xs"}>
                  {o.tiers!.map((t) => <option key={t.pct} value={t.pct}>{t.label}</option>)}
                </select>
              ) : null}
            </div>
          ))}
        </fieldset>
        {credits.map((o) => (
          <div key={o.id}>
            <label className="block"><input type="checkbox" checked={credit === o.id} onChange={(e) => setCredit(e.target.checked ? o.id : "")} /> {o.name}</label>
            {credit === o.id ? (
              <select value={tier[o.id] ?? 0} onChange={(e) => setTier({ ...tier, [o.id]: Number(e.target.value) })} className={field + " ml-5 text-xs"}>
                {o.tiers!.map((t) => <option key={t.pct} value={t.pct}>{t.label}</option>)}
              </select>
            ) : null}
          </div>
        ))}
      </div>

      <div className="text-sm">
        {!r ? <p className="text-muted">Enter a volume and a price.</p> : (
          <>
            <table className="w-full">
              <tbody>
                <tr><td className="py-1">Gross value</td><td className="text-right font-mono">{usd(r.gross)}</td><td /></tr>
                {r.taxable !== r.gross ? <tr><td className="py-1">Taxable value, after the deductions the rule states</td><td className="text-right font-mono">{usd(r.taxable)}</td><td className="pl-2">{st.value_deduction ? <Cite id={st.value_deduction.cite} /> : null}</td></tr> : null}
                {r.base.map((l) => (
                  <tr key={l.id} className="border-t border-rule">
                    <td className="py-1">{l.name}, {l.basis === "per_unit" ? `$${l.rate} per ${prod.unit}` : pct(l.rate)}</td>
                    <td className="text-right font-mono">{usd(l.tax)}</td><td className="pl-2"><Cite id={l.cite} /></td>
                  </tr>
                ))}
                <tr className="border-t border-ink font-semibold"><td className="py-1">Tax at the base rate</td><td className="text-right font-mono">{usd(r.baseTotal)}</td><td /></tr>
                {r.applied.map((a) => (
                  <tr key={a.id}><td className="py-1 text-muted">{a.name}: {a.effect}</td><td /><td className="pl-2"><Cite id={a.cite} /></td></tr>
                ))}
                <tr className="font-semibold"><td className="py-1">Tax with the exemptions chosen</td><td className="text-right font-mono">{usd(r.withTotal)}</td><td /></tr>
                <tr className="font-semibold text-[var(--color-down)]"><td className="py-1">Savings</td><td className="text-right font-mono">{usd(r.savings)}</td><td /></tr>
                {r.fees.map((f) => (
                  <tr key={f.id} className="border-t border-rule"><td className="py-1 text-muted">{f.name} (a fee, not in the tax or the savings)</td><td className="text-right font-mono text-muted">{usd(f.amount)}</td><td className="pl-2"><Cite id={f.cite} /></td></tr>
                ))}
              </tbody>
            </table>
            {[...rateOpts, ...credits].filter((o) => o.id === option || o.id === credit).map((o) => (
              <div key={o.id} className="mt-3 border-l-2 border-accent pl-2 text-xs">
                <p><strong>{o.name}.</strong> Who qualifies: {o.who}. What it reduces: {o.what}.{o.how_long ? ` How long: ${o.how_long}.` : ""}</p>
                <p className="text-muted">&quot;{o.quote}&quot; (<Cite id={o.cite} />)</p>
              </div>
            ))}
            <p className="mt-3 text-xs text-muted">{st.basis_note}</p>
          </>
        )}
      </div>
    </div>
  );
}
